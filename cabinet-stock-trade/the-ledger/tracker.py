#!/usr/bin/env python3
"""
Gov Trades Tracker — data agent.

Pulls disclosure data from FREE, PUBLIC sources and writes JSON into ./data,
which the static index.html dashboard reads. Designed to run locally or as a
scheduled GitHub Action. No paid keys required for the core data.

Sources (all public):
  - Congress trades : House & Senate Stock Watcher open datasets (STOCK Act PTRs)
  - Corporate insiders : SEC EDGAR full-text search for Form 4 filings
  - Federal contracts : USASpending.gov award search API (DHS + DoD)
  - Executive branch  : pointers to OGE 278 disclosures (NO trade stream exists)

Optional AI layer:
  - If ANTHROPIC_API_KEY is set, generates a plain-English summary per dataset.

Honesty notes baked in:
  - The President and Cabinet do NOT file periodic transaction reports. There is
    no weekly buy/sell feed for them. We surface their actual OGE filings instead.
  - All amounts in congressional data are DISCLOSED RANGES, not exact figures,
    and arrive on a lag of up to 45 days.
"""

from __future__ import annotations

import json
import os
import sys
import time
import datetime as dt
from collections import Counter, defaultdict
from urllib import request, error

# --------------------------------------------------------------------------- #
# Config — every endpoint is overridable so you can repoint if a URL changes.
# --------------------------------------------------------------------------- #
CONFIG = {
    "lookback_days": 183,  # ~6 months
    "user_agent": os.environ.get(
        "TRACKER_UA",
        "gov-trades-tracker/1.0 (open-source research; set TRACKER_UA to your email)",
    ),
    "endpoints": {
        # House & Senate Stock Watcher publish open JSON. Verify these resolve;
        # community-maintained mirrors occasionally move.
        "house": "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json",
        "senate": "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json",
        # SEC EDGAR full-text search (Form 4 = insider transactions).
        "sec_form4": "https://efts.sec.gov/LATEST/search-index?q=%22%22&forms=4",
        # USASpending award search (POST).
        "usaspending": "https://api.usaspending.gov/api/v2/search/spending_by_award/",
    },
    # Toptier agency names as USASpending recognizes them.
    "agencies": {
        "DHS": "Department of Homeland Security",
        "DoD": "Department of Defense",
    },
    "data_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
}

NOW = dt.datetime.now(dt.timezone.utc)
CUTOFF = NOW - dt.timedelta(days=CONFIG["lookback_days"])


# --------------------------------------------------------------------------- #
# HTTP helpers
# --------------------------------------------------------------------------- #
def _get(url: str, timeout: int = 60) -> bytes:
    req = request.Request(url, headers={"User-Agent": CONFIG["user_agent"]})
    with request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _post_json(url: str, payload: dict, timeout: int = 60) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "User-Agent": CONFIG["user_agent"],
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _parse_date(s: str) -> dt.datetime | None:
    if not s:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y", "%Y-%m-%dT%H:%M:%S"):
        try:
            d = dt.datetime.strptime(s.strip()[:19], fmt)
            return d.replace(tzinfo=dt.timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


# --------------------------------------------------------------------------- #
# 1) Congressional trades (House + Senate Stock Watcher)
# --------------------------------------------------------------------------- #
def fetch_congress() -> dict:
    out = {"status": "ok", "source": "House/Senate Stock Watcher (STOCK Act PTRs)",
           "transactions": [], "error": None}
    rows = []

    for chamber, url in (("house", CONFIG["endpoints"]["house"]),
                         ("senate", CONFIG["endpoints"]["senate"])):
        try:
            raw = json.loads(_get(url).decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            out["status"] = "partial"
            out["error"] = f"{chamber}: {e}"
            continue

        for t in raw:
            # Field names differ slightly between the two datasets; normalize.
            tx_date = _parse_date(t.get("transaction_date") or t.get("transactionDate") or "")
            if tx_date and tx_date < CUTOFF:
                continue
            ttype = (t.get("type") or t.get("transaction_type") or "").lower()
            rows.append({
                "chamber": chamber,
                "name": t.get("representative") or t.get("senator") or t.get("name") or "Unknown",
                "ticker": (t.get("ticker") or "").upper().replace("--", ""),
                "asset": t.get("asset_description") or t.get("asset") or "",
                "type": ("buy" if "purchase" in ttype or "buy" in ttype
                         else "sell" if "sale" in ttype or "sell" in ttype
                         else ttype or "other"),
                "amount_range": t.get("amount") or "",
                "date": tx_date.strftime("%Y-%m-%d") if tx_date else "",
                "is_option": "option" in (t.get("asset_description") or "").lower(),
            })

    out["transactions"] = rows
    return out


# --------------------------------------------------------------------------- #
# 2) Corporate insiders (SEC EDGAR Form 4)
# --------------------------------------------------------------------------- #
def fetch_insiders() -> dict:
    out = {"status": "ok", "source": "SEC EDGAR Form 4 full-text search",
           "filings": [], "error": None}
    try:
        raw = json.loads(_get(CONFIG["endpoints"]["sec_form4"]).decode("utf-8"))
        hits = raw.get("hits", {}).get("hits", [])
        for h in hits[:200]:
            src = h.get("_source", {})
            out["filings"].append({
                "company": (src.get("display_names") or ["?"])[0],
                "form": src.get("file_type") or "4",
                "filed": src.get("file_date") or "",
                "accession": h.get("_id", ""),
            })
    except Exception as e:  # noqa: BLE001
        out["status"] = "error"
        out["error"] = str(e)
    return out


# --------------------------------------------------------------------------- #
# 3) Federal contracts (USASpending) — DHS + DoD
# --------------------------------------------------------------------------- #
def fetch_contracts() -> dict:
    out = {"status": "ok", "source": "USASpending.gov award search",
           "agencies": {}, "error": None}
    start = CUTOFF.strftime("%Y-%m-%d")
    end = NOW.strftime("%Y-%m-%d")

    for label, agency_name in CONFIG["agencies"].items():
        payload = {
            "filters": {
                "time_period": [{"start_date": start, "end_date": end}],
                "agencies": [{"type": "awarding", "tier": "toptier", "name": agency_name}],
                "award_type_codes": ["A", "B", "C", "D"],  # contracts
            },
            "fields": ["Award ID", "Recipient Name", "Award Amount",
                       "Awarding Agency", "Description"],
            "sort": "Award Amount",
            "order": "desc",
            "limit": 25,
            "page": 1,
        }
        try:
            res = _post_json(CONFIG["endpoints"]["usaspending"], payload)
            awards = []
            for a in res.get("results", []):
                awards.append({
                    "recipient": a.get("Recipient Name", ""),
                    "amount": a.get("Award Amount", 0),
                    "description": (a.get("Description") or "")[:160],
                    "award_id": a.get("Award ID", ""),
                })
            out["agencies"][label] = awards
            time.sleep(0.5)
        except Exception as e:  # noqa: BLE001
            out["status"] = "partial"
            out["error"] = f"{label}: {e}"
            out["agencies"][label] = []
    return out


# --------------------------------------------------------------------------- #
# 4) Executive branch — honest pointer, NOT a trade stream
# --------------------------------------------------------------------------- #
def build_executive() -> dict:
    return {
        "status": "info",
        "source": "U.S. Office of Government Ethics (OGE) public disclosures",
        "note": ("The President and Cabinet secretaries do NOT file periodic "
                 "transaction reports. No dated weekly buy/sell feed exists for "
                 "them. They file annual OGE Form 278e disclosures showing assets "
                 "and broad income ranges. Those are the real records — linked below."),
        "filings_portal": "https://extapps2.oge.gov/201/Presiden.nsf",
        "search": "https://www.oge.gov/web/oge.nsf/Officials%20Individual%20Disclosures%20Search%20Collection",
    }


# --------------------------------------------------------------------------- #
# Aggregation: per-ticker stats, buy/sell counts, options
# --------------------------------------------------------------------------- #
def summarize_congress(tx: list[dict]) -> dict:
    by_ticker = defaultdict(lambda: {"buy": 0, "sell": 0, "options": 0, "names": set()})
    buys = sells = options = 0
    for t in tx:
        tk = t["ticker"] or "(undisclosed)"
        if t["type"] == "buy":
            by_ticker[tk]["buy"] += 1
            buys += 1
        elif t["type"] == "sell":
            by_ticker[tk]["sell"] += 1
            sells += 1
        if t["is_option"]:
            by_ticker[tk]["options"] += 1
            options += 1
        by_ticker[tk]["names"].add(t["name"])

    table = []
    for tk, s in by_ticker.items():
        table.append({
            "ticker": tk, "buy": s["buy"], "sell": s["sell"],
            "options": s["options"], "net": s["buy"] - s["sell"],
            "traders": len(s["names"]),
            "total": s["buy"] + s["sell"],
        })
    table.sort(key=lambda r: r["total"], reverse=True)

    top_buyers = Counter(t["name"] for t in tx if t["type"] == "buy").most_common(15)
    return {
        "totals": {"buys": buys, "sells": sells, "options": options,
                   "transactions": len(tx), "tickers": len(by_ticker)},
        "by_ticker": table[:100],
        "most_active": [{"name": n, "trades": c} for n, c in top_buyers],
    }


# --------------------------------------------------------------------------- #
# Optional AI summary (only if a key is present)
# --------------------------------------------------------------------------- #
def ai_summary(payload: dict) -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 600,
            "messages": [{
                "role": "user",
                "content": ("In 4-6 sentences, summarize notable patterns in this "
                            "6-month government-trade dataset for a finance-savvy "
                            "reader. Be factual, flag the 45-day lag and that amounts "
                            "are ranges, and do not give investment advice.\n\n"
                            + json.dumps(payload)[:6000]),
            }],
        }).encode()
        req = request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return "".join(b.get("text", "") for b in data.get("content", []))
    except Exception as e:  # noqa: BLE001
        return f"(AI summary unavailable: {e})"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def write(name: str, obj: dict) -> None:
    path = os.path.join(CONFIG["data_dir"], name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    print(f"  wrote {path}")


def main() -> int:
    os.makedirs(CONFIG["data_dir"], exist_ok=True)
    print(f"Gov Trades Tracker — run {NOW.isoformat()}  (lookback {CONFIG['lookback_days']}d)")

    print("[1/4] Congress…")
    congress = fetch_congress()
    congress["summary"] = summarize_congress(congress["transactions"])

    print("[2/4] Insiders (SEC Form 4)…")
    insiders = fetch_insiders()

    print("[3/4] Contracts (DHS/DoD)…")
    contracts = fetch_contracts()

    print("[4/4] Executive branch (OGE pointers)…")
    executive = build_executive()

    manifest = {
        "generated_utc": NOW.isoformat(),
        "lookback_days": CONFIG["lookback_days"],
        "cutoff_utc": CUTOFF.isoformat(),
        "sources": {
            "congress": congress["status"],
            "insiders": insiders["status"],
            "contracts": contracts["status"],
            "executive": executive["status"],
        },
        "headline": {
            "congress_buys": congress["summary"]["totals"]["buys"],
            "congress_sells": congress["summary"]["totals"]["sells"],
            "congress_options": congress["summary"]["totals"]["options"],
            "congress_transactions": congress["summary"]["totals"]["transactions"],
        },
        "disclaimer": ("Amounts are disclosed ranges, not exact figures. Filings lag "
                       "up to 45 days. Executive branch has no trade stream. "
                       "Informational only — not investment advice."),
    }
    manifest["ai_summary"] = ai_summary(manifest["headline"])

    write("congress.json", congress)
    write("insiders.json", insiders)
    write("contracts.json", contracts)
    write("executive.json", executive)
    write("manifest.json", manifest)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

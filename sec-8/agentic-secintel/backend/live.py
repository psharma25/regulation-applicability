"""Live, on-demand data fetch.

Primary source: SEC EDGAR full-text search (https://efts.sec.gov/LATEST/search-index).
It is free, keyless, and real-time — the best public source you can hit on demand with
no credentials. We pull the most recent Form 8-K cyber-incident disclosures (Item 1.05
material incidents, plus voluntary cyber 8-Ks) and merge them into the live view.

SEC asks every automated client to send a descriptive User-Agent with contact info.
Set it once:   export SEC_USER_AGENT="Your Name your@email.com"

Hooks for PRC Data Breach Chronology and individual state-AG portals are stubbed at the
bottom — those require purchased datasets or per-site scraping, so they're opt-in.
"""
import os, re, json, datetime, requests
from concurrent.futures import ThreadPoolExecutor, as_completed

EFTS = "https://efts.sec.gov/LATEST/search-index"
UA = os.environ.get("SEC_USER_AGENT", "SecIntel research client admin@example.com")
LIVE_PATH = os.path.join(os.path.dirname(__file__), "data", "live_incidents.json")
ENRICH = os.environ.get("LIVE_ENRICH", "1") == "1"            # open each filing and extract fields
ENRICH_LIMIT = int(os.environ.get("LIVE_ENRICH_LIMIT", "12"))  # cap filings fetched per refresh

# queries run on each refresh; (label that becomes sec_item, query, forms)
QUERIES = [
    ("1.05", '"Item 1.05"', "8-K"),
    ("8.01 (cyber)", '"cybersecurity incident"', "8-K"),
]


def _headers():
    return {"User-Agent": UA, "Accept": "application/json"}


def _filing_url(hit):
    src = hit.get("_source", {})
    _id = hit.get("_id", "")
    acc, _, fname = _id.partition(":")
    acc_nodash = acc.replace("-", "")
    ciks = src.get("ciks") or ["0"]
    try:
        cik = int(ciks[0])
    except (ValueError, TypeError):
        cik = ciks[0]
    if acc_nodash and fname:
        return f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{fname}"
    return f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}"


def _entity(src):
    names = src.get("display_names") or ["Unknown filer"]
    return names[0].split("  (")[0].strip()


def _parse_hits(payload, sec_item):
    out = []
    hits = (payload.get("hits") or {}).get("hits") or []
    for h in hits:
        src = h.get("_source", {})
        date = src.get("file_date", "")
        ent = _entity(src)
        acc = h.get("_id", "").partition(":")[0]
        out.append({
            "id": f"sec-{acc}" if acc else f"sec-{ent[:20]}-{date}",
            "entity": ent,
            "product": "SEC Form 8-K filing",
            "domains": ["SEC 8-K (live)"],
            "year": (date or "")[:4],
            "date_disclosed": date,
            "threat_type": "Cyber incident disclosed on Form 8-K (read filing for detail)",
            "threat_category": "Disclosed cyber incident (8-K)",
            "impacted": "Disclosed in filing — open source link",
            "unit": "filing",
            "impacted_num": 0,
            "reported_state_ag": False,
            "reported_sec": True,
            "sec_item": sec_item,
            "nation_state": False,
            "attribution": "",
            "financial_loss_usd": None,
            "financial_loss": "See filing",
            "data_types": "See filing",
            "reputational_impact": "",
            "summary": "",
            "enriched": False,
            "source": _filing_url(h),
        })
    return out


def _strip_html(html):
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&#160;", " ").replace("&#8217;", "'").replace("&rsquo;", "'")
                .replace("&#8220;", '"').replace("&#8221;", '"').replace("&ldquo;", '"').replace("&rdquo;", '"'))
    return re.sub(r"\s+", " ", text).strip()


NATION_TERMS = {
    "china": "China", "chinese": "China", "russia": "Russia", "russian": "Russia",
    "iran": "Iran", "iranian": "Iran", "north korea": "North Korea", "dprk": "North Korea",
    "state-sponsored": "State-sponsored", "state sponsored": "State-sponsored",
    "nation-state": "Nation-state", "nation state": "Nation-state",
}
ACTOR_TERMS = ["alphv", "blackcat", "lockbit", "cl0p", "clop", "scattered spider",
               "midnight blizzard", "lazarus", "lapsus", "akira", "rhysida", "play ransomware"]
THREATS = [
    (r"ransom", "Ransomware"),
    (r"unauthorized (third part|access|actor)", "Unauthorized access"),
    (r"phish", "Phishing"),
    (r"business email compromise|bec\b", "Business email compromise"),
    (r"denial[- ]of[- ]service|ddos", "Denial of service"),
    (r"social engineer", "Social engineering"),
]
MONEY = re.compile(r"\$\s?([\d][\d,\.]*)\s?(billion|million|bn|mm|m|b)\b", re.I)


def _extract_fields(text):
    low = text.lower()
    out = {}

    # threat category
    for pat, label in THREATS:
        if re.search(pat, low):
            out["threat_category"] = label
            break

    # attribution / nation-state
    found_nation, found_actor = [], []
    for term, label in NATION_TERMS.items():
        if term in low and label not in found_nation:
            found_nation.append(label)
    for a in ACTOR_TERMS:
        if a in low:
            found_actor.append(a.title())
    attribution = "; ".join(found_nation + found_actor)
    if attribution:
        out["attribution"] = attribution
    out["nation_state"] = bool(found_nation)

    # financial impact — prefer a $ figure near impact/cost/expense/material language
    best = None
    for m in MONEY.finditer(text):
        ctx = low[max(0, m.start() - 80): m.end() + 80]
        score = sum(w in ctx for w in ("cost", "expense", "impact", "material", "loss", "incur", "charge"))
        if best is None or score > best[0]:
            best = (score, m.group(0).strip())
    if best:
        out["financial_loss"] = re.sub(r"\s+", " ", best[1])

    # summary — first sentence mentioning the incident
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for s in sentences:
        sl = s.lower()
        if any(k in sl for k in ("cybersecurity incident", "unauthorized", "ransom", "threat actor",
                                  "security incident", "material")):
            if 40 <= len(s) <= 400:
                out["summary"] = s.strip()
                break
    return out


def _enrich_row(row):
    try:
        r = requests.get(row["source"], headers={"User-Agent": UA}, timeout=15)
        r.raise_for_status()
        text = _strip_html(r.text)
        fields = _extract_fields(text)
        for k, v in fields.items():
            if v not in (None, "", []):
                row[k] = v
        if fields.get("summary"):
            row["impacted"] = "See summary / filing"
        row["enriched"] = True
    except Exception as e:
        row["enriched"] = False
        row["summary"] = ""
    return row


def _enrich(rows):
    targets = rows[:ENRICH_LIMIT]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(_enrich_row, r) for r in targets]
        for _ in as_completed(futures):
            pass
    return rows


def fetch_sec(limit_per_query=40, dedupe=True):
    rows, seen = [], set()
    for sec_item, q, forms in QUERIES:
        try:
            r = requests.get(EFTS, params={"q": q, "forms": forms}, headers=_headers(), timeout=20)
            r.raise_for_status()
            parsed = _parse_hits(r.json(), sec_item)
        except Exception as e:
            parsed = []
            print(f"[live] query {q!r} failed: {e}")
        for row in parsed[:limit_per_query]:
            if dedupe and row["id"] in seen:
                continue
            seen.add(row["id"])
            rows.append(row)
    rows.sort(key=lambda x: x.get("date_disclosed", ""), reverse=True)
    return rows


def refresh():
    """Pull latest, optionally open each filing to extract fields, persist, return summary."""
    rows = fetch_sec()
    if ENRICH and rows:
        rows = _enrich(rows)
    enriched = sum(1 for r in rows if r.get("enriched"))
    payload = {
        "fetched_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "SEC EDGAR full-text search (efts.sec.gov)",
        "count": len(rows),
        "enriched": enriched,
        "incidents": rows,
    }
    os.makedirs(os.path.dirname(LIVE_PATH), exist_ok=True)
    with open(LIVE_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    return {"count": len(rows), "enriched": enriched,
            "fetched_at": payload["fetched_at"], "source": payload["source"]}


def load_live():
    if os.path.exists(LIVE_PATH):
        try:
            return json.load(open(LIVE_PATH))
        except Exception:
            return None
    return None


# --- opt-in hooks for additional sources (require access / scraping) -----------
def fetch_prc():  # Privacy Rights Clearinghouse — purchased dataset; add your loader here.
    return []


def fetch_state_ag(state):  # e.g. CA/WA/TX portals — per-site scraping; add per state.
    return []


if __name__ == "__main__":  # offline self-test of the parser
    sample = {"hits": {"hits": [
        {"_id": "0001193125-24-011295:d708866d8k.htm",
         "_source": {"ciks": ["0000789019"], "display_names": ["MICROSOFT CORP  (MSFT)  (CIK 0000789019)"], "file_date": "2024-01-19", "form": "8-K"}},
    ]}}
    parsed = _parse_hits(sample, "1.05")
    assert parsed[0]["entity"] == "MICROSOFT CORP"
    assert parsed[0]["source"] == "https://www.sec.gov/Archives/edgar/data/789019/000119312524011295/d708866d8k.htm"
    assert parsed[0]["reported_sec"] is True and parsed[0]["domains"] == ["SEC 8-K (live)"]

    doc = ("<html><body><p>On January 12, 2024, the Company detected a cybersecurity "
           "incident involving unauthorized access by a nation-state threat actor "
           "attributed to Russia. The Company expects to incur costs of approximately "
           "$25 million related to the incident, which it does not believe is material.</p>"
           "<p>The threat actor used a ransomware tool.</p></body></html>")
    f = _extract_fields(_strip_html(doc))
    assert f["nation_state"] is True, f
    assert "Russia" in f["attribution"], f
    assert f["threat_category"] in ("Unauthorized access", "Ransomware"), f
    assert "$25 million" in f["financial_loss"], f
    assert "cybersecurity incident" in f["summary"].lower(), f
    print("self-test OK")
    print("  url   :", parsed[0]["source"])
    print("  fields:", json.dumps(f, indent=2))

"""Multi-source incident tracker — runs on demand from the dashboard button.

Pulls ALL security incidents / breaches it can reach from:
  • SEC EDGAR full-text search (efts.sec.gov) — Form 8-K (Item 1.05) AND Form 10-K
    (Item 1C Cybersecurity), paginated, filtered to 2025–2026.
  • HHS OCR "Breach Portal" (ocrportal.hhs.gov) — HIPAA breaches of 500+ individuals.
  • State Attorney-General breach portals — Massachusetts (mass.gov), California,
    Washington, Oregon, Maine, Montana, Maryland, Iowa, New Hampshire, Vermont, etc.
    Every state is FETCHED and parsed best-effort; whatever returns a readable table
    becomes records, the rest report status="manual" with the portal URL.

Each record records WHERE it came from (`source` URL + `source_feed` label) and the
provenance panel lists every source's status + count. Nothing is fabricated: a source
that can't be fetched/parsed is reported as manual/unavailable with its URL.

SEC asks for a descriptive User-Agent:  export SEC_USER_AGENT="Your Name your@email.com"
"""
import os, re, json, datetime, requests
from concurrent.futures import ThreadPoolExecutor, as_completed

import live  # reuse _filing_url, _entity, _strip_html, _extract_fields, _enrich_row, ENRICH_LIMIT

UA = os.environ.get("SEC_USER_AGENT", "SecIntel research client admin@example.com")
LIVE_PATH = os.path.join(os.path.dirname(__file__), "data", "live_incidents.json")
EFTS = "https://efts.sec.gov/LATEST/search-index"
START = os.environ.get("TRACKER_START", "2025-01-01")
TODAY = datetime.date.today().isoformat()
SEC_PAGES = int(os.environ.get("TRACKER_SEC_PAGES", "6"))      # 10 hits/page
STATE_LIMIT = int(os.environ.get("TRACKER_STATE_LIMIT", "60"))  # max rows kept per state


def _rec(**kw):
    base = dict(id="", entity="Unknown", product="", domains=["Live"], sector="Other",
                year="", date_disclosed="", threat_type="", threat_category="Disclosed (see source)",
                impacted="See source", unit="filing", impacted_num=0, states=[],
                reported_state_ag=False, reported_sec=False, reported_hhs=False, sec_item="",
                nation_state=False, attribution="", financial_loss_usd=None, financial_loss="See source",
                data_types="See source", reputational_impact="", summary="", enriched=False,
                source_feed="", source="")
    base.update(kw)
    return base


def _hdr(json_accept=False):
    h = {"User-Agent": UA}
    if json_accept:
        h["Accept"] = "application/json"
    return h


# ----------------------------------------------------------------- SEC (paginated)
def _efts(query, form):
    hits = []
    for p in range(SEC_PAGES):
        try:
            r = requests.get(EFTS, params={"q": query, "forms": form, "dateRange": "custom",
                                           "startdt": START, "enddt": TODAY, "from": p * 10},
                             headers=_hdr(True), timeout=20)
            r.raise_for_status()
            page = (r.json().get("hits") or {}).get("hits") or []
        except Exception as e:
            if not hits:
                raise
            break
        if not page:
            break
        hits += page
        if len(page) < 10:
            break
    return hits


def _sec(form, sec_item, feed, domain, queries, enrich=False):
    seen, rows = set(), []
    try:
        hits = []
        for q in queries:
            hits += _efts(q, form)
    except Exception as e:
        return [], {"status": "unavailable", "note": str(e)[:120]}
    for h in hits:
        acc = h.get("_id", "").partition(":")[0]
        if acc in seen:
            continue
        seen.add(acc)
        src = h.get("_source", {})
        date = src.get("file_date", "")
        rows.append(_rec(
            id=f"{feed.lower().replace(' ', '')}-{acc}" if acc else f"{feed}-{date}",
            entity=live._entity(src), product=f"SEC {form} filing",
            domains=[domain], sector="SEC filer", year=date[:4], date_disclosed=date,
            threat_type=f"Cyber disclosure on Form {form} (read filing for detail)",
            threat_category=f"Disclosed cyber ({form})", impacted="Disclosed in filing",
            reported_sec=True, sec_item=sec_item, source_feed=feed, source=live._filing_url(h)))
    if enrich and rows:
        with ThreadPoolExecutor(max_workers=4) as ex:
            list(as_completed([ex.submit(live._enrich_row, x) for x in rows[:live.ENRICH_LIMIT]]))
    return rows, {"status": "ok" if rows else "empty", "note": f"{len(rows)} filings {START}…{TODAY}"}


# ----------------------------------------------------------------- HTML table helper
def _rows_from_tables(html, max_rows=400):
    out = []
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", html):
        cells = [re.sub(r"\s+", " ", live._strip_html(td)).strip()
                 for td in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
        if cells and any(cells):
            out.append(cells)
        if len(out) >= max_rows:
            break
    return out


def _num(s):
    m = re.search(r"[\d,]{2,}", s or "")
    return int(m.group(0).replace(",", "")) if m else 0


def _yr(s):
    m = re.search(r"(20\d\d)", s or "")
    return m.group(1) if m else ""


def _looks_header(cells):
    j = " ".join(cells).lower()
    return any(w in j for w in ("organization", "covered entity", "name of", "business name", "entity name", "company"))


# ----------------------------------------------------------------- HHS OCR
HHS_URL = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"


def _hhs():
    try:
        r = requests.get(HHS_URL, headers=_hdr(), timeout=30)
        r.raise_for_status()
        rows = _rows_from_tables(r.text)
    except Exception as e:
        return [], {"status": "manual", "note": "fetch failed — export from portal: " + str(e)[:70], "url": HHS_URL}
    recs = []
    for c in rows:
        if len(c) < 5 or _looks_header(c):
            continue
        name, st = c[0], (c[1] if len(c) > 1 else "")
        affected = _num(c[3]) if len(c) > 3 else 0
        date = c[4] if len(c) > 4 else ""
        btype = c[5] if len(c) > 5 else "HIPAA breach"
        if not name or not _yr(date):
            continue
        recs.append(_rec(
            id=f"hhs-{re.sub(r'[^a-z0-9]+', '-', name.lower())[:28]}-{_yr(date)}",
            entity=name, product="HIPAA-regulated entity", domains=["HHS OCR (live)"],
            sector="Healthcare", year=_yr(date), date_disclosed=date,
            threat_type=btype, threat_category=btype,
            impacted=f"{affected:,} individuals" if affected else "See portal", unit="individuals",
            impacted_num=affected, states=[st] if re.fullmatch(r"[A-Z]{2}", st or "") else [],
            reported_hhs=True, source_feed="HHS OCR", source=HHS_URL))
        if len(recs) >= 200:
            break
    if recs:
        return recs, {"status": "ok", "note": f"{len(recs)} from portal table", "url": HHS_URL}
    return [], {"status": "manual", "note": "portal is interactive — export CSV from the site", "url": HHS_URL}


# ----------------------------------------------------------------- State AG portals
# (name, url). Every one is fetched + parsed best-effort.
STATE_PORTALS = {
    "MA": ("Massachusetts", "https://www.mass.gov/lists/data-breach-notification-reports"),
    "CA": ("California", "https://oag.ca.gov/privacy/databreach/list"),
    "WA": ("Washington", "https://www.atg.wa.gov/data-breach-notifications"),
    "OR": ("Oregon", "https://justice.oregon.gov/consumer/DataBreach/"),
    "ME": ("Maine", "https://www.maine.gov/agviewer/content/ag/985235c7-cb95-4be2-8792-a1252b4f8318/list.html"),
    "MT": ("Montana", "https://dojmt.gov/consumer/databreach/"),
    "MD": ("Maryland", "https://www.marylandattorneygeneral.gov/Pages/IdentityTheft/breachnotices.aspx"),
    "IA": ("Iowa", "https://www.iowaattorneygeneral.gov/for-consumers/security-breach-notifications"),
    "NH": ("New Hampshire", "https://www.doj.nh.gov/consumer/security-breaches/"),
    "VT": ("Vermont", "https://ago.vermont.gov/consumer-protection-data-breaches"),
    "TX": ("Texas", "https://oag.my.site.com/datasecuritybreachreport/apex/DataSecurityReportsPage"),
    "NY": ("New York", "https://ag.ny.gov/internet/data-breach"),
    "IL": ("Illinois", "https://illinoisattorneygeneral.gov/"),
    "DE": ("Delaware", "https://attorneygeneral.delaware.gov/fraud/cpu/securitybreachnotification/database/"),
    "WI": ("Wisconsin", "https://datcp.wi.gov/Pages/Programs_Services/DataBreaches.aspx"),
    "IN": ("Indiana", "https://www.in.gov/attorneygeneral/consumer-protection-division/id-theft-prevention/security-breaches/"),
}


def _state(code):
    name, url = STATE_PORTALS[code]
    try:
        r = requests.get(url, headers=_hdr(), timeout=25)
        r.raise_for_status()
        rows = _rows_from_tables(r.text)
    except Exception as e:
        return [], {"status": "manual", "note": "fetch failed: " + str(e)[:70], "url": url}
    recs = []
    for c in rows:
        if not c or not c[0] or _looks_header(c) or len(c[0]) < 2:
            continue
        entity = c[0]
        date = next((x for x in c[1:] if _yr(x)), "")
        if not _yr(date) and len(c) == 1:
            continue
        recs.append(_rec(
            id=f"{code.lower()}-{re.sub(r'[^a-z0-9]+', '-', entity.lower())[:28]}-{_yr(date)}",
            entity=entity, product=f"{name} AG breach notice", domains=["State AG (live)"],
            sector="State-reported", year=_yr(date), date_disclosed=date,
            threat_type="Reported data breach", threat_category="State-reported breach",
            impacted="See notice", states=[code], reported_state_ag=True,
            source_feed=f"{name} AG", source=url))
        if len(recs) >= STATE_LIMIT:
            break
    if recs:
        return recs, {"status": "ok", "note": f"{len(recs)} parsed", "url": url}
    return [], {"status": "manual", "note": "no readable table — open portal to search/export", "url": url}


# ----------------------------------------------------------------- Washington (Socrata JSON API — real, keyless)
WA_SOCRATA = "https://data.wa.gov/resource/sb4j-ca4h.json"


def _wa_socrata():
    try:
        r = requests.get(WA_SOCRATA, params={"$limit": 300, "$order": ":id DESC"},
                         headers=_hdr(True), timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return [], {"status": "unavailable", "note": str(e)[:90], "url": WA_SOCRATA}
    recs = []
    for row in data:
        name = (row.get("name_of_business") or row.get("organization_name") or row.get("business_name")
                or row.get("name_of_entity") or row.get("entity") or "")
        if not name:
            continue
        date = (row.get("date_reported_to_ago") or row.get("date_reported") or row.get("reported_date")
                or row.get("date_of_breach") or row.get("breach_start") or "")
        affected = row.get("washingtonians_affected") or row.get("number_of_washingtonians_affected") or row.get("wa_affected")
        try:
            affected = int(float(affected)) if affected not in (None, "") else 0
        except (ValueError, TypeError):
            affected = 0
        y = _yr(str(date)) or _yr(str(row.get("year", "")))
        recs.append(_rec(
            id=f"wa-{re.sub(r'[^a-z0-9]+', '-', name.lower())[:28]}-{y}",
            entity=name, product="WA AG breach notice", domains=["State AG (live)"],
            sector="State-reported", year=y, date_disclosed=str(date),
            threat_type=row.get("type_of_breach") or "Reported data breach",
            threat_category=row.get("type_of_breach") or "State-reported breach",
            impacted=f"{affected:,} Washingtonians" if affected else "See notice", unit="individuals",
            impacted_num=affected, states=["WA"], reported_state_ag=True,
            source_feed="Washington AG (data.wa.gov)", source="https://www.atg.wa.gov/data-breach-notifications"))
        if len(recs) >= STATE_LIMIT * 3:
            break
    return recs, {"status": "ok" if recs else "empty", "note": f"{len(recs)} via Socrata API", "url": WA_SOCRATA}


# ----------------------------------------------------------------- CISA Known Exploited Vulnerabilities (real JSON feed)
CISA_KEV = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def _cisa(since="2025-01-01"):
    try:
        r = requests.get(CISA_KEV, headers=_hdr(True), timeout=25)
        r.raise_for_status()
        vulns = r.json().get("vulnerabilities", [])
    except Exception as e:
        return [], {"status": "unavailable", "note": str(e)[:90], "url": CISA_KEV}
    recs = []
    for v in vulns:
        added = v.get("dateAdded", "")
        if added < since:
            continue
        vendor = v.get("vendorProject", ""); product = v.get("product", "")
        recs.append(_rec(
            id=f"cisa-{v.get('cveID', '')}",
            entity=f"{vendor} {product}".strip() or v.get("cveID", "CISA KEV"),
            product=v.get("vulnerabilityName", "Known exploited vulnerability"),
            domains=["CISA KEV (live)"], sector="Exploited vulnerability",
            year=_yr(added), date_disclosed=added,
            threat_type=v.get("shortDescription", "")[:300] or "Actively exploited vulnerability",
            threat_category="Exploited vulnerability (CISA KEV)",
            impacted=f"{v.get('cveID','')} — {vendor} {product}".strip(), unit="cve", impacted_num=0,
            attribution="Known ransomware use" if v.get("knownRansomwareCampaignUse") == "Known" else "",
            data_types=v.get("requiredAction", "")[:200],
            source_feed="CISA KEV", source="https://www.cisa.gov/known-exploited-vulnerabilities-catalog"))
    recs.sort(key=lambda x: x["date_disclosed"], reverse=True)
    return recs, {"status": "ok" if recs else "empty", "note": f"{len(recs)} KEV since {since}", "url": CISA_KEV}


# ----------------------------------------------------------------- orchestrator
ALL_SOURCES = ["sec8k", "sec10k", "hhs", "states", "cisa"]


def run_tracker(sources=None, enrich=True):
    sources = sources or ALL_SOURCES
    incidents, provenance = [], []

    if "sec8k" in sources:
        rows, meta = _sec("8-K", "1.05", "SEC 8-K", "SEC 8-K (live)",
                          ['"Item 1.05"', '"material cybersecurity incident"'], enrich=enrich)
        incidents += rows
        provenance.append({"key": "sec8k", "label": "SEC 8-K (Item 1.05)", "source_url": EFTS,
                           "count": len(rows), **meta})
    if "sec10k" in sources:
        rows, meta = _sec("10-K", "10-K Item 1C", "SEC 10-K", "SEC 10-K (live)",
                          ['"Item 1C"', '"Item 1C. Cybersecurity"'], enrich=False)
        incidents += rows
        provenance.append({"key": "sec10k", "label": "SEC 10-K (Item 1C Cybersecurity)", "source_url": EFTS,
                           "count": len(rows), **meta})
    if "hhs" in sources:
        rows, meta = _hhs()
        incidents += rows
        provenance.append({"key": "hhs", "label": "HHS OCR Breach Portal (HIPAA 500+)",
                           "source_url": meta.get("url", HHS_URL), "count": len(rows),
                           "status": meta["status"], "note": meta["note"]})
    if "states" in sources:
        # Washington via its real Socrata JSON API; the rest via portal HTML best-effort.
        rows, meta = _wa_socrata()
        incidents += rows
        provenance.append({"key": "state:WA", "label": "Washington AG (data.wa.gov API)",
                           "source_url": meta.get("url"), "count": len(rows),
                           "status": meta["status"], "note": meta["note"]})
        other = [c for c in STATE_PORTALS if c != "WA"]
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(_state, code): code for code in other}
            results = {futs[f]: f.result() for f in as_completed(futs)}
        for code in other:
            rows, meta = results[code]
            incidents += rows
            provenance.append({"key": f"state:{code}", "label": f"{STATE_PORTALS[code][0]} AG",
                               "source_url": meta.get("url"), "count": len(rows),
                               "status": meta["status"], "note": meta["note"]})
    if "cisa" in sources:
        rows, meta = _cisa()
        incidents += rows
        provenance.append({"key": "cisa", "label": "CISA Known Exploited Vulnerabilities",
                           "source_url": meta.get("url", CISA_KEV), "count": len(rows),
                           "status": meta["status"], "note": meta["note"]})

    incidents.sort(key=lambda x: x.get("date_disclosed", ""), reverse=True)
    payload = {
        "fetched_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "window": f"{START} … {TODAY}",
        "source": "Multi-source tracker (SEC EDGAR, HHS OCR, state AG portals)",
        "count": len(incidents),
        "enriched": sum(1 for r in incidents if r.get("enriched")),
        "sources": provenance,
        "incidents": incidents,
    }
    os.makedirs(os.path.dirname(LIVE_PATH), exist_ok=True)
    with open(LIVE_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    return {k: payload[k] for k in ("fetched_at", "window", "count", "enriched", "sources")}


if __name__ == "__main__":  # offline parser tests (no network)
    sample_hhs = ("<table><tr><th>Name of Covered Entity</th><th>State</th><th>Type</th>"
                  "<th>Individuals Affected</th><th>Breach Submission Date</th><th>Type of Breach</th></tr>"
                  "<tr><td>Acme Health</td><td>CA</td><td>Provider</td><td>12,345</td>"
                  "<td>03/15/2025</td><td>Hacking/IT Incident</td></tr></table>")
    recs = [c for c in _rows_from_tables(sample_hhs) if len(c) >= 5 and not _looks_header(c)]
    assert recs and recs[0][0] == "Acme Health" and _num(recs[0][3]) == 12345 and _yr(recs[0][4]) == "2025", recs
    sample_state = ("<table><tr><th>Organization Name</th><th>Reported Date</th></tr>"
                    "<tr><td>Gamma LLC</td><td>06/01/2025</td></tr></table>")
    srecs = [c for c in _rows_from_tables(sample_state) if not _looks_header(c) and c[0]]
    assert srecs[0][0] == "Gamma LLC" and _yr(srecs[0][1]) == "2025", srecs
    print("HHS + state table parsers OK")
    print("states configured:", list(STATE_PORTALS))
    print("window:", START, "…", TODAY, "| SEC pages:", SEC_PAGES)

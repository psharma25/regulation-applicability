"""
Feed agent: pulls new CVEs from NVD 2.0 and flags CISA KEV / known-exploited.

This is the trigger source. In production you'd run poll() on a schedule (cron,
APScheduler, or a systemd timer). The web UI also exposes a manual "Scan feeds"
button so an analyst can trigger a pull on demand.

NVD 2.0:  https://services.nvd.nist.gov/rest/json/cves/2.0
KEV:      https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
"""
import time
import uuid

import requests

from .. import db  # type: ignore  # resolved when run as package; see app bootstrap

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
KEV_FEED = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def _kev_set():
    try:
        r = requests.get(KEV_FEED, timeout=30)
        r.raise_for_status()
        return {v["cveID"] for v in r.json().get("vulnerabilities", [])}
    except Exception:
        return set()


def _parse_nvd_item(item, kev):
    cve = item.get("cve", {})
    cid = cve.get("id")
    descs = cve.get("descriptions", [])
    title = next((d["value"] for d in descs if d.get("lang") == "en"), cid)

    severity, cvss = "NONE", None
    metrics = cve.get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if metrics.get(key):
            data = metrics[key][0]["cvssData"]
            cvss = data.get("baseScore")
            severity = data.get("baseSeverity") or metrics[key][0].get("baseSeverity") or "NONE"
            break

    cpes = []
    for cfg in cve.get("configurations", []):
        for node in cfg.get("nodes", []):
            for m in node.get("cpeMatch", []):
                if m.get("criteria"):
                    cpes.append(m["criteria"])

    cwes = []
    for w in cve.get("weaknesses", []):
        for d in w.get("description", []):
            if d.get("value"):
                cwes.append(d["value"])

    return {
        "id": cid,
        "title": title,
        "severity": (severity or "NONE").upper(),
        "cvss": cvss,
        "in_kev": cid in kev,
        "cpes": sorted(set(cpes)),
        "cwes": sorted(set(cwes)),
        "description": title,
        "published": cve.get("published"),
    }


def fetch_nvd(keyword=None, days=2, results=40):
    """Fetch recent CVEs. keyword narrows to your product/component space."""
    params = {"resultsPerPage": results, "startIndex": 0}
    if keyword:
        params["keywordSearch"] = keyword
    else:
        end = time.gmtime()
        start = time.gmtime(time.time() - days * 86400)
        fmt = "%Y-%m-%dT%H:%M:%S.000"
        params["lastModStartDate"] = time.strftime(fmt, start)
        params["lastModEndDate"] = time.strftime(fmt, end)
    headers = {}
    import os
    if os.environ.get("NVD_API_KEY"):
        headers["apiKey"] = os.environ["NVD_API_KEY"]
    r = requests.get(NVD_API, params=params, headers=headers, timeout=40)
    r.raise_for_status()
    return r.json().get("vulnerabilities", [])


def ingest(parsed_items):
    """Insert parsed CVEs as INGESTED advisories. Returns list of new ids."""
    new = []
    for it in parsed_items:
        existing = db.get_advisory_by_cve(it["id"])
        if existing:
            continue
        adv_id = "ADV-" + uuid.uuid4().hex[:10]
        db.insert_advisory({
            "id": adv_id,
            "cve_id": it["id"],
            "title": it["title"][:240],
            "source": "KEV" if it["in_kev"] else "NVD",
            "severity": it["severity"],
            "cvss": it["cvss"],
            "in_kev": it["in_kev"],
            "state": "INGESTED",
            "cve_detail": it,
        })
        db.log(adv_id, "feed-agent", "ingested",
               f"{it['id']} sev={it['severity']} kev={it['in_kev']}")
        new.append(adv_id)
    return new


def poll(keyword=None, days=2):
    kev = _kev_set()
    raw = fetch_nvd(keyword=keyword, days=days)
    parsed = [_parse_nvd_item(x, kev) for x in raw]
    return ingest(parsed)


def ingest_manual(cve_id, title, severity="HIGH", cvss=8.0, cpes=None, cwes=None, in_kev=False):
    """Inject a CVE by hand (e.g. a zero-day reported privately, not yet in NVD)."""
    if db.get_advisory_by_cve(cve_id):
        return None
    adv_id = "ADV-" + uuid.uuid4().hex[:10]
    detail = {
        "id": cve_id, "title": title, "severity": severity.upper(), "cvss": cvss,
        "in_kev": in_kev, "cpes": cpes or [], "cwes": cwes or [], "description": title,
    }
    db.insert_advisory({
        "id": adv_id, "cve_id": cve_id, "title": title[:240],
        "source": "MANUAL", "severity": severity.upper(), "cvss": cvss,
        "in_kev": in_kev, "state": "INGESTED", "cve_detail": detail,
    })
    db.log(adv_id, "analyst", "ingested-manual", cve_id)
    return adv_id

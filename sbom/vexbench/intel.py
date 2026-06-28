"""
intel.py — agent tools for live threat context with offline fallback.

  kev(cve)  -> bool      is the CVE on the CISA Known Exploited Vulnerabilities list?
  epss(cve) -> float|None  FIRST EPSS probability (0..1)

Tries the live feed first (cached for the process), falls back to the bundled
sample in ./data so the program runs fully offline with zero config. To refresh
the offline cache, run:  python intel.py --refresh
"""
import json
import os
import time

import httpx

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "data")
_KEV_CACHE = os.path.join(_DATA, "kev_sample.json")
_EPSS_CACHE = os.path.join(_DATA, "epss_sample.json")

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
EPSS_URL = "https://api.first.org/data/v1/epss"

_kev_set = None
_epss_map = None
_offline = os.environ.get("VEXBENCH_OFFLINE", "0") == "1"


def _load_cache(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def _ensure_kev():
    global _kev_set
    if _kev_set is not None:
        return
    cache = _load_cache(_KEV_CACHE, {"cves": []})
    _kev_set = set(c.upper() for c in cache.get("cves", []))
    if _offline:
        return
    try:
        r = httpx.get(KEV_URL, timeout=6.0)
        if r.status_code == 200:
            data = r.json()
            live = {v["cveID"].upper() for v in data.get("vulnerabilities", [])}
            if live:
                _kev_set = live
    except Exception:
        pass  # keep cached set


def _ensure_epss():
    global _epss_map
    if _epss_map is None:
        _epss_map = dict(_load_cache(_EPSS_CACHE, {}))


def kev(cve: str) -> bool:
    if not cve:
        return False
    _ensure_kev()
    return cve.strip().upper() in _kev_set


def epss(cve: str):
    if not cve:
        return None
    _ensure_epss()
    key = cve.strip().upper()
    if key in _epss_map:
        return _epss_map[key]
    if _offline:
        return None
    try:
        r = httpx.get(EPSS_URL, params={"cve": key}, timeout=6.0)
        if r.status_code == 200:
            rows = r.json().get("data", [])
            if rows:
                v = float(rows[0]["epss"])
                _epss_map[key] = v
                return v
    except Exception:
        pass
    return None


def _refresh():
    """Pull current KEV catalog + EPSS for the cached CVEs into ./data."""
    os.makedirs(_DATA, exist_ok=True)
    print("Fetching CISA KEV ...")
    r = httpx.get(KEV_URL, timeout=30.0)
    cves = sorted({v["cveID"].upper() for v in r.json().get("vulnerabilities", [])})
    json.dump({"refreshed": time.strftime("%Y-%m-%d"), "cves": cves},
              open(_KEV_CACHE, "w"), indent=1)
    print(f"  KEV cached: {len(cves)} CVEs")
    print("Fetching EPSS for KEV CVEs (batched) ...")
    out = {}
    for i in range(0, len(cves), 100):
        batch = ",".join(cves[i:i + 100])
        rr = httpx.get(EPSS_URL, params={"cve": batch}, timeout=30.0)
        for row in rr.json().get("data", []):
            out[row["cve"].upper()] = float(row["epss"])
    json.dump(out, open(_EPSS_CACHE, "w"), indent=1)
    print(f"  EPSS cached: {len(out)} scores")


if __name__ == "__main__":
    import sys
    if "--refresh" in sys.argv:
        _refresh()
    else:
        print("kev(CVE-2021-44228) =", kev("CVE-2021-44228"))
        print("epss(CVE-2021-44228) =", epss("CVE-2021-44228"))

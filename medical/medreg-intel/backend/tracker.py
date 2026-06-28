"""Server-side openFDA tracker with delta persisted to disk (data/tracker_snapshot.json)."""
import os, json, datetime, requests

HERE = os.path.dirname(__file__)
SNAP = os.path.join(HERE, "data", "tracker_snapshot.json")
OF = "https://api.fda.gov/device"


def _total(path, search):
    try:
        r = requests.get(f"{OF}/{path}.json", params={"search": search, "limit": 1}, timeout=20)
        r.raise_for_status()
        return r.json().get("meta", {}).get("results", {}).get("total", 0)
    except Exception:
        return None


def _date(s):
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if s and len(s) == 8 else (s or "—")


def run(persist=True):
    try:
        r = requests.get(f"{OF}/recall.json", params={
            "search": "reason_for_recall:cybersecurity",
            "sort": "event_date_initiated:desc", "limit": 30}, timeout=25)
        r.raise_for_status()
        results = r.json().get("results", [])
    except Exception as e:
        return {"ok": False, "error": str(e)[:160]}
    recalls = [{
        "id": x.get("recall_number") or (x.get("product_description", "")[:40]),
        "firm": x.get("recalling_firm", "—"),
        "device": (x.get("openfda", {}).get("device_name") or x.get("product_description", "")[:90]),
        "date": _date(x.get("event_date_initiated", "")),
        "reason": (x.get("reason_for_recall", "") or "")[:200],
    } for x in results]
    prev = []
    if os.path.exists(SNAP):
        try:
            prev = json.load(open(SNAP)).get("ids", [])
        except Exception:
            prev = []
    ids = [r["id"] for r in recalls]
    new = [i for i in ids if i not in prev] if prev else []
    if persist:
        os.makedirs(os.path.dirname(SNAP), exist_ok=True)
        json.dump({"ids": ids, "at": datetime.datetime.utcnow().isoformat() + "Z"}, open(SNAP, "w"))
    for r in recalls:
        r["new"] = r["id"] in new
    return {
        "ok": True,
        "fetched_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "totals": {
            "cyber_recalls": _total("recall", "reason_for_recall:cybersecurity"),
            "cyber_maude": _total("event", "mdr_text.text:cybersecurity"),
            "clearances_2025_2026": _total("510k", "decision_date:[2025-01-01+TO+2026-12-31]"),
        },
        "delta": {"new": len(new), "baseline": prev != []},
        "recalls": recalls,
    }

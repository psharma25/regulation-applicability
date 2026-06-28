"""Loads the seed dataset and provides filtering + indexing helpers.
Also merges an optional LIVE overlay (data/live_incidents.json) produced on demand
by live.refresh(), so freshly pulled SEC filings appear alongside the seed data."""
import json, os
from functools import lru_cache

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "incidents.json")
LIVE_PATH = os.path.join(os.path.dirname(__file__), "data", "live_incidents.json")


@lru_cache(maxsize=1)
def _load_seed():
    with open(DATA_PATH) as f:
        return json.load(f)["incidents"]


def _load_live():
    if os.path.exists(LIVE_PATH):
        try:
            return json.load(open(LIVE_PATH)).get("incidents", [])
        except Exception:
            return []
    return []


def _load():
    return _load_seed() + _load_live()


def live_meta():
    if os.path.exists(LIVE_PATH):
        try:
            d = json.load(open(LIVE_PATH))
            return {"fetched_at": d.get("fetched_at"), "count": d.get("count", 0),
                    "enriched": d.get("enriched", 0), "source": d.get("source"),
                    "window": d.get("window"), "sources": d.get("sources", [])}
        except Exception:
            pass
    return {"fetched_at": None, "count": 0, "enriched": 0, "source": None, "window": None, "sources": []}


def all_incidents():
    return list(_load())


def domains():
    ds = sorted({d for i in _load() for d in i["domains"]})
    return ds


def products_by_domain():
    """Map each domain -> list of {id, entity, product} within it."""
    out = {}
    for i in _load():
        for d in i["domains"]:
            out.setdefault(d, []).append(
                {"id": i["id"], "entity": i["entity"], "product": i["product"]}
            )
    for d in out:
        out[d].sort(key=lambda x: x["entity"])
    return out


def sectors():
    return sorted({i.get("sector", "Other") for i in _load()})


def states_list():
    return sorted({s for i in _load() for s in i.get("states", [])})


def _yr(i):
    try:
        return int(str(i.get("year", ""))[:4])
    except ValueError:
        return 0


def years():
    return sorted({_yr(i) for i in _load() if _yr(i)})


def filter_incidents(domain=None, product_id=None, nation_state=None, threat_category=None,
                     sector=None, state=None, year_from=None, year_to=None, reported_sec=None,
                     reported_state_ag=None):
    rows = _load()
    if domain and domain != "All domains":
        rows = [i for i in rows if domain in i["domains"]]
    if product_id and product_id != "All products":
        rows = [i for i in rows if i["id"] == product_id]
    if nation_state is not None:
        rows = [i for i in rows if i["nation_state"] is bool(nation_state)]
    if threat_category:
        rows = [i for i in rows if i["threat_category"].lower() == threat_category.lower()]
    if sector and sector != "All sectors":
        rows = [i for i in rows if i.get("sector") == sector]
    if state and state != "All states":
        rows = [i for i in rows if state in i.get("states", [])]
    if reported_sec is not None:
        rows = [i for i in rows if i["reported_sec"] is bool(reported_sec)]
    if reported_state_ag is not None:
        rows = [i for i in rows if i["reported_state_ag"] is bool(reported_state_ag)]
    if year_from is not None:
        rows = [i for i in rows if _yr(i) >= int(year_from)]
    if year_to is not None:
        rows = [i for i in rows if _yr(i) <= int(year_to)]
    return rows


def get_incident(incident_id):
    for i in _load():
        if i["id"] == incident_id:
            return i
    return None


def compute_stats(rows=None):
    rows = rows if rows is not None else _load()
    individuals_units = {"individuals", "records"}
    total_records = sum(i["impacted_num"] for i in rows if i["unit"] in individuals_units)
    total_fin = sum(i["financial_loss_usd"] or 0 for i in rows)
    by_domain = {}
    for i in rows:
        for d in i["domains"]:
            by_domain[d] = by_domain.get(d, 0) + 1
    by_threat = {}
    for i in rows:
        by_threat[i["threat_category"]] = by_threat.get(i["threat_category"], 0) + 1
    return {
        "incidents": len(rows),
        "records_impacted": total_records,
        "nation_state": sum(1 for i in rows if i["nation_state"]),
        "reported_sec": sum(1 for i in rows if i["reported_sec"]),
        "reported_state_ag": sum(1 for i in rows if i["reported_state_ag"]),
        "financial_loss_usd": total_fin,
        "by_domain": dict(sorted(by_domain.items(), key=lambda x: -x[1])),
        "by_threat": dict(sorted(by_threat.items(), key=lambda x: -x[1])),
    }

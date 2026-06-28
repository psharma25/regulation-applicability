"""FastAPI application: JSON API + serves the static frontend.

Run:  uvicorn backend.main:app --reload  (from repo root)
or:   ./run.sh
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import dataset
import agent
import live
import tracker

app = FastAPI(title="Agentic SecIntel", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if os.environ.get("LIVE_ON_START") == "1":
    try:
        live.refresh()
    except Exception as e:
        print(f"[live] startup refresh skipped: {e}")


@app.get("/api/meta")
def meta():
    return {
        "domains": dataset.domains(),
        "products_by_domain": dataset.products_by_domain(),
        "sectors": dataset.sectors(),
        "states": dataset.states_list(),
        "years": dataset.years(),
        "ollama": agent.ollama_available(),
        "model": agent.OLLAMA_MODEL,
        "live": dataset.live_meta(),
    }


@app.get("/api/incidents")
def incidents(domain: str = None, product_id: str = None, nation_state: bool = None, threat_category: str = None,
              sector: str = None, state: str = None, year_from: int = None, year_to: int = None, reported_sec: bool = None,
              reported_state_ag: bool = None):
    rows = dataset.filter_incidents(domain=domain, product_id=product_id, nation_state=nation_state,
                                    threat_category=threat_category, sector=sector, state=state,
                                    year_from=year_from, year_to=year_to, reported_sec=reported_sec,
                                    reported_state_ag=reported_state_ag)
    return {"count": len(rows), "incidents": rows}


@app.get("/api/stats")
def stats(domain: str = None, product_id: str = None, nation_state: bool = None, threat_category: str = None,
          sector: str = None, state: str = None, year_from: int = None, year_to: int = None, reported_sec: bool = None,
          reported_state_ag: bool = None):
    rows = dataset.filter_incidents(domain=domain, product_id=product_id, nation_state=nation_state,
                                    threat_category=threat_category, sector=sector, state=state,
                                    year_from=year_from, year_to=year_to, reported_sec=reported_sec,
                                    reported_state_ag=reported_state_ag)
    return dataset.compute_stats(rows)


class AgentReq(BaseModel):
    message: str
    filters: dict = {}
    history: list = []


@app.post("/api/agent")
def ask_agent(req: AgentReq):
    return agent.run_agent(req.message, filters=req.filters, history=req.history)


@app.post("/api/live/refresh")
def live_refresh():
    """Back-compat: run the full multi-source tracker on demand."""
    return tracker_run()


@app.post("/api/tracker/run")
def tracker_run(sources: str = None):
    """Run the multi-source tracker (SEC 8-K + 10-K 2025–2026, HHS OCR, state AGs).
    `sources` = comma list of: sec8k,sec10k,hhs,states (default all)."""
    sel = [s.strip() for s in sources.split(",")] if sources else None
    try:
        return {"ok": True, **tracker.run_tracker(sources=sel)}
    except Exception as e:
        return {"ok": False, "error": str(e), "hint": "Set SEC_USER_AGENT and check internet access."}


@app.get("/api/agency-stats")
def agency_stats():
    """Real annual breach statistics from state AGs (mass.gov, atg.wa.gov) + HHS + CISA."""
    import json, os
    p = os.path.join(os.path.dirname(__file__), "data", "agency_stats.json")
    try:
        return json.load(open(p))
    except Exception as e:
        return {"sources": [], "error": str(e)}


@app.get("/api/tracker/sources")
def tracker_sources():
    """The configured sources (where data is obtained) + last-run provenance."""
    reg = [{"key": "sec8k", "label": "SEC 8-K (Item 1.05)", "url": tracker.EFTS},
           {"key": "sec10k", "label": "SEC 10-K (Item 1C Cybersecurity)", "url": tracker.EFTS},
           {"key": "hhs", "label": "HHS OCR Breach Portal", "url": tracker.HHS_URL},
           {"key": "cisa", "label": "CISA Known Exploited Vulnerabilities", "url": tracker.CISA_KEV},
           {"key": "state:WA", "label": "Washington AG (data.wa.gov API)", "url": tracker.WA_SOCRATA}]
    reg += [{"key": f"state:{c}", "label": f"{n} AG", "url": u}
            for c, (n, u) in tracker.STATE_PORTALS.items() if c != "WA"]
    return {"window": f"{tracker.START} … {tracker.TODAY}", "registry": reg, "last_run": dataset.live_meta()}


@app.get("/api/live/status")
def live_status():
    return dataset.live_meta()


# ---- static frontend (mounted last so /api wins) ----
FRONTEND = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(FRONTEND):
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")

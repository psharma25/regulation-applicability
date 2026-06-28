"""FastAPI application.

Endpoints:
  GET  /                      the web dashboard
  POST /api/scan              start a scan (runs in background); returns scan_id
  GET  /api/scan/{id}         poll scan status + results + log
  GET  /api/scan/{id}/xlsx    download the generated scoring workbook
  GET  /api/latest            most recent completed scan

State is in-memory (single-process). For multi-worker deployment, back this
with Redis or a DB; the scan payloads are small.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from .agent.orchestrator import Agent, new_scan
from .collectors.discovery import DiscoveryCollector
from .collectors.ransomwarelive import RansomwareLiveCollector
from .collectors.rss import CisaCollector, RssCollector
from .config import get_settings
from .export.workbook import build_workbook
from .models import ScanResult

app = FastAPI(title="Threat Actor Reputation Tracker", version="1.0")

SCANS: dict[str, ScanResult] = {}
LATEST: dict[str, str] = {}
STATIC = Path(__file__).parent / "static"


def _build_agent() -> Agent:
    return Agent(
        collectors=[
            RansomwareLiveCollector(),
            CisaCollector(),
            RssCollector(),
        ],
        discovery=DiscoveryCollector(),
    )


async def _run(scan: ScanResult) -> None:
    agent = _build_agent()
    try:
        await agent.run_scan(scan)
        path = build_workbook(scan, get_settings().data_dir)
        scan.workbook_path = str(path)
        scan.add_log(f"Workbook written: {path.name}")
        LATEST["id"] = scan.scan_id
    except Exception as exc:
        scan.status = "error"
        scan.error = str(exc)
        scan.add_log(f"Scan failed: {exc}")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (STATIC / "index.html").read_text(encoding="utf-8")


@app.post("/api/scan")
async def start_scan(background: BackgroundTasks) -> dict:
    scan = new_scan()
    SCANS[scan.scan_id] = scan
    scan.add_log("Scan queued")
    background.add_task(_run, scan)
    return {"scan_id": scan.scan_id, "status": scan.status}


@app.get("/api/scan/{scan_id}")
async def scan_status(scan_id: str) -> dict:
    scan = SCANS.get(scan_id)
    if not scan:
        raise HTTPException(404, "Unknown scan id")
    return scan.model_dump()


@app.get("/api/scan/{scan_id}/xlsx")
async def download_xlsx(scan_id: str):
    scan = SCANS.get(scan_id)
    if not scan or not scan.workbook_path:
        raise HTTPException(404, "Workbook not ready")
    p = Path(scan.workbook_path)
    if not p.exists():
        raise HTTPException(404, "Workbook file missing")
    return FileResponse(
        p,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=p.name,
    )


@app.get("/api/latest")
async def latest() -> dict:
    sid = LATEST.get("id")
    if not sid or sid not in SCANS:
        return {"status": "none"}
    return SCANS[sid].model_dump()


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "scans": len(SCANS)}

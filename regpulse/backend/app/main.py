"""RegPulse Intelligence — FastAPI entrypoint."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .db import init_db, SessionLocal
from .services import seed as seed_svc, rag, scan, scheduler
from .routers import auth as auth_router, regulations as reg_router, core as core_router

app = FastAPI(title="RegPulse Intelligence", version="1.0",
              description="Weekly, local-AI regulatory & control intelligence.")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(auth_router.router)
app.include_router(reg_router.router)
app.include_router(core_router.router)


@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    try:
        seed_svc.seed(db)            # idempotent
        rag.ensure_embeddings(db)    # embeds only what is missing
        # run an initial scan if none exists, so delta is available immediately
        if not scan.latest_delta(db)[0]:
            scan.run_scan(db)
    finally:
        db.close()
    scheduler.start()                # weekly cadence


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---- serve the static web interface (single-file SPA) -----------------------
_FRONTEND = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(_FRONTEND):
    app.mount("/", StaticFiles(directory=_FRONTEND, html=True), name="frontend")

"""FastAPI application: agentic RAG API + downloadable risk templates + static web UI.

Run:  uvicorn backend.main:app --reload  (from the repo root)
"""
from __future__ import annotations
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, excel
from .excel.library import LIBRARIES
from .rag import agent
from .rag.retriever import get_retriever
from .rag.llm import ollama_available

app = FastAPI(title=config.APP_TITLE, version="1.0.0")


class ChatRequest(BaseModel):
    message: str


@app.get("/api/health")
def health():
    r = get_retriever()
    return {
        "status": "ok",
        "retrieval_mode": r.mode,
        "knowledge_chunks": len(r.chunks),
        "llm": f"ollama:{config.OLLAMA_MODEL}" if ollama_available() else "extractive-fallback",
        "domains": [d["id"] for d in excel.domains()],
    }


@app.get("/api/domains")
def domains():
    return {"domains": excel.domains()}


@app.get("/api/library/{domain}")
def library(domain: str):
    spec = LIBRARIES.get(domain)
    if not spec:
        raise HTTPException(404, f"unknown domain '{domain}'")
    return {"domain": domain, "sheet": spec["sheet"], "title": spec["title"],
            "columns": spec["columns"], "rows": spec["rows"]}


@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "message is required")
    return agent.route(req.message)


@app.get("/api/forms/{domain}/download")
def download(domain: str):
    if domain not in excel.GENERATORS:
        raise HTTPException(404, f"unknown domain '{domain}'")
    meta = excel.GENERATORS[domain]
    tmp = Path(tempfile.gettempdir()) / meta["filename"]
    excel.generate(domain, str(tmp))
    return FileResponse(
        str(tmp),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=meta["filename"],
    )


# ---- static frontend (mounted last so /api/* takes precedence) ----
if Path(config.FRONTEND_DIR).exists():
    app.mount("/", StaticFiles(directory=str(config.FRONTEND_DIR), html=True), name="frontend")
else:
    @app.get("/", response_class=HTMLResponse)
    def root():
        return "<h1>Risk Assessment AI</h1><p>API running. Frontend directory not found.</p>"

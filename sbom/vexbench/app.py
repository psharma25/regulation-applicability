"""
app.py — VEX Bench server. Serves the single-page frontend and exposes the
agentic enrichment, RAG, and threat-intel endpoints.

Run:  uvicorn app:app --host 0.0.0.0 --port 8000
or:   python app.py
"""
import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import agent
import intel
import llm
import rag
import risk

_HERE = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="VEX Bench", version="1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class EnrichReq(BaseModel):
    rows: list[dict]
    only_empty: bool = True
    mode: str = "auto"          # auto | agent | deterministic


class RowsReq(BaseModel):
    rows: list[dict]


class QueryReq(BaseModel):
    query: str
    k: int = 4


@app.get("/")
def index():
    return FileResponse(os.path.join(_HERE, "index.html"))


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "ollama": llm.available(),
        "ollama_model": llm.OLLAMA_MODEL,
        "offline": intel._offline,
        "corpus": rag.corpus_stats(),
    }


@app.post("/api/enrich")
def enrich(req: EnrichReq):
    rows, trace = agent.enrich_all(req.rows, only_empty=req.only_empty, mode=req.mode)
    return {"rows": rows, "trace": trace,
            "engine": "agent" if (req.mode == "agent" or (req.mode == "auto" and llm.available())) else "deterministic"}


@app.post("/api/recompute")
def recompute(req: RowsReq):
    for r in req.rows:
        risk.compute(r)
    return {"rows": req.rows}


@app.post("/api/retrieve")
def retrieve(req: QueryReq):
    return {"hits": rag.retrieve(req.query, k=req.k)}


@app.get("/api/intel/{cve}")
def cve_intel(cve: str):
    return {"cve": cve, "kev": intel.kev(cve), "epss": intel.epss(cve)}


# Optional: let the backend parse an uploaded file too (frontend also parses client-side).
@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    raw = await file.read()
    name = file.filename.lower()
    try:
        if name.endswith(".json") or name.endswith(".cdx") or name.endswith(".sarif"):
            import json
            data = json.loads(raw)
            rows = _rows_from_json(data)
        else:
            rows = _rows_from_csv(raw.decode("utf-8", "ignore"))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    for r in rows:
        risk.compute(r)
    return {"rows": rows, "count": len(rows)}


def _rows_from_json(d):
    rows = []
    if isinstance(d, dict) and d.get("bomFormat") == "CycloneDX":
        comps = {c.get("bom-ref") or c.get("purl") or c.get("name"): c for c in d.get("components", [])}
        for v in d.get("vulnerabilities", []):
            refs = [a.get("ref") for a in v.get("affects", [])]
            comp = next((comps[x] for x in refs if x in comps), {})
            rating = next((r for r in v.get("ratings", []) if r.get("score") is not None), None)
            rows.append({"component": comp.get("name", ""), "version": comp.get("version", ""),
                         "purl": comp.get("purl", ""), "vulnId": v.get("id", ""),
                         "cvss": rating.get("score") if rating else ""})
    elif isinstance(d, dict) and isinstance(d.get("rows"), list):
        rows = d["rows"]
    elif isinstance(d, list):
        rows = d
    return rows


def _rows_from_csv(text):
    import csv
    import io
    return list(csv.DictReader(io.StringIO(text)))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    print(f"\n  VEX Bench  ->  http://localhost:{port}")
    print(f"  Ollama: {'detected' if llm.available() else 'not found (deterministic mode)'}  "
          f"| corpus: {rag.corpus_stats()['chunks']} chunks\n")
    uvicorn.run(app, host="0.0.0.0", port=port)

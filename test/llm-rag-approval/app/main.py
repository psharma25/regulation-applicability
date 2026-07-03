"""FastAPI app: RAG question-answering with a human-approval queue.

Flow:
  1. Asker submits a question  -> POST /api/ask        (status: generating)
  2. LLM drafts an answer      ->                       (status: pending_review)
  3. Reviewer approves/edits/rejects -> POST /api/review/{id}
  4. Asker polls               -> GET /api/status/{id}  (sees answer only after approval)

Self-approval mode: the same person simply opens the Review tab.
"""
import os
import uuid
import threading
import requests as http
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import rag

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

app = FastAPI(title="RAG with human approval")

# Allow the standalone HTML page (opened from disk or another origin)
# to call this API. Fine for an experiment; tighten for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store; fine for an experiment.
ANSWERS: dict[str, dict] = {}
LOCK = threading.Lock()

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the question using ONLY the provided "
    "context. If the context does not contain the answer, say you don't know. "
    "Be concise."
)


class AskRequest(BaseModel):
    question: str


class ReviewRequest(BaseModel):
    action: str                      # "approve" | "reject"
    edited_answer: str | None = None
    note: str | None = None


def _generate(item_id: str, question: str) -> None:
    try:
        sources = rag.retrieve(question)
        context = "\n\n---\n\n".join(
            f"[{s['source']}] {s['text']}" for s in sources
        ) or "(no relevant documents found)"
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        resp = http.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "system": SYSTEM_PROMPT,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )
        resp.raise_for_status()
        draft = resp.json()["response"].strip()
        with LOCK:
            ANSWERS[item_id].update(
                status="pending_review", draft=draft, sources=sources
            )
    except Exception as e:  # surface errors to the UI instead of hanging
        with LOCK:
            ANSWERS[item_id].update(status="error", error=str(e))


@app.on_event("startup")
def startup() -> None:
    n = rag.build_index()
    print(f"RAG index built: {n} chunks")


@app.post("/api/ask")
def ask(req: AskRequest):
    item_id = uuid.uuid4().hex[:8]
    with LOCK:
        ANSWERS[item_id] = {
            "id": item_id,
            "question": req.question,
            "status": "generating",
        }
    threading.Thread(target=_generate, args=(item_id, req.question)).start()
    return {"id": item_id}


@app.get("/api/status/{item_id}")
def status(item_id: str):
    item = ANSWERS.get(item_id)
    if not item:
        return {"status": "not_found"}
    # The asker only sees the final answer once a human approved it.
    public = {"id": item["id"], "status": item["status"]}
    if item["status"] == "approved":
        public["answer"] = item["final_answer"]
        public["sources"] = [s["source"] for s in item.get("sources", [])]
    if item["status"] == "rejected":
        public["note"] = item.get("note", "The reviewer rejected this answer.")
    if item["status"] == "error":
        public["error"] = item.get("error")
    return public


@app.get("/api/pending")
def pending():
    with LOCK:
        return [
            item for item in ANSWERS.values() if item["status"] == "pending_review"
        ]


@app.post("/api/review/{item_id}")
def review(item_id: str, req: ReviewRequest):
    with LOCK:
        item = ANSWERS.get(item_id)
        if not item or item["status"] != "pending_review":
            return {"ok": False, "error": "not pending"}
        if req.action == "approve":
            item["final_answer"] = (req.edited_answer or item["draft"]).strip()
            item["status"] = "approved"
        else:
            item["status"] = "rejected"
            item["note"] = req.note or "The reviewer rejected this answer."
    return {"ok": True}


@app.post("/api/reingest")
def reingest():
    n = rag.build_index()
    return {"ok": True, "chunks": n}


app.mount("/", StaticFiles(directory="static", html=True), name="static")

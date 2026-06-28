"""MedReg Intel API + static server. Serves the docs/ build and the corpus, runs the openFDA
tracker server-side (with persisted deltas), generates downloadable templates, and answers
questions with an open-source agentic backend (Ollama + retrieval fallback)."""
import os, json
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import tracker
import agent

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "data")
DOCS = os.path.abspath(os.path.join(HERE, "..", "docs"))
app = FastAPI(title="MedReg Intel")


def _load(name):
    p = os.path.join(DATA, f"{name}.json")
    return json.load(open(p)) if os.path.exists(p) else []


@app.get("/api/corpus")
def corpus():
    return {k: _load(k) for k in ("regulations", "submissions", "requirements", "incidents", "rta", "ai", "secreqs", "risk", "templates")}


@app.post("/api/tracker/run")
def tracker_run():
    return tracker.run()


class Q(BaseModel):
    question: str


@app.post("/api/agent")
def ask(q: Q):
    return agent.answer(q.question)


@app.get("/api/template/{tid}", response_class=PlainTextResponse)
def template(tid: str):
    for t in _load("templates"):
        if t["id"] == tid:
            return t["content"]
    return "Not found."


@app.get("/api/meta")
def meta():
    return {"ollama": agent.ollama_available(), "model": agent.OLLAMA_MODEL,
            "collections": {k: len(_load(k)) for k in ("regulations", "submissions", "requirements", "incidents", "rta", "ai", "secreqs", "risk", "templates")}}


@app.get("/api/{collection}")
def collection(collection: str):
    if collection in ("regulations", "submissions", "requirements", "incidents", "rta", "ai", "secreqs", "risk", "templates"):
        return _load(collection)
    return {"error": "unknown collection"}


if os.path.isdir(DOCS):
    app.mount("/", StaticFiles(directory=DOCS, html=True), name="static")

"""LLM client. Uses a local Ollama server (open source) when reachable;
otherwise returns a grounded extractive answer built from retrieved context,
so the app is always functional offline.
"""
from __future__ import annotations
import json
import urllib.request
import urllib.error
from typing import List, Tuple

from .. import config
from .retriever import Chunk

SYSTEM_PROMPT = (
    "You are a risk-management assistant for medical-device, finance and technology domains. "
    "Answer ONLY from the provided context. Cite the source name in brackets like [iso14971]. "
    "If the context is insufficient, say so. Be concise and practical."
)


def ollama_available() -> bool:
    try:
        req = urllib.request.Request(f"{config.OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def _ollama_generate(prompt: str) -> str:
    payload = json.dumps({
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {"temperature": 0.2},
    }).encode()
    req = urllib.request.Request(
        f"{config.OLLAMA_HOST}/api/generate", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=config.LLM_TIMEOUT) as r:
        return json.loads(r.read().decode()).get("response", "").strip()


def _extractive(query: str, context: List[Tuple[Chunk, float]]) -> str:
    if not context:
        return ("I don't have knowledge-base content on that yet. Add Markdown files to "
                "backend/knowledge/ and restart. (No LLM server detected — running in offline "
                "extractive mode.)")
    lines = ["**Answer assembled from the knowledge base** (no LLM server detected — set "
             "`OLLAMA_HOST` and pull a model for generative answers):", ""]
    for chunk, score in context:
        snippet = chunk.text.strip()
        if len(snippet) > 600:
            snippet = snippet[:600].rsplit(" ", 1)[0] + "…"
        lines.append(f"- {snippet}  \n  _source: [{chunk.source}]_")
    return "\n".join(lines)


def answer(query: str, context: List[Tuple[Chunk, float]]) -> dict:
    sources = sorted({c.source for c, _ in context})
    if ollama_available():
        ctx = "\n\n".join(f"[{c.source}] {c.text}" for c, _ in context)
        prompt = f"Context:\n{ctx}\n\nQuestion: {query}\n\nAnswer (cite sources in brackets):"
        try:
            text = _ollama_generate(prompt)
            return {"answer": text, "sources": sources, "engine": f"ollama:{config.OLLAMA_MODEL}"}
        except Exception as e:  # fall back gracefully
            return {"answer": _extractive(query, context) + f"\n\n_(LLM error: {e})_",
                    "sources": sources, "engine": "extractive-fallback"}
    return {"answer": _extractive(query, context), "sources": sources, "engine": "extractive"}

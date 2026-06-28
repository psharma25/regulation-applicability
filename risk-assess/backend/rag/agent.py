"""Lightweight agentic router.

The agent inspects the user message, picks a tool, and returns a structured
response. Tools:
  * list_forms     -> enumerate downloadable risk templates
  * generate_form  -> resolve a domain and return a download action
  * answer_question-> RAG over the knowledge base (retriever + LLM)

This is intentionally dependency-free (no LangChain required) so the repo runs
anywhere; you can swap in a full agent framework via the same interface.
"""
from __future__ import annotations
import re
from .. import excel
from .retriever import get_retriever
from . import llm

_DOMAIN_HINTS = {
    "medical": ["medical", "device", "iso 14971", "14971", "patient", "clinical", "samd", "health"],
    "finance": ["finance", "financial", "credit", "market risk", "liquidity", "basel", "coso", "bank", "loan"],
    "technology": ["technology", "tech", "cyber", "security", "reputation", "ip", "intellectual property",
                   "software", "saas", "breach", "nist", "27005"],
}

_GENERATE_RX = re.compile(r"\b(download|generate|create|build|make|excel|spreadsheet|template|form|export)\b", re.I)


def _resolve_domain(text: str):
    t = text.lower()
    best, score = None, 0
    for dom, hints in _DOMAIN_HINTS.items():
        s = sum(1 for h in hints if h in t)
        if s > score:
            best, score = dom, s
    return best


def route(message: str) -> dict:
    text = message.strip()
    low = text.lower()

    # tool: list_forms
    if re.search(r"\b(list|which|what).*(forms?|templates?|domains?)\b", low) or low in {"forms", "templates"}:
        return {"action": "list_forms", "tool": "list_forms", "domains": excel.domains()}

    # tool: generate_form
    if _GENERATE_RX.search(low):
        dom = _resolve_domain(low)
        if dom:
            meta = excel.GENERATORS[dom]
            return {
                "action": "download", "tool": "generate_form", "domain": dom,
                "label": meta["label"], "download_url": f"/api/forms/{dom}/download",
                "message": f"Here is the {meta['label']} risk assessment template. Click to download.",
            }
        return {
            "action": "clarify", "tool": "generate_form",
            "message": "Which domain — medical, finance, or technology?",
            "domains": excel.domains(),
        }

    # tool: answer_question (RAG)
    hits = get_retriever().search(text)
    result = llm.answer(text, hits)
    return {
        "action": "answer", "tool": "answer_question",
        "message": result["answer"], "sources": result["sources"], "engine": result["engine"],
        "retrieval_mode": get_retriever().mode,
    }

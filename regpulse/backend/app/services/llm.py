"""LLM access layer.

Design goal = minimise cost. Order of preference:
  1. Deterministic templates (USE_LLM=false)  -> $0, offline, default.
  2. Local Ollama (open source models)          -> $0 inference, local GPU/CPU.
  3. Optional OpenAI-compatible endpoint         -> only if explicitly configured.

Every caller passes a `fallback` string so the system always returns useful
output even when no model is available.
"""
import json
import urllib.request
from ..config import settings


def _ollama(prompt: str, system: str = "") -> str | None:
    try:
        body = json.dumps({
            "model": settings.LLM_MODEL,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {"temperature": 0.2, "num_ctx": 2048},
        }).encode()
        req = urllib.request.Request(settings.OLLAMA_URL + "/api/generate",
                                     data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["response"].strip()
    except Exception:
        return None


def _openai(prompt: str, system: str = "") -> str | None:
    if not (settings.OPENAI_BASE_URL and settings.OPENAI_API_KEY):
        return None
    try:
        body = json.dumps({
            "model": settings.LLM_MODEL,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": prompt}],
            "temperature": 0.2,
        }).encode()
        req = urllib.request.Request(
            settings.OPENAI_BASE_URL.rstrip("/") + "/chat/completions",
            data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {settings.OPENAI_API_KEY}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def generate(prompt: str, system: str = "", fallback: str = "") -> str:
    """Return model output, or `fallback` when no model is available/enabled."""
    if not settings.USE_LLM:
        return fallback
    return _ollama(prompt, system) or _openai(prompt, system) or fallback

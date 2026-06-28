"""
LLM client used by every agent.

Design rule for this codebase: the LLM is an *augmentation*, never a dependency.
Every agent has a deterministic path that produces a correct, defensible result
with no model at all. The LLM only adds narrative rationale and prose. If Ollama
is unreachable, disabled, or returns garbage, the program keeps working and the
output is still audit-ready.

Configure via env:
    LLM_ENABLED   "1" (default) / "0"
    OLLAMA_HOST   default http://localhost:11434
    OLLAMA_MODEL  default llama3.1:8b
"""
import json
import os

import requests

LLM_ENABLED = os.environ.get("LLM_ENABLED", "1") == "1"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")


def llm_available():
    if not LLM_ENABLED:
        return False
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def generate(prompt, system=None, json_mode=False, timeout=120):
    """Return model text, or None on any failure (caller must have a fallback)."""
    if not LLM_ENABLED:
        return None
    body = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }
    if system:
        body["system"] = system
    if json_mode:
        body["format"] = "json"
    try:
        r = requests.post(f"{OLLAMA_HOST}/api/generate", json=body, timeout=timeout)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception:
        return None


def generate_json(prompt, system=None, timeout=120):
    """Generate and parse JSON; returns dict/list or None."""
    raw = generate(prompt, system=system, json_mode=True, timeout=timeout)
    if not raw:
        return None
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except Exception:
        return None

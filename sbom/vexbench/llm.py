"""
llm.py — thin Ollama client. The agent degrades to a deterministic pipeline
whenever Ollama is unavailable, so this is always optional.
"""
import json
import os

import httpx

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")


def available() -> bool:
    try:
        r = httpx.get(OLLAMA_URL + "/api/tags", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


def generate(prompt: str, system: str = "", temperature: float = 0.1,
             force_json: bool = True, timeout: float = 60.0) -> str:
    body = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if force_json:
        body["format"] = "json"
    r = httpx.post(OLLAMA_URL + "/api/generate", json=body, timeout=timeout)
    r.raise_for_status()
    return r.json().get("response", "")


def parse_json_loose(s: str):
    if not s:
        return None
    try:
        return json.loads(s.replace("```json", "").replace("```", "").strip())
    except Exception:
        i, j = s.find("{"), s.rfind("}")
        if 0 <= i < j:
            try:
                return json.loads(s[i:j + 1])
            except Exception:
                return None
    return None

"""LLM layer.

Primary backend is Ollama (local, open-source models — llama3.1, mistral,
qwen2.5, etc.). If Ollama is unreachable or disabled, a deterministic
heuristic extractor is used instead, so the tracker runs end-to-end with no
external services and no API keys.

The LLM's job is narrow and structured: given evidence about one actor and one
scoring criterion, return a 1-10 value plus a one-line rationale as JSON. We
keep the surface small so weak local models stay reliable.
"""
from __future__ import annotations

import json
import re

import httpx

from ..config import get_settings
from ..models import Evidence


class LLMUnavailable(Exception):
    pass


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.backend = "none"

    async def detect(self) -> str:
        """Probe Ollama once; record which backend we'll use."""
        if self.settings.disable_llm:
            self.backend = "heuristic"
            return self.backend
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{self.settings.ollama_host}/api/tags")
                if r.status_code == 200:
                    self.backend = f"ollama:{self.settings.ollama_model}"
                    return self.backend
        except Exception:
            pass
        self.backend = "heuristic"
        return self.backend

    async def _ollama_json(self, prompt: str) -> dict:
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1},
        }
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout) as client:
            r = await client.post(
                f"{self.settings.ollama_host}/api/generate", json=payload
            )
            r.raise_for_status()
            text = r.json().get("response", "{}")
        return _safe_json(text)

    async def score_criterion(
        self,
        actor_name: str,
        criterion_key: str,
        criterion_desc: str,
        evidence: list[Evidence],
        prior: float,
    ) -> tuple[float, str, str]:
        """Return (value 1-10, rationale, source)."""
        if self.backend.startswith("ollama"):
            try:
                return await self._score_with_ollama(
                    actor_name, criterion_key, criterion_desc, evidence, prior
                )
            except Exception:
                pass  # fall through to heuristic on any LLM failure
        val, why = _heuristic_score(criterion_key, evidence, prior)
        return val, why, "heuristic"

    async def _score_with_ollama(
        self, actor_name, criterion_key, criterion_desc, evidence, prior
    ) -> tuple[float, str, str]:
        ev_text = "\n".join(
            f"- ({e.source}) {e.title}: {e.snippet}" for e in evidence[:12]
        ) or "(no fresh evidence found this scan)"
        prompt = (
            "You are a threat-intelligence analyst scoring a ransomware actor on "
            "ONE criterion. Respond ONLY with JSON: "
            '{"value": <integer 1-10>, "rationale": "<=20 words"}.\n\n'
            f"Actor: {actor_name}\n"
            f"Criterion: {criterion_key} — {criterion_desc}\n"
            f"Analyst prior (1-10): {prior}\n"
            "Scale: for impact/activity/capability/ransom/nation-state, 10 = most "
            "severe. For decryptor_reliability/deal_honoring, 10 = most reliable "
            "(honors deals), 1 = routinely cheats.\n"
            "Adjust the prior only if evidence justifies it; otherwise stay near it.\n\n"
            f"Evidence:\n{ev_text}\n"
        )
        data = await self._ollama_json(prompt)
        val = float(data.get("value", prior))
        val = max(1.0, min(10.0, val))
        why = str(data.get("rationale", ""))[:160]
        return val, why, self.backend


def _safe_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return {}
        return {}


# --- Heuristic fallback -----------------------------------------------------
# Deterministic, evidence-aware nudges around the analyst prior. Keeps the tool
# fully functional with no model installed.

def _heuristic_score(
    criterion_key: str, evidence: list[Evidence], prior: float
) -> tuple[float, str]:
    val = float(prior)
    why = "analyst prior (no model installed)"

    # Victim volume: scale from ransomware.live counts if present.
    counts = [
        e.raw.get("recent_count") or e.raw.get("victim_count")
        for e in evidence
        if e.raw.get("recent_count") or e.raw.get("victim_count")
    ]
    if criterion_key == "activity_volume" and counts:
        top = max(counts)
        if top >= 100:
            val = 10
        elif top >= 50:
            val = 9
        elif top >= 20:
            val = 7
        elif top >= 5:
            val = 5
        else:
            val = 3
        why = f"{top} recent victims observed"

    # Mentions in fresh advisories nudge capability/impact up slightly.
    if criterion_key in {"capability", "targeting_impact"} and len(evidence) >= 2:
        val = min(10.0, val + 0.5)
        why = f"{len(evidence)} recent reports referencing actor"

    return round(val, 1), why

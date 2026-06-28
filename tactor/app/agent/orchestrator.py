"""Agentic orchestrator.

The agent runs a plan-act-reason loop per actor:

  1. PLAN     decide which collectors (tools) to invoke for the actor
  2. ACT       run collectors concurrently to gather public evidence
  3. REASON    for each rubric criterion, ask the LLM (or heuristic) to derive
               a 1-10 value + rationale from the prior and the fresh evidence
  4. SCORE     fold criteria into the two composite indices
  5. REFLECT   record confidence and a one-line per-actor assessment

It is deliberately tool-driven and source-agnostic: adding a collector or a
rubric criterion changes behavior with no orchestration changes.
"""
from __future__ import annotations

import asyncio
import re
import uuid
from datetime import datetime

from ..config import load_config
from ..models import ActorScore, CriterionScore, Evidence, ScanResult
from ..scoring.rubric import compute_composites
from .llm import LLMClient


def _normalize(name: str) -> str:
    """Canonical key for dedup: lowercase, strip non-alphanumerics."""
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


# Generic / non-actor labels that sometimes appear in feeds and should never be
# promoted to a tracked actor.
_DISCOVERY_STOPLIST = {
    "", "unknown", "n/a", "na", "other", "misc", "test",
}

# Conservative defaults for a freshly discovered actor: transient groups have
# little incentive to honor deals, so reliability defaults are low.
_DISCOVERY_PRIORS = {
    "activity_volume": 4,
    "capability": 5,
    "targeting_impact": 5,
    "nation_state": 3,
    "ransom_scale": 5,
    "decryptor_reliability": 4,
    "deal_honoring": 4,
}


class Agent:
    def __init__(self, collectors: list, discovery=None) -> None:
        self.collectors = collectors
        self.discovery = discovery
        self.llm = LLMClient()

    def _known_keys(self, actors_cfg: list[dict]) -> set[str]:
        keys: set[str] = set()
        for cfg in actors_cfg:
            keys.add(_normalize(cfg["name"]))
            for alias in cfg.get("aliases", []):
                keys.add(_normalize(alias))
        return keys

    async def discover_new(self, actors_cfg: list[dict], min_victims: int = 1) -> list[dict]:
        """Return on-the-fly configs for active groups not already seeded."""
        if not self.discovery:
            return []
        try:
            candidates = await self.discovery.discover()
        except Exception:
            return []

        known = self._known_keys(actors_cfg)
        new_cfgs: list[dict] = []
        seen: set[str] = set()
        for c in candidates:
            key = _normalize(c.get("name", ""))
            if not key or key in known or key in seen or key in _DISCOVERY_STOPLIST:
                continue
            if c.get("recent_count", 0) < min_victims and not c.get("description"):
                # Skip dormant/empty entries with no signal at all.
                continue
            seen.add(key)
            note = "Discovered on live source this scan."
            if c.get("sample_sector"):
                note += f" Recent sector: {c['sample_sector']}."
            if c.get("description"):
                note = c["description"]
            new_cfgs.append(
                {
                    "name": c["name"],
                    "aliases": [],
                    "origin": "Unknown",
                    "model": "Unknown",
                    "status": "active",
                    "nation_state_class": "criminal",
                    "discovered": True,
                    "notes": note,
                    "priors": dict(_DISCOVERY_PRIORS),
                    "_seed_recent": c.get("recent_count", 0),
                }
            )
        return new_cfgs

    def _plan(self, actor_cfg: dict) -> list:
        # Simple planner: in-house groups rarely appear in ransomware.live group
        # endpoints under a clean slug, but all collectors are cheap, so we run
        # them all. Hook for future per-actor tool selection.
        return self.collectors

    async def _act(self, actor_cfg: dict) -> list[Evidence]:
        names = [actor_cfg["name"], *actor_cfg.get("aliases", [])]
        tools = self._plan(actor_cfg)
        results = await asyncio.gather(
            *(c.collect(actor_cfg["name"], actor_cfg.get("aliases", [])) for c in tools),
            return_exceptions=True,
        )
        evidence: list[Evidence] = []
        for r in results:
            if isinstance(r, list):
                evidence.extend(r)
        return evidence

    async def _reason(
        self, actor_cfg: dict, evidence: list[Evidence]
    ) -> dict[str, CriterionScore]:
        criteria_cfg = load_config()["rubric"]["criteria"]
        priors = actor_cfg.get("priors", {})
        scores: dict[str, CriterionScore] = {}

        async def one(key: str, meta: dict) -> tuple[str, CriterionScore]:
            prior = float(priors.get(key, 5))
            value, rationale, source = await self.llm.score_criterion(
                actor_cfg["name"], key, meta["description"], evidence, prior
            )
            conf = 0.5
            if source.startswith("ollama"):
                conf = 0.8 if evidence else 0.55
            elif source == "heuristic" and evidence:
                conf = 0.6
            elif source == "heuristic":
                conf = 0.4
            return key, CriterionScore(
                key=key,
                label=meta["label"],
                raw=value,
                confidence=conf,
                rationale=rationale,
                source=source,
            )

        pairs = await asyncio.gather(*(one(k, m) for k, m in criteria_cfg.items()))
        for k, cs in pairs:
            scores[k] = cs
        return scores

    async def assess_actor(self, actor_cfg: dict) -> ActorScore:
        evidence = await self._act(actor_cfg)
        criteria = await self._reason(actor_cfg, evidence)

        victim_counts = [
            e.raw.get("recent_count") or e.raw.get("victim_count") or 0
            for e in evidence
        ]
        # Discovered actors carry a victim count from the discovery pass even if
        # the per-actor collectors found nothing under a clean slug.
        seed_recent = actor_cfg.get("_seed_recent", 0)
        recent = max(victim_counts) if victim_counts else 0
        recent = max(recent, seed_recent)

        actor = ActorScore(
            name=actor_cfg["name"],
            aliases=actor_cfg.get("aliases", []),
            origin=actor_cfg.get("origin", "Unknown"),
            model=actor_cfg.get("model", "Unknown"),
            status=actor_cfg.get("status", "active"),
            nation_state_class=actor_cfg.get("nation_state_class", "criminal"),
            first_seen=actor_cfg.get("first_seen"),
            discovered=actor_cfg.get("discovered", False),
            sectors=actor_cfg.get("sectors", []),
            notable_victims=actor_cfg.get("notable_victims", []),
            notes=actor_cfg.get("notes", ""),
            criteria=criteria,
            recent_victims=recent,
            evidence=evidence,
            last_scanned=datetime.utcnow().isoformat(timespec="seconds"),
        )
        return compute_composites(actor)

    async def run_scan(self, result: ScanResult) -> ScanResult:
        backend = await self.llm.detect()
        result.llm_backend = backend
        result.add_log(f"LLM backend: {backend}")

        config = load_config()
        actors_cfg = list(config["actors"])
        seed_count = len(actors_cfg)

        # Discovery: find active groups not already seeded, and append them.
        new_cfgs = await self.discover_new(actors_cfg)
        if new_cfgs:
            actors_cfg.extend(new_cfgs)
            result.discovered_count = len(new_cfgs)
            names = ", ".join(c["name"] for c in new_cfgs[:8])
            more = "" if len(new_cfgs) <= 8 else f" (+{len(new_cfgs) - 8} more)"
            result.add_log(f"Discovery: {len(new_cfgs)} new actor(s) added — {names}{more}")
        else:
            result.add_log("Discovery: no new actors (sources offline or all known)")

        result.add_log(
            f"Scanning {len(actors_cfg)} actors "
            f"({seed_count} seeded + {result.discovered_count} discovered) "
            f"across {len(self.collectors)} sources"
        )

        for cfg in actors_cfg:
            try:
                actor = await self.assess_actor(cfg)
                result.actors.append(actor)
                tag = " [new]" if actor.discovered else ""
                result.add_log(
                    f"{actor.name}{tag}: severity {actor.threat_severity}, "
                    f"reliability {actor.deal_reliability} "
                    f"({len(actor.evidence)} evidence items)"
                )
            except Exception as exc:  # never let one actor kill the scan
                result.add_log(f"{cfg['name']}: error — {exc}")

        result.actors.sort(key=lambda a: a.threat_severity, reverse=True)
        result.status = "complete"
        result.finished = datetime.utcnow().isoformat(timespec="seconds")
        result.add_log("Scan complete")
        return result


def new_scan() -> ScanResult:
    return ScanResult(
        scan_id=uuid.uuid4().hex[:12],
        started=datetime.utcnow().isoformat(timespec="seconds"),
    )

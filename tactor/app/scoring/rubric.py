"""Scoring engine.

Converts per-criterion raw values (1-10) into two composite indices using the
weights defined in config/actors.yaml:

  Threat Severity  — how dangerous the actor is (higher = worse for you)
  Deal Reliability — if forced to pay, how likely they honor it (higher = more
                     reliable criminal; a planning input, not an endorsement)

Weights within each composite are normalized, so they need not sum to 1.
"""
from __future__ import annotations

from ..config import load_config
from ..models import ActorScore


def _weights(kind: str) -> dict[str, float]:
    crit = load_config()["rubric"]["criteria"]
    raw = {k: v.get(f"weight_{kind}", 0.0) for k, v in crit.items()}
    total = sum(raw.values()) or 1.0
    return {k: w / total for k, w in raw.items()}


def compute_composites(actor: ActorScore) -> ActorScore:
    sev_w = _weights("severity")
    rel_w = _weights("reliability")

    severity = sum(
        actor.criteria[k].raw * w for k, w in sev_w.items() if k in actor.criteria
    )
    reliability = sum(
        actor.criteria[k].raw * w for k, w in rel_w.items() if k in actor.criteria
    )

    actor.threat_severity = round(severity, 1)
    actor.deal_reliability = round(reliability, 1)

    confs = [c.confidence for c in actor.criteria.values()] or [0.5]
    actor.confidence = round(sum(confs) / len(confs), 2)
    return actor


def severity_band(score: float) -> str:
    if score >= 8.5:
        return "Critical"
    if score >= 7:
        return "High"
    if score >= 5:
        return "Elevated"
    if score >= 3:
        return "Moderate"
    return "Low"


def reliability_band(score: float) -> str:
    if score >= 7:
        return "Often honors payment"
    if score >= 5:
        return "Mixed / inconsistent"
    if score >= 3:
        return "Frequently cheats"
    return "Assume no recovery"

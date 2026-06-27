"""Applicability engine: given a user profile, decide which regulations apply
and explain *why*. Rule-based and explainable by design; an optional LLM pass
can enrich the rationale, but the decision itself is deterministic and free.
"""
from typing import Dict, List
from sqlalchemy.orm import Session
from .. import models
from . import llm

# Market criticality drives default priority ordering.
_MARKET_WEIGHT = {"United States": 0, "EU": 0, "EEA": 0, "United Kingdom": 1,
                  "China": 1, "Japan": 1, "Australia": 1, "Canada": 1, "Global": 2}

_REASON = {
    "markets": "you deploy in {v}",
    "product_types": "your product is a {v}",
    "data_types": "you process {v}",
    "flags": "your product is {v}",
}
_LABEL = {"phi": "US health data (PHI/ePHI)", "eu_personal": "EU personal/health data",
          "pii": "personal data (PII)", "payment": "payment/card data",
          "software": "software-based", "connected": "network-connected",
          "ai": "AI/ML-enabled", "ot": "operational-technology / ICS",
          "manufactures": "manufactured", "samd": "Software-as-a-Medical-Device",
          "medical_device": "medical device", "ivd": "in-vitro diagnostic",
          "healthcare_saas": "healthcare SaaS"}


def _label(v: str) -> str:
    return _LABEL.get(v, v)


def _matches(applies_when: Dict, profile: Dict):
    """A regulation applies if, for every criterion it specifies, the profile
    satisfies at least one value (AND across criteria, OR within). Returns the
    matched reasons or None."""
    if not applies_when:
        return None
    reasons = []
    for key, needed in applies_when.items():
        have = set(profile.get(key, []) or [])
        hit = have.intersection(needed)
        if not hit:
            return None  # a required criterion is unmet
        reasons.append((key, sorted(hit)))
    return reasons


def _priority(reg, reasons, profile) -> str:
    score = 0
    # market criticality
    markets = profile.get("markets", [])
    score += min([_MARKET_WEIGHT.get(m, 2) for m in markets], default=2)
    # emerging regs are higher priority to get ahead of
    if reg.emerging:
        score -= 1
    # data sensitivity raises priority
    if set(profile.get("data_types", [])) & {"phi", "eu_personal"}:
        score -= 1
    if reg.domain in ("privacy", "cybersecurity"):
        score -= 1
    return ["Critical", "High", "Medium", "Low"][max(0, min(3, score + 1))]


def evaluate(db: Session, profile: Dict, enrich: bool = False) -> List[Dict]:
    out = []
    for reg in db.query(models.Regulation).all():
        reasons = _matches(reg.applies_when or {}, profile)
        if reasons is None:
            continue
        why_parts = []
        for key, vals in reasons:
            shown = ", ".join(_label(v) for v in vals)
            why_parts.append(_REASON[key].format(v=shown))
        why = "Applies because " + "; and ".join(why_parts) + "."
        if enrich:
            why = llm.generate(
                prompt=f"In one sentence, explain why {reg.name} applies to a product that: {why}",
                system="You are a regulatory affairs assistant. Be concise and factual.",
                fallback=why)
        latest = reg.versions[-1] if reg.versions else None
        out.append({
            "reg_id": reg.id, "name": reg.name, "domain": reg.domain,
            "url": reg.url, "why": why, "emerging": reg.emerging,
            "priority": _priority(reg, reasons, profile),
            "change_type": latest.change_type if latest else None,
        })
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    out.sort(key=lambda x: (order[x["priority"]], not x["emerging"], x["name"]))
    return out

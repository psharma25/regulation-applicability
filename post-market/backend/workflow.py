"""
Disclosure lifecycle state machine.

The whole point of the program is that an advisory can only move forward through
explicit, auditable gates. Each transition is validated here, not in the routes,
so the rules live in one reviewable place.

    INGESTED -> TRIAGED -> VERIFYING -> VERIFIED -> DRAFTING -> DRAFT_READY
             -> IN_REVIEW -> APPROVED -> PUBLISHED
                                |
                                +-- (any reject) --> CHANGES_REQUESTED -> DRAFTING

    Off-ramp from TRIAGED: NOT_APPLICABLE (terminal, but still produces a VEX
    "known_not_affected" record, which is itself a disclosure obligation).
"""

STATES = [
    "INGESTED", "TRIAGED", "NOT_APPLICABLE", "VERIFYING", "VERIFIED",
    "DRAFTING", "DRAFT_READY", "IN_REVIEW", "CHANGES_REQUESTED",
    "APPROVED", "PUBLISHED",
]
import time

# Allowed forward transitions. Reverse/rework handled explicitly below.
TRANSITIONS = {
    "INGESTED": {"TRIAGED"},
    "TRIAGED": {"VERIFYING", "NOT_APPLICABLE"},
    "VERIFYING": {"VERIFIED", "NOT_APPLICABLE"},
    "VERIFIED": {"DRAFTING"},
    "DRAFTING": {"DRAFT_READY"},
    "DRAFT_READY": {"IN_REVIEW"},
    "IN_REVIEW": {"APPROVED", "CHANGES_REQUESTED"},
    "CHANGES_REQUESTED": {"DRAFTING"},
    "APPROVED": {"PUBLISHED"},
    "NOT_APPLICABLE": set(),
    "PUBLISHED": set(),
}

# Human-friendly station labels for the lifecycle rail in the UI.
STATIONS = ["INGESTED", "TRIAGED", "VERIFIED", "DRAFT_READY", "APPROVED", "PUBLISHED"]


class TransitionError(Exception):
    pass


def can_transition(current, target):
    return target in TRANSITIONS.get(current, set())


def assert_transition(current, target):
    if not can_transition(current, target):
        raise TransitionError(f"Illegal transition {current} -> {target}")


def signoff_summary(advisory, required_roles):
    """Return per-role status and whether all required gates are satisfied."""
    latest = {}
    for s in advisory.get("signoffs", []):
        latest[s["role"]] = s  # signoffs are time-ordered; last wins
    roles = {}
    for role in required_roles:
        s = latest.get(role)
        roles[role] = s["decision"] if s else "pending"
    approved = all(roles[r] == "approved" for r in required_roles)
    rejected = any(roles[r] == "rejected" for r in required_roles)
    return {"roles": roles, "all_approved": approved, "any_rejected": rejected}


# ---------------------------------------------------------------------------
# Enterprise step-by-step disclosure process (the guided workflow).
# Each macro step maps to one or more state-machine states, names the
# human-in-the-loop decision, and carries a target SLA used for the timeline
# and metrics. Disclosure artifacts use the CSAF 2.0 / VEX format that vendors
# submit to CISA, so "create disclosure" produces a CISA-compatible document.
# ---------------------------------------------------------------------------

DAY = 86400

MACRO_STEPS = [
    {"key": "discover", "label": "Discover vulnerability",
     "desc": "Ingest from NVD / CISA KEV / CISA ICS Medical Advisories, or inject a zero-day.",
     "states": ["INGESTED"], "hitl": None, "sla_days": 1,
     "checkpoint_from": "ingested", "checkpoint_to": "triaged"},
    {"key": "validate_impact", "label": "Validate impact",
     "desc": "Triage against device SBOMs, then confirm in the environment.",
     "states": ["TRIAGED", "VERIFYING", "VERIFIED"], "hitl": "Impacted? Yes / No",
     "sla_days": 3, "checkpoint_from": "triaged", "checkpoint_to": "verified"},
    {"key": "create_disclosure", "label": "Create disclosure (CISA format)",
     "desc": "Generate a CSAF 2.0 / VEX advisory in the format vendors report to CISA.",
     "states": ["DRAFTING", "DRAFT_READY"], "hitl": None, "sla_days": 2,
     "checkpoint_from": "verified", "checkpoint_to": "submitted-for-review"},
    {"key": "validate_signoff", "label": "Validate (legal · business · security · communication)",
     "desc": "Multi-stakeholder human sign-off. Any rejection returns for changes.",
     "states": ["IN_REVIEW", "CHANGES_REQUESTED"], "hitl": "Approve / Reject per role",
     "sla_days": 5, "checkpoint_from": "submitted-for-review", "checkpoint_to": "approved"},
    {"key": "publish", "label": "Disclosure draft / publish",
     "desc": "Publish advisory.md + CSAF/VEX + FDA report draft.",
     "states": ["APPROVED", "PUBLISHED"], "hitl": None, "sla_days": 1,
     "checkpoint_from": "approved", "checkpoint_to": "published"},
]

STATE_TO_MACRO = {s: m["key"] for m in MACRO_STEPS for s in m["states"]}
# Off-ramp
STATE_TO_MACRO["NOT_APPLICABLE"] = "validate_impact"

# audit action names that mark the boundary of each macro step
_CHECKPOINT_ACTIONS = {
    "ingested": ("ingested", "ingested-manual", "seed-ingested"),
    "triaged": ("triaged",),
    "verified": ("verified",),
    "submitted-for-review": ("submitted-for-review",),
    "approved": ("approved",),
    "published": ("published",),
}


def _checkpoints(audit):
    ts = {}
    for a in audit:
        act = a.get("action")
        for cp, names in _CHECKPOINT_ACTIONS.items():
            if act in names and cp not in ts:
                ts[cp] = a.get("at")
    return ts


def timeline(advisory):
    """Per-macro-step elapsed seconds (None if not reached) and total cycle time."""
    ts = _checkpoints(advisory.get("audit", []))
    out = {"steps": [], "total_seconds": None}
    for m in MACRO_STEPS:
        a, b = m["checkpoint_from"], m["checkpoint_to"]
        dur = (ts[b] - ts[a]) if (a in ts and b in ts) else None
        out["steps"].append({
            "key": m["key"], "label": m["label"],
            "seconds": dur, "sla_seconds": m["sla_days"] * DAY,
            "within_sla": (dur is not None and dur <= m["sla_days"] * DAY),
            "current": STATE_TO_MACRO.get(advisory["state"]) == m["key"],
        })
    if "ingested" in ts and "published" in ts:
        out["total_seconds"] = ts["published"] - ts["ingested"]
    return out


def current_macro(state):
    return STATE_TO_MACRO.get(state)


def sla_status(advisory):
    """For an in-progress advisory, time spent in the current step and whether it
    has breached that step's SLA. Terminal states are never overdue."""
    state = advisory["state"]
    if state in ("PUBLISHED", "NOT_APPLICABLE"):
        return {"in_progress": False, "overdue": False}
    macro_key = STATE_TO_MACRO.get(state)
    m = next((x for x in MACRO_STEPS if x["key"] == macro_key), None)
    if not m:
        return {"in_progress": True, "overdue": False}
    ts = _checkpoints(advisory.get("audit", []))
    start = ts.get(m["checkpoint_from"])
    if start is None:
        return {"in_progress": True, "overdue": False, "macro": macro_key}
    elapsed = time.time() - start
    target = m["sla_days"] * DAY
    return {
        "in_progress": True, "macro": macro_key, "macro_label": m["label"],
        "elapsed_seconds": elapsed, "sla_seconds": target,
        "overdue": elapsed > target, "over_by_seconds": max(0, elapsed - target),
    }

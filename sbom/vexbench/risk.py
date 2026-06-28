"""
risk.py — deterministic, transparent risk engine.

Likelihood  <- EPSS + CISA KEV + exploit maturity + attack vector + reachability
Impact      <- max(patient-safety, business)   (ISO 14971 / AAMI TIR57 flavored)
Inherent    <- 5x5 matrix(likelihood, impact)
Residual    <- inherent - control effectiveness ; VEX Fixed/Not-affected -> 0

The LLM never touches these numbers. It only drafts prose. This module is the
single source of truth for scoring and is unit-tested in test_risk.py.
"""

SEV_BANDS = ["Informational", "Low", "Medium", "High", "Critical"]


def band(i: int) -> str:
    return SEV_BANDS[max(0, min(4, i))]


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def cvss_severity_idx(cvss) -> int:
    c = _f(cvss)
    if c is None:
        return 0
    if c >= 9:
        return 4
    if c >= 7:
        return 3
    if c >= 4:
        return 2
    if c > 0:
        return 1
    return 0


def exploit_index(r: dict) -> float:
    """0..1 probability-of-exploitation proxy."""
    e = 0.0
    epss = _f(r.get("epss"))
    if epss is not None:
        e = max(e, epss)
    if r.get("kev") == "Yes":
        e = max(e, 0.92)
    mat = {"None": 0.0, "PoC": 0.25, "Functional": 0.6, "Weaponized": 0.9}.get(r.get("exploitMaturity"))
    if mat is not None:
        e = max(e, mat)
    av = {"Network": 0.10, "Adjacent": 0.04, "Local": -0.06, "Physical": -0.12}.get(r.get("attackVector"))
    if av is not None:
        e = min(1.0, max(0.0, e + av))
    if r.get("reachable") == "No":          # VEX: vulnerable code not in execute path
        e *= 0.25
    return max(0.0, min(1.0, e))


def impact_idx(r: dict) -> int:
    ps = {"Negligible": 1, "Minor": 1, "Serious": 3, "Critical": 4, "Catastrophic": 4}.get(r.get("patientSafety"), 0)
    bi = {"Low": 1, "Moderate": 2, "High": 3, "Severe": 4}.get(r.get("businessImpact"), 0)
    return max(ps, bi, 0)


_MATRIX = [  # rows = impact 0..4, cols = likelihood 0..4
    [0, 0, 1, 1, 2],
    [0, 1, 1, 2, 2],
    [1, 1, 2, 3, 3],
    [1, 2, 3, 3, 4],
    [2, 2, 3, 4, 4],
]


def likelihood_idx(r: dict) -> int:
    e = exploit_index(r)
    sev = cvss_severity_idx(r.get("cvss"))
    li = round(e * 4)
    if r.get("kev") == "Yes":
        li = max(li, 3)
    li = max(li, max(0, sev - 1))
    return min(4, max(0, li))


def _control_drop(eff) -> int:
    return {"None": 0, "Low": 0, "Moderate": 1, "High": 2}.get(eff, 0)


def compute(r: dict) -> dict:
    """Mutates and returns the finding dict with computed fields + _debug numerics."""
    r["computedSeverity"] = band(cvss_severity_idx(r.get("cvss")))
    ii = impact_idx(r)
    r["impact"] = band(ii)
    li = likelihood_idx(r)

    inh = _MATRIX[ii][li]
    vex = r.get("vexStatus")
    if vex == "Not affected":
        inh = 0
    elif vex == "Fixed":
        inh = min(inh, 1)
    r["inherentRisk"] = band(inh)

    res = inh - _control_drop(r.get("controlEffectiveness"))
    if vex in ("Not affected", "Fixed"):
        res = 0
    res = max(0, res)
    r["residualRisk"] = band(res)

    r["_li"], r["_ii"], r["_inh"], r["_res"] = li, ii, inh, res
    r["_exploit"] = round(exploit_index(r), 3)

    if not r.get("disposition"):
        if vex == "Fixed":
            r["disposition"] = "Remediated"
        elif vex == "Not affected":
            r["disposition"] = "Mitigable"
        elif res <= 1 and r.get("controlEffectiveness") not in (None, "", "None"):
            r["disposition"] = "Mitigated"
        elif inh >= 3:
            r["disposition"] = "Mitigable"
    return r

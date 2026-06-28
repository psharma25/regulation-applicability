"""
test_risk.py — guards the scoring engine. Run:  python -m pytest -q  (or python test_risk.py)
"""
import risk


def s(r):
    risk.compute(r)
    return r


def test_kev_actively_exploited_is_critical():
    r = s({"cvss": 9.8, "kev": "Yes", "epss": 0.71, "exploitMaturity": "Functional",
           "attackVector": "Network", "reachable": "Yes",
           "patientSafety": "Serious", "businessImpact": "Severe"})
    assert r["computedSeverity"] == "Critical"
    assert r["residualRisk"] == "Critical"


def test_vex_not_affected_collapses_residual():
    # CVSS 10 + KEV + weaponized, but code not in execute path -> not affected
    r = s({"cvss": 10, "kev": "Yes", "epss": 0.97, "exploitMaturity": "Weaponized",
           "attackVector": "Network", "reachable": "No", "vexStatus": "Not affected",
           "patientSafety": "Minor"})
    assert r["computedSeverity"] == "Critical"      # intrinsic severity unchanged
    assert r["inherentRisk"] == "Informational"     # but not exploitable here
    assert r["residualRisk"] == "Informational"


def test_compensating_control_lowers_residual():
    r = s({"cvss": 9.8, "kev": "No", "epss": 0.09, "exploitMaturity": "PoC",
           "attackVector": "Network", "reachable": "Yes",
           "patientSafety": "Critical", "businessImpact": "High",
           "controlEffectiveness": "Moderate"})
    assert r["inherentRisk"] == "Critical"
    assert r["residualRisk"] == "High"              # Moderate control drops one band


def test_low_impact_pulls_high_cvss_down():
    r = s({"cvss": 8.8, "kev": "No", "exploitMaturity": "None", "attackVector": "Local",
           "patientSafety": "Negligible", "businessImpact": "Low"})
    assert r["computedSeverity"] == "High"
    assert r["residualRisk"] in ("Low", "Informational")


def test_fixed_is_remediated():
    r = s({"cvss": 7.5, "vexStatus": "Fixed", "component": "x", "version": "1"})
    assert r["residualRisk"] == "Informational"
    assert r["disposition"] == "Remediated"


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
            ok += 1
        except AssertionError:
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{ok}/{len(fns)} passed")

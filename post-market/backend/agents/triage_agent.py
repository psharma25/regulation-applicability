"""
Triage agent: decides whether a CVE is applicable to the org's devices and which
ones are affected.

Two layers:
  1. Deterministic applicability matcher (the source of truth). Matches CVE CPEs
     and keywords against each device's SBOM components. This always runs and is
     fully explainable -- exactly what a regulator or auditor wants.
  2. An optional bounded agentic loop (plan -> act -> observe) that lets the LLM
     reason over the same tools and produce a narrative rationale + a recommended
     VEX status. If the LLM is unavailable, we fall back to a rule-derived
     rationale so the conclusion is identical, only the prose is templated.

VEX status values produced: known_affected | known_not_affected | under_investigation
"""
import re

from . import base


# ---- deterministic core -----------------------------------------------------

def _tokens(text):
    return set(re.findall(r"[a-z0-9][a-z0-9._-]+", (text or "").lower()))


def _cpe_product(cpe):
    # cpe:2.3:a:vendor:product:version:...
    parts = cpe.split(":")
    return (parts[3] if len(parts) > 4 else "").lower(), (parts[4] if len(parts) > 4 else "").lower()


def match_devices(cve_detail, devices):
    """Return list of {device, matched_components[], how}."""
    cve_cpes = cve_detail.get("cpes", [])
    cve_vendor_products = [_cpe_product(c) for c in cve_cpes]
    desc_tokens = _tokens(cve_detail.get("description") or cve_detail.get("title"))

    hits = []
    for dev in devices:
        matched = []
        for comp in dev.get("sbom", []):
            cname = (comp.get("component") or "").lower()
            csupplier = (comp.get("supplier") or "").lower()
            ccpe = comp.get("cpe") or ""
            reasons = []

            # 1) CPE product-name overlap (strongest signal)
            cprod = _cpe_product(ccpe)[1] if ccpe else ""
            for vend, prod in cve_vendor_products:
                if prod and (prod == cprod or (cprod and prod in cprod) or (cname and prod in cname)):
                    reasons.append(f"cpe-product:{prod}")

            # 2) component name appears in CVE description tokens
            if cname and {cname} & desc_tokens:
                reasons.append(f"name:{cname}")
            if csupplier and {csupplier} & desc_tokens:
                reasons.append(f"supplier:{csupplier}")

            if reasons:
                matched.append({
                    "component": comp.get("component"),
                    "version": comp.get("version"),
                    "cpe": ccpe,
                    "reasons": sorted(set(reasons)),
                })
        if matched:
            hits.append({
                "device_id": dev["id"],
                "device_name": dev["name"],
                "submission": dev.get("submission"),
                "fda_number": dev.get("fda_number"),
                "matched_components": matched,
            })
    return hits


# ---- agentic loop (bounded) -------------------------------------------------

TOOLS_DOC = """You can call these tools by returning JSON {"action": <tool>, "args": {...}}.
Tools:
  inventory_summary()         -> counts of devices and components
  match()                     -> deterministic component matches for this CVE
  conclude(applicable, vex_status, rationale, affected_device_ids)
Return ONLY one JSON object per step."""

SYSTEM = ("You are a medical-device PSIRT triage analyst. You assess whether a CVE "
          "affects the organization's products based on their SBOMs. Be conservative: "
          "if a component matches, mark applicable. Prefer known_affected when there is "
          "any credible match, under_investigation when ambiguous, known_not_affected only "
          "when clearly unrelated.")


def _agentic_trace(cve_detail, devices, det_hits):
    """Run a small plan-act-observe loop. Returns (conclusion, trace)."""
    if not base.llm_available():
        return None, []

    cve_blurb = (f"CVE {cve_detail.get('id')} | sev {cve_detail.get('severity')} "
                 f"cvss {cve_detail.get('cvss')} | KEV={cve_detail.get('in_kev')}\n"
                 f"desc: {cve_detail.get('description')}\n"
                 f"cpes: {cve_detail.get('cpes')}")
    trace, observations = [], []
    for step in range(4):
        prompt = (f"{TOOLS_DOC}\n\nCVE under review:\n{cve_blurb}\n\n"
                  f"Observations so far:\n{observations}\n\nNext step (one JSON object):")
        decision = base.generate_json(prompt, system=SYSTEM)
        if not decision or "action" not in decision:
            break
        action = decision["action"]
        trace.append(decision)
        if action == "inventory_summary":
            obs = {"devices": len(devices),
                   "components": sum(len(d.get("sbom", [])) for d in devices)}
        elif action == "match":
            obs = {"matches": [{"device": h["device_name"],
                                "components": [m["component"] for m in h["matched_components"]]}
                               for h in det_hits]}
        elif action == "conclude":
            return decision.get("args", decision), trace
        else:
            obs = {"error": f"unknown tool {action}"}
        observations.append({action: obs})
    return None, trace


# ---- public entrypoint ------------------------------------------------------

def triage(cve_detail, devices):
    det_hits = match_devices(cve_detail, devices)
    applicable = len(det_hits) > 0

    conclusion, trace = _agentic_trace(cve_detail, devices, det_hits)

    if conclusion:
        rationale = conclusion.get("rationale") or ""
        vex = conclusion.get("vex_status") or ("known_affected" if applicable else "known_not_affected")
        # The deterministic matcher overrides applicability to stay defensible.
        if applicable and vex == "known_not_affected":
            vex = "under_investigation"
    else:
        if applicable:
            names = ", ".join(h["device_name"] for h in det_hits)
            comps = ", ".join(sorted({m["component"] for h in det_hits
                                      for m in h["matched_components"]}))
            rationale = (f"Deterministic SBOM match: component(s) [{comps}] present in "
                         f"device(s) [{names}]. CVE base severity {cve_detail.get('severity')}"
                         f"{' and listed in CISA KEV (known exploited)' if cve_detail.get('in_kev') else ''}.")
            vex = "known_affected"
        else:
            rationale = ("No SBOM component or CPE in the device inventory matches this CVE. "
                         "Recommend documenting a known_not_affected VEX justification "
                         "(vulnerable_code_not_present).")
            vex = "known_not_affected"

    return {
        "applicable": applicable,
        "vex_status": vex,
        "affected_devices": det_hits,
        "rationale": rationale,
        "agent_trace": trace,
        "llm_used": bool(conclusion),
    }

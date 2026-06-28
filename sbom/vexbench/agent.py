"""
agent.py — the agentic core.

For each finding the agent runs a bounded ReAct loop:

  observe finding -> decide a tool -> execute -> feed observation back -> repeat
  -> emit a final assessment (patient-safety, business impact, disposition, rationale)

Tools available to the agent:
  kev(cve)        live CISA Known-Exploited check
  epss(cve)       live FIRST EPSS probability
  retrieve(query) RAG over FDA 524B / VEX / ISO 14971 corpus

The risk math is NEVER delegated to the model: after the agent fills the
qualitative fields, risk.compute() produces severity / inherent / residual
deterministically. If Ollama is unavailable the same tools run in a fixed
pipeline (still RAG-grounded, still threat-intel-enriched) so output is
identical in shape and the program is fully functional offline.
"""
import json

import intel
import llm
import rag
import risk

MAX_STEPS = 6

_SYSTEM = (
    "You are a medical-device product-security analyst preparing an FDA premarket "
    "cybersecurity (section 524B) submission. You assess one SBOM vulnerability at a "
    "time. You may call tools to gather evidence before deciding. Think about patient "
    "safety per ISO 14971 and exploitability per EPSS/KEV. "
    "Respond with EXACTLY ONE json object per turn and nothing else.\n"
    "To use a tool: {\"action\":\"tool\",\"tool\":\"kev|epss|retrieve\",\"arg\":\"...\"}\n"
    "When ready: {\"action\":\"final\",\"assessment\":{"
    "\"patientSafety\":\"Negligible|Minor|Serious|Critical|Catastrophic\","
    "\"businessImpact\":\"Low|Moderate|High|Severe\","
    "\"vexStatus\":\"Under investigation|Affected|Not affected|Fixed\","
    "\"vexJustification\":\"\",\"controlEffectiveness\":\"None|Low|Moderate|High\","
    "\"disposition\":\"Remediated|Mitigated|Mitigable|Not currently remediable|Accepted (no action)\","
    "\"remediation\":\"1-2 sentences\","
    "\"rationale\":\"why this disposition; if not remediable, state why not\"}}"
)

_TOOLNAMES = {"kev", "epss", "retrieve"}


def _run_tool(name, arg):
    if name == "kev":
        return {"cve": arg, "on_kev": intel.kev(arg)}
    if name == "epss":
        return {"cve": arg, "epss": intel.epss(arg)}
    if name == "retrieve":
        hits = rag.retrieve(arg, k=3)
        return {"query": arg, "passages": [h["text"][:600] for h in hits],
                "sources": [h["source"] for h in hits]}
    return {"error": f"unknown tool {name}"}


def _finding_brief(r):
    keys = ["component", "version", "supplier", "vulnId", "cvss", "cvssVector",
            "epss", "kev", "exploitMaturity", "attackVector", "reachable", "vexStatus"]
    return {k: r.get(k) for k in keys if r.get(k) not in (None, "")}


# ---------------------------------------------------------------- agentic path
def _agentic(r, trace):
    transcript = [f"FINDING: {json.dumps(_finding_brief(r))}"]
    assessment = None
    for step in range(MAX_STEPS):
        prompt = "\n".join(transcript) + "\nYour single json action:"
        try:
            raw = llm.generate(prompt, system=_SYSTEM, force_json=True)
        except Exception as e:
            trace.append(f"llm error: {e}; switching to deterministic")
            return None
        msg = llm.parse_json_loose(raw)
        if not msg:
            trace.append(f"step {step}: unparseable -> stop")
            break
        action = msg.get("action")
        if action == "final" and isinstance(msg.get("assessment"), dict):
            assessment = msg["assessment"]
            trace.append(f"step {step}: final assessment")
            break
        if action == "tool" and msg.get("tool") in _TOOLNAMES:
            obs = _run_tool(msg["tool"], msg.get("arg", ""))
            trace.append(f"step {step}: {msg['tool']}({msg.get('arg','')}) -> {json.dumps(obs)[:160]}")
            transcript.append(f"ACTION: {json.dumps(msg)}")
            transcript.append(f"OBSERVATION: {json.dumps(obs)}")
            continue
        trace.append(f"step {step}: malformed action -> stop")
        break
    return assessment


# ----------------------------------------------------------- deterministic path
def _deterministic(r, trace):
    cve = r.get("vulnId", "")
    # tool pass: enrich threat intel if missing
    if cve and not r.get("kev"):
        r["kev"] = "Yes" if intel.kev(cve) else "No"
        trace.append(f"kev({cve}) -> {r['kev']}")
    if cve and not r.get("epss"):
        e = intel.epss(cve)
        if e is not None:
            r["epss"] = round(e, 4)
            trace.append(f"epss({cve}) -> {r['epss']}")
    risk.compute(r)
    # RAG-grounded rationale
    q = f"{r.get('component','')} {cve} patient safety remediation residual risk"
    hits = rag.retrieve(q, k=2)
    if hits:
        trace.append("retrieve -> " + ", ".join(h["source"] for h in hits))
    a = {}
    if not r.get("patientSafety"):
        a["patientSafety"] = "Serious" if r["_inh"] >= 3 else ("Minor" if r["_inh"] == 2 else "Negligible")
    if not r.get("businessImpact"):
        a["businessImpact"] = {4: "Severe", 3: "High", 2: "Moderate"}.get(r["_inh"], "Low")
    # apply impact fields and recompute BEFORE drafting prose, so rationale matches residual
    for k, v in a.items():
        r[k] = v
    risk.compute(r)
    a["rationale"] = _draft_rationale(r)
    a["remediation"] = _draft_remediation(r)
    return a


def _draft_rationale(r):
    if r.get("vexStatus") == "Not affected":
        j = (r.get("vexJustification") or "not exploitable in this configuration").replace("_", " ")
        return f"Not affected: {j}. Listed for transparency; no remediation required this release."
    if r.get("vexStatus") == "Fixed":
        return (f"Remediated by upgrading {r.get('component')} past {r.get('version')}. "
                "Confirm fixed version in the shipped build and regression-test.")
    parts = [f"{r.get('vulnId','Finding')} affects {r.get('component','')} {r.get('version','')}.".strip()]
    parts.append(f"CVSS {r.get('cvss','n/a')} ({r['computedSeverity']})"
                 + (", on CISA KEV — actively exploited" if r.get('kev') == 'Yes' else '')
                 + f"; exploitability ~{int(r['_exploit']*100)}%.")
    if r["_ii"] >= 3:
        parts.append(f"Impact is safety-relevant ({r.get('patientSafety') or r['impact']}); "
                     "could affect device intended use.")
    if r["_res"] >= 3:
        reasons = []
        if r.get("reachable") != "No" and r.get("attackVector") == "Network":
            reasons.append("network-reachable attack surface remains")
        if (r.get("controlEffectiveness") or "None") == "None":
            reasons.append("no compensating control in place yet")
        why = (" Why not yet resolved: " + "; ".join(reasons) + ".") if reasons else ""
        parts.append(f"Residual risk is {r['residualRisk']}.{why} "
                     "Recommend upstream patch or scoped compensating control before sign-off.")
    else:
        parts.append(f"Residual reduced to {r['residualRisk']} via "
                     f"{r.get('controlEffectiveness') or 'planned'} compensating controls.")
    return " ".join(parts)


def _draft_remediation(r):
    if r.get("vexStatus") == "Fixed":
        return f"Upgrade {r.get('component')} to the fixed version; confirm in the shipped build's SBOM."
    if r.get("vexStatus") == "Not affected":
        return "No action — see justification."
    if r["_res"] >= 3:
        return (f"Patch {r.get('component')} to a non-vulnerable version. If none: isolate the component "
                "(segmentation / disable affected feature), add input validation, schedule fix next release.")
    return ("Apply compensating control"
            + (", restrict network exposure" if r.get("attackVector") == "Network" else "")
            + "; monitor for exploitation; plan patch in roadmap.")


# ----------------------------------------------------------------------- public
def enrich_one(r, only_empty=True, mode="auto"):
    """Enrich a single finding in place. Returns (finding, trace)."""
    trace = []
    use_agent = mode == "agent" or (mode == "auto" and llm.available())
    assessment = None
    if use_agent:
        trace.append("mode: agentic (Ollama)")
        assessment = _agentic(r, trace)
    if assessment is None:
        if use_agent:
            trace.append("mode: deterministic (fallback)")
        else:
            trace.append("mode: deterministic")
        assessment = _deterministic(r, trace)

    for k, v in (assessment or {}).items():
        if v in (None, ""):
            continue
        if only_empty and r.get(k) not in (None, ""):
            # don't overwrite analyst-entered values, except always refresh prose
            if k not in ("rationale", "remediation"):
                continue
        r[k] = v
    risk.compute(r)            # numbers are ALWAYS deterministic
    return r, trace


def enrich_all(rows, only_empty=True, mode="auto"):
    out_trace = []
    for i, r in enumerate(rows):
        _, t = enrich_one(r, only_empty=only_empty, mode=mode)
        out_trace.append({"row": i, "steps": t})
    return rows, out_trace

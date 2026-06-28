"""
Medical Device CVD Console -- FastAPI backend.

One web interface to trigger each step of coordinated vulnerability disclosure:
  scan feeds -> triage -> verify -> draft -> sign-off -> publish.

Run:  uvicorn backend.app:app --reload  (from the project root)
"""
import json
import os
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from . import db, workflow, trust_centers
from .agents import base, disclosure_agent, feed_agent, triage_agent

FRONTEND = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
OUTPUT_DIR = os.environ.get("CVD_OUTPUT_DIR",
                            os.path.join(os.path.dirname(os.path.dirname(__file__)), "published"))

ORG = {
    "name": os.environ.get("ORG_NAME", "Meridian Medical Systems"),
    "namespace": os.environ.get("ORG_NAMESPACE", "https://psirt.meridianmed.example"),
    "contact": os.environ.get("ORG_CONTACT", "psirt@meridianmed.example"),
}

app = FastAPI(title="Medical Device CVD Console")


@app.on_event("startup")
def _startup():
    db.init_db()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    from . import seed
    seed.ensure_seed()
    seed.ensure_disclosure_seed()
    seed.ensure_incident_seed()


# ---- models -----------------------------------------------------------------

class ScanReq(BaseModel):
    keyword: str | None = None
    days: int = 2


class ManualCveReq(BaseModel):
    cve_id: str
    title: str
    severity: str = "HIGH"
    cvss: float = 8.0
    cpes: list[str] = []
    cwes: list[str] = []
    in_kev: bool = False


class VerifyReq(BaseModel):
    status: str          # confirmed | not_reproducible | mitigated
    evidence: str
    actor: str = "analyst"


class SignoffReq(BaseModel):
    role: str
    decision: str        # approved | rejected
    actor: str = "user"
    comment: str = ""


class RolesReq(BaseModel):
    roles: list[str]


# ---- system / config --------------------------------------------------------

@app.get("/")
def index():
    return FileResponse(FRONTEND)


@app.get("/api/health")
def health():
    return {"ok": True, "llm_available": base.llm_available(),
            "model": base.OLLAMA_MODEL if base.LLM_ENABLED else None,
            "states": workflow.STATES, "stations": workflow.STATIONS,
            "required_roles": db.get_required_roles(), "org": ORG}


@app.get("/api/devices")
def devices():
    return db.list_devices()


# ---- trust centers ----------------------------------------------------------

@app.get("/api/trust-centers")
def get_trust_centers():
    return {"directory_source": trust_centers.DIRECTORY_SOURCE,
            "trust_centers": trust_centers.TRUST_CENTERS}


# ---- incidents --------------------------------------------------------------

class IncidentReq(BaseModel):
    vendor: str
    product: str | None = None
    title: str
    cve: str | None = None
    severity: str = "MEDIUM"
    cvss: float | None = None
    status: str = "monitoring"
    disclosed_date: str | None = None
    patch_available: str | None = None
    patch_deployed: str | None = None
    source_url: str | None = None
    affected_device: str | None = None


class PatchReq(BaseModel):
    patch_deployed: str
    status: str | None = None


@app.get("/api/incidents")
def get_incidents():
    return db.list_incidents()


@app.post("/api/incidents")
def create_incident(req: IncidentReq):
    import uuid
    tc = trust_centers.by_company().get(req.vendor)
    if not tc:
        tc = trust_centers.match_for_supplier(req.vendor)
    inc = req.model_dump()
    inc["id"] = "INC-" + uuid.uuid4().hex[:10].upper()
    inc["trust_center"] = tc["trust_center"] if tc else None
    inc["seeded"] = 0
    db.upsert_incident(inc)
    return {"id": inc["id"]}


@app.put("/api/incidents/{incident_id}/patch")
def set_patch_deployed(incident_id: str, req: PatchReq):
    fields = {"patch_deployed": req.patch_deployed}
    if req.status:
        fields["status"] = req.status
    db.update_incident(incident_id, **fields)
    return {"ok": True}


@app.post("/api/advisories/{advisory_id}/to-incident")
def advisory_to_incident(advisory_id: str):
    """Promote a published advisory into the incident register with patch timing."""
    import time as _t, uuid
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    if a["state"] != "PUBLISHED":
        raise HTTPException(409, "publish the advisory before logging it as an incident")
    tr = a.get("triage") or {}
    devs = tr.get("affected_devices", [])
    vendor = ORG["name"]
    inc = {
        "id": "INC-" + uuid.uuid4().hex[:10].upper(),
        "vendor": vendor,
        "product": ", ".join(d["device_name"] for d in devs) or "—",
        "title": a.get("title"),
        "cve": a.get("cve_id"),
        "severity": a.get("severity"),
        "cvss": a.get("cvss"),
        "status": "resolved",
        "disclosed_date": _t.strftime("%Y-%m-%d"),
        "patch_available": "See published advisory",
        "patch_deployed": _t.strftime("%Y-%m-%d") + " (published advisory)",
        "source_url": None,
        "trust_center": ORG.get("namespace"),
        "affected_device": devs[0]["device_id"] if devs else None,
        "seeded": 0,
    }
    db.upsert_incident(inc)
    db.log(advisory_id, "user", "logged-incident", inc["id"])
    return {"id": inc["id"]}


@app.get("/api/config/roles")
def get_roles():
    return {"required_roles": db.get_required_roles()}


@app.put("/api/config/roles")
def put_roles(req: RolesReq):
    db.set_required_roles(req.roles)
    return {"required_roles": db.get_required_roles()}


# ---- advisories list/detail -------------------------------------------------

@app.get("/api/advisories")
def advisories():
    out = []
    for a in db.list_advisories():
        full = db.get_advisory(a["id"])
        rec = {k: a[k] for k in
               ("id", "cve_id", "title", "source", "severity", "cvss",
                "in_kev", "state", "updated_at", "cisa_url", "authority",
                "ext_vendor", "vendor_disclosed", "vendor_disclosure_url", "sector")}
        rec["sla"] = workflow.sla_status(full)
        out.append(rec)
    return out


@app.get("/api/advisories/{advisory_id}")
def advisory_detail(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    a["signoff_summary"] = workflow.signoff_summary(a, db.get_required_roles())
    a["timeline"] = workflow.timeline(a)
    a["current_macro"] = workflow.current_macro(a["state"])
    a["sla"] = workflow.sla_status(a)
    return a


@app.get("/api/process")
def process_guide():
    return {"steps": workflow.MACRO_STEPS, "required_roles": db.get_required_roles()}


def _fmt_days(seconds):
    return None if seconds is None else round(seconds / workflow.DAY, 1)


@app.get("/api/metrics")
def metrics():
    advs = db.list_advisories()
    by_state, by_sev = {}, {}
    by_sector = {}
    for a in advs:
        by_state[a["state"]] = by_state.get(a["state"], 0) + 1
        s = a.get("severity") or "NONE"
        by_sev[s] = by_sev.get(s, 0) + 1
        sec = a.get("sector") or "Unspecified"
        d = by_sector.setdefault(sec, {"disclosed": 0, "not_impacting": 0, "in_progress": 0, "total": 0})
        d["total"] += 1
        if a["state"] == "PUBLISHED":
            d["disclosed"] += 1
        elif a["state"] == "NOT_APPLICABLE":
            d["not_impacting"] += 1
        else:
            d["in_progress"] += 1

    disclosed = by_state.get("PUBLISHED", 0)
    not_impacting = by_state.get("NOT_APPLICABLE", 0)
    terminal = disclosed + not_impacting
    in_progress = len(advs) - terminal

    overdue = 0
    for a in advs:
        st = workflow.sla_status(db.get_advisory(a["id"]))
        if st.get("overdue"):
            overdue += 1

    # timeline aggregates across advisories that reached each checkpoint
    step_acc = {m["key"]: [] for m in workflow.MACRO_STEPS}
    cycle = []
    for a in advs:
        full = db.get_advisory(a["id"])
        tl = workflow.timeline(full)
        for st in tl["steps"]:
            if st["seconds"] is not None:
                step_acc[st["key"]].append(st["seconds"])
        if tl["total_seconds"] is not None:
            cycle.append(tl["total_seconds"])

    step_metrics = []
    for m in workflow.MACRO_STEPS:
        vals = step_acc[m["key"]]
        avg = sum(vals) / len(vals) if vals else None
        within = sum(1 for v in vals if v <= m["sla_days"] * workflow.DAY)
        step_metrics.append({
            "key": m["key"], "label": m["label"],
            "avg_days": _fmt_days(avg), "sla_days": m["sla_days"],
            "samples": len(vals),
            "sla_adherence": round(100 * within / len(vals)) if vals else None,
        })

    sev_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"]
    return {
        "total_tracked": len(advs),
        "cves_disclosed": disclosed,
        "cves_not_impacting": not_impacting,
        "in_progress": in_progress,
        "overdue": overdue,
        "severity_distribution": {k: by_sev.get(k, 0) for k in sev_order if by_sev.get(k)},
        "sector_breakdown": by_sector,
        "state_distribution": by_state,
        "avg_cycle_days": _fmt_days(sum(cycle) / len(cycle) if cycle else None),
        "step_metrics": step_metrics,
        "sla_target_days": sum(m["sla_days"] for m in workflow.MACRO_STEPS),
    }


@app.get("/api/metrics/report.md", response_class=PlainTextResponse)
def metrics_report():
    """A board-to-SOC style Markdown summary for export."""
    m = metrics()
    lines = [
        f"# {ORG['name']} — Coordinated Vulnerability Disclosure Metrics",
        f"_Generated {time.strftime('%Y-%m-%d %H:%M')} · SLA target {m['sla_target_days']} days end-to-end_",
        "",
        "## Headline",
        f"- CVEs disclosed (published): **{m['cves_disclosed']}**",
        f"- CVEs not impacting (known_not_affected): **{m['cves_not_impacting']}**",
        f"- In progress: **{m['in_progress']}**  (overdue against step SLA: **{m['overdue']}**)",
        f"- Average cycle time: **{m['avg_cycle_days']} days**",
        "",
        "## Severity distribution",
    ]
    for k, v in m["severity_distribution"].items():
        lines.append(f"- {k.title()}: {v}")
    lines += ["", "## Timeline per step (avg vs SLA · adherence)"]
    for s in m["step_metrics"]:
        lines.append(f"- {s['label']}: {s['avg_days']}d / {s['sla_days']}d SLA · "
                     f"{s['sla_adherence']}% within SLA (n={s['samples']})")
    lines += ["", "_CSAF 2.0 / VEX disclosures; FDA report is a drafting aid, not a regulatory filing._"]
    return "\n".join(lines)


# ---- step 1: scan feeds (trigger) ------------------------------------------

@app.post("/api/scan")
def scan(req: ScanReq):
    try:
        new_ids = feed_agent.poll(keyword=req.keyword, days=req.days)
    except Exception as e:
        raise HTTPException(502, f"feed error: {e}")
    return {"ingested": new_ids, "count": len(new_ids)}


@app.post("/api/advisories/manual")
def manual(req: ManualCveReq):
    adv_id = feed_agent.ingest_manual(req.cve_id, req.title, req.severity, req.cvss,
                                      req.cpes, req.cwes, req.in_kev)
    if not adv_id:
        raise HTTPException(409, "CVE already tracked")
    return {"id": adv_id}


# ---- step 2: triage ---------------------------------------------------------

@app.post("/api/advisories/{advisory_id}/triage")
def do_triage(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    result = triage_agent.triage(a.get("cve_detail") or {}, db.list_devices())
    target = "TRIAGED"
    workflow.assert_transition(a["state"], target) if a["state"] == "INGESTED" else None
    db.update_advisory(advisory_id, triage=result, state="TRIAGED")
    db.log(advisory_id, "triage-agent", "triaged",
           f"applicable={result['applicable']} vex={result['vex_status']} llm={result['llm_used']}")
    return db.get_advisory(advisory_id)


@app.post("/api/advisories/{advisory_id}/start-verification")
def start_verification(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    workflow.assert_transition(a["state"], "VERIFYING")
    db.update_advisory(advisory_id, state="VERIFYING")
    db.log(advisory_id, "user", "verification-started")
    return db.get_advisory(advisory_id)


@app.post("/api/advisories/{advisory_id}/not-applicable")
def mark_na(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    workflow.assert_transition(a["state"], "NOT_APPLICABLE")
    db.update_advisory(advisory_id, state="NOT_APPLICABLE")
    db.log(advisory_id, "user", "marked-not-applicable")
    return db.get_advisory(advisory_id)


# ---- step 3: verify in environment -----------------------------------------

@app.post("/api/advisories/{advisory_id}/verify")
def verify(advisory_id: str, req: VerifyReq):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    if a["state"] not in ("VERIFYING", "TRIAGED"):
        raise HTTPException(409, f"cannot verify from state {a['state']}")
    ver = {"status": req.status, "evidence": req.evidence,
           "by": req.actor, "at": time.time()}
    next_state = "VERIFIED" if req.status in ("confirmed", "mitigated") else "NOT_APPLICABLE"
    db.update_advisory(advisory_id, verification=ver, state=next_state)
    db.log(advisory_id, req.actor, "verified", f"{req.status}: {req.evidence[:120]}")
    return db.get_advisory(advisory_id)


# ---- step 4: draft disclosure ----------------------------------------------

@app.post("/api/advisories/{advisory_id}/draft")
def draft(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    if a["state"] not in ("VERIFIED", "CHANGES_REQUESTED"):
        raise HTTPException(409, f"cannot draft from state {a['state']}")
    db.update_advisory(advisory_id, state="DRAFTING")
    doc = disclosure_agent.draft(db.get_advisory(advisory_id), ORG)
    db.update_advisory(advisory_id, document=doc, state="DRAFT_READY")
    db.log(advisory_id, "disclosure-agent", "drafted",
           f"llm={base.llm_available()}")
    return db.get_advisory(advisory_id)


class EditDocReq(BaseModel):
    advisory_md: str


@app.put("/api/advisories/{advisory_id}/document")
def edit_doc(advisory_id: str, req: EditDocReq):
    a = db.get_advisory(advisory_id)
    if not a or not a.get("document"):
        raise HTTPException(404, "no draft")
    doc = a["document"]
    doc["advisory_md"] = req.advisory_md
    db.update_advisory(advisory_id, document=doc)
    db.log(advisory_id, "user", "edited-advisory")
    return db.get_advisory(advisory_id)


# ---- step 5: review + sign-off ---------------------------------------------

@app.post("/api/advisories/{advisory_id}/submit-review")
def submit_review(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    workflow.assert_transition(a["state"], "IN_REVIEW")
    db.clear_signoffs(advisory_id)
    db.update_advisory(advisory_id, state="IN_REVIEW")
    db.log(advisory_id, "user", "submitted-for-review", "new review round; prior sign-offs reset")
    return db.get_advisory(advisory_id)


@app.post("/api/advisories/{advisory_id}/signoff")
def signoff(advisory_id: str, req: SignoffReq):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    if a["state"] != "IN_REVIEW":
        raise HTTPException(409, "advisory is not in review")
    if req.decision not in ("approved", "rejected"):
        raise HTTPException(400, "decision must be approved|rejected")
    db.add_signoff(advisory_id, req.role, req.decision, req.actor, req.comment)
    db.log(advisory_id, req.actor, f"signoff-{req.decision}", f"{req.role}: {req.comment[:120]}")

    a = db.get_advisory(advisory_id)
    summary = workflow.signoff_summary(a, db.get_required_roles())
    if summary["any_rejected"]:
        db.update_advisory(advisory_id, state="CHANGES_REQUESTED")
    elif summary["all_approved"]:
        db.update_advisory(advisory_id, state="APPROVED")
        db.log(advisory_id, "workflow", "approved", "all required validations passed")
    out = db.get_advisory(advisory_id)
    out["signoff_summary"] = workflow.signoff_summary(out, db.get_required_roles())
    return out


# ---- step 6: publish --------------------------------------------------------

@app.post("/api/advisories/{advisory_id}/publish")
def publish(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a:
        raise HTTPException(404, "not found")
    workflow.assert_transition(a["state"], "PUBLISHED")
    doc = a.get("document") or {}
    base_name = f"{a['cve_id']}_{a['id']}"
    paths = {}
    md_path = os.path.join(OUTPUT_DIR, base_name + ".md")
    with open(md_path, "w") as f:
        f.write(doc.get("advisory_md", ""))
    paths["advisory_md"] = md_path
    csaf_path = os.path.join(OUTPUT_DIR, base_name + ".csaf.json")
    with open(csaf_path, "w") as f:
        json.dump(doc.get("csaf", {}), f, indent=2)
    paths["csaf"] = csaf_path
    fda_path = os.path.join(OUTPUT_DIR, base_name + ".fda-report.json")
    with open(fda_path, "w") as f:
        json.dump(doc.get("fda_report", {}), f, indent=2)
    paths["fda_report"] = fda_path

    db.update_advisory(advisory_id, state="PUBLISHED")
    db.log(advisory_id, "user", "published", json.dumps(paths))
    out = db.get_advisory(advisory_id)
    out["published_files"] = paths
    return out


@app.get("/api/advisories/{advisory_id}/advisory.md", response_class=PlainTextResponse)
def advisory_md(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a or not a.get("document"):
        raise HTTPException(404, "no draft")
    return a["document"].get("advisory_md", "")


@app.get("/api/advisories/{advisory_id}/csaf.json")
def csaf_json(advisory_id: str):
    a = db.get_advisory(advisory_id)
    if not a or not a.get("document"):
        raise HTTPException(404, "no draft")
    return JSONResponse(a["document"].get("csaf", {}))

"""Weekly scan pipeline.

crawler.fetch()  -> retrieve current source text for a regulation (live HTTP in
                    production; offline-safe stub that returns the stored summary
                    so the pipeline always runs in dev/CI).
delta.diff()     -> compare new content hash to the last snapshot and classify
                    new / updated / unchanged, with an LLM-or-template delta note.
run_scan()       -> orchestrates: crawl -> diff -> snapshot -> re-embed changed.

Cost optimisation: only regulations whose content hash changed are re-embedded
and re-summarised, so a typical weekly run touches a handful of records.
"""
import hashlib
import urllib.request
import datetime as dt
from sqlalchemy.orm import Session
from .. import models
from . import rag, llm


# ---------------------------------------------------------------- crawler ----
def fetch(reg: models.Regulation) -> str:
    """Return current source text. Tries a lightweight HTTP fetch; falls back to
    the stored summary so the pipeline is fully offline-capable."""
    try:
        req = urllib.request.Request(reg.url, headers={"User-Agent": "RegPulse/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read(200_000).decode("utf-8", "ignore")
        # crude text reduction (strip tags) — production would use trafilatura
        import re
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:8000] or reg.summary
    except Exception:
        return reg.summary or reg.name


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()


# ------------------------------------------------------------------ delta ----
def classify(reg: models.Regulation, new_hash: str, prior_hash: str | None) -> str:
    if prior_hash is None:
        return "new"
    return "unchanged" if new_hash == prior_hash else "updated"


def impact_of(reg: models.Regulation) -> str:
    if reg.domain in ("cybersecurity", "privacy", "ai") or reg.emerging:
        return "high"
    if reg.category in ("qms", "premarket", "payments"):
        return "medium"
    return "low"


def delta_note(reg: models.Regulation, change_type: str, new_text: str) -> str:
    if change_type == "unchanged":
        return "No material change detected this cycle."
    base = (f"{'New regulation added to coverage.' if change_type=='new' else 'Source content changed since the last snapshot.'} "
            f"Review {reg.name} for impact on mapped controls.")
    return llm.generate(
        prompt=f"Summarise in 1-2 sentences what a compliance owner should check given a change to {reg.name}. Context: {new_text[:1500]}",
        system="You are a regulatory change analyst. Be specific and concise.",
        fallback=base)


# --------------------------------------------------------------- scan run ----
def run_scan(db: Session) -> models.ScanRun:
    run = models.ScanRun(started_at=dt.datetime.utcnow(), status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    new = updated = unchanged = 0
    for reg in db.query(models.Regulation).all():
        text = fetch(reg)
        new_hash = content_hash(text)
        prior = (db.query(models.RegulationVersion)
                 .filter(models.RegulationVersion.reg_id == reg.id)
                 .order_by(models.RegulationVersion.created_at.desc()).first())
        # On the very first scan there is no prior version; use the seed hash
        # stored on the regulation as the baseline.
        prior_hash = prior.source_hash if prior else reg.source_hash
        change = classify(reg, new_hash, prior_hash)

        if change == "new":
            new += 1
        elif change == "updated":
            updated += 1
        else:
            unchanged += 1

        ver = models.RegulationVersion(
            reg_id=reg.id, source_hash=new_hash, summary=reg.summary,
            change_type=change, impact=impact_of(reg),
            delta=delta_note(reg, change, text), scan_id=run.id)
        db.add(ver)

        # only mutate + re-embed when changed (cost optimisation)
        if change != "unchanged":
            reg.source_hash = new_hash
            reg.updated_at = dt.datetime.utcnow()

    db.commit()
    rag.ensure_embeddings(db)  # re-embeds only changed regs

    run.finished_at = dt.datetime.utcnow()
    run.new_count, run.updated_count, run.unchanged_count = new, updated, unchanged
    run.status = "done"
    db.commit()
    db.refresh(run)
    return run


def latest_delta(db: Session, limit: int = 100):
    run = (db.query(models.ScanRun)
           .filter(models.ScanRun.status == "done")
           .order_by(models.ScanRun.started_at.desc()).first())
    if not run:
        return None, []
    versions = (db.query(models.RegulationVersion)
                .filter(models.RegulationVersion.scan_id == run.id)
                .limit(limit).all())
    items = []
    order = {"new": 0, "updated": 1, "unchanged": 2}
    imp = {"high": 0, "medium": 1, "low": 2}
    for v in versions:
        reg = db.get(models.Regulation, v.reg_id)
        items.append({"reg_id": v.reg_id, "name": reg.name if reg else v.reg_id,
                      "url": reg.url if reg else "", "change_type": v.change_type,
                      "impact": v.impact, "delta": v.delta,
                      "version": reg.version if reg else ""})
    items.sort(key=lambda x: (order.get(x["change_type"], 3), imp.get(x["impact"], 3)))
    return run, items

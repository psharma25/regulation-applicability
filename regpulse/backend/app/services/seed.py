"""Load seed regulations + controls into the DB (idempotent)."""
import json
import os
from sqlalchemy.orm import Session
from ..config import settings
from .. import models


def seed(db: Session):
    regs = json.load(open(os.path.join(settings.DATA_DIR, "regulations.json")))
    controls = json.load(open(os.path.join(settings.DATA_DIR, "controls.json")))

    for r in regs:
        if db.get(models.Regulation, r["id"]):
            continue
        db.add(models.Regulation(
            id=r["id"], name=r["name"], body=r.get("body"), domain=r.get("domain"),
            region=r.get("region"), category=r.get("category"), url=r.get("url"),
            summary=r.get("summary"), emerging=r.get("emerging", False),
            jurisdictions=r.get("jurisdictions", []), topics=r.get("topics", []),
            applies_when=r.get("applies_when", {}), version=r.get("version"),
            source_hash=r.get("source_hash"),
            briefing={k: r.get(k) for k in ("what_it_is", "why_important", "detail",
                                            "change", "change_date", "change_impact",
                                            "change_note", "delta", "impact")}))

    for c in controls:
        if db.get(models.Control, c["id"]):
            continue
        db.add(models.Control(
            id=c["id"], domain=c["domain"], title=c["title"],
            explanation=c["explanation"], actions=c["actions"], priority=c["priority"],
            severity=c["severity"], score=c["score"], phase=c["phase"],
            effort=c["effort"], regulations=c["regulations"]))
    db.commit()

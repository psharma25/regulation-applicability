"""Applicability, roadmap generation, weekly scan/delta, and user persistence."""
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas, auth
from ..services import applicability, roadmap, scan

router = APIRouter(prefix="/api", tags=["core"])


# ------------------------------------------------------------- controls -----
@router.get("/controls")
def list_controls(db: Session = Depends(get_db)):
    out = []
    for c in db.query(models.Control).all():
        out.append({"id": c.id, "domain": c.domain, "title": c.title,
                    "explanation": c.explanation, "actions": c.actions or [],
                    "priority": c.priority, "severity": c.severity, "score": c.score,
                    "phase": c.phase, "effort": c.effort,
                    "regulations": c.regulations or []})
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    out.sort(key=lambda x: (x["phase"], order.get(x["priority"], 9), -x["score"]))
    return out


# ---------------------------------------------------------- applicability ----
@router.post("/applicability", response_model=schemas.ApplicabilityResult)
def applicable(body: schemas.ProfileIn, db: Session = Depends(get_db)):
    profile = body.model_dump()
    items = applicability.evaluate(db, {
        "markets": profile["markets"], "product_types": profile["product_types"],
        "data_types": profile["data_types"], "flags": profile["flags"]})
    return {"profile": profile, "applicable": items, "count": len(items)}


# --------------------------------------------------------------- roadmap ----
@router.post("/roadmap.xlsx")
def roadmap_xlsx(body: schemas.RoadmapRequest, db: Session = Depends(get_db)):
    data = roadmap.to_excel(db, body.reg_ids, body.profile_name)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="regpulse_roadmap.xlsx"'})


@router.post("/roadmap")
def roadmap_json(body: schemas.RoadmapRequest, db: Session = Depends(get_db)):
    return {"rows": roadmap.build(db, body.reg_ids)}


# ------------------------------------------------------------ weekly scan ----
@router.post("/scan/run")
def run_scan(db: Session = Depends(get_db)):
    run = scan.run_scan(db)
    return {"id": run.id, "new": run.new_count, "updated": run.updated_count,
            "unchanged": run.unchanged_count,
            "started_at": run.started_at, "finished_at": run.finished_at}


@router.get("/scan/delta")
def get_delta(db: Session = Depends(get_db)):
    run, items = scan.latest_delta(db)
    if not run:
        return {"run": None, "items": []}
    return {"run": {"id": run.id, "started_at": run.started_at,
                    "new": run.new_count, "updated": run.updated_count,
                    "unchanged": run.unchanged_count}, "items": items}


# ----------------------------------------------- persistence (auth needed) ---
@router.get("/profiles", response_model=list[schemas.ProfileOut])
def list_profiles(user: models.User = Depends(auth.current_user),
                  db: Session = Depends(get_db)):
    return user.profiles


@router.post("/profiles", response_model=schemas.ProfileOut)
def save_profile(body: schemas.ProfileIn,
                 user: models.User = Depends(auth.current_user),
                 db: Session = Depends(get_db)):
    p = models.Profile(user_id=user.id, name=body.name, data={
        "markets": body.markets, "product_types": body.product_types,
        "data_types": body.data_types, "flags": body.flags})
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.post("/analyses")
def save_analysis(body: schemas.SaveAnalysisIn,
                  user: models.User = Depends(auth.current_user),
                  db: Session = Depends(get_db)):
    a = models.SavedAnalysis(user_id=user.id, name=body.name,
                             applicable=body.applicable)
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id, "name": a.name, "created_at": a.created_at}


@router.get("/analyses")
def list_analyses(user: models.User = Depends(auth.current_user)):
    return [{"id": a.id, "name": a.name, "applicable": a.applicable,
             "created_at": a.created_at} for a in user.analyses]

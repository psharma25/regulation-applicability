"""Regulation browsing, detail, semantic search, and per-regulation roadmap."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
import io
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models
from ..services import rag, roadmap

router = APIRouter(prefix="/api/regulations", tags=["regulations"])


@router.get("")
def list_regs(domain: str | None = None, q: str | None = None,
              db: Session = Depends(get_db)):
    query = db.query(models.Regulation)
    if domain and domain != "all":
        query = query.filter(models.Regulation.domain == domain)
    regs = query.all()
    if q:
        ql = q.lower()
        regs = [r for r in regs if ql in (r.name + r.summary + " " +
                " ".join(r.topics or [])).lower()]
    return [_card(r) for r in regs]


@router.get("/search")
def semantic_search(q: str = Query(...), k: int = 5, db: Session = Depends(get_db)):
    """RAG semantic search over regulation text."""
    return [{"score": s, **_card(r)} for r, s in rag.search(db, q, k)]


@router.get("/{reg_id}")
def detail(reg_id: str, db: Session = Depends(get_db)):
    reg = db.get(models.Regulation, reg_id)
    if not reg:
        return {"error": "not found"}
    latest = reg.versions[-1] if reg.versions else None
    controls = [c.id for c in db.query(models.Control).all()
                if reg_id in (c.regulations or [])]
    return {**_card(reg), "summary": reg.summary, "body": reg.body,
            "jurisdictions": reg.jurisdictions, "topics": reg.topics,
            "briefing": reg.briefing or {},
            "latest_delta": (latest.delta if latest else (reg.briefing or {}).get("delta")),
            "mapped_controls": controls}


@router.get("/{reg_id}/roadmap.xlsx")
def reg_roadmap(reg_id: str, db: Session = Depends(get_db)):
    data = roadmap.to_excel(db, [reg_id], profile_name=reg_id)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{reg_id}_roadmap.xlsx"'})


def _card(r: models.Regulation):
    latest = r.versions[-1] if r.versions else None
    return {"id": r.id, "name": r.name, "body": r.body, "domain": r.domain,
            "region": r.region, "category": r.category, "url": r.url,
            "summary": r.summary, "emerging": r.emerging,
            "jurisdictions": r.jurisdictions, "version": r.version,
            "change_type": latest.change_type if latest else None}

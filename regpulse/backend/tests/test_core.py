"""Core logic tests — run with: pytest -q  (uses an in-memory SQLite DB)."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DATABASE_URL"] = "sqlite://"   # in-memory
os.environ["ENABLE_SCHEDULER"] = "false"
os.environ["USE_LLM"] = "false"

from sqlalchemy import create_engine          # noqa: E402
from sqlalchemy.orm import sessionmaker        # noqa: E402
from sqlalchemy.pool import StaticPool         # noqa: E402
import app.db as dbmod                         # noqa: E402

# rebind engine to a shared in-memory DB for tests
engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                       poolclass=StaticPool)
dbmod.engine = engine
dbmod.SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

from app import models                          # noqa: E402
from app.services import seed, applicability, roadmap, scan, rag  # noqa: E402
from app import auth                            # noqa: E402


@pytest.fixture(scope="module")
def db():
    models.Base.metadata.create_all(bind=engine)
    s = dbmod.SessionLocal()
    seed.seed(s)
    yield s
    s.close()


def test_seed_loaded(db):
    assert db.query(models.Regulation).count() >= 30
    assert db.query(models.Control).count() >= 20


def test_applicability_us_phi(db):
    profile = {"markets": ["United States"], "product_types": ["samd"],
               "data_types": ["phi"], "flags": ["software", "connected"]}
    items = applicability.evaluate(db, profile)
    ids = {i["reg_id"] for i in items}
    assert "HIPAA" in ids                 # US + PHI
    assert "FDA-CYBER" in ids             # connected software in US
    assert "EU-MDR" not in ids            # no EU market
    # rationale present and priorities valid
    assert all(i["why"].startswith("Applies because") for i in items)
    assert all(i["priority"] in {"Critical", "High", "Medium", "Low"} for i in items)


def test_applicability_eu_ai(db):
    profile = {"markets": ["EU"], "product_types": ["medical_device"],
               "data_types": ["eu_personal"], "flags": ["ai", "software"]}
    ids = {i["reg_id"] for i in applicability.evaluate(db, profile)}
    assert {"EU-MDR", "EU-GDPR", "EU-AI-ACT"} <= ids


def test_roadmap_dedup_and_excel(db):
    reg_ids = ["HIPAA", "EU-GDPR", "ISO-27001"]
    rows = roadmap.build(db, reg_ids)
    assert rows, "should produce controls"
    # de-dup: each control appears once, tagged with covered regs only
    assert len({r["id"] for r in rows}) == len(rows)
    iam = next(r for r in rows if r["id"] == "IAM-01")
    assert set(iam["regulations"]) <= set(reg_ids)
    # ordered by phase then priority
    phases = [r["phase"] for r in rows]
    assert phases == sorted(phases)
    xlsx = roadmap.to_excel(db, reg_ids, "Test")
    assert xlsx[:2] == b"PK"              # valid xlsx zip
    assert len(xlsx) > 5000


def test_weekly_scan_and_delta(db):
    run1 = scan.run_scan(db)
    # first scan: everything matches its seed hash -> unchanged baseline
    assert run1.new_count + run1.updated_count + run1.unchanged_count == \
        db.query(models.Regulation).count()
    _, items = scan.latest_delta(db)
    assert items and all("change_type" in i for i in items)

    # simulate a source change on one regulation, re-scan, expect 'updated'
    reg = db.get(models.Regulation, "EU-AI-ACT")
    reg.summary = reg.summary + " UPDATED CLAUSE."
    db.commit()
    # monkeypatch fetch to return new text
    orig = scan.fetch
    scan.fetch = lambda r: r.summary
    try:
        run2 = scan.run_scan(db)
    finally:
        scan.fetch = orig
    _, items2 = scan.latest_delta(db)
    changed = {i["reg_id"]: i["change_type"] for i in items2}
    assert changed.get("EU-AI-ACT") in ("updated", "new")


def test_rag_search(db):
    rag.ensure_embeddings(db)
    hits = rag.search(db, "software bill of materials cybersecurity", k=5)
    assert hits and all(0.0 <= s <= 1.0 for _, s in hits)


def test_auth_password_and_token():
    h = auth.hash_password("s3cret")
    assert auth.verify_password("s3cret", h)
    assert not auth.verify_password("wrong", h)
    tok = auth.create_token("a@b.com")
    assert tok.count(".") == 2

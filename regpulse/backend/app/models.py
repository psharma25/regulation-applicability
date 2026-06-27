"""ORM models. JSON columns keep this portable across Postgres and SQLite."""
import datetime as dt
from sqlalchemy import (Column, Integer, String, Text, Boolean, Float,
                        DateTime, ForeignKey, JSON)
from sqlalchemy.orm import relationship
from .db import Base


def now():
    return dt.datetime.utcnow()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=now)
    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("SavedAnalysis", back_populates="user", cascade="all, delete-orphan")


class Regulation(Base):
    __tablename__ = "regulations"
    id = Column(String(40), primary_key=True)          # e.g. "EU-MDR"
    name = Column(String(255), nullable=False)
    body = Column(String(120))                          # issuing body
    domain = Column(String(40))                         # device/manufacturing/itot/...
    region = Column(String(40))
    category = Column(String(60))
    url = Column(Text)
    summary = Column(Text)
    emerging = Column(Boolean, default=False)
    jurisdictions = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    applies_when = Column(JSON, default=dict)
    version = Column(String(60))
    source_hash = Column(String(80))
    briefing = Column(JSON, default=dict)   # what_it_is, why_important, detail, change*
    updated_at = Column(DateTime, default=now)
    versions = relationship("RegulationVersion", back_populates="regulation",
                            cascade="all, delete-orphan", order_by="RegulationVersion.created_at")


class RegulationVersion(Base):
    """Immutable snapshot captured by each weekly scan -> enables delta."""
    __tablename__ = "regulation_versions"
    id = Column(Integer, primary_key=True)
    reg_id = Column(String(40), ForeignKey("regulations.id"))
    source_hash = Column(String(80))
    summary = Column(Text)
    change_type = Column(String(20))   # new / updated / unchanged
    delta = Column(Text)               # human-readable what-changed
    impact = Column(String(20))        # high / medium / low
    scan_id = Column(Integer, ForeignKey("scan_runs.id"))
    created_at = Column(DateTime, default=now)
    regulation = relationship("Regulation", back_populates="versions")


class Control(Base):
    __tablename__ = "controls"
    id = Column(String(40), primary_key=True)
    domain = Column(String(40))
    title = Column(String(255))
    explanation = Column(Text)
    actions = Column(JSON, default=list)
    priority = Column(String(20))
    severity = Column(String(20))
    score = Column(Float)
    phase = Column(Integer)
    effort = Column(String(4))
    regulations = Column(JSON, default=list)   # list of reg ids


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(120))
    data = Column(JSON, default=dict)          # markets, product_types, data_types, flags
    created_at = Column(DateTime, default=now)
    user = relationship("User", back_populates="profiles")


class SavedAnalysis(Base):
    __tablename__ = "saved_analyses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    name = Column(String(120))
    applicable = Column(JSON, default=list)    # cached applicability result
    created_at = Column(DateTime, default=now)
    user = relationship("User", back_populates="analyses")


class ScanRun(Base):
    __tablename__ = "scan_runs"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=now)
    finished_at = Column(DateTime)
    new_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    unchanged_count = Column(Integer, default=0)
    status = Column(String(20), default="running")


class Embedding(Base):
    """Cached vector for a regulation chunk. Re-computed only on hash change
    (a key cost optimisation)."""
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True)
    reg_id = Column(String(40), ForeignKey("regulations.id"))
    source_hash = Column(String(80))
    chunk = Column(Text)
    vector = Column(JSON)   # list[float]; pgvector column in prod migration

"""Data models shared across the tracker."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """A single piece of evidence gathered by a collector."""

    source: str                      # collector name, e.g. "ransomware.live"
    title: str
    url: Optional[str] = None
    snippet: str = ""
    published: Optional[str] = None
    raw: dict = Field(default_factory=dict)


class CriterionScore(BaseModel):
    key: str
    label: str
    raw: float                       # 1-10 derived value
    confidence: float = 0.5          # 0-1, how much we trust the derivation
    rationale: str = ""
    source: str = "prior"            # "prior" | "llm" | "heuristic"


class ActorScore(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    origin: str = "Unknown"
    model: str = "Unknown"
    status: str = "active"                  # active | defunct
    nation_state_class: str = "criminal"   # directed | tolerated | criminal
    discovered: bool = False                # True if found by scan, not in seed config
    notes: str = ""

    criteria: dict[str, CriterionScore] = Field(default_factory=dict)
    threat_severity: float = 0.0     # composite 1-10
    deal_reliability: float = 0.0    # composite 1-10
    recent_victims: int = 0
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: float = 0.5
    last_scanned: Optional[str] = None


class ScanResult(BaseModel):
    scan_id: str
    started: str
    finished: Optional[str] = None
    status: str = "running"          # running | complete | error
    llm_backend: str = "none"
    actors: list[ActorScore] = Field(default_factory=list)
    discovered_count: int = 0
    log: list[str] = Field(default_factory=list)
    workbook_path: Optional[str] = None
    error: Optional[str] = None

    def add_log(self, msg: str) -> None:
        stamp = datetime.utcnow().strftime("%H:%M:%S")
        self.log.append(f"[{stamp}] {msg}")

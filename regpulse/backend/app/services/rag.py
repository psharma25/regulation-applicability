"""Retrieval-Augmented Generation helpers.

Embeddings backend preference (all open source / local):
  1. Ollama embeddings (e.g. nomic-embed-text)
  2. sentence-transformers (all-MiniLM-L6-v2) if installed
  3. Deterministic hashing embedding (always works, offline, for dev/tests)

Cost optimisation: vectors are cached per regulation keyed by source_hash, so
the (relatively expensive) embedding step runs only when a regulation actually
changes during the weekly scan.
"""
import hashlib
import json
import math
import urllib.request
from typing import List
from sqlalchemy.orm import Session
from ..config import settings
from .. import models

_DIM = 256


def _hash_embed(text: str) -> List[float]:
    """Feature-hashing embedding: deterministic, dependency-free fallback."""
    vec = [0.0] * _DIM
    for tok in text.lower().split():
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % _DIM] += 1.0
    n = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / n for v in vec]


def _ollama_embed(text: str):
    try:
        body = json.dumps({"model": settings.EMBED_MODEL, "prompt": text}).encode()
        req = urllib.request.Request(settings.OLLAMA_URL + "/api/embeddings",
                                     data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["embedding"]
    except Exception:
        return None


_st_model = None


def _st_embed(text: str):
    global _st_model
    try:
        if _st_model is None:
            from sentence_transformers import SentenceTransformer
            _st_model = SentenceTransformer("all-MiniLM-L6-v2")
        return _st_model.encode(text, normalize_embeddings=True).tolist()
    except Exception:
        return None


def embed(text: str) -> List[float]:
    if settings.USE_LLM:
        v = _ollama_embed(text) or _st_embed(text)
        if v:
            return v
    return _hash_embed(text)


def cosine(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def ensure_embeddings(db: Session):
    """Embed regulations whose source_hash has no cached vector. Runs cheaply
    because unchanged regulations are skipped."""
    for reg in db.query(models.Regulation).all():
        existing = (db.query(models.Embedding)
                    .filter(models.Embedding.reg_id == reg.id,
                            models.Embedding.source_hash == reg.source_hash).first())
        if existing:
            continue
        # drop stale vectors for this reg
        db.query(models.Embedding).filter(models.Embedding.reg_id == reg.id).delete()
        chunk = f"{reg.name}. {reg.summary} Topics: {', '.join(reg.topics or [])}."
        db.add(models.Embedding(reg_id=reg.id, source_hash=reg.source_hash,
                                chunk=chunk, vector=embed(chunk)))
    db.commit()


def search(db: Session, query: str, k: int = 5):
    """Return top-k (regulation, score) by cosine similarity."""
    qv = embed(query)
    rows = db.query(models.Embedding).all()
    scored = [(e.reg_id, cosine(qv, e.vector or [])) for e in rows]
    scored.sort(key=lambda x: x[1], reverse=True)
    out = []
    seen = set()
    for rid, sc in scored:
        if rid in seen:
            continue
        seen.add(rid)
        reg = db.get(models.Regulation, rid)
        if reg:
            out.append((reg, round(sc, 4)))
        if len(out) >= k:
            break
    return out

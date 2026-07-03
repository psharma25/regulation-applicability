"""Minimal RAG index: chunk docs, embed them, retrieve by cosine similarity.

"Training" the RAG = building this index from the documents in docs/.
Re-run build_index() whenever documents change.
"""
import os
import numpy as np
from sentence_transformers import SentenceTransformer

DOCS_DIR = os.environ.get("DOCS_DIR", "docs")
CHUNK_SIZE = 800        # characters per chunk
CHUNK_OVERLAP = 150

_model = None
_chunks: list[dict] = []      # {text, source}
_embeddings: np.ndarray | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _read_file(path: str) -> str:
    if path.lower().endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - CHUNK_OVERLAP
    return chunks


def build_index() -> int:
    """Read every .md/.txt/.pdf in DOCS_DIR, chunk, embed. Returns chunk count."""
    global _chunks, _embeddings
    _chunks = []
    for name in sorted(os.listdir(DOCS_DIR)):
        path = os.path.join(DOCS_DIR, name)
        if not os.path.isfile(path):
            continue
        if not name.lower().endswith((".md", ".txt", ".pdf")):
            continue
        for chunk in _chunk_text(_read_file(path)):
            _chunks.append({"text": chunk, "source": name})
    if _chunks:
        texts = [c["text"] for c in _chunks]
        _embeddings = _get_model().encode(texts, normalize_embeddings=True)
    else:
        _embeddings = None
    return len(_chunks)


def retrieve(question: str, k: int = 4) -> list[dict]:
    """Return top-k chunks most similar to the question."""
    if _embeddings is None or not _chunks:
        return []
    q = _get_model().encode([question], normalize_embeddings=True)[0]
    scores = _embeddings @ q
    top = np.argsort(scores)[::-1][:k]
    return [
        {**_chunks[i], "score": round(float(scores[i]), 3)}
        for i in top
        if scores[i] > 0.1
    ]

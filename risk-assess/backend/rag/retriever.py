"""Open-source retriever over the bundled risk-knowledge base.

Primary path: sentence-transformers dense embeddings + cosine similarity.
Fallback path: scikit-learn TF-IDF (no model download, fully offline).
Either way, no proprietary services are used.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np

from .. import config


@dataclass
class Chunk:
    text: str
    source: str


def _read_knowledge() -> List[Chunk]:
    chunks: List[Chunk] = []
    for md in sorted(Path(config.KNOWLEDGE_DIR).glob("*.md")):
        raw = md.read_text(encoding="utf-8")
        # split on blank lines into paragraphs, then pack to ~CHUNK_SIZE chars
        paras = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
        buf = ""
        for p in paras:
            if len(buf) + len(p) + 1 <= config.CHUNK_SIZE:
                buf = f"{buf}\n{p}".strip()
            else:
                if buf:
                    chunks.append(Chunk(buf, md.stem))
                buf = p
        if buf:
            chunks.append(Chunk(buf, md.stem))
    return chunks


class Retriever:
    def __init__(self):
        self.chunks = _read_knowledge()
        self.mode = "none"
        self._model = None
        self._matrix = None
        self._vectorizer = None
        if self.chunks:
            self._build_index()

    def _want_embeddings(self) -> bool:
        if config.USE_EMBEDDINGS == "false":
            return False
        if config.USE_EMBEDDINGS == "true":
            return True
        return True  # auto: try, fall back on failure

    def _build_index(self):
        texts = [c.text for c in self.chunks]
        if self._want_embeddings():
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(config.EMBEDDING_MODEL)
                emb = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                self._matrix = np.asarray(emb, dtype="float32")
                self.mode = "embeddings"
                return
            except Exception:
                self._model = None
        # fallback: TF-IDF
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self._matrix = self._vectorizer.fit_transform(texts)
            self.mode = "tfidf"
        except Exception:
            self.mode = "keyword"

    def search(self, query: str, top_k: int | None = None):
        top_k = top_k or config.RAG_TOP_K
        if not self.chunks:
            return []
        if self.mode == "embeddings":
            q = self._model.encode([query], normalize_embeddings=True)[0]
            scores = self._matrix @ np.asarray(q, dtype="float32")
        elif self.mode == "tfidf":
            from sklearn.metrics.pairwise import cosine_similarity
            qv = self._vectorizer.transform([query])
            scores = cosine_similarity(qv, self._matrix)[0]
        else:  # naive keyword overlap
            terms = set(re.findall(r"\w+", query.lower()))
            scores = np.array([len(terms & set(re.findall(r"\w+", c.text.lower()))) for c in self.chunks], dtype="float32")
        order = np.argsort(scores)[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in order if scores[i] > 0]


_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever

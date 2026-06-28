"""
rag.py — dependency-free lexical RAG (BM25) over the bundled knowledge corpus.

No embeddings, no model download, no network. The corpus lives in ./knowledge
as markdown, split into chunks on blank lines / headings. Always works offline.
If you later want dense retrieval, swap retrieve() for an Ollama-embeddings call;
the agent only depends on retrieve(query, k) -> list[dict].
"""
import math
import os
import re
from functools import lru_cache

_HERE = os.path.dirname(os.path.abspath(__file__))
_KNOWLEDGE_DIR = os.path.join(_HERE, "knowledge")
_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str):
    return _TOKEN.findall(text.lower())


def _load_chunks():
    chunks = []
    if not os.path.isdir(_KNOWLEDGE_DIR):
        return chunks
    for fn in sorted(os.listdir(_KNOWLEDGE_DIR)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(_KNOWLEDGE_DIR, fn)
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        # split on headings or blank-line paragraphs
        parts = re.split(r"\n(?=#{1,6}\s)|\n\s*\n", raw)
        for p in parts:
            p = p.strip()
            if len(p) < 40:
                continue
            chunks.append({"source": fn, "text": p, "tokens": _tokenize(p)})
    return chunks


class _BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = docs
        self.k1, self.b = k1, b
        self.N = len(docs)
        self.avgdl = (sum(len(d["tokens"]) for d in docs) / self.N) if self.N else 0
        self.df = {}
        for d in docs:
            for t in set(d["tokens"]):
                self.df[t] = self.df.get(t, 0) + 1
        self.idf = {
            t: math.log(1 + (self.N - n + 0.5) / (n + 0.5)) for t, n in self.df.items()
        }

    def search(self, query, k=4):
        q = _tokenize(query)
        scored = []
        for d in self.docs:
            tf = {}
            for t in d["tokens"]:
                tf[t] = tf.get(t, 0) + 1
            dl = len(d["tokens"]) or 1
            score = 0.0
            for t in q:
                if t not in tf:
                    continue
                idf = self.idf.get(t, 0)
                f = tf[t]
                denom = f + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1))
                score += idf * (f * (self.k1 + 1)) / denom
            if score > 0:
                scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"source": d["source"], "text": d["text"], "score": round(s, 3)}
            for s, d in scored[:k]
        ]


@lru_cache(maxsize=1)
def _index():
    return _BM25(_load_chunks())


def retrieve(query: str, k: int = 4):
    """Return up to k relevant knowledge chunks for a query."""
    try:
        return _index().search(query, k)
    except Exception:
        return []


def corpus_stats():
    idx = _index()
    return {"chunks": idx.N, "sources": sorted({d["source"] for d in idx.docs})}

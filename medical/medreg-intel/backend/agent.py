"""Open-source agentic Q&A over the corpus. Uses Ollama if available; deterministic retrieval fallback."""
import os, json, requests

HERE = os.path.dirname(__file__)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")


def _corpus():
    out = {}
    for k in ("regulations", "submissions", "requirements", "incidents", "rta", "ai"):
        p = os.path.join(HERE, "data", f"{k}.json")
        out[k] = json.load(open(p)) if os.path.exists(p) else []
    return out


def ollama_available():
    try:
        return requests.get(f"{OLLAMA_URL}/api/tags", timeout=2).ok
    except Exception:
        return False


def _retrieve(q, corpus, k=8):
    terms = [t for t in q.lower().split() if len(t) > 2]
    scored = []
    for coll, rows in corpus.items():
        for r in rows:
            blob = json.dumps(r).lower()
            score = sum(blob.count(t) for t in terms)
            if score:
                scored.append((score, coll, r))
    scored.sort(key=lambda x: -x[0])
    return scored[:k]


def answer(question):
    corpus = _corpus()
    hits = _retrieve(question, corpus)
    context = "\n".join(f"[{c}] {r.get('name') or r.get('device') or r.get('trigger')}: "
                        f"{r.get('summary') or r.get('desc') or r.get('detail') or r.get('what') or ''}" for _, c, r in hits)
    if ollama_available():
        try:
            prompt = (f"You are a medical-device regulatory and cybersecurity assistant. Using ONLY the context, "
                      f"answer concisely and cite the bracketed collection. If unknown, say so.\n\nContext:\n{context}\n\nQuestion: {question}")
            r = requests.post(f"{OLLAMA_URL}/api/generate",
                              json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=60)
            r.raise_for_status()
            return {"mode": f"ollama:{OLLAMA_MODEL}", "answer": r.json().get("response", "").strip(),
                    "sources": [{"collection": c, "name": rr.get("name") or rr.get("device") or rr.get("trigger")} for _, c, rr in hits]}
        except Exception:
            pass
    # deterministic fallback
    if not hits:
        return {"mode": "retrieval", "answer": "No matching entries. Try terms like 'SBOM', '524B', 'PCCP', 'RTA', or a device name.", "sources": []}
    lines = [f"• [{c}] {r.get('name') or r.get('device') or r.get('trigger')} — "
             f"{(r.get('summary') or r.get('desc') or r.get('detail') or r.get('what') or '')[:160]}" for _, c, r in hits]
    return {"mode": "retrieval (Ollama offline)", "answer": "Most relevant entries:\n" + "\n".join(lines),
            "sources": [{"collection": c, "name": r.get('name') or r.get('device') or r.get('trigger')} for _, c, r in hits]}

# Risk Assessment AI

An **open-source, agentic RAG web app** that answers risk-management questions over a bundled
knowledge base of risk standards and generates **downloadable Excel risk-assessment templates**
for three domains:

| Domain | Standard basis | Distinctive scoring |
|---|---|---|
| **Medical device** | ISO 14971:2019 (+ ISO/TR 24971, IEC 62304/62366) | Severity × Probability (P = P1 × P2), risk-control hierarchy, residual & benefit-risk |
| **Finance** | ISO 31000 · COSO ERM · Basel taxonomy | Likelihood × Impact **plus** Expected Annual Loss = Exposure × Annual Probability |
| **Technology** | NIST RMF/CSF · ISO 27005 · FAIR | Explicit **Reputation / Financial / IP** loss dimensions; Aggregate Impact = MAX of the three |

Every component is open source. With no LLM configured it runs fully offline (TF-IDF retrieval +
extractive answers); add a local **Ollama** model for generative answers. Nothing proprietary, no API keys.

---

## Architecture

```
Browser (vanilla JS UI)
        │  /api/chat, /api/forms/{domain}/download
        ▼
FastAPI (backend/main.py)
        ├── Agent router (backend/rag/agent.py)   ── picks a tool
        │      ├── answer_question → Retriever + LLM
        │      ├── generate_form   → Excel registry
        │      └── list_forms
        ├── Retriever (backend/rag/retriever.py)   sentence-transformers ─► TF-IDF fallback
        ├── LLM client (backend/rag/llm.py)        Ollama HTTP ─► extractive fallback
        ├── Knowledge base (backend/knowledge/*.md)
        └── Excel generators (backend/excel/*.py)  openpyxl, live formulas
```

The "agentic" layer inspects each message, selects a tool (RAG answer, form generation, or listing),
and returns a structured action the UI renders (text answer with citations, or a download button).
It is dependency-free so it runs anywhere; swap in LangChain/LlamaIndex behind the same interface if desired.

## Open the web interface — three ways

1. **No install (open in browser):** double-click `index.html` at the repo root. Self-contained page with the risk calculators, the hazard/threat mapping library, and one-click Excel downloads (generated client-side). Nothing to run. The same file is published automatically via **GitHub Pages** — enable Pages (Settings → Pages → Source: GitHub Actions) and the app is live at `https://<your-user>.github.io/<repo>/`.
2. **One-click launcher (runs the full program):** double-click `start.command` (macOS) or `start.bat` (Windows). It installs dependencies on first run, starts the server, and opens `http://localhost:8000` — the full app with the agentic RAG chat.
3. **Manual:** `uvicorn backend.main:app --reload` then open `http://localhost:8000`.

## Quick start

### Option A — local Python
```bash
git clone <your-repo-url> risk-assessment-ai
cd risk-assessment-ai
pip install -r requirements.txt
uvicorn backend.main:app --reload
# open http://localhost:8000
```

### Option B — Docker
```bash
docker compose up --build       # app on :8000, optional ollama on :11434
# then (optional, for generative answers):
docker compose exec ollama ollama pull llama3.2
```

### Enable a local LLM (optional)
```bash
# install Ollama from https://ollama.com  (open source)
ollama serve & ollama pull llama3.2
export OLLAMA_HOST=http://localhost:11434 OLLAMA_MODEL=llama3.2
```

### Enable dense embeddings (optional, better retrieval)
```bash
pip install sentence-transformers
export USE_EMBEDDINGS=auto
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | engine status (retrieval mode, LLM, chunk count) |
| GET | `/api/domains` | list available templates |
| POST | `/api/chat` | `{ "message": "..." }` → agentic answer or download action |
| GET | `/api/forms/{domain}/download` | download the `.xlsx` template (`medical` / `finance` / `technology`) |

## Excel templates

Each workbook contains a **Risk Assessment/Register** sheet (worked examples + blank rows) and a
**Scales** sheet (scoring scales, colour-coded acceptability thresholds, and a 5×5 risk matrix).
Blue cells are inputs; black cells are live formulas. Key formulas:

- Medical: `P = ROUNDUP(P1*P2/5,0)`, `Risk Index = Severity × P`
- Finance: `Inherent Score = Likelihood × Impact`, `Expected Annual Loss = Exposure × Annual Probability`
- Technology: `Aggregate Impact = MAX(Reputation, Financial, IP)`, `Risk Score = Likelihood × Aggregate Impact`

Risk level (Low/Medium/High/Intolerable) and acceptability are looked up against thresholds on the Scales sheet.

## Tests
```bash
pytest -q
```
Covers health, domain listing, agent routing, downloads, and presence of live formulas in each workbook.

## Extending
- **Add a domain:** create `backend/excel/<domain>.py` with a `build(path)` function and register it in `backend/excel/__init__.py`.
- **Add knowledge:** drop Markdown files in `backend/knowledge/` and restart.
- **Swap the agent/LLM:** keep the `route(message) -> dict` contract in `backend/rag/agent.py`.

## License
MIT. Informational tool — not a substitute for professional regulatory, legal, medical, or financial advice.

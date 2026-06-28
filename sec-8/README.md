# SecIntel — Agentic Security-Incident Intelligence

A self-hostable web platform that turns a dataset of security incidents (those reported to U.S. **state Attorneys General** and/or the **SEC**) into a filterable, AI-analyzable console. Pick a **domain** (Manufacturing, FDA / Medical Device, Telecom, …) and a **product/entity**, watch the **statistics recompute live at the top of the page**, and ask a **local open-source LLM** to reason over the current selection.

100% open source. No API keys. The AI runs locally via [Ollama](https://ollama.com); if Ollama isn't running, the platform falls back to a transparent heuristic planner so it still works out of the box.

![domains: Manufacturing · FDA / Medical Device · Telecom · Technology · Finance · Healthcare · Critical Infrastructure · Retail & Entertainment · Data Broker](https://img.shields.io/badge/domains-9-34D8C6) ![license](https://img.shields.io/badge/license-MIT-blue)

---

## What it does

- **Live statistics band** — incidents, individuals impacted, nation-state count, SEC-reported, state-AG-reported, and a by-domain mini-chart. Recomputes on every filter change.
- **Six filters** — Domain (incl. **AI**), Sector, State (AG) dropdown, Product/entity, a Year-from/Year-to range, plus **SEC-reported** and **Nation-state** toggles. Every filter recomputes the stat band live and composes with the others.
- **Incident feed** — click any card to expand threat, attribution, financial / data / reputational loss, and source.
- **Agentic AI analyst** — a genuine tool-calling loop: the model decides when to call `filter_incidents`, `compute_statistics`, or `get_incident`, runs them against the dataset, and answers from the results (not from memory). The current domain/product filter is passed as context.
- **Refresh live (on demand)** — a button in the header that pulls the **latest SEC EDGAR cyber 8-K filings** every time you click it, merges them in under a new `SEC 8-K (live)` domain, and recomputes the stats. No key required.

## Run tracker — multi-source, on demand

Click **Run tracker** (top-right of the full app). It pulls on demand from several authoritative sources, merges the results into the dashboard, and shows a **"Where this data was obtained"** panel listing each source, its status, count, and a link to the exact portal. Window: **2025-01-01 → today** (2025–2026).

Sources (each record also carries its own `source` URL and `source_feed` label):

| Source | What it pulls | Where it's obtained |
|---|---|---|
| **SEC 8-K (Item 1.05)** | Material cyber-incident 8-Ks, 2025–2026 (paginated) | SEC EDGAR full-text search (`efts.sec.gov`) |
| **SEC 10-K (Item 1C)** | Annual cybersecurity disclosures, 2025–2026 (paginated) | SEC EDGAR full-text search |
| **HHS OCR Breach Portal** | HIPAA breaches of 500+ individuals — portal table parsed | `ocrportal.hhs.gov` |
| **CISA Known Exploited Vulnerabilities** | Actively-exploited CVEs added 2025–2026 — live JSON feed | `cisa.gov` KEV catalog |
| **Washington AG** | Per-breach records via the official **Socrata JSON API** | `data.wa.gov` (sb4j-ca4h) |
| **Other state AG portals (15)** | State breach notices — each portal fetched & table-parsed | **MA (mass.gov)**, CA, OR, ME, MT, MD, IA, NH, VT, TX, NY, IL, DE, WI, IN |

The app also shows a **State & Agency Breach Statistics** panel with the official annual totals (breaches + residents affected) fetched from the state pages — e.g. Massachusetts (mass.gov): 2,198 breaches / 3,008,989 residents in 2025; Washington (atg.wa.gov): 11.6M notices / 279 breaches in the 2024 report — alongside HHS national totals and the live CISA KEV feed. Per-company detail for most states lives in their annual PDFs or interactive portals; Washington exposes a full machine-readable API, which the tracker uses directly.

Set your SEC contact once (SEC returns HTTP 403 without it):

```bash
export SEC_USER_AGENT="Your Name your@email.com"
```

Tracked records flow into the same filters: they appear under live domains (`SEC 8-K (live)`, `SEC 10-K (live)`, `HHS OCR (live)`, `State AG (live)`), extend the **year range** to 2025–2026, set **SEC-reported / State AG / HHS OCR** flags, and (for 8-Ks) get the deep-extraction summary/financial/attribution. The live cache is git-ignored, so the tracker **re-pulls fresh each run**. Tune it:

```bash
LIVE_ENRICH_LIMIT=20 ./run.sh           # open more 8-K filings for extraction (default 12)
# choose sources: POST /api/tracker/run?sources=sec8k,sec10k,hhs,states
```

> The **standalone `index.html`** and **GitHub Pages** build are static (seed data only); the tracker's Run button there explains that the live pull runs in the full app (start.sh / Docker), since a static page can't fetch these sources from the browser.

## Architecture

```
Browser (frontend/)  ──HTTP──▶  FastAPI (backend/main.py)
  stat band, dropdowns,                 │
  incident feed, chat            ┌──────┴───────┐
                                 ▼              ▼
                          dataset.py        agent.py
                       (filter/stats)   (agentic loop)
                                 │              │
                                 ▼              ▼
                       data/incidents.json   Ollama  ── tools.py ──┐
                       (seed data)          (local LLM)  filter / stats / get
                                                  └── heuristic fallback ◀────┘
```

- **`backend/dataset.py`** — loads `data/incidents.json`, filters, computes stats.
- **`backend/tools.py`** — the three tools + their JSON schema (sent to the LLM for function calling).
- **`backend/agent.py`** — Ollama tool-calling loop; transparent heuristic planner when Ollama is offline.
- **`backend/live.py`** — on-demand SEC EDGAR fetch + merge (the **Refresh live** button), with hooks for more sources.
- **`backend/main.py`** — JSON API (`/api/meta`, `/api/incidents`, `/api/stats`, `/api/agent`) and serves the static frontend.
- **`frontend/`** — dependency-free HTML/CSS/JS (only Google Fonts over CDN).

## Run it — pick one

**A. Just open it (no install, no server)**

Double-click **`index.html`** at the repo root. It's a single self-contained file (styles, data, and logic all inlined) — the dashboard opens straight in your browser: stat band, domain→product dropdowns, incident feed, and an in-browser analyst. Use this to look around instantly; the **live SEC refresh** and the **local LLM** need the backend (option B/C below).

**B. One-click (local, full app: live refresh + optional local LLM)**

- macOS / Linux: double-click **`start.sh`** (or `./start.sh`)
- Windows: double-click **`start.bat`**

It creates a virtualenv, installs dependencies, starts the server, and opens `http://localhost:8000` in your browser. That's the whole web interface.

**C. Docker (run as-is, anywhere)**

```bash
docker compose up --build      # → http://localhost:8000
```

**D. GitHub Pages (zero install — runs from a URL after you push)**

The repo ships a static build in **`docs/`**. After pushing (below), enable Pages once and it serves the dashboard at `https://<you>.github.io/secintel/`. The static build includes the stat band, domain→product dropdowns, incident feed, and an in-browser analyst; the **live SEC refresh** and **local LLM** need the backend (options A/B), since GitHub Pages can't run a server.

> Manual run (any OS): `pip install -r requirements.txt` then `cd backend && uvicorn main:app --port 8000`.

### Enable the open-source LLM (full agentic mode)

```bash
# install Ollama from https://ollama.com, then:
ollama pull llama3.1          # or qwen2.5, mistral, etc.
ollama serve                  # if not already running
./run.sh
```

The badge top-right flips from `heuristic (Ollama offline)` to `ollama · llama3.1`. Pick any tool-calling-capable model:

```bash
OLLAMA_MODEL=qwen2.5 ./run.sh
```

## Push to GitHub

```bash
cd secintel
git init
git add .
git commit -m "SecIntel: agentic security-incident intelligence platform"
git branch -M main
git remote add origin https://github.com/<you>/secintel.git
git push -u origin main
```

Then turn on the live URL: **repo Settings → Pages → Source = "GitHub Actions."** The included workflow (`.github/workflows/pages.yml`) publishes `docs/` on every push. After editing the dataset, regenerate the static data with `./scripts/build_static.sh`.

## The data

`backend/data/incidents.json` ships with 32 seed incidents spanning 10 domains, including **15 real, source-linked 2025–2026 incidents** across all three channels: SEC-reported (United Natural Foods 8-K, Conduent, Coupang, Aflac), state-AG-reported incl. **Massachusetts** (PowerSchool, Hertz, WK Kellogg, Conduent), and HHS OCR (Yale New Haven Health 5.5M, DaVita, Kettering Health, Radiology Associates of Richmond, Healthcare Interactive, Blue Shield of California, Covenant Health, NYC Health + Hospitals 2026). Each carries its source URL. These are representative, source-linked, not the exhaustive thousands — the **Run tracker** button pulls the full live set on your machine.

Each record carries the fields a vCISO actually needs: domain(s), product/entity, threat type & category, individuals/devices impacted, **reported-to-state-AG**, **reported-to-SEC (with 8-K item)**, **nation-state Y/N + attribution**, and **financial / data / reputational** loss.

**Regenerate or extend** the dataset by editing `backend/data/build_dataset.py` and running it:

```bash
cd backend/data && python3 build_dataset.py
```

> **Provenance:** seed data is illustrative and source-linked where available. Counts and costs are frequently revised after disclosure — verify against the cited primary sources before any regulatory, legal, or board use. Planning intelligence only, not legal advice.

### Where to pull the full, authoritative data

- **Privacy Rights Clearinghouse — Data Breach Chronology** (14 state AGs + HHS): https://privacyrights.org/data-breaches
- **State AG portals**: California, Washington, Texas, Massachusetts, HHS OCR
- **SEC EDGAR full-text search** — Form 8-K Item 1.05 (material) / Item 8.01 (voluntary)

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/meta` | domains, products-by-domain, Ollama status |
| GET | `/api/incidents?domain=&product_id=&nation_state=&threat_category=` | filtered incidents |
| GET | `/api/stats?…` | aggregate statistics for the filter |
| POST | `/api/agent` | `{message, filters, history}` → agent reply + tool trace |
| POST | `/api/tracker/run` | run multi-source tracker (SEC 8-K+10-K, HHS, states); `?sources=` to select |
| GET | `/api/tracker/sources` | configured sources (where data is obtained) + last-run provenance |
| POST | `/api/live/refresh` | alias for the full tracker run |
| GET | `/api/live/status` | last run time, counts, per-source provenance |

## Extending

- **New tool** → add a function in `tools.py`, append its schema to `TOOLS`, handle it in `run_tool`. The agent can call it immediately.
- **Swap the model** → set `OLLAMA_MODEL`. Any Ollama tool-calling model works.
- **Bring your own data** → replace `incidents.json` (keep the field names) — dropdowns, stats, and the agent adapt automatically.

## License

MIT — see [LICENSE](LICENSE).

# RegPulse Intelligence

## ⚡ Fastest way to try it — no install
Open **`RegPulse.html`** (or `index.html`) by double-clicking it. It runs entirely in your
browser with the full dataset embedded — 91 regulations, 54 controls, applicability engine,
on-demand **Live Scan**, weekly delta, roadmaps and HTML/Excel downloads. No Python, no server, nothing to install.
You can also publish it free on **GitHub Pages** (Settings → Pages → deploy from `main`,
root) and the same `index.html` will be served.

The FastAPI server below is **optional** — use it only when you want live weekly crawling,
user accounts, a database and a vector store. `requirements.txt` (root and `backend/`) is for
that server.

---

> **Customer flow:** the app leads with **Applicability** — a customer enters their tool/product, markets and data and gets the regulations that apply and why. Weekly delta is an operator feature and now sits as the second-to-last tab. Coverage is **74 regulations across 14 jurisdictions** (US, EU, UK, Switzerland, Canada, Brazil, Japan, China, South Korea, India, Singapore, Australia + global standards), spanning device, manufacturing, IT/OT, privacy, AI **and SaaS/cloud products** (B2B SaaS, fintech, EdTech, consumer and government cloud) — now **91 regulations and 54 controls**, with deepened **CMMC 2.0 / NIST 800-171** and **PCI DSS v4.0.1** roadmaps (13 controls each).

**Weekly, local-AI regulatory & control intelligence for medical-device, manufacturing, and IT/OT compliance.**

RegPulse scans regulations across the world — existing and emerging — and for each one gives you the official source link, a plain-language summary, and a **prioritized, practical, downloadable Excel roadmap** of how to implement it. Tell it about your product, deployment markets and data, and it tells you **which regulations apply and why**. When several regulations apply, it builds **one combined, de-duplicated roadmap** (implement once, comply many). It runs **weekly** and shows you the **delta** — what changed. Users log in so their profiles and analyses persist.

Everything runs on **open-source** components and can run **fully local at $0 inference cost**.

---

## What it does

| Capability | How |
|---|---|
| **Regulation database** | 37 seeded regulations across device / manufacturing / IT-OT / privacy / AI, each with official URL, summary, jurisdictions, and applicability rules. Easily extended. |
| **Applicability engine** | Rule-based + explainable. Given your markets, product type, data types and characteristics, returns the regulations in scope, **why each applies**, and a priority order. |
| **Actionable roadmaps** | Each regulation maps to practical controls (explanation + action steps + priority + severity + phase + effort). Exported as a formatted **Excel** workbook, inline or downloadable. |
| **Combined roadmaps** | Select multiple regulations → overlapping controls are de-duplicated and tagged with every regulation they satisfy. |
| **Weekly delta** | A scheduled agent re-crawls sources, re-summarizes, diffs against last week's snapshot (content-hash), and classifies new / updated / unchanged with impact. |
| **Live Scan (on demand)** | Trigger the same pipeline yourself from the **Live Scan** tab — pick a scope, watch per-source progress, and get a dated, downloadable report. Mirrors the scheduled run. |
| **Accounts & persistence** | Register / log in (JWT). Save profiles and analyses across sessions. |
| **Local AI / RAG** | Local LLM (Ollama) + embeddings + cosine retrieval, with deterministic offline fallbacks so it always runs. |

---

## Architecture

```
                    ┌──────────────────────────────────────────────┐
  Web browser  ───▶ │  FastAPI  (serves SPA + REST API)            │
                    │   /api/auth  /api/regulations  /api/...      │
                    └───────┬───────────────┬──────────────┬───────┘
                            │               │              │
                   ┌────────▼──────┐ ┌──────▼──────┐ ┌─────▼───────┐
                   │ Applicability │ │   Roadmap   │ │  Scan/Delta │
                   │ rules engine  │ │  + openpyxl │ │  scheduler  │
                   └───────────────┘ └─────────────┘ └─────┬───────┘
                            │               │              │ weekly cron
                   ┌────────▼───────────────▼──────────────▼───────┐
                   │  RAG service: embeddings + cosine retrieval   │
                   │  LLM service: Ollama → OpenAI-compat → template│
                   └────────────────────┬──────────────────────────┘
                                        │
                          ┌─────────────▼─────────────┐
                          │  Postgres + pgvector (OSS) │
                          └────────────────────────────┘
```

**Tech (all open source):** FastAPI · SQLAlchemy · Postgres + pgvector · Ollama (Llama 3.2 / nomic-embed-text) · APScheduler · openpyxl · python-jose + bcrypt · vanilla-JS frontend.

The "agentic" pipeline is a small, explicit graph of steps — crawl → embed → summarize → diff → score — that you can extend with a framework like LangGraph if you want tool-using agents. It is deliberately simple so it is cheap to run and easy to audit.

---

## Quickstart

### Option A — zero infrastructure (SQLite, $0, offline)
```bash
cd backend
pip install -r requirements.txt
DATABASE_URL=sqlite:///./regpulse.db USE_LLM=false uvicorn app.main:app --reload
# open http://localhost:8000
```
On first start it seeds the database, builds embeddings, and runs an initial scan. The UI is served at `/`.

### Option B — full stack with Docker (Postgres + pgvector)
```bash
cp .env.example .env          # edit SECRET_KEY
docker compose up --build     # API on http://localhost:8000, Postgres on 5432
```

### Option C — add a local open-source LLM (Ollama)
```bash
docker compose --profile ai up --build -d
./scripts/pull_models.sh      # pulls llama3.2:3b + nomic-embed-text
# set USE_LLM=true in .env, then:
docker compose up -d api
```
With `USE_LLM=false` (default) the app uses deterministic templates and a hashing embedding — useful, free, and fully offline. Turning the LLM on enriches summaries, delta notes and applicability rationales, and gives semantically strong retrieval.

### Run the tests
```bash
cd backend && python -m pytest -q     # 7 tests, in-memory SQLite
```

---

## Cost optimization (built in)

The system is designed so the **default cost is $0** and scales gracefully:

1. **Template-first generation.** Core outputs (roadmaps, applicability rationale, control text) are produced deterministically from structured data. The LLM is *optional enrichment*, not a dependency — so you pay for inference only when you choose to.
2. **Local open-source models.** When you do enable AI, it runs on Ollama (Llama 3.2 3B + nomic-embed-text) on your own CPU/GPU — no per-token API cost.
3. **Content-hash diffing.** The weekly scan only re-summarizes and **re-embeds regulations whose source actually changed**, so a typical run touches a handful of records, not all of them.
4. **Embedding cache.** Vectors are cached per regulation keyed by `source_hash`; unchanged sources are never re-embedded.
5. **Work off the request path.** Heavy work runs on the weekly scheduler; user requests are served from precomputed data and return instantly.
6. **Small models + tight context.** 3B-class models with capped context windows keep latency and compute low; retrieval is hybrid so prompts stay short.
7. **Optional hosted fallback.** If you ever want a hosted model, point `OPENAI_BASE_URL`/`OPENAI_API_KEY` at any OpenAI-compatible endpoint (e.g. a cheap inference provider) — the rest of the system is unchanged.

---

## Deploy from GitHub

```bash
git init && git add . && git commit -m "RegPulse Intelligence"
git branch -M main
git remote add origin https://github.com/<you>/regpulse.git
git push -u origin main
```
Anyone can then run `docker compose up --build`. For a hosted deploy, any container host (Fly.io, Render, a VPS, ECS) works — provide a managed Postgres via `DATABASE_URL` and set `SECRET_KEY`.

> **Push the folder, not a zip.** Git tracks files individually; commit the unzipped project contents (`git add .` from inside `regpulse/`) so diffs, history and GitHub Actions work. A committed `.zip` is one opaque blob and Actions can't run anything inside it. The included `.gitignore` already excludes the local `*.db` and the cron log.

---

## Running the scan on a schedule

A script never runs itself — something has to trigger it. RegPulse ships with two ready-made options. Pick **one**.

### Option A — GitHub Actions (recommended, $0, no machine of yours required)

`.github/workflows/weekly-scan.yml` runs `scripts/run_scan.py` every **Monday 06:00 UTC**, then commits the dated report into `scan-reports/`. It runs in template/offline mode, so there's nothing to pay for and no Ollama needed (GitHub's runners can't run Ollama anyway).

1. Push the repo to GitHub (see above).
2. In the repo: **Settings → Actions → General → Workflow permissions → Read and write permissions** (lets the workflow commit the report back).
3. That's it — it runs weekly. To run it now, go to the **Actions** tab → *Weekly RegPulse Scan* → **Run workflow**.

Change the cadence by editing the `cron:` line (GitHub cron is UTC).

### Option B — Local cron (use this if you want Ollama-enriched runs)

`scripts/regpulse-weekly.sh` runs the scan on your machine and pushes the report. Use this when you want the LLM enrichment (`USE_LLM=true` with Ollama running locally). Caveats: your machine must be **awake** at scan time, and pushing from cron needs **non-interactive git auth** (an SSH deploy key or a cached credential helper) or the push will hang.

```bash
crontab -e
# add (06:00 every Monday); use absolute paths:
0 6 * * 1 /full/path/to/regpulse/scripts/regpulse-weekly.sh >> /full/path/to/regpulse/scan-reports/cron.log 2>&1
```

### Running it once, by hand

```bash
python scripts/run_scan.py        # writes scan-reports/scan-YYYY-MM-DD.json + latest.json
```

> **Heads-up on the first run.** With a brand-new database there's no prior snapshot, so the first scan classifies everything as *updated* while it establishes the baseline. From the second run onward it diffs properly (new / updated / unchanged).

### Do I have to run the script weekly myself?

No — that's the whole point of Option A or B. The in-app **Live Scan** tab and the single-file `RegPulse.html` let you trigger a scan **on demand**, but the *unattended* weekly run only happens once you've wired up one of the schedulers above. Nothing fires on a timer until then.

---


## Extending coverage

- **Add regulations / controls:** edit `scripts/build_seed.py` and run `make seed`. Each regulation has an `applies_when` predicate (`markets`, `product_types`, `data_types`, `flags`) that the applicability engine evaluates.
- **Real crawling:** `app/services/scan.py::fetch()` does a lightweight HTTP fetch with an offline fallback. For production, swap in `trafilatura`/`readability` for clean text extraction and add per-source parsers.
- **Tool-using agents:** wrap the scan/applicability steps in LangGraph nodes to add retrieval-augmented reasoning, citations, or human-in-the-loop review.

---

## Project layout
```
regpulse/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, startup seed + scheduler, serves SPA
│   │   ├── config.py db.py models.py schemas.py auth.py
│   │   ├── routers/             # auth, regulations, core (applicability/roadmap/scan/persistence)
│   │   ├── services/            # llm, rag, applicability, roadmap, scan, scheduler, seed
│   │   └── data/                # regulations.json, controls.json (seed)
│   ├── tests/test_core.py
│   ├── requirements.txt  Dockerfile
├── frontend/                    # index.html + app.js (vanilla SPA)
├── scripts/                     # build_seed.py, run_scan.py, regpulse-weekly.sh, init.sql, pull_models.sh
├── .github/workflows/           # weekly-scan.yml (GitHub Actions scheduler)
├── scan-reports/                # dated scan reports written by the scheduler
├── docker-compose.yml  Makefile  .env.example  LICENSE
```

---

## Disclaimer

RegPulse provides regulatory and control intelligence for **planning purposes only** and is **not legal, regulatory, or audit advice**. Regulation summaries, deltas, and control mappings are model-assisted starting points and **must be validated against the official source** linked on each entry, and confirmed with your regulatory, quality, security and privacy advisors. Verify all source URLs periodically; regulators reorganize their sites.

MIT licensed.

# Device Dossier — Medical-Device Cyber Intelligence (RAG + agentic AI)

Review a **device white paper**, build a **device-specific RAG**, and run an **agentic extraction** that pulls a structured cyber dossier — a plain-language summary, **cyber risks**, **security features**, and **where the device is deployed**. Then build a **second RAG** for the same device from **published CVEs/advisories** (NVD, CISA KEV, CISA ICS-Medical, with an HHS HC3 pointer), and **ask grounded questions** against the paper, the CVEs, or both. Everything **re-runs on demand**.

Runs on a local **Ollama** model when available; otherwise a **deterministic engine** (TF-IDF retrieval + lexicon/extractive analysis) keeps the whole app working **offline with zero setup**.

## What you get

- **Per-device corpora (two RAGs):** `paper` (the white paper) and `cve` (published vulnerabilities + recalls). Ask against either or **both**.
- **AI chatbot at the top:** ask grounded questions about the device first thing; answers cite the source passages `[1] [2]`.
- **Agentic dossier extraction** — retrieves per-aspect context, then extracts:
  - **Security & privacy features** (built-in controls)
  - **Cyber risks**
  - **Data processed** (PHI/PII and other data types)
  - **Environment** (where/how it's deployed)
  - **Interfaces** (other devices/systems/networks it connects to)
- **CVEs, advisories & recalls** — NVD + CISA KEV + CISA ICS-Medical with **severity, status, and remediation/patch** per item; **FDA cybersecurity recalls** (openFDA) with **current recall status** (Ongoing / Completed / Terminated); plus a **vendor trust-center** pointer. Results become a searchable corpus.
- **Zero-setup fallback:** no Ollama, no internet for the paper workflow — it still summarizes, extracts, and answers.

## BOM & network exposure

The **BOM & exposure** tab adds:

- **SBOM / HBOM** — software and hardware component *candidates* extracted from the device documentation, **plus upload of the real SBOM** (CycloneDX JSON or SPDX JSON/tag-value) for an authoritative parsed component list (name, version, type, supplier, license).
- **FDA records & MDR** — public **510(k)** clearances and **MAUDE** adverse-event reports via openFDA, with software/cyber-related events flagged.
- **SOC 2** — surfaced as a vendor trust-center pointer (SOC 2 reports are confidential and not fetchable).
- **Network exposure** — optional **Shodan** search (your own API key; passive, authorized-use only) with port/org/country facets, and the **free keyless Shodan InternetDB** lookup for a specific IP (open ports, CPEs, known vulns).

> **What's real vs. not:** full SBOMs and SOC 2 reports are **not** in public FDA data — the tool extracts component mentions and lets you upload the genuine SBOM. 510(k) and MAUDE are public (openFDA). Shodan requires your own key and must only be used against assets you're authorized to assess. Example devices ship with **illustrative** BOM/exposure data (clearly labeled); the live server pulls real records.

## Run it

```bash
./run.sh            # http://localhost:8000  (creates a venv, installs deps)
./run.sh 9000       # custom port
```

Or manually:

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Or Docker:

```bash
docker build -t device-dossier .
docker run -p 8000:8000 device-dossier
```

Open the URL, then click **Load example devices** to populate one device from each of **Insulet, BD, Johnson & Johnson MedTech, Philips, Abbott, and Stryker** (Omnipod 5, BD Alaris, Monarch Platform, IntelliVue MX750, Gallant ICD, Mako SmartRobotics) — each ingested and pre-analyzed. Or **+ Add device** and ingest the included `sample/infusion_pump_whitepaper.txt` (or any PDF/.txt), click **Run analysis**, then try the **CVEs** and **Ask** tabs.

> The bundled example profiles are **illustrative summaries compiled from public information** for demonstration — they are not vendor documents. Verify any detail against each manufacturer's product-security/trust center and FDA submission. Live CVE lookups use the device's keywords against NVD/CISA.
>
> **Note:** *Load example devices* works even if you just open `static/index.html` directly without starting the server — it shows the pre-computed example dossiers as an offline demo. Ingesting your own papers, fetching live CVEs, and Q&A require the local server running (`./run.sh`).

## Optional: local LLM (Ollama)

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text     # better retrieval (optional)
ollama serve
```

The app auto-detects Ollama (the engine chip in the sidebar shows the active model). Override via env vars: `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_EMBED_MODEL`.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/status` | engine / model in use |
| GET/POST | `/api/devices` | list / create devices |
| GET/DELETE | `/api/devices/{id}` | fetch full record / delete |
| POST | `/api/devices/{id}/paper` | ingest white paper (PDF or text) → builds paper RAG |
| POST | `/api/devices/{id}/analyze` | agentic dossier extraction (re-run on demand) |
| POST | `/api/devices/{id}/cves` | fetch CVEs/advisories → builds CVE RAG |
| POST | `/api/devices/{id}/ask` | grounded Q&A (`corpus`: `paper` \| `cve` \| `both`) |

## Layout

```
app.py        FastAPI: storage, endpoints, static serving
rag.py        chunking + TF-IDF/embeddings retrieval index
agent.py      agentic extraction + grounded Q&A (Ollama or deterministic)
sources.py    NVD / CISA KEV / CISA ICS-Medical fetchers (+ HHS note)
static/       single-file frontend (device dossier UI)
sample/       example infusion-pump white paper
```

## Notes & limits

- Live CVE feeds need internet. NVD is rate-limited; for heavy use add an `NVD_API_KEY` (extendable in `sources.py`).
- The deterministic extractor is lexicon-based and intentionally conservative — it surfaces candidate sentences for analyst review, not a finished assessment. Enable Ollama for narrative synthesis.
- Indicative product-security aid, not a substitute for a formal security assessment, threat model, or penetration test.

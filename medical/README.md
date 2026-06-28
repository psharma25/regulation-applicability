# MedReg Intel

**Medical device regulatory & cybersecurity intelligence** — regulations, submission pathways, the specific requirements behind each submission, FDA cybersecurity incidents, RTA & enforcement examples, and AI obligations, with **downloadable submission templates** and a **live openFDA tracker** that shows you the delta since your last run.

Soft pastel interface on a white background. Open-source, GitHub-pushable, and runnable three ways.

---

## Three ways to run

1. **Standalone (no install).** Double-click the root **`index.html`**. Everything — all reference data and the template downloads — works offline. The live tracker calls the FDA's openFDA API directly from your browser (CORS-enabled), so it also works from a plain file or GitHub Pages.
2. **Full app (agentic).** `./start.sh` (or `docker compose up`) serves the UI + API at `http://localhost:8000`, runs the tracker server-side with **deltas persisted to disk**, and answers questions with an **open-source agentic backend** (Ollama + retrieval fallback).
3. **GitHub Pages.** Push the repo; the included workflow publishes `docs/` (same app, served statically).

```bash
# standalone
open index.html

# full app
./start.sh                 # http://localhost:8000
OLLAMA_MODEL=llama3.1 ./start.sh   # enable the local LLM for Q&A

# rebuild data + standalone after editing the corpus
./run.sh
```

## What's inside

| Tab | Contents |
|-----|----------|
| **Regulations** | 34 national & international frameworks — US (FD&C Act, §524B, 21 CFR 807/814/820/803/806, premarket & postmarket cyber guidance, PCCP, GMLP), EU (MDR, IVDR, MDCG 2019-16, CRA, AI Act, NIS2, GDPR), IMDRF, ISO/IEC/AAMI/UL standards, and UK/Canada/Australia/Japan/China. Filter by region; cyber/AI tags. |
| **Submissions** | 510(k) Traditional/Special/Abbreviated, PMA + supplements, De Novo, HDE, Pre-Sub (Q-Sub), 513(g), IDE, EU CE — with form, review clock, and key requirements. |
| **Requirements** | The specific artifacts each submission needs, mapped to citations — cyber (SRM, threat model, SBOM, architecture views, 8 control categories, testing, CVD, labeling), AI (PCCP, GMLP, transparency, bias, monitoring), plus QMS/SW/clinical. |
| **FDA cyber incidents** | Named device cybersecurity incidents/recalls reported to FDA — Baxter Welch Allyn Life2000 (Class I), Contec CMS8000, Illumina UCS, BD Alaris, Medtronic MiniMed/Conexus, St. Jude/Abbott, GE MDhex, Philips, Swisslog PwnedPiper. |
| **RTA & fines** | What triggers a Refuse-to-Accept or enforcement — missing §524B content, legacy-change cyber gaps, 510(k) admin completeness, False Claims Act exposure, 806 recalls, AI changes outside a PCCP. |
| **AI requirements** | PCCP, GMLP (10 principles), transparency, bias/generalizability, data management, real-world monitoring, EU AI Act overlay, adversarial-ML security. |
| **Templates** | Downloadable Markdown/JSON starting points: Cybersecurity Management Plan, Security Risk Assessment, Threat Model, CycloneDX SBOM, CVD Policy, Postmarket Cyber Plan, Premarket Cyber Checklist, PCCP, GMLP Checklist, 510(k) Cyber Section, Pre-Sub Request. |

## Live tracker (openFDA)

Click **Run tracker**. It pulls from `api.fda.gov`:
- **Device cybersecurity recalls** (`reason_for_recall:cybersecurity`), newest first
- **Cybersecurity MAUDE reports** count (`mdr_text.text:cybersecurity`)
- **510(k) clearances** in 2025–2026

It stores a snapshot (browser `localStorage` standalone, or `backend/data/tracker_snapshot.json` in the full app) and marks **NEW** recalls and a **delta count** since your last run. No API key needed.

## RAG & agentic AI (built in, extensible)

Two layers ship today and are designed to grow:

1. **Client-side RAG (in the one-file `index.html`).** The **Ask** button runs retrieval over the entire embedded knowledge base (regulations, submissions, requirements, incidents, RTA, AI, templates), ranks by term/title relevance, and links each hit to its tab. No server, no key — works offline from the single file.
2. **Agentic LLM (full app).** `POST /api/agent {"question": "..."}` retrieves the most relevant corpus entries and, if a local **Ollama** model is reachable, composes a grounded answer that cites each source (`backend/agent.py`). With Ollama offline it returns the ranked entries — never fabricated.

**To extend down the road:** swap the keyword retriever in `agent.py` for embeddings (e.g., `sentence-transformers` + FAISS/Chroma) for semantic RAG; add tool-calling/agent loops (LangGraph, llama-index, or the Anthropic API) over the same corpus; or point `OLLAMA_URL`/`OLLAMA_MODEL` at any local model. The corpus is plain JSON in `backend/data/*.json`, so it's a clean RAG index to build on.

## One self-contained file

The root **`index.html`** is fully self-contained — CSS, JS, the entire knowledge base, **and the example PDFs (embedded as data URIs)** are all inlined. Copy that one file anywhere and everything works, including "View example PDF." The `docs/` build (for GitHub Pages) keeps the PDFs in `docs/examples/`.

## Profiles (technology lens)

Filter the whole app by jurisdiction (US / International) and technology profile: AI, SaMD, SiMD, Software, Hardware, Firmware, Connected, Cloud, AWS, Azure, GCP, and **Mobile-iOS / Mobile-Android** (mobile medical apps are tagged across the SaMD items, with FDA's mobile medical applications policy in the register).

## Edit the corpus

All content lives in `backend/data/build_data.py`. Edit it, then `./run.sh` to regenerate `backend/data/*.json`, `docs/data.js`, and the standalone `index.html`.

## Disclaimer

Curated from FDA guidance (§524B; the June 27 2025 final premarket cybersecurity guidance; PCCP final guidance), EU MDR/IVDR & MDCG 2019-16, IMDRF, and named device incidents. **Every item links to its source — verify before any regulatory use.** Templates are starting points, not legal advice. Live data is the FDA's; counts are point-in-time.


## Gold-standard PDF examples (`docs/examples/`)

Four polished, professional PDF exemplars of "what good looks like," grounded in the **public record of real cleared devices** and clearly labeled as illustrative reconstructions of FDA-expected structure (FDA does not release the confidential cybersecurity content of cleared submissions):

- **Premarket Cybersecurity Package** & **Security Risk Assessment (SW96)** & **510(k) Cybersecurity Section** — grounded in the **BD Alaris™ Infusion System** (510(k) cleared July 2023; enhanced cybersecurity + EMR interoperability; remediated the 2020 Class I recall).
- **PCCP + GMLP (AI)** — grounded in **IDx-DR / LumineticsCore** (FDA De Novo **DEN180001**, 2018, first autonomous AI; pivotal trial 900 patients/10 sites, 87.2% sensitivity / 90.7% specificity vs the Wisconsin reading center).

They are linked from the **Templates** tab and regenerated with `python3 scripts/make_examples.py`. The in-editor "Worked example" toggle shows a fictional-device version to illustrate structure; the PDFs are the real-device-grounded versions.

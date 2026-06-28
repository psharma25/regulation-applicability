# PostureLedger

Portfolio security-maturity ratings for investors. A single-file, no-install web app that lets a VC add every company in a portfolio and assess each one against **foundational**, **intermediate**, and **advanced** security controls — then auto-computes a maturity rating (F / I / A / Below bar) per company and rolls it up across the portfolio.

## Why these tiers

The criteria are the **CIS Controls v8.1 Implementation Groups** — the same model diligence teams already use — mapped to **NIST CSF 2.0** functions:

| Tier | CIS Group | Meaning |
|------|-----------|---------|
| **Foundational** | IG1 | Essential cyber hygiene every company should clear |
| **Intermediate** | IG2 | A resourced, operating security program |
| **Advanced** | IG3 | Mature, adversary-ready, independently assured |

Ratings are **cumulative and gated**: a company must clear the foundational bar to be eligible for intermediate, and intermediate before advanced. Each control is scored **Met / Partial / No**, and a tier is awarded when its score clears a threshold (85% / 80% / 75%).

## Features

- Add / edit / **remove** portfolio companies (sector, stage, headcount, contact, notes)
- 33 CIS-aligned controls across the three tiers — **tap any control** to see "what good looks like" and the **evidence to request** in diligence
- Auto-computed per-company rating with a maturity **ladder** and portfolio distribution
- **Applicable regulation & frameworks** auto-scoped by sector (digital health → HIPAA, FDA 524B, EU MDR; fintech → PCI DSS, GLBA, SOC 2; AI → EU AI Act, NIST AI RMF, ISO 42001; etc.)
- **Stage-based maturity expectations** — benchmarks each company against what's expected at its funding stage (Seed → foundational, Series B → intermediate, Growth → advanced) and flags meets / below / exceeds
- **Gap analysis** — exactly which controls block the next tier, quick wins first
- **Agentic advisor**: deterministic by default (offline); optional local **Ollama** for narrative analysis
- **Downloadable slide decks** — a beautiful self-contained per-company diligence deck and a portfolio-wide deck, plus **PowerPoint (.pptx)** export
- Portfolio rollup, search, filter by rating, sort; JSON import/export
- All data persists in the browser (localStorage)

## Slide decks

From a company's detail panel, **Download slide deck** produces a self-contained `.html` deck (cover, executive summary, maturity profile, applicable regulation, priority actions, per-tier scorecards, methodology). Open it and use **Save PDF** to share — no software required. **PowerPoint (.pptx)** export is also available (first build fetches the generator over the internet). **Portfolio deck** (top bar) builds a board-ready overview across all companies.

## Run it

Just open `index.html` in a browser — that's it.

Or serve locally:

```bash
./run.sh           # http://localhost:8000
./run.sh 9000      # custom port
```

Or with Docker:

```bash
docker build -t postureledger .
docker run -p 8080:80 postureledger   # http://localhost:8080
```

## Optional: AI advisor (Ollama)

1. Install [Ollama](https://ollama.com) and pull a model: `ollama pull llama3.1:8b`
2. `ollama serve`
3. In the app: **Advisor settings → Local Ollama**, set endpoint/model, save.

Without Ollama, the deterministic gap engine still produces a full prioritized analysis.

---

*Criteria mapped to CIS Controls v8.1 IG1/IG2/IG3 and NIST CSF 2.0. For diligence and portfolio oversight; not a substitute for a formal audit.*

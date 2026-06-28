# ATLAS Watch — AI Threat Intelligence (standalone)

A **single-file, zero-dependency web app** that collects, scores, and explains
real-world security threats against AI systems. Everything runs in the browser:
open `index.html` and it works — no server, no build step, no install.

> Threat data: **MITRE ATLAS** (techniques, real-world case studies, mitigations)
> + the **OWASP GenAI Top 10 for LLM Applications (2025)**.

## Run it

- **Locally:** double-click `index.html` (or `python -m http.server` then open it).
- **GitHub Pages:** push this repo, then *Settings → Pages → Deploy from a branch →
  `main` / `root`*. Your app is live at `https://<user>.github.io/<repo>/`.

That's it. The whole app — data, severity scoring, RAG retrieval, the analyst,
and a YAML parser — is embedded in `index.html`.

## What's inside

- **Severity scoring** (0–100, Critical/High/Medium/Low) weighted toward *how
  real* a threat is: ATLAS maturity (`Realized` → in the wild, `Demonstrated` →
  red-team/research, `Feasible` → academic), real-world incident links, the
  tactics it enables, and blast radius. Every score is explained.
- **Threat Analyst** — ask a question; it retrieves the most relevant grounded
  threats (in-browser TF-IDF RAG), aggregates severity, writes a cited brief,
  and recommends linked ATLAS mitigations. Fully deterministic and offline.
- **Reality Meter** — a Feasible → Demonstrated → Realized gauge on every threat,
  so "is this an actual real-world threat?" reads at a glance.
- **Filters & search** by source, type, severity, maturity, platform, and a
  real-world-only toggle; a detail drawer with sources, tactics, mitigations,
  and linked case studies.

## Collecting fresh data from MITRE

The app ships with an embedded snapshot so it works offline. Click
**↻ Refresh from MITRE** (top-right) to pull the latest ATLAS release live from
the official `mitre-atlas/atlas-data` repository, parse it in the browser, and
rebuild the index. If you're offline or the network blocks it, the app keeps
using the embedded snapshot.

To bake a newer snapshot into the file permanently, regenerate `index.html` from
the source generator in the full project (the FastAPI version), or just rely on
the live refresh button.

## Notes

- No telemetry, no external runtime dependencies, no cookies/localStorage.
- This is a defensive threat-intelligence and education tool. It catalogs and
  explains *published* threats; it contains no attack tooling.

## Attribution

- **MITRE ATLAS™** — © The MITRE Corporation, distributed for public release.
- **OWASP Top 10 for LLM Applications (2025)** — OWASP GenAI Security Project
  (CC BY-SA 4.0). Risk labels referenced descriptively; summaries independently authored.
- Bundled YAML parser: [js-yaml](https://github.com/nodeca/js-yaml) (MIT).

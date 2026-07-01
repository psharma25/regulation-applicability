# BitSense Security Policy Studio

A single-file, offline GRC documentation studio: 132 pre-written policies, standards,
procedures, work instructions and RACI matrices across five pillars (Enterprise, IT,
Product, M&A and PQC Readiness), with search, a glossary, a framework-coverage heatmap,
and a weekly compliance agent.

## Files
```
policies.html                          the studio (open or serve this)
regulations.json                       framework register the studio reads at runtime
agent/refresh_regulations.py           the compliance agent (updates the register)
.github/workflows/compliance-agent.yml GitHub Action (weekly + on demand + on push)
README.md                              this file
```

## Use it now (no setup)
Open `policies.html` in a browser, or serve it. Everything works offline: browse by
pillar, switch Cards / Compact / Table views, search, open the glossary and the coverage
heatmap. Sections start collapsed and the library opens in Compact view.

> Opening via `file://` (double-click) always uses the register embedded in the HTML,
> because browsers block local `fetch()`. The live `regulations.json` is only read when
> the page is served over http(s) (e.g. GitHub Pages).

## Deploy on GitHub (agent runs by default)
1. Create a repo and add all files at the **repo root**, keeping the folder layout above.
2. **Settings -> Actions -> General -> Workflow permissions -> Read and write**, then Save.
   (Required so the agent can commit an updated `regulations.json`.)
3. Push to `main`. The workflow runs **automatically on that first push**, then **every
   Monday**, and any time you click **Run workflow** on the **Actions** tab.
4. (Optional) **Settings -> Pages -> Deploy from branch -> main / root** to serve
   `policies.html`. Once served over https, the page loads the agent-maintained
   `regulations.json` and the in-page **Run compliance agent** button re-scans every
   document and flags any whose cited frameworks changed.

## What the agent does
`agent/refresh_regulations.py` maintains `regulations.json` from a canonical list
(`CANON`). Any entry with an `updated` date after the studio baseline (2026-01-31)
flags every document that references that framework. Extend `CANON`, or wire it to
authoritative sources (fda.gov, csrc.nist.gov, eur-lex.europa.eu, hhs.gov).

## Note
Every document is a template. Validate and have an accountable owner approve before
adoption. The coverage-heatmap scoring is an assessment, not an attestation.

(c) 2026 BitSense. All rights reserved.

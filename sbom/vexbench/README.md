# VEX Bench

An agentic, RAG-grounded workbench that turns an SBOM or scanner export into a machine-readable
VEX you can attach to an **FDA premarket cybersecurity (section 524B)** package. It enriches each
finding with live exploitability intel, reasons about patient-safety impact against a bundled
knowledge corpus, computes residual risk deterministically, and drafts a remediation rationale —
then exports CycloneDX VEX, CSAF, Excel, or CSV. Every field stays editable.

Runs as a **single standalone program**. Zero config, works fully offline, gets smarter when a
local Ollama is present. Push this repo as-is.

```
git clone <your-repo> && cd vexbench
./run.sh                 # macOS/Linux  (run.bat on Windows)
# open http://localhost:8000
```

No Python venv fuss? `docker compose up` instead.

---

## What makes it "agentic"

For each vulnerability the agent runs a bounded ReAct loop — it decides which tools to call,
gathers evidence, then commits to an assessment:

```
observe finding → call a tool → read observation → repeat → final assessment
```

Tools the agent can use:

| Tool | What it does |
|------|--------------|
| `kev(cve)` | live CISA Known-Exploited check (cached offline) |
| `epss(cve)` | live FIRST EPSS exploitation probability (cached offline) |
| `retrieve(query)` | **RAG** over the bundled FDA 524B / VEX / CVSS-EPSS-KEV / ISO 14971 corpus |

The model fills the qualitative fields (patient-safety impact, business impact, VEX status,
disposition, rationale). **The risk math is never delegated to the model** — after the agent runs,
`risk.compute()` produces severity / inherent / residual deterministically from a transparent 5×5
matrix. That keeps the scoring defensible for a regulatory submission.

If Ollama isn't installed, the same tools run in a fixed pipeline — still threat-intel-enriched,
still RAG-grounded — so output is identical in shape and the program is fully functional with no
network and no model. Use `ⓘ Trace` in the UI (or the `trace` field in `/api/enrich`) to see exactly
which tools fired and why.

---

## Architecture

```
index.html        single-page frontend (parsers, editable grid, exporters) — served by the backend
app.py            FastAPI server + REST API
agent.py          agentic ReAct loop + deterministic fallback
rag.py            dependency-free BM25 retriever over ./knowledge
risk.py           deterministic risk engine (unit-tested)
intel.py          CISA KEV + FIRST EPSS tools (live + offline cache)
llm.py            Ollama client (optional)
knowledge/*.md    RAG corpus (FDA 524B, VEX, CVSS/EPSS/KEV, ISO 14971)
data/*.json       offline KEV/EPSS seed caches
```

The frontend also runs **client-only** if you just open `index.html` without the server — you keep
parsing, editing, deterministic scoring, and export, but lose the agent/RAG endpoints.

---

## In

Drag in any of: CycloneDX (JSON/XML), SPDX, SARIF (any SAST/DAST), Wiz export, Tenable/Nessus
(`.nessus`/CSV), CSAF, Excel, CSV. Unknown formats route through a generic column mapper. Multiple
files merge into one register. A `sample_sbom.cdx.json` is included to try immediately.

## Engine

- **Likelihood** ← EPSS + CISA KEV + exploit maturity + attack vector + reachability (VEX in-path).
- **Impact** ← max(patient-safety, business). Bands are ISO 14971 / AAMI TIR57 flavored.
- **Inherent** ← 5×5 matrix. **Residual** ← inherent − control effectiveness; VEX *Fixed*/*Not
  affected* → 0.

`python test_risk.py` (or `pytest`) covers the edge cases — including the log4j "present but not in
execute path" case that should collapse to Informational despite a CVSS of 10.

## FDA

`⌖ Auto-tag` applies 524B / NTIA tags. `⚑ Submission gaps` flags missing minimum elements before
packaging. FDA-expected columns carry an `FDA` badge.

## Out (you pick the format)

CycloneDX VEX · CycloneDX SBOM+VDR · CSAF 2.0 VEX · Excel · CSV · native JSON (round-trips back in).

---

## Configuration

Environment variables (all optional):

| Var | Default | Purpose |
|-----|---------|---------|
| `PORT` | `8000` | server port |
| `OLLAMA_URL` | `http://localhost:11434` | local LLM endpoint |
| `OLLAMA_MODEL` | `llama3.1:8b` | model the agent reasons with |
| `VEXBENCH_OFFLINE` | `0` | set `1` to force offline (no live KEV/EPSS) |

Enable the agent's reasoning:

```
# install Ollama from https://ollama.com
ollama pull llama3.1:8b
./run.sh        # the UI auto-detects Ollama and switches to Agent mode
```

Refresh the offline threat-intel caches with the live catalogs:

```
python intel.py --refresh
```

---

## API

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | backend status, Ollama detection, RAG corpus stats |
| `POST /api/enrich` | `{rows, only_empty, mode}` → enriched rows + agent trace |
| `POST /api/recompute` | `{rows}` → rows with fresh risk scores |
| `POST /api/retrieve` | `{query, k}` → RAG passages |
| `GET /api/intel/{cve}` | KEV + EPSS for one CVE |

`mode` is `auto` (agent if Ollama present, else deterministic), `agent`, or `deterministic`.

---

## A note on scanners

Named adapters: Wiz, Tenable/Nessus, SARIF, CycloneDX, SPDX, CSAF. There is no scanner called
"Mythos" — that was a carryover from an earlier session. Any other tool routes through the generic
mapper; share one real export row and it gets a named adapter.

## Disclaimer

VEX Bench drafts and organizes a submission; it does not replace regulatory or clinical judgment.
Review every disposition and rationale before it goes into a filing.

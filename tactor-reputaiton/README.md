# Threat Actor Reputation Tracker

An agentic, self-hostable tool that scores ransomware / extortion actors on two
axes and exports a defensible scoring workbook — refreshed on demand from public
threat-intel sources. Built to run **as-is** with no API keys: it uses local,
open-source LLMs via [Ollama](https://ollama.com) when available, and falls back
to a deterministic heuristic engine when they aren't.

```
┌──────────────┐   plan/act/reason/score   ┌───────────────────────────┐
│  Web UI      │ ───────────────────────▶  │  Agent orchestrator        │
│ (Run scan)   │                           │  ├─ Collectors (tools)     │
│  dossier     │ ◀─── live status/log ───  │  │   ransomware.live        │
│  board       │                           │  │   CISA advisories (RSS)  │
└──────┬───────┘                           │  │   threat-intel RSS       │
       │  download .xlsx                   │  ├─ LLM layer               │
       ▼                                   │  │   Ollama → heuristic      │
┌──────────────┐                           │  └─ Scoring rubric          │
│ Scorecard    │ ◀──── openpyxl ──────────  │     2 weighted composites   │
│ workbook     │                           └───────────────────────────┘
└──────────────┘
```

## What a scan does

Every scan does two things:

1. **Refreshes the pre-loaded roster.** The tracker ships with ~19 known actors
   in [`config/actors.yaml`](config/actors.yaml) (Qilin, Akira, LockBit, Cl0p,
   Play, DragonForce, Lazarus, INC, Medusa, Black Basta, Rhysida, and others,
   including defunct cautionary cases like ALPHV/BlackCat and RansomHub). Each is
   re-scored against fresh evidence.
2. **Discovers new actors.** It enumerates groups currently active on public
   sources, dedupes them against the seeded names *and aliases* (case- and
   punctuation-insensitive), filters junk/placeholder labels, and adds any
   genuinely new group with conservative defaults — flagged **`discovered`** /
   **NEW** in the board and the workbook's `Source` column. New groups default to
   low Deal Reliability, reflecting that transient operators have little incentive
   to honor payment until they build a track record.

Promote a discovered actor to a permanent, curated entry by copying it into
`config/actors.yaml` with researched priors, aliases, origin, and notes.

## Two scores per actor

- **Threat Severity (1–10)** — how dangerous, active, and capable the actor is.
  Higher is worse for you.
- **Deal Reliability (1–10)** — *if* you were ever forced to pay, how likely the
  actor honors the deal (working decryptor, no re-extortion). Higher means a more
  "reliable" criminal. **This is a planning input, not an endorsement.**

Criteria and weights live in [`config/actors.yaml`](config/actors.yaml) and are
fully editable — add criteria, change weights, or add actors without touching code.

## Quick start

### Option A — static showcase (no install)

The repo root ships a standalone [`index.html`](index.html): the full board with
the preloaded roster and real computed scores, baked in so it runs anywhere with
no backend. Open it locally, or enable **GitHub Pages** (Settings → Pages → deploy
from the repo root) to publish it. It's a snapshot for viewing/sharing; the live
scan, discovery, and Excel export need the Python app below.

### Option B — full app (live scans + workbook)

```bash
git clone <your-repo-url> threat-actor-reputation-tracker
cd threat-actor-reputation-tracker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the web app
uvicorn app.main:app --reload
# open http://localhost:8000  →  click "Run scan"
```

No model? It just works — the heuristic backend runs automatically.

### With a local LLM (recommended, fully open-source)

```bash
# install Ollama, then:
ollama pull llama3.1:8b      # or mistral, qwen2.5, etc.
export OLLAMA_MODEL=llama3.1:8b
uvicorn app.main:app
```

### Headless / scheduled refresh

```bash
python -m app.cli            # writes a timestamped .xlsx to ./data
python -m app.cli --no-llm   # force heuristic backend
# cron example (weekly):
# 0 6 * * 1 cd /path/to/repo && .venv/bin/python -m app.cli
```

### Docker

```bash
docker build -t reputation-tracker .
docker run -p 8000:8000 reputation-tracker
# To use a host Ollama:  -e OLLAMA_HOST=http://host.docker.internal:11434
```

## Configuration (env vars)

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.1:8b` | Local model name |
| `DISABLE_LLM` | `0` | Set `1` to force heuristic backend |
| `RANSOMWARELIVE_BASE` | `https://api.ransomware.live/v2` | Victim/group data |
| `CISA_FEED` | CISA advisories XML | Advisory mentions |
| `EXTRA_RSS` | BleepingComputer, CP Research | Comma-separated extra feeds |

## How the agent works

For each actor the orchestrator runs a **plan → act → reason → score → reflect**
loop (`app/agent/orchestrator.py`):

1. **Plan** which collectors (tools) to run.
2. **Act**: collectors gather public evidence concurrently.
3. **Reason**: for every rubric criterion, the LLM (or heuristic) derives a 1–10
   value + short rationale, anchored on the analyst prior and adjusted by evidence.
4. **Score**: criteria fold into the two weighted composites (`app/scoring/rubric.py`).
5. **Reflect**: per-criterion confidence is recorded and surfaced in the UI/workbook.

Adding a source = drop a new collector in `app/collectors/` and register it in
`app/main.py`. Adding a criterion = one block in `config/actors.yaml`.

## Workbook output

`Scorecard` (color-graded composites + criteria, with rationale comments),
`Rubric` (criteria + weights), `Evidence` (sources gathered this scan),
`About` (methodology + data caveats).

## Scope, ethics & data limits

- **Sources are public and ToS-safe by design.** The tracker uses free public
  threat-intel sources (ransomware.live, CISA advisories, RSS). It deliberately
  does **not** scrape login-walled or ToS-restricted review/data sites.
- **This is a defensive tool** — for risk assessment, IR planning, and informing
  pay/no-pay deliberations. It contains no offensive capability.
- **Data honesty.** Ransoms actually *paid* and payer identities are mostly
  undisclosed; per-group decryptor success rates are tracked privately by
  negotiation firms. Reliability scores reflect reputation and incentive
  structure, not verified success rates. Across all groups, ~⅓ of victims who
  pay receive non-functional decryptors — payment never guarantees recovery.
- **Sanctions.** Paying a state-directed actor (e.g. DPRK/Lazarus) may itself
  violate OFAC sanctions. The `directed` nation-state class flags this.

Not legal, financial, or incident-response advice. Engage a professional
negotiation firm (e.g. Coveware, Kivu, Arete) and counsel for live incidents.

## License

MIT — see `LICENSE`.

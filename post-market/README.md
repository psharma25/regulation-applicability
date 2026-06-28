# Medical Device CVD Console

An open-source **coordinated vulnerability disclosure (CVD) pipeline** for medical
device manufacturers. One web interface drives a CVE from feed to published advisory
through explicit, auditable gates:

```
  Scan feeds (NVD/KEV) ─► Triage ─► Verify in env ─► Draft ─► Sign-off ─► Publish
       │ trigger          │ agent    │ analyst        │ agent   │ gates     │ artifacts
       ▼                  ▼          ▼                ▼         ▼           ▼
   new CVE          SBOM match   evidence +      advisory.md  legal /     advisory.md
   (or zero-day     + VEX        confirmed/      CSAF / VEX   business /  + CSAF/VEX
   manual inject)   status       mitigated       FDA draft    security /  + FDA report
                                                              regulatory  (draft)
```

Every agent is **Ollama-backed with a deterministic fallback** — the program runs and
produces valid, audit-ready output with no model at all. The LLM only adds narrative.

## Architecture

| Layer | What it does |
|---|---|
| `backend/agents/feed_agent.py` | Pulls NVD 2.0 + CISA KEV; manual zero-day injection. The trigger. |
| `backend/agents/triage_agent.py` | Deterministic SBOM/CPE applicability matcher (source of truth) + bounded agentic plan→act→observe loop for rationale and recommended VEX status. |
| `backend/agents/disclosure_agent.py` | Generates `advisory.md`, a **CSAF 2.0 / VEX** document, and a **FD&C 524B-aligned FDA report draft**. |
| `backend/workflow.py` | The disclosure state machine. Every transition is validated here. |
| `backend/db.py` | SQLite, no ORM — plain SQL, fully auditable. Devices, advisories, sign-offs, audit log. |
| `backend/app.py` | FastAPI routes; one endpoint per workflow step. |
| `frontend/index.html` | Single-file vanilla-JS PSIRT console. No build step. |

### Workflow states

`INGESTED → TRIAGED → VERIFYING → VERIFIED → DRAFTING → DRAFT_READY → IN_REVIEW → APPROVED → PUBLISHED`,
with `CHANGES_REQUESTED` (any rejection, resets the review round) and `NOT_APPLICABLE`
(produces a `known_not_affected` VEX) off-ramps.

### Sign-off gates

Required roles are org-configurable (`security, legal, business, regulatory` by default
via `PUT /api/config/roles`). **All** required roles must approve before publish; any
rejection sends the advisory back and resets sign-offs for a fresh round. Full history
is retained in the audit log.

## Run it

**Zero-install (deterministic mode, no LLM):**
```bash
LLM_ENABLED=0 ./run.sh        # http://localhost:8000
```

**With local LLM (free, private):**
```bash
ollama pull llama3.1:8b
./run.sh
```

**Docker (app + Ollama):**
```bash
docker compose up --build
docker compose exec ollama ollama pull llama3.1:8b
```

## Configuration (env)

| Var | Default | Notes |
|---|---|---|
| `LLM_ENABLED` | `1` | `0` forces deterministic-only |
| `OLLAMA_HOST` | `http://localhost:11434` | |
| `OLLAMA_MODEL` | `llama3.1:8b` | |
| `NVD_API_KEY` | — | optional, higher NVD rate limits |
| `ORG_NAME` / `ORG_CONTACT` / `ORG_NAMESPACE` | sample org | stamped into advisories/CSAF |
| `CVD_DB_PATH` / `CVD_OUTPUT_DIR` | local | SQLite + published artifacts |

## Outputs

On publish, three files are written to `CVD_OUTPUT_DIR`:
`<CVE>_<ADV>.md` (human advisory), `<CVE>_<ADV>.csaf.json` (machine VEX for downstream
SBOM tooling), `<CVE>_<ADV>.fda-report.json` (regulatory draft).

## Security incidents & trust centers

The console has four tabs (light theme): **Disclosures**, **Incidents**, **Trust Centers**, **Metrics**.

### Disclosures (tab 1) — the step-by-step process

Tab 1 opens on a guided **step-by-step disclosure process** (`GET /api/process`) that the
enterprise follows for every vulnerability:

1. **Discover vulnerability** — ingest from NVD / CISA KEV / CISA ICS Medical Advisories (SLA 1d).
2. **Validate impact** — SBOM triage + environment confirmation; **human-in-the-loop Impacted? Yes/No** (SLA 3d).
3. **Create disclosure (CISA format)** — generate a **CSAF 2.0 / VEX** advisory, the format vendors submit to CISA (SLA 2d).
4. **Validate** — multi-stakeholder **human sign-off by security, legal, business, communication**; any rejection returns for changes (SLA 5d).
5. **Disclosure draft / publish** — write advisory.md + CSAF/VEX + FDA report draft (SLA 1d).

Selecting an advisory shows its lifecycle rail, a **per-step timeline** (elapsed vs SLA marker)
and total cycle time, the **cross-reference** panel, the active step's human gate, and the
generated artifacts.

### Cross-reference (CVE per CISA ↔ vendor trust center)

Each advisory and incident records the authoritative **CISA / NVD** link and, for third-party
medical-device CVEs, whether the **vendor disclosed it on their trust center** (Yes/No + link).
The prepopulated set includes the contrast pair: **Contec CMS8000** (CVE-2024-12248, 9.8 — CISA
ICSMA-25-030-01, vendor did **not** disclose; CISA/FDA advised removal) versus **Medtronic Paceart
Optima** (CVE-2023-31222, 9.8 — ICSMA-23-180-01, Medtronic **did** disclose on medtronic.com/security).

### Prepopulated from reliable sources

Disclosures are seeded with real example CVEs from CISA / NVD (Contec CMS8000, Medtronic Paceart,
Log4Shell, curl SOCKS5, OpenSSL "SpookySSL", BusyBox) across the pipeline with backdated timelines.
Incidents are seeded from public CISA/vendor advisories (Contec, Medtronic, BD, Philips, Siemens
Healthineers) with patch-deployment timing. Component CVEs that match the device SBOM are driven to
PUBLISHED; third-party medical-device CVEs that don't match are filed known_not_affected. Every entry
carries its source link.

### Metrics (tab 4)

`GET /api/metrics` returns: **CVEs disclosed** (published), **CVEs not impacting**
(known_not_affected), in-progress, **severity distribution**, **per-step timeline** (avg vs SLA and
SLA adherence), and average total cycle time against the 12-day SLA target.

### Trust Centers (tab 3)

`backend/trust_centers.py` — manufacturer product-security sites (`GET /api/trust-centers`),
verified against vendor pages and the Health-ISAC Medical Device Manufacturer directory
(https://health-isac.org/landing-page/mdm-security/), used to link components and check disclosure.

### Sectors: MedTech and IT/OT

Every disclosure, incident, and trust center is tagged by **sector** — **MedTech** or
**IT/OT** — and each tab (Disclosures, Incidents, Trust Centers) has an All / MedTech / IT/OT
toggle; Metrics shows a per-sector breakdown. Prepopulated IT/OT content uses real, sourced
examples: Schneider Electric PowerLogic (CVE-2024-10497, ICSA-25-028-02), Siemens IAM client
(CVE-2025-40800, SSA-868571), Rockwell Micro8xx (CVE-2025-13824), Mitsubishi MELSEC iQ-F
(CVE-2025-7731, mitigation-only — no vendor fix), Progress MOVEit (CVE-2023-34362, CISA KEV),
and Fortinet FortiOS (CVE-2024-21762, CISA KEV), plus OT/IT trust centers (Siemens ProductCERT,
Schneider, Rockwell, Mitsubishi, ABB, Cisco PSIRT, Fortinet PSIRT, Ivanti, Progress, CISA
ICSA/KEV). The org inventory adds two connected IT/OT assets (a lab automation controller and an
IoT gateway) so component CVEs (jQuery CVE-2020-11023, curl CVE-2022-32221) drive IT/OT
disclosures through the same pipeline.

### Per-step tabs, live position, and AI/RAG assist

The Disclosures tab carries a sub-tab per process step (Overview · Discover · Validate impact ·
Create disclosure · Validate · Publish). Each step tab shows a completion bar and three groups —
**currently in this step** (where the org is now, with elapsed-vs-SLA and overdue flags),
**completed this step**, and **not yet reached** — so you can see exactly where every advisory
sits and whether a step is done. When an advisory is open, its current step is marked on the
sub-nav. Metrics sits next to Disclosures in the top nav.

The triage and disclosure agents can run as **live LLMs**: the backend build uses **Ollama**
(local, free) with a deterministic fallback, and the single-file build has an **AI assist** toggle
that calls a live model in-browser. Both are **RAG-grounded** — they retrieve from the device SBOM
inventory and trust-center registry, show that retrieved context, and reason over it; if no model
is reachable, the deterministic agents stand.

## Scope & disclaimers

The FDA report is a **drafting aid**, clearly marked, not regulatory or legal advice.
Reporting obligations, timelines, and submission pathways under FD&C 524B and postmarket
cybersecurity guidance must be confirmed by qualified regulatory and legal counsel. The
console is the workflow and evidence layer; it does not file anything with FDA.

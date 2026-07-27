# CVD Console — Coordinated Vulnerability Disclosure

Production-organized distribution of the CVD workflow console. The repository
contains one canonical application—there is no nested ZIP and no build-time
framework dependency.

## Quick start

```bash
npm test
npm start
```

Open `http://127.0.0.1:8080`.

### First run

On **Select an advisory**, click one advisory and then click the green **Notify**
button. That creates the case and starts the coordinated disclosure process.
Choose **Paste or log a different advisory** to enter real CISA, NVD, vendor, or
researcher text instead. Review extracted fields before continuing.

Configure Slack, Teams, or email delivery from **Notifications → Notification
settings**. Notification settings control delivery; they do not import
vulnerability data. Use **Trust Center** to review published disclosures.

For a container deployment:

```bash
docker compose up --build
```

For GitHub Pages, upload this folder to a repository and enable
**Settings → Pages → GitHub Actions**.

## Production boundary

The static interface is production-packaged for reliable hosting, but it remains
a browser-local application. Use it for demos, training, tabletop exercises, or
non-sensitive individual work. Before processing embargoed vulnerabilities or
operating as a multi-user system of record, implement the authenticated service
boundary in [`docs/PRODUCTION.md`](docs/PRODUCTION.md). In particular, webhook
credentials and approval records must move to a server-side secrets and audit
service.

Single-file HTML application. No build step, no CDN, no server. Open `index.html`
in a browser, or drop it into any static host (GitHub Pages, Cloudflare Pages, S3).
All data is stored in the browser's localStorage under the key `cvd.console.v3`.

## What it does

Runs a vulnerability report through seven stages with three human approval gates:

| Stage | Gate | Who acts |
|---|---|---|
| 01 Intake | — | PSIRT logs the report; the awareness date starts the clock |
| 02 Impact analysis | — | SBOM match across the product portfolio; scope confirmed |
| 03 Risk validation | **Gate A** | Security + Product agree reachability, patient impact, mitigations, residual risk — then close or escalate |
| 04 Disclosure draft | **Gate B** | Privacy, Legal, Regulatory, Quality, Communications, CISO |
| 05 Communication plan | **Gate C** | CISO or designee + Regulatory authorise release |
| 06 Communicate | — | Each channel sent and timestamped |
| 07 Closed | — | Permanent record; Trust Center entry if published |

## Moving the case forward

The process runs left to right across the top as seven circular nodes. To the right of
it sits a **Next** button labelled with whatever the case actually needs next — run the
impact analysis, generate the draft, approve the gate — so a whole case can be run
without hunting for controls. Below the flow, the **What to do now** bar names the
outstanding step, lists the people the process is waiting on, and offers the specific
controls for it — including a
single-click **Approve all and continue** override recorded against whoever you are
acting as (the name badge in the top bar).

Action colors are intentional: **green** identifies the current process step, the
panel requiring attention, and the primary button that advances the case. **Red**
identifies a held gate, recorded objection, or open case beyond the 30-day disclosure
window. Completed steps retain their quieter completed treatment.

In Simulation the console fills in the mechanical parts of each stage as you reach it —
the assessment values, the draft, the recommended channels — so a full case is **one
Next click per stage, six in total**. It never invents a decision: at Gate A you either
accept the calculated recommendation in one step or pick the other route and record why.
**▶ Auto-run** does the same thing unattended, pausing if it reaches something only a
person should decide.

The report that opened the case — source, CVE, CWE, severity, awareness date,
exploitation status and the affected version range — stays pinned to the top of every
stage, in both playbooks, with an Edit intake link back to it.

## If something goes wrong

Every render is wrapped: if a screen cannot be drawn, the console says so plainly and
offers **Start over from a clean state** rather than failing silently. The same control
sits in the top bar. Starting over clears every case, notification and preference held
in this browser and restores the seeded portfolio — it touches nothing outside the
browser. Stored state carries a schema stamp, so anything written by an earlier build,
or anything corrupt, is discarded at boot instead of being loaded.

## Choosing what to send

Stage 06 is a queue, not a single button. Every authorised channel carries a tick box —
all ticked by default — so you can send the Trust Center advisory and the customer
notice today and hold the CVE record until the coordinator confirms. **Send N selected**
acts only on what is ticked; the rest stay queued.

A channel you are not going to use at all gets **Defer**, which asks for a reason and
takes it out of the plan. The case cannot be published until every authorised channel
has been either sent or deferred, and the deferred ones appear in the closing record
with their reason and timestamp — the first thing an auditor asks about is a channel
that was approved and never used.

## Panels

Every panel under the process collapses. Only the panel the process is waiting on is
open by default; the rest stay shut until you want them. Each panel header carries a
pop-out control that opens it full screen with its own zoom. `Expand all`,
`Collapse all`, and `Show only what needs me` sit at the top of each stage.

The product portfolio works the same way: products start collapsed and open one at a
time to reveal the version in service and the full component list, with matched
components highlighted.

## Notifications

Slack, Teams, and email. When a gate opens, a message is drafted for every person who
still has to sign, with the finding, the severity, the residual risk, the products in
scope, and where the case sits against the 30-day clock. Configure incoming webhooks
under Notifications → settings. Slack accepts a direct post from the browser; Teams
and mail servers generally do not, so those messages stay in the outbox with a copy
button and a pre-addressed mail link. Nothing is ever sent silently — every message is
kept with its status.

## Two playbooks

- **Simulation** — one Next button walks the whole process. Signatures are applied
  automatically with sample approvers and the clock advances by a realistic amount
  per stage. For demos, training, and tabletop exercises.
- **Live** — every named approver signs their own gate by typing their name.
  Objections hold the gate until withdrawn and re-taken.

Switch in the top bar. The mode is recorded on each case.

## Risk model

Scoring is arithmetic and reproducible. Nothing in the scoring path is model-derived.

```
inherent = CVSS × (0.55 + 0.45·reachability) × (0.60 + 0.40·attack path) × patient-safety factor
residual = inherent × (1 − combined mitigation effect)     effect capped at 85%
residual is floored at 5.0 where exploitation is confirmed in the wild (KEV)
```

Generated text is confined to advisory wording and is always editable before anyone
signs it.

## Your organisation and products

**Set up your company and products** on the start screen, or **+ Import** in the
portfolio panel. Set the company name — it flows into advisory headers, the Trust
Center title, notification text and the contact address — and paste your product list,
one per line:

```
AuroraFlow 3000 Infusion Pump | 4.2.1 | openssl 3.0.8, zlib 1.2.13
CardioLink Gateway CG-200 | 3.8.2 | openssl 3.0.8, libxml2 2.9.14
VitalView VM-9 Patient Monitor
```

Everything after the name is optional; a name on its own is enough to get started. You
can also upload a JSON array (`name`, `version`, `sbom` / `components`) or a CSV with
product and component columns, and either merge with or replace the seeded portfolio.

## The incoming trigger

The report that opened the case is shown as a pop-up the moment it arrives, and stays
available three ways: a collapsible **Incoming trigger** frame at the top of the left
panel, a **Read report** button on every stage, and — for Live cases — a notification
circulated to Product Security, the Product Owner and the CISO as soon as the case is
logged. The pop-up carries the identifier, severity, weakness, EPSS, exploitation
status, awareness date, and the affected version range with the products that carry it.

## Resetting

Two different things, both reversible only by doing them:

- **↺ Reset to 01** on any stage sends *that case* back to intake. The incoming report
  is kept; every assessment, decision, signature, draft, channel and send is cleared and
  the clock restarts. Use this to re-run a simulation on the same report.
- **↺ Start over** in the top bar clears *everything* in the browser — cases,
  notifications, imported products, company name, preferences — and restores the seeded
  portfolio, landing you back on the start screen at stage 01.

Both ask for confirmation through an in-app dialog rather than the browser's native
`confirm()`, which is silently blocked when the page runs inside a sandboxed frame and
would make the buttons appear dead.

## Configuration

- **Organisation name** — the database icon in the top bar. Used in advisory headers
  and the Trust Center title.
- **Products and SBOMs** — "+ Product" in the portfolio panel. The seeded portfolio
  is eight fictional medtech products.
- **People** — "+ Person" in the case file panel. The function assigned to a person
  decides which gate they sign.
- **Disclosure window** — 30 days by default (`FDA_WINDOW_DAYS` in the source).

## Keyboard

`⌘/Ctrl + K` new case · `[` collapse portfolio · `]` collapse case file ·
`⌘/Ctrl + ↑ ↓` zoom · `?` help · `Esc` close dialog

## Exports

Case record (JSON), advisory (text), and CSAF-style VEX (JSON) from the closing
screen. Full application export and import from the database icon.

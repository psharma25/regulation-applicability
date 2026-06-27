# BitSense Security Policy Studio

A **single-file, fully offline** security documentation library. Pick a security pillar and one or more industries, then browse a classified set of controlled documents — **Policies, Standards, Procedures, Work Instructions and RACI matrices** — every one of them **pre-written and rendered instantly**. Edit any document in place, stamp it with your Organization name and effective date, and run a **regulation rescan** to flag what needs review. No API key, no build step.

> **126 documents + 12 RACI matrices** across **4 pillars**, tagged to their management system — **ISMS** (ISO/IEC 27001) or **QMS** (ISO 13485 / FDA) — and aligned to recognized open frameworks.

## Run it

- **Locally:** open `index.html` in any browser.
- **GitHub Pages:** push this repo, enable Pages on the default branch (`/root`), and the site is live at `https://<user>.github.io/<repo>/`.

## What's new in this version

- **M&A Security pillar** — cyber due diligence, post-merger integration, carve-out / divestiture separation and TSA security. Full set: 6 policies, 4 standards, 4 procedures, 3 work instructions + 3 RACI matrices.
- **In-place editing** — click **Edit** on any document to edit its Markdown; **Save** keeps it for the session, **Revert** restores the original. Edited documents are badged in the library.
- **Organization & Effective-date placeholders** — set them in the top bar; they flow into every document header. Left blank, documents show `[Organization Name]` / `[Effective Date]` placeholders, ready to fill.
- **Rescan regulations** — the **↻ Rescan regulations** button (in the library toolbar) checks every document against a built-in regulatory register, refreshes review dates, and flags documents whose cited frameworks have changed since the baseline. It produces a report and an in-document "Regulatory watch" banner.

### How the rescan works (and how to keep it current)

The register is embedded in the app and **also shipped as `regulations.json`** in this repo. On rescan, the app loads `regulations.json` (when served over http/https) and merges it over the built-in register, so you maintain regulations in one editable file:

```json
{
  "baseline": "2026-01-31",
  "regulations": [
    { "id": "fda_qmsr", "name": "FDA QMSR (21 CFR 820)", "version": "...", "updated": "2026-02-02",
      "note": "…", "match": ["21 cfr 820", "qmsr"] }
  ]
}
```

Any framework whose `updated` date is later than `baseline` is treated as changed; every document whose text contains one of that framework's `match` keywords is flagged for review. Update the dates/notes (or add entries) and re-run the scan.

**The rescan is advisory.** It refreshes review metadata and surfaces what changed — it does **not** rewrite policy text. An accountable owner must review and update flagged documents, and you should always verify against official sources.

## What's inside

| Path | Contents |
|---|---|
| `index.html` | The complete studio app (self-contained) |
| `regulations.json` | The editable regulatory register used by Rescan |
| `policies/<pillar>/` | Every document as an individual Markdown file |
| `raci/` | All 12 RACI matrices as Markdown |
| `bundle/<pillar>-library.md` | One combined Markdown file per pillar |

### Pillars

- **Enterprise Security** — 36 docs + 3 RACI
- **IT Security** — 38 docs + 3 RACI
- **Product Security** — 35 docs + 3 RACI
- **M&A Security** — 17 docs + 3 RACI

## Important

Every document is a **template** — a framework-aligned starting point, not an approved policy. Tailor it to your environment and obligations, map RACI roles to real job titles, set Organization and Effective date, and route it through document control with an accountable owner before adoption.

## License

MIT (see `LICENSE`). Referenced standards remain the property of their respective bodies; this project paraphrases requirements and cites clauses without reproducing standard text.

---
Built for BitSense · thebitsense.com

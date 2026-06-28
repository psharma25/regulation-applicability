# The Ledger — Government Disclosure Tracker

An open-source, agentic tracker for U.S. government financial disclosures. It pulls
**congressional stock & option trades**, **corporate insider Form 4 filings**, and
**trending DHS / DoD contracts** from free public sources, then renders them in a
static dashboard you can deploy to GitHub Pages as-is.

```
the-ledger/
├── index.html              ← root dashboard (reads /data, deploys on GitHub Pages)
├── tracker.py              ← the agent: fetches public data → writes /data/*.json
├── data/                   ← committed JSON the dashboard reads (seed data included)
├── .github/workflows/      ← scheduled GitHub Action that refreshes /data daily
├── requirements.txt        ← (stdlib only — nothing to install for the core)
└── LICENSE                 ← MIT
```

## Quick start

```bash
git clone <your-fork-url> && cd the-ledger
python tracker.py          # fetches live data, writes data/*.json
# then open index.html in a browser (or push to GitHub Pages)
```

No dependencies for the core tracker — it uses only the Python standard library.

## Deploy to GitHub Pages

1. Push this repo to GitHub.
2. **Settings → Pages →** deploy from `main`, root (`/`).
3. The dashboard loads the committed `data/*.json` immediately.
4. Enable the included Action (**Actions** tab → enable workflows) so data refreshes
   daily and auto-commits. You can also trigger it manually with **Run workflow**.

The page ships with **seed sample data** so it renders before your first real run.
Seed rows are clearly labelled `⚠ SEED SAMPLE` in the UI.

## The "Run Tracker" button

A static page can't execute Python, so the button does a **live client-side fetch**
of the public congressional endpoints. Most of these enforce CORS and will block a
browser request — that's expected. When blocked, the page falls back to the committed
`data/` files. **The authoritative refresh path is `python tracker.py` or the GitHub
Action**, which run server-side and aren't subject to CORS.

## Data sources (all free, all public)

| Panel | Source | Notes |
|------|--------|-------|
| Congress | House & Senate Stock Watcher open JSON | STOCK Act PTRs; amounts are **ranges**, lag ≤45 days |
| Insiders | SEC EDGAR full-text search (Form 4) | Officers/directors/10%+ owners; 2-day filing window |
| Contracts | USASpending.gov award API | Top DHS & DoD awards by amount, trailing 6 months |
| President & Cabinet | U.S. Office of Government Ethics | See the honesty note below |

### About the President & Cabinet panel — read this

There is **no weekly buy/sell feed for the President or Cabinet secretaries.** Unlike
members of Congress, they do not file Periodic Transaction Reports. They file *annual*
OGE Form 278e disclosures (assets and income in broad ranges). The dashboard surfaces
links to those real filings rather than inventing a trade stream. Any product claiming
to show "the President's weekly stock picks" is inferring from delayed annual snapshots
or fabricating — treat it with skepticism.

## Configuration

Endpoints and the lookback window live in the `CONFIG` dict at the top of `tracker.py`
and in the `CONFIG` object in `index.html`. If a community dataset URL moves, repoint it
there. Set a contact `TRACKER_UA` env var (SEC asks API users to identify themselves).

## Optional: AI summaries

If you set an `ANTHROPIC_API_KEY` (locally as an env var, or as a GitHub repo secret),
`tracker.py` adds a short plain-English summary of each refresh to `manifest.json`. It's
strictly optional — everything else works without any key.

```bash
export ANTHROPIC_API_KEY=sk-...   # optional
python tracker.py
```

## Limitations & honesty

- **Lag:** congressional filings arrive up to 45 days after the trade. This is a
  *lagging* indicator, not a real-time signal.
- **Ranges, not amounts:** you never see exact trade size, only disclosed brackets
  (e.g. `$15K–$50K`).
- **No exits visible until filed:** you can't see when a position was closed until
  that sale is itself disclosed.
- **Not investment advice.** This is a transparency tool for research, not a
  copy-trading system. Nothing here is a recommendation to buy or sell anything.

## License

MIT — see `LICENSE`.

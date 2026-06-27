#!/usr/bin/env python3
"""Headless RegPulse scan — for the scheduler (GitHub Actions or local cron).

Runs the same pipeline as the in-app "Live Scan" / weekly scheduler, but with no
web server: seed (idempotent) -> embeddings -> run_scan -> write a dated report
into scan-reports/ so the scheduler can commit it back to the repo.

Runs at $0 in template/offline mode by default (USE_LLM=false). It does NOT need
Ollama; the GitHub-hosted runner can't run Ollama, and that's fine — turn the LLM
on only for local runs where Ollama is available.

Usage:
    python scripts/run_scan.py
Env:
    DATABASE_URL   default sqlite:///./regpulse.db  (use Postgres in prod)
    USE_LLM        default false                    (true needs local Ollama)
"""
import os
import sys
import json
import datetime as dt

# Make `app` importable when run from the repo root.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "backend"))

os.environ.setdefault("DATABASE_URL", "sqlite:///" + os.path.join(ROOT, "regpulse.db"))
os.environ.setdefault("USE_LLM", "false")
os.environ.setdefault("ENABLE_SCHEDULER", "false")  # we trigger the run ourselves

from app.db import init_db, SessionLocal              # noqa: E402
from app.services import seed as seed_svc, rag, scan  # noqa: E402


def main():
    init_db()
    db = SessionLocal()
    try:
        seed_svc.seed(db)          # idempotent
        rag.ensure_embeddings(db)  # embeds only what's missing
        run = scan.run_scan(db)    # crawl -> fingerprint -> diff -> score
        _run, items = scan.latest_delta(db)

        report = {
            "run_id": run.id,
            "ran_at": dt.datetime.utcnow().isoformat() + "Z",
            "new": run.new_count,
            "updated": run.updated_count,
            "unchanged": run.unchanged_count,
            "items": items,
        }

        out_dir = os.path.join(ROOT, "scan-reports")
        os.makedirs(out_dir, exist_ok=True)
        stamp = dt.datetime.utcnow().strftime("%Y-%m-%d")
        # dated report (history) + latest.json (stable pointer)
        with open(os.path.join(out_dir, f"scan-{stamp}.json"), "w") as f:
            json.dump(report, f, indent=2, default=str)
        with open(os.path.join(out_dir, "latest.json"), "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"Scan {run.id}: {run.new_count} new, {run.updated_count} updated, "
              f"{run.unchanged_count} unchanged -> scan-reports/scan-{stamp}.json")
    finally:
        db.close()


if __name__ == "__main__":
    main()

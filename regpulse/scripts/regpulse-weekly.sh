#!/usr/bin/env bash
# regpulse-weekly.sh — local cron alternative to the GitHub Actions scheduler.
#
# Use this instead of GitHub Actions when you want the LLM-enriched run on your
# own machine (Ollama available). The machine must be awake at scan time, and
# pushing from cron needs non-interactive git auth (an SSH deploy key or a
# cached credential helper) or the push will hang.
#
# Install (run `crontab -e` and add the line below for 06:00 every Monday):
#   0 6 * * 1 /full/path/to/regpulse/scripts/regpulse-weekly.sh >> /full/path/to/regpulse/scan-reports/cron.log 2>&1
set -euo pipefail

# Resolve the repo root from this script's location.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Activate a virtualenv if you use one (uncomment and adjust):
# source .venv/bin/activate

# Set to "true" if Ollama is running locally and you want enriched summaries.
export USE_LLM="${USE_LLM:-false}"
export ENABLE_SCHEDULER="false"

python scripts/run_scan.py

# Commit + push the report. Requires non-interactive git auth.
git add scan-reports/
if git diff --cached --quiet; then
  echo "$(date -u +%FT%TZ) No changes this cycle."
else
  git commit -m "chore: weekly scan $(date -u +%Y-%m-%d)"
  git push origin main
fi

#!/usr/bin/env bash
# One-click start for macOS / Linux. Double-click or run ./start.sh
set -e
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
[ -d .venv ] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt
: "${SEC_USER_AGENT:=SecIntel research client admin@example.com}"; export SEC_USER_AGENT
URL="http://localhost:8000"
( sleep 2; (command -v open >/dev/null && open "$URL") || (command -v xdg-open >/dev/null && xdg-open "$URL") || true ) &
echo "→ Opening $URL  (Ctrl+C to stop)"
cd backend
exec uvicorn main:app --host 0.0.0.0 --port 8000

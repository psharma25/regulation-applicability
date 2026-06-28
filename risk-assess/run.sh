#!/usr/bin/env bash
set -e
python -m venv .venv 2>/dev/null || true
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt
echo "Starting Risk Assessment AI on http://localhost:8000"
uvicorn backend.main:app --reload --port 8000

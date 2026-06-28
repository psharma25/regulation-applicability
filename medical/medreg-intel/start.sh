#!/usr/bin/env bash
# Full app: builds data, then serves API + UI at http://localhost:8000
set -e
cd "$(dirname "$0")"
python3 backend/data/build_data.py
pip install -r requirements.txt --quiet --break-system-packages 2>/dev/null || pip install -r requirements.txt --quiet
cd backend
exec uvicorn main:app --host 0.0.0.0 --port 8000

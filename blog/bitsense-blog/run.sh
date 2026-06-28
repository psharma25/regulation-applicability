#!/usr/bin/env bash
# One-click local run. Creates a venv, installs deps, starts the server.
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo ""
echo "  BitSense Blog → http://localhost:8000"
echo "  (write endpoints are OPEN on localhost; set ADMIN_TOKEN to lock them)"
echo ""
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

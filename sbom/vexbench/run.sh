#!/usr/bin/env bash
# One-click run. Creates a venv, installs deps, starts the server.
set -e
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
if [ ! -d .venv ]; then
  echo "Creating virtualenv ..."
  $PY -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo
echo "Starting VEX Bench on http://localhost:${PORT:-8000}"
echo "(Ollama optional: install from https://ollama.com then 'ollama pull llama3.1:8b')"
exec python app.py

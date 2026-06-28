#!/usr/bin/env bash
# Start SecIntel. Optional: have Ollama running for full agentic mode.
#   ollama serve & ; ollama pull llama3.1
set -e
cd "$(dirname "$0")/backend"
python3 -m pip install -r ../requirements.txt >/dev/null 2>&1 || true
export OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.1}"
echo "→ http://localhost:8000   (Ollama model: $OLLAMA_MODEL)"
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload

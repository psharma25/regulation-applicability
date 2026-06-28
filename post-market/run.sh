#!/usr/bin/env bash
# One-click run. No install beyond Python deps. Ollama optional (deterministic fallback).
set -e
cd "$(dirname "$0")"
PORT="${PORT:-8000}"
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q -r requirements.txt
echo ""
echo "  CVD Console -> http://localhost:${PORT}"
echo "  LLM: ${LLM_ENABLED:-1} (set LLM_ENABLED=0 to force deterministic mode)"
echo "  Ollama: ${OLLAMA_HOST:-http://localhost:11434} model ${OLLAMA_MODEL:-llama3.1:8b}"
echo ""
exec uvicorn backend.app:app --host 0.0.0.0 --port "${PORT}"

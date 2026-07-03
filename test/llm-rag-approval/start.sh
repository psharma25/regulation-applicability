#!/usr/bin/env bash
set -e
MODEL="${OLLAMA_MODEL:-llama3.2:1b}"

if ! pgrep -x ollama > /dev/null; then
  echo "==> Starting Ollama..."
  nohup ollama serve > /tmp/ollama.log 2>&1 &
fi

echo "==> Waiting for Ollama to be ready..."
for i in $(seq 1 30); do
  curl -s http://localhost:11434 > /dev/null && break
  sleep 1
done

echo "==> Pulling model $MODEL (instant if already downloaded)..."
ollama pull "$MODEL"

echo "==> Starting web app on port 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

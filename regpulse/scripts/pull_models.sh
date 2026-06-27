#!/usr/bin/env bash
# Pull the open-source local models used for generation + embeddings.
# Run after `docker compose --profile ai up -d ollama`.
set -e
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull nomic-embed-text
echo "Models ready. Set USE_LLM=true in .env and restart the api service."

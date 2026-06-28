"""Runtime configuration (all via environment variables; sensible offline defaults)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# LLM (open-source, local). Ollama-compatible HTTP API.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60"))

# Embeddings. sentence-transformers model name; falls back to TF-IDF if unavailable.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
USE_EMBEDDINGS = os.getenv("USE_EMBEDDINGS", "auto")  # auto | true | false

RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

APP_TITLE = "Risk Assessment AI"

"""Runtime settings. All overridable via environment variables."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "actors.yaml"
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


class Settings:
    # --- LLM ---
    # The agent tries Ollama first (fully local / open-source). If it is not
    # reachable it falls back to a deterministic heuristic extractor so the
    # program runs as-is with zero external dependencies or API keys.
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    llm_timeout: float = float(os.getenv("LLM_TIMEOUT", "60"))
    disable_llm: bool = os.getenv("DISABLE_LLM", "0") == "1"

    # --- Collectors ---
    # All sources here are public and free to query. No login-walled or
    # ToS-restricted review/scraping sources are used.
    ransomwarelive_base: str = os.getenv(
        "RANSOMWARELIVE_BASE", "https://api.ransomware.live/v2"
    )
    cisa_feed: str = os.getenv(
        "CISA_FEED", "https://www.cisa.gov/cybersecurity-advisories/all.xml"
    )
    extra_rss: list[str] = [
        u.strip()
        for u in os.getenv(
            "EXTRA_RSS",
            "https://www.bleepingcomputer.com/feed/,"
            "https://research.checkpoint.com/feed/",
        ).split(",")
        if u.strip()
    ]
    http_timeout: float = float(os.getenv("HTTP_TIMEOUT", "20"))
    user_agent: str = os.getenv(
        "USER_AGENT", "threat-actor-reputation-tracker/1.0 (research)"
    )

    data_dir: Path = DATA_DIR


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)

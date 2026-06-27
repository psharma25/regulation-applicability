"""Central configuration, read from environment variables (12-factor)."""
import os


class Settings:
    # --- database (open source) -------------------------------------------
    # Defaults to local SQLite so the app runs with zero infra; production
    # uses Postgres + pgvector via DATABASE_URL.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./regpulse.db")

    # --- auth --------------------------------------------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ACCESS_TOKEN_MINUTES: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "10080"))  # 7 days

    # --- LLM / RAG (open source, local-first) ------------------------------
    # When USE_LLM is false, the app uses deterministic templates only -> $0
    # inference cost and fully offline. Turn on once Ollama is running.
    USE_LLM: bool = os.getenv("USE_LLM", "false").lower() == "true"
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.2:3b")          # small + cheap
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")  # 768-d, local

    # Optional OpenAI-compatible fallback (e.g. a cheap hosted endpoint).
    # Left blank by default to keep everything local & free.
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # --- scheduler ---------------------------------------------------------
    SCAN_CRON_DAY: str = os.getenv("SCAN_CRON_DAY", "mon")  # weekly cadence
    SCAN_CRON_HOUR: int = int(os.getenv("SCAN_CRON_HOUR", "3"))
    ENABLE_SCHEDULER: bool = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"

    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")


settings = Settings()

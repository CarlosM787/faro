"""Application configuration.

All settings are environment-driven (12-factor). The app is fully functional
with no secrets set: when ``ANTHROPIC_API_KEY`` is absent, the LLM layer
falls back to a local Ollama model automatically.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings (prefix-less, `.env` supported)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- LLM provider selection (env-only switching; see TECH-NOTES) ---
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"

    # --- Quant assumptions (documented; see docs/TECH-NOTES.md) ---
    # Annualized risk-free rate used for Sharpe/Sortino/alpha (approx. 3-month
    # T-bill; constant by design for reproducibility — documented limitation).
    risk_free_rate: float = 0.043
    benchmark_ticker: str = "SPY"
    trading_days_per_year: int = 252

    # --- Data & storage ---
    data_dir: Path = Path("data")
    database_url: str = "sqlite:///data/faro.sqlite3"
    cache_max_age_hours: float = 24.0

    # --- API ---
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def llm_provider(self) -> Literal["anthropic", "ollama"]:
        """Which LLM provider is active. Anthropic is primary when a key exists."""
        return "anthropic" if self.anthropic_api_key else "ollama"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (import-safe, override-friendly in tests)."""
    return Settings()

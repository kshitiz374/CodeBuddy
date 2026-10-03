from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ai_provider: str = "mock"
    ollama_base_url: str = "http://localhost:11434"
    model_name: str = "qwen2.5-coder:7b"
    ai_timeout_seconds: float = 120.0
    database_url: str = "sqlite:///./data/codebuddy.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    api_port: int = 8000
    data_dir: Path = Path("data")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_local_provider(self) -> bool:
        return self.ai_provider.lower() in {"ollama", "local"}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings

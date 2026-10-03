from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.services.ai.base import AIProvider
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai.ollama_provider import OllamaProvider


def _build_provider() -> AIProvider:
    settings = get_settings()
    provider_name = (settings.ai_provider or "mock").strip().lower()
    if provider_name in {"ollama", "local"}:
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model_name=settings.model_name,
            timeout_seconds=settings.ai_timeout_seconds,
        )
    return MockAIProvider()


@lru_cache
def _cached_provider() -> AIProvider:
    return _build_provider()


def get_provider() -> AIProvider:
    """Return the configured AI provider.

    Tests may monkeypatch this function; cache clearing uses the private cache.
    """
    return _cached_provider()


def reset_provider_cache() -> None:
    _cached_provider.cache_clear()

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthStatus
from app.services.ai import factory

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthStatus)
async def health() -> HealthStatus:
    settings = get_settings()
    return HealthStatus(
        status="ok",
        provider=settings.ai_provider,
        model_name=settings.model_name if settings.is_local_provider else None,
        detail="CodeBuddy API is running",
    )


@router.get("/model/status")
async def model_status() -> dict:
    provider = factory.get_provider()
    status = await provider.status()
    settings = get_settings()
    return {
        **status,
        "privacy": (
            "Local inference mode: code is processed by the configured provider on this machine "
            "when using Ollama/mock. Cloud providers (if added later) are labeled separately."
            if settings.is_local_provider or provider.is_local
            else "Non-local provider selected. Review privacy implications before pasting private code."
        ),
        "ollama_base_url": settings.ollama_base_url,
        "configured_model_name": settings.model_name,
        "ai_provider_setting": settings.ai_provider,
    }

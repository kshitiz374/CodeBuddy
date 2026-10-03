from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(default="error")
    message: str
    details: dict | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class HealthStatus(BaseModel):
    status: str
    provider: str
    model_name: str | None = None
    detail: str | None = None

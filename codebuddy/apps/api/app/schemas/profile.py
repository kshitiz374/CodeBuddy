from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

LEVELS = {"beginner", "intermediate", "advanced"}
EXPLANATION_STYLES = {"simple", "detailed", "analogy-heavy", "example-first"}


class ProfileUpdate(BaseModel):
    name: str | None = None
    level: str | None = None
    languages: list[str] | None = None
    topics: list[str] | None = None
    preferred_explanation: str | None = None
    hint_first: bool | None = None

    @field_validator("level")
    @classmethod
    def _check_level(cls, v: str | None) -> str | None:
        if v is None:
            return v
        value = v.strip().lower()
        if value not in LEVELS:
            raise ValueError(f"level must be one of {sorted(LEVELS)}")
        return value

    @field_validator("preferred_explanation")
    @classmethod
    def _check_style(cls, v: str | None) -> str | None:
        if v is None:
            return v
        value = v.strip().lower()
        if value not in EXPLANATION_STYLES:
            raise ValueError(f"preferred_explanation must be one of {sorted(EXPLANATION_STYLES)}")
        return value

    @field_validator("languages", "topics")
    @classmethod
    def _check_lists(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        cleaned = [item.strip() for item in v if item and item.strip()]
        if not cleaned:
            raise ValueError("list cannot be empty when provided")
        return cleaned


class ProfileOut(BaseModel):
    name: str
    level: str
    languages: list[str]
    topics: list[str]
    preferred_explanation: str
    hint_first: bool
    updated_at: datetime | None = None

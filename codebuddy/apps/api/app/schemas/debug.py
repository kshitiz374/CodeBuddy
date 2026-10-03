from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

SUPPORTED_LANGUAGES = {"cpp", "python", "java", "c", "javascript", "typescript", "go", "rust"}
LANG_ALIASES = {
    "c++": "cpp",
    "cplusplus": "cpp",
    "cxx": "cpp",
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "ts": "typescript",
}


def normalize_language(raw: str) -> str:
    value = (raw or "").strip().lower()
    value = LANG_ALIASES.get(value, value)
    if value not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{raw}'. Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )
    return value


class DebugRequest(BaseModel):
    code: str = Field(min_length=1, description="Source code to analyze")
    language: str = Field(min_length=1)
    error_message: str | None = None
    expected_behavior: str | None = None
    actual_behavior: str | None = None
    hint_level: Literal["identify", "hint", "explain", "fix", "learn"] = "learn"
    include_prior_mistakes: bool = True

    @field_validator("language")
    @classmethod
    def _check_language(cls, v: str) -> str:
        return normalize_language(v)

    @field_validator("code")
    @classmethod
    def _check_code(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Code cannot be empty or whitespace-only")
        return v


class DeterministicInfo(BaseModel):
    source: str = "static_analysis"
    findings: list[str] = Field(default_factory=list)
    compiler_output: str | None = None
    executed: bool = False


class PriorMistake(BaseModel):
    exists: bool = False
    summary: str | None = None
    topic: str | None = None
    connection: str | None = None
    mistake_id: str | None = None


class DebugResponse(BaseModel):
    problem: str
    severity: str = "error"
    location: str | None = None
    explanation: str
    hint: str
    concept: str
    fix: str
    lesson: str
    deterministic: DeterministicInfo = Field(default_factory=DeterministicInfo)
    prior_mistake: PriorMistake = Field(default_factory=PriorMistake)
    session_id: str
    provider: str
    model_name: str | None = None


class HintRequest(BaseModel):
    session_id: str
    next_level: Literal["hint", "explain", "fix", "learn"] = "hint"


class HintResponse(BaseModel):
    session_id: str
    level: str
    content: str
    provider: str

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ExplainRequest(BaseModel):
    query: str = Field(min_length=2, description="Concept or question to explain")
    language: str | None = None
    code: str | None = None
    depth: str = "standard"

    @field_validator("query")
    @classmethod
    def _check_query(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Query is too short")
        return cleaned


class ExplainResponse(BaseModel):
    concept: str
    simple_explanation: str
    analogy: str
    example_code: str
    step_by_step: str
    common_mistake: str
    mini_question: str
    provider: str
    model_name: str | None = None
    session_id: str | None = None

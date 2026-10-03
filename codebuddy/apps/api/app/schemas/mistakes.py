from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MistakeCreate(BaseModel):
    topic: str = Field(min_length=1, max_length=80)
    problem_summary: str = Field(min_length=1)
    cause: str = Field(min_length=1)
    lesson: str = Field(min_length=1)
    language: str | None = None
    session_id: str | None = None


class MistakeOut(BaseModel):
    id: str
    topic: str
    problem_summary: str
    cause: str
    lesson: str
    language: str | None
    session_id: str | None
    created_at: datetime


class PatternBucket(BaseModel):
    topic: str
    count: int


class MistakeDashboard(BaseModel):
    total: int
    patterns: list[PatternBucket]
    note: str = (
        "These bars count mistakes recorded in this app. "
        "They are not a scientifically validated measure of learning ability."
    )
    items: list[MistakeOut]

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.debug import DebugResponse
from app.schemas.explain import ExplainResponse


class HistoryItem(BaseModel):
    id: str
    kind: str
    title: str
    language: str | None
    created_at: datetime


class HistoryOut(BaseModel):
    items: list[HistoryItem]
    total: int


class SessionDetail(BaseModel):
    debug: DebugResponse | None = None
    explain: ExplainResponse | None = None

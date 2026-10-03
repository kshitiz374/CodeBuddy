from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import DebugSession, ExplainSession
from app.schemas.debug import DebugResponse
from app.schemas.explain import ExplainResponse
from app.schemas.history import HistoryItem, HistoryOut
from app.services.ai import factory
from app.services.learning import session_store

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryOut)
def history(db: Session = Depends(get_db), limit: int = 20) -> HistoryOut:
    limit = max(1, min(limit, 100))
    debug_rows = db.query(DebugSession).order_by(DebugSession.created_at.desc()).limit(limit).all()
    explain_rows = db.query(ExplainSession).order_by(ExplainSession.created_at.desc()).limit(limit).all()
    items: list[HistoryItem] = []
    for row in debug_rows:
        items.append(
            HistoryItem(
                id=row.id,
                kind="debug",
                title=row.problem[:120],
                language=row.language,
                created_at=row.created_at,
            )
        )
    for row in explain_rows:
        items.append(
            HistoryItem(
                id=row.id,
                kind="explain",
                title=row.concept[:120],
                language=row.language,
                created_at=row.created_at,
            )
        )
    items.sort(key=lambda x: x.created_at, reverse=True)
    return HistoryOut(items=items[:limit], total=len(items))


@router.get("/debug/{session_id}", response_model=DebugResponse)
def debug_detail(session_id: str, db: Session = Depends(get_db)) -> DebugResponse:
    row = db.get(DebugSession, session_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "session_not_found", "message": f"No debug session {session_id}"},
        )
    provider = factory.get_provider()
    return session_store.debug_session_to_response(
        row,
        provider=provider.name,
        model_name=provider.model_name,
    )


@router.get("/explain/{session_id}", response_model=ExplainResponse)
def explain_detail(session_id: str, db: Session = Depends(get_db)) -> ExplainResponse:
    row = db.get(ExplainSession, session_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "session_not_found", "message": f"No explain session {session_id}"},
        )
    provider = factory.get_provider()
    return session_store.explain_session_to_response(
        row,
        provider=provider.name,
        model_name=provider.model_name,
    )

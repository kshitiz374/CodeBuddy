from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.mistakes import MistakeCreate, MistakeDashboard, MistakeOut, PatternBucket
from app.services.learning import mistake_memory

router = APIRouter(prefix="/api/mistakes", tags=["mistakes"])


@router.get("", response_model=MistakeDashboard)
def list_mistakes_dashboard(db: Session = Depends(get_db)) -> MistakeDashboard:
    items = mistake_memory.list_mistakes(db)
    patterns = [PatternBucket(**row) for row in mistake_memory.pattern_counts(db)]
    return MistakeDashboard(
        total=len(items),
        patterns=patterns,
        items=[MistakeOut(**mistake_memory.mistake_to_out_dict(m)) for m in items],
    )


@router.post("", response_model=MistakeOut, status_code=201)
def create_mistake(payload: MistakeCreate, db: Session = Depends(get_db)) -> MistakeOut:
    mistake = mistake_memory.create_mistake(db, payload)
    return MistakeOut(**mistake_memory.mistake_to_out_dict(mistake))


@router.get("/{mistake_id}", response_model=MistakeOut)
def get_mistake(mistake_id: str, db: Session = Depends(get_db)) -> MistakeOut:
    from app.models.entities import Mistake

    mistake = db.get(Mistake, mistake_id)
    if mistake is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "mistake_not_found", "message": f"No mistake {mistake_id}"},
        )
    return MistakeOut(**mistake_memory.mistake_to_out_dict(mistake))

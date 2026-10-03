from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.services.learning import profile_store

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)) -> ProfileOut:
    profile = profile_store.get_or_create_profile(db)
    data = profile_store.profile_to_dict(profile)
    return ProfileOut(
        name=data["name"],
        level=data["level"],
        languages=data["languages"],
        topics=data["topics"],
        preferred_explanation=data["preferred_explanation"],
        hint_first=data["hint_first"],
        updated_at=profile.updated_at,
    )


@router.put("", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db)) -> ProfileOut:
    profile = profile_store.update_profile(db, payload.model_dump(exclude_none=True))
    data = profile_store.profile_to_dict(profile)
    return ProfileOut(
        name=data["name"],
        level=data["level"],
        languages=data["languages"],
        topics=data["topics"],
        preferred_explanation=data["preferred_explanation"],
        hint_first=data["hint_first"],
        updated_at=profile.updated_at,
    )

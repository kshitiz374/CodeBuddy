from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.entities import LearningProfile

DEFAULT_PROFILE = {
    "name": "Friend",
    "level": "beginner",
    "languages": ["C++", "Python"],
    "topics": ["arrays", "linked lists", "recursion", "pointers"],
    "preferred_explanation": "simple",
    "hint_first": True,
}


def _loads(raw: str | None, fallback):
    if not raw:
        return fallback
    try:
        data = json.loads(raw)
        return data if isinstance(data, fallback.__class__ if fallback is not list else list) else fallback
    except json.JSONDecodeError:
        return fallback


def profile_to_dict(profile: LearningProfile | None) -> dict:
    if profile is None:
        return dict(DEFAULT_PROFILE)
    return {
        "name": profile.name,
        "level": profile.level,
        "languages": _loads(profile.languages, ["C++", "Python"]),
        "topics": _loads(profile.topics, ["arrays", "recursion"]),
        "preferred_explanation": profile.preferred_explanation,
        "hint_first": bool(profile.hint_first),
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


def get_or_create_profile(db: Session) -> LearningProfile:
    profile = db.query(LearningProfile).order_by(LearningProfile.updated_at.desc()).first()
    if profile is not None:
        return profile
    profile = LearningProfile(
        name=DEFAULT_PROFILE["name"],
        level=DEFAULT_PROFILE["level"],
        languages=json.dumps(DEFAULT_PROFILE["languages"]),
        topics=json.dumps(DEFAULT_PROFILE["topics"]),
        preferred_explanation=DEFAULT_PROFILE["preferred_explanation"],
        hint_first=1 if DEFAULT_PROFILE["hint_first"] else 0,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, payload: dict) -> LearningProfile:
    profile = get_or_create_profile(db)
    if payload.get("name") is not None:
        profile.name = payload["name"]
    if payload.get("level") is not None:
        profile.level = payload["level"]
    if payload.get("languages") is not None:
        profile.languages = json.dumps(payload["languages"])
    if payload.get("topics") is not None:
        profile.topics = json.dumps(payload["topics"])
    if payload.get("preferred_explanation") is not None:
        profile.preferred_explanation = payload["preferred_explanation"]
    if payload.get("hint_first") is not None:
        profile.hint_first = 1 if payload["hint_first"] else 0
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

from __future__ import annotations

import json
import re
from collections import Counter

from sqlalchemy.orm import Session

from app.models.entities import Mistake, utcnow
from app.schemas.mistakes import MistakeCreate


def _normalize_topic(topic: str) -> str:
    return re.sub(r"\s+", " ", (topic or "").strip().lower())


def create_mistake(db: Session, payload: MistakeCreate) -> Mistake:
    mistake = Mistake(
        topic=payload.topic.strip(),
        problem_summary=payload.problem_summary.strip(),
        cause=payload.cause.strip(),
        lesson=payload.lesson.strip(),
        language=payload.language,
        session_id=payload.session_id,
        created_at=utcnow(),
    )
    db.add(mistake)
    db.commit()
    db.refresh(mistake)
    return mistake


def list_mistakes(db: Session, limit: int = 200) -> list[Mistake]:
    return (
        db.query(Mistake)
        .order_by(Mistake.created_at.desc())
        .limit(limit)
        .all()
    )


def pattern_counts(db: Session) -> list[dict]:
    rows = list_mistakes(db, limit=1000)
    counter = Counter(_normalize_topic(m.topic) for m in rows)
    # Present original casing from the most recent mistake per topic.
    original: dict[str, str] = {}
    for m in reversed(rows):
        key = _normalize_topic(m.topic)
        original.setdefault(key, m.topic)
    return [
        {"topic": original.get(topic, topic.title()), "count": count}
        for topic, count in counter.most_common()
    ]


def find_similar_mistake(
    db: Session,
    *,
    topic_hints: list[str] | None = None,
    text: str = "",
    limit: int = 5,
) -> Mistake | None:
    """Find a prior mistake by topic/keyword overlap only (local, explainable)."""
    rows = list_mistakes(db, limit=200)
    if not rows:
        return None

    haystack_text = _normalize_topic(text)
    hint_set = {_normalize_topic(h) for h in (topic_hints or []) if h}
    # Also seed hints from common analysis topics if caller passed none.
    for token in re.findall(r"[a-zA-Z+#]{3,}", haystack_text):
        hint_set.add(token.lower())

    best: Mistake | None = None
    best_score = 0
    for row in rows:
        row_blob = _normalize_topic(
            " ".join([row.topic, row.problem_summary, row.cause, row.lesson, row.language or ""])
        )
        score = 0
        for hint in hint_set:
            if not hint:
                continue
            if hint in row_blob:
                score += 2 if _normalize_topic(row.topic) == hint else 1
        if score > best_score:
            best_score = score
            best = row
    return best if best_score >= 2 else None


def mistake_to_out_dict(mistake: Mistake) -> dict:
    return {
        "id": mistake.id,
        "topic": mistake.topic,
        "problem_summary": mistake.problem_summary,
        "cause": mistake.cause,
        "lesson": mistake.lesson,
        "language": mistake.language,
        "session_id": mistake.session_id,
        "created_at": mistake.created_at,
    }


def serialize_prior_mistake(mistake: Mistake | None) -> dict:
    if mistake is None:
        return {
            "exists": False,
            "summary": None,
            "topic": None,
            "connection": None,
            "mistake_id": None,
        }
    return {
        "exists": True,
        "summary": mistake.problem_summary,
        "topic": mistake.topic,
        "connection": (
            f"Earlier you recorded: '{mistake.problem_summary}' "
            f"(lesson: {mistake.lesson}). Compare that lesson with this new analysis."
        ),
        "mistake_id": mistake.id,
    }


def dumps_mistakes(mistakes: list[Mistake]) -> str:
    data = [
        {
            "topic": m.topic,
            "problem_summary": m.problem_summary,
            "cause": m.cause,
            "lesson": m.lesson,
        }
        for m in mistakes
    ]
    return json.dumps(data)

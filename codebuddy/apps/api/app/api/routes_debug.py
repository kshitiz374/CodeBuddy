from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import DebugSession
from app.schemas.debug import DebugRequest, DebugResponse, HintRequest, HintResponse
from app.services.ai.base import AnalysisContext
from app.services.ai import factory
from app.services.analysis.static_analysis import analyze_code
from app.services.learning import mistake_memory, profile_store, session_store

router = APIRouter(prefix="/api", tags=["debug"])

_TOPIC_KEYWORDS = {
    "cpp": ["pointer", "memory", "array", "linked", "recursion", "segfault", "nullptr"],
    "c": ["pointer", "memory", "array", "segmentation"],
    "python": ["indent", "name", "type", "list", "dict", "exception"],
    "java": ["null", "class", "string", "array", "exception"],
}


def _infer_topic_hints(language: str, code: str, error_message: str | None, findings: list[str]) -> list[str]:
    blob = " ".join([code or "", error_message or "", " ".join(findings)]).lower()
    hints = list(_TOPIC_KEYWORDS.get(language, []))
    for keyword in [
        "pointer", "nullptr", "null", "malloc", "new", "linked list", "recursion",
        "index", "indentation", "indent", "nameerror", "typeerror", "segfault",
        "segmentation fault", "undefined reference", "memory leak",
    ]:
        if keyword in blob:
            hints.append(keyword.replace(" ", "_"))
    # De-duplicate while preserving order
    seen = set()
    unique = []
    for h in hints:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    return unique


@router.post("/debug", response_model=DebugResponse)
async def debug_code(payload: DebugRequest, db: Session = Depends(get_db)) -> DebugResponse:
    provider = factory.get_provider()
    profile = profile_store.profile_to_dict(profile_store.get_or_create_profile(db))

    static = analyze_code(payload.code, payload.language, payload.error_message)
    findings = static.messages

    prior_mistake_row = None
    if payload.include_prior_mistakes:
        prior_mistake_row = mistake_memory.find_similar_mistake(
            db,
            topic_hints=_infer_topic_hints(payload.language, payload.code, payload.error_message, findings),
            text=" ".join(filter(None, [payload.error_message, payload.actual_behavior, " ".join(findings)])),
        )

    ctx = AnalysisContext(
        code=payload.code,
        language=payload.language,
        error_message=payload.error_message,
        expected_behavior=payload.expected_behavior,
        actual_behavior=payload.actual_behavior,
        profile=profile,
        deterministic_findings=findings,
        prior_mistakes=(
            [
                {
                    "topic": prior_mistake_row.topic,
                    "problem_summary": prior_mistake_row.problem_summary,
                    "cause": prior_mistake_row.cause,
                    "lesson": prior_mistake_row.lesson,
                }
            ]
            if prior_mistake_row
            else []
        ),
        hint_level=payload.hint_level,
    )

    try:
        result = await provider.analyze_code(ctx)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail={
                "code": "ai_provider_error",
                "message": "The AI provider failed while analyzing this problem.",
                "details": {
                    "provider": provider.name,
                    "reason": str(exc),
                    "hint": (
                        "If using Ollama, ensure it is running and the model is pulled. "
                        "Set AI_PROVIDER=mock to use the offline mentor stub."
                    ),
                },
            },
        ) from exc

    source = "both" if findings else provider.name
    session = session_store.save_debug_session(
        db,
        payload,
        result,
        provider=provider.name,
        deterministic_source=source,
        findings=findings,
        prior_mistake=mistake_memory.serialize_prior_mistake(prior_mistake_row),
        model_name=provider.model_name,
    )
    return session_store.debug_session_to_response(
        session,
        provider=provider.name,
        model_name=provider.model_name,
    )


@router.post("/hint", response_model=HintResponse)
async def next_hint(payload: HintRequest, db: Session = Depends(get_db)) -> HintResponse:
    session = db.get(DebugSession, payload.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "session_not_found", "message": f"No debug session {payload.session_id}"},
        )

    provider = factory.get_provider()
    level_content = {
        "hint": session.hint,
        "explain": session.explanation + "\n\nConcept: " + session.concept,
        "fix": session.fix,
        "learn": session.lesson,
    }
    content = level_content.get(payload.next_level, session.hint)
    return HintResponse(
        session_id=session.id,
        level=payload.next_level,
        content=content,
        provider=provider.name,
    )

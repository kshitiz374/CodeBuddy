from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.explain import ExplainRequest, ExplainResponse
from app.services.ai.base import ConceptContext
from app.services.ai import factory
from app.services.learning import profile_store, session_store

router = APIRouter(prefix="/api", tags=["explain"])


@router.post("/explain", response_model=ExplainResponse)
async def explain_concept(payload: ExplainRequest, db: Session = Depends(get_db)) -> ExplainResponse:
    provider = factory.get_provider()
    profile = profile_store.profile_to_dict(profile_store.get_or_create_profile(db))
    ctx = ConceptContext(
        query=payload.query,
        language=payload.language,
        code=payload.code,
        profile=profile,
        depth=payload.depth,
    )
    try:
        result = await provider.explain_concept(ctx)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail={
                "code": "ai_provider_error",
                "message": "The AI provider failed while explaining this concept.",
                "details": {"provider": provider.name, "reason": str(exc)},
            },
        ) from exc

    session = session_store.save_explain_session(db, payload, result)
    return session_store.explain_session_to_response(
        session,
        provider=provider.name,
        model_name=provider.model_name,
    )

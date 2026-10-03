from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.entities import DebugSession, ExplainSession, utcnow
from app.schemas.debug import DebugRequest, DebugResponse, DeterministicInfo, PriorMistake
from app.schemas.explain import ExplainRequest, ExplainResponse
from app.services.ai.base import AnalysisResult, ConceptResult


def save_debug_session(
    db: Session,
    request: DebugRequest,
    result: AnalysisResult,
    *,
    provider: str,
    deterministic_source: str,
    findings: list[str],
    prior_mistake: dict,
    model_name: str | None,
) -> DebugSession:
    session = DebugSession(
        language=request.language,
        code=request.code,
        error_message=request.error_message,
        expected_behavior=request.expected_behavior,
        actual_behavior=request.actual_behavior,
        problem=result.problem,
        severity=result.severity,
        location=result.location,
        explanation=result.explanation,
        hint=result.hint,
        concept=result.concept,
        fix=result.fix,
        lesson=result.lesson,
        deterministic_source=deterministic_source,
        findings_json=json.dumps(findings),
        prior_mistake_json=json.dumps(prior_mistake),
        created_at=utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def debug_session_to_response(
    session: DebugSession,
    *,
    provider: str,
    model_name: str | None = None,
) -> DebugResponse:
    try:
        findings = json.loads(session.findings_json or "[]")
    except json.JSONDecodeError:
        findings = []
    try:
        prior = json.loads(session.prior_mistake_json or "{}") if session.prior_mistake_json else {}
    except json.JSONDecodeError:
        prior = {}
    return DebugResponse(
        problem=session.problem,
        severity=session.severity,
        location=session.location,
        explanation=session.explanation,
        hint=session.hint,
        concept=session.concept,
        fix=session.fix,
        lesson=session.lesson,
        deterministic=DeterministicInfo(
            source=session.deterministic_source,
            findings=findings if isinstance(findings, list) else [],
            compiler_output=None,
            executed=False,
        ),
        prior_mistake=PriorMistake(**prior) if prior else PriorMistake(),
        session_id=session.id,
        provider=provider,
        model_name=model_name,
    )


def save_explain_session(
    db: Session,
    request: ExplainRequest,
    result: ConceptResult,
) -> ExplainSession:
    session = ExplainSession(
        query=request.query,
        language=request.language,
        concept=result.concept,
        simple_explanation=result.simple_explanation,
        analogy=result.analogy,
        example_code=result.example_code,
        step_by_step=result.step_by_step,
        common_mistake=result.common_mistake,
        mini_question=result.mini_question,
        created_at=utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def explain_session_to_response(
    session: ExplainSession,
    *,
    provider: str,
    model_name: str | None = None,
) -> ExplainResponse:
    return ExplainResponse(
        concept=session.concept,
        simple_explanation=session.simple_explanation,
        analogy=session.analogy,
        example_code=session.example_code,
        step_by_step=session.step_by_step,
        common_mistake=session.common_mistake,
        mini_question=session.mini_question,
        provider=provider,
        model_name=model_name,
        session_id=session.id,
    )

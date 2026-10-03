from __future__ import annotations

import json

from app.services.ai.base import AnalysisContext, ConceptContext

SYSTEM_PROMPT = """You are CodeBuddy, a patient programming mentor.

Your objective is not merely to provide the correct code.

First understand:
- What the user attempted
- What they expected
- What actually happened

Explain problems in simple language.

Do not immediately reveal the complete solution.

Prefer this order when details allow:
1. Diagnosis (problem category)
2. Hint (point to the relevant part of the code)
3. Concept explanation
4. Correct approach
5. Corrected code
6. Lesson learned

Never claim to have executed code unless the system actually executed it.
Never invent compiler output.
If information is insufficient, explicitly say what is missing.
Adapt explanations to the user's learning profile.
Use the user's previous mistake history only when it is actually relevant.

Respond with a single JSON object only. No markdown fences. No extra prose.
"""


def _profile_block(profile: dict) -> str:
    if not profile:
        return "No learning profile provided."
    return json.dumps(profile, ensure_ascii=False)


def _mistakes_block(mistakes: list[dict]) -> str:
    if not mistakes:
        return "No prior mistakes provided."
    slim = [
        {
            "topic": m.get("topic"),
            "problem_summary": m.get("problem_summary"),
            "cause": m.get("cause"),
            "lesson": m.get("lesson"),
        }
        for m in mistakes
    ]
    return json.dumps(slim, ensure_ascii=False)


def build_debug_messages(ctx: AnalysisContext) -> list[dict[str, str]]:
    payload = {
        "language": ctx.language,
        "code": ctx.code,
        "error_message": ctx.error_message or "",
        "expected_behavior": ctx.expected_behavior or "",
        "actual_behavior": ctx.actual_behavior or "",
        "requested_hint_level": ctx.hint_level,
        "learning_profile": json.loads(_profile_block(ctx.profile))
        if isinstance(ctx.profile, str)
        else ctx.profile,
        "deterministic_findings": ctx.deterministic_findings,
        "prior_mistakes": ctx.prior_mistakes,
    }
    user = (
        "Analyze this programming problem as CodeBuddy.\n"
        f"Input:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Return JSON with keys exactly:\n"
        "problem, severity, location, explanation, hint, concept, fix, lesson\n"
        "Rules:\n"
        "- severity: error|warning|concept\n"
        "- location: short code location guess or empty string\n"
        "- Do not pretend code was executed.\n"
        "- If deterministic_findings exist, incorporate them into problem/explanation.\n"
        "- If prior_mistakes are relevant, mention the connection in lesson or explanation briefly.\n"
        "- hint_first profile => keep fix less dominant; still include a short corrected approach.\n"
        "- preferred_explanation simple => plain language, short sentences."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def build_explain_messages(ctx: ConceptContext) -> list[dict[str, str]]:
    payload = {
        "query": ctx.query,
        "language": ctx.language or "",
        "code": ctx.code or "",
        "depth": ctx.depth,
        "learning_profile": ctx.profile or {},
    }
    user = (
        "Explain this programming concept as CodeBuddy.\n"
        f"Input:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "Return JSON with keys exactly:\n"
        "concept, simple_explanation, analogy, example_code, step_by_step, common_mistake, mini_question\n"
        "Rules:\n"
        "- Keep example_code small and runnable-looking (no fake compiler output).\n"
        "- mini_question should invite the learner to try something concrete.\n"
        "- Adapt tone to profile level."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def parse_debug_json(text: str) -> dict:
    return _parse_json_object(text, required_keys={
        "problem", "severity", "location", "explanation", "hint", "concept", "fix", "lesson"
    })


def parse_explain_json(text: str) -> dict:
    return _parse_json_object(text, required_keys={
        "concept", "simple_explanation", "analogy", "example_code",
        "step_by_step", "common_mistake", "mini_question"
    })


def _parse_json_object(text: str, required_keys: set[str]) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Model did not return a JSON object")
    raw = cleaned[start : end + 1]
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Model JSON must be an object")
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(f"Model JSON missing keys: {sorted(missing)}")
    return data

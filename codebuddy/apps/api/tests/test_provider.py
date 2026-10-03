from __future__ import annotations

import pytest

from app.services.ai.base import AnalysisContext, ConceptContext
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai.prompts import parse_debug_json, parse_explain_json


@pytest.mark.asyncio
async def test_mock_analyze_pointer():
    provider = MockAIProvider()
    result = await provider.analyze_code(
        AnalysisContext(
            code="Node* head;\nhead->data = 10;",
            language="cpp",
            error_message="Segmentation fault",
        )
    )
    assert "pointer" in result.problem.lower() or "valid object" in result.problem.lower()
    assert result.hint
    assert result.lesson


@pytest.mark.asyncio
async def test_mock_explain_recursion():
    provider = MockAIProvider()
    result = await provider.explain_concept(ConceptContext(query="Explain recursion"))
    assert result.concept.lower().startswith("recursion") or "recursion" in result.concept.lower()
    assert result.mini_question


def test_parse_json_helpers():
    debug = parse_debug_json(
        '{"problem":"p","severity":"error","location":"l","explanation":"e","hint":"h","concept":"c","fix":"f","lesson":"l2"}'
    )
    assert debug["problem"] == "p"
    explain = parse_explain_json(
        '{"concept":"c","simple_explanation":"s","analogy":"a","example_code":"e","step_by_step":"t","common_mistake":"m","mini_question":"q"}'
    )
    assert explain["concept"] == "c"


def test_parse_json_rejects_missing():
    with pytest.raises(ValueError):
        parse_debug_json('{"problem":"only"}')

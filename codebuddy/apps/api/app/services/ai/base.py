from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisContext:
    code: str
    language: str
    error_message: str | None = None
    expected_behavior: str | None = None
    actual_behavior: str | None = None
    profile: dict[str, Any] = field(default_factory=dict)
    deterministic_findings: list[str] = field(default_factory=list)
    prior_mistakes: list[dict[str, Any]] = field(default_factory=list)
    hint_level: str = "learn"


@dataclass
class AnalysisResult:
    problem: str
    severity: str
    location: str | None
    explanation: str
    hint: str
    concept: str
    fix: str
    lesson: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConceptContext:
    query: str
    language: str | None = None
    code: str | None = None
    profile: dict[str, Any] = field(default_factory=dict)
    depth: str = "standard"


@dataclass
class ConceptResult:
    concept: str
    simple_explanation: str
    analogy: str
    example_code: str
    step_by_step: str
    common_mistake: str
    mini_question: str
    raw: dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """Provider interface so Ollama (or anything else) can be swapped cleanly."""

    name: str = "base"
    is_local: bool = False
    model_name: str | None = None

    @abstractmethod
    async def analyze_code(self, request: AnalysisContext) -> AnalysisResult:
        raise NotImplementedError

    @abstractmethod
    async def explain_concept(self, request: ConceptContext) -> ConceptResult:
        raise NotImplementedError

    async def hint(self, request: AnalysisContext) -> str:
        result = await self.analyze_code(request)
        return result.hint

    async def status(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "model_name": self.model_name,
            "is_local": self.is_local,
            "available": True,
            "detail": "ready",
        }

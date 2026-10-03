from __future__ import annotations

from typing import Any

import httpx

from app.services.ai.base import (
    AIProvider,
    AnalysisContext,
    AnalysisResult,
    ConceptContext,
    ConceptResult,
)
from app.services.ai.prompts import (
    build_debug_messages,
    build_explain_messages,
    parse_debug_json,
    parse_explain_json,
)


class OllamaProvider(AIProvider):
    """Local open-weight model via the Ollama HTTP API.

    Business logic depends only on AIProvider; this class is the transport detail.
    """

    name = "ollama"
    is_local = True

    def __init__(
        self,
        base_url: str,
        model_name: str,
        timeout_seconds: float = 120.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self._client = client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _chat(self, messages: list[dict[str, str]]) -> str:
        client = await self._get_client()
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2},
        }
        response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        try:
            content = data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Ollama response shape: {data}") from exc
        return content or ""

    async def analyze_code(self, request: AnalysisContext) -> AnalysisResult:
        text = await self._chat(build_debug_messages(request))
        data = parse_debug_json(text)
        return AnalysisResult(
            problem=str(data.get("problem", "Unspecified problem")),
            severity=str(data.get("severity", "error")),
            location=(str(data.get("location") or "") or None),
            explanation=str(data.get("explanation", "")),
            hint=str(data.get("hint", "")),
            concept=str(data.get("concept", "")),
            fix=str(data.get("fix", "")),
            lesson=str(data.get("lesson", "")),
            raw=data,
        )

    async def explain_concept(self, request: ConceptContext) -> ConceptResult:
        text = await self._chat(build_explain_messages(request))
        data = parse_explain_json(text)
        return ConceptResult(
            concept=str(data.get("concept", request.query)),
            simple_explanation=str(data.get("simple_explanation", "")),
            analogy=str(data.get("analogy", "")),
            example_code=str(data.get("example_code", "")),
            step_by_step=str(data.get("step_by_step", "")),
            common_mistake=str(data.get("common_mistake", "")),
            mini_question=str(data.get("mini_question", "")),
            raw=data,
        )

    async def status(self) -> dict[str, Any]:
        client = await self._get_client()
        try:
            tags = await client.get("/api/tags")
            tags.raise_for_status()
            models = [m.get("name", "") for m in tags.json().get("models", [])]
            available = any(
                m == self.model_name or m.startswith(self.model_name.split(":")[0])
                for m in models
            )
            detail = (
                f"Ollama reachable. Model '{self.model_name}' "
                + ("found." if available else "not found. Pull it with: ollama pull " + self.model_name)
            )
            return {
                "provider": self.name,
                "model_name": self.model_name,
                "is_local": True,
                "available": True,
                "detail": detail,
                "models": models,
            }
        except Exception as exc:  # noqa: BLE001 - status should never crash the API
            return {
                "provider": self.name,
                "model_name": self.model_name,
                "is_local": True,
                "available": False,
                "detail": f"Ollama not reachable at {self.base_url}: {exc}",
            }

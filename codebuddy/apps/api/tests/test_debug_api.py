from __future__ import annotations


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "provider" in data


def test_model_status_mock(client):
    res = client.get("/api/model/status")
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "mock"
    assert data["available"] is True
    assert "privacy" in data


def test_debug_pointer_bug(client):
    payload = {
        "code": "Node* head;\n\nhead->data = 10;",
        "language": "C++",
        "error_message": "Segmentation fault",
        "expected_behavior": "set data to 10",
        "actual_behavior": "crash",
    }
    res = client.post("/api/debug", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["problem"]
    assert data["hint"]
    assert data["concept"]
    assert data["lesson"]
    assert data["deterministic"]["executed"] is False
    assert data["session_id"]
    # static analysis should mention pointer heuristic for this snippet
    joined = " ".join(data["deterministic"]["findings"]).lower()
    assert "pointer" in joined or "node" in joined


def test_debug_rejects_empty_code(client):
    res = client.post("/api/debug", json={"code": "   ", "language": "python"})
    assert res.status_code == 422


def test_debug_rejects_bad_language(client):
    res = client.post("/api/debug", json={"code": "print(1)", "language": "brainfuck"})
    assert res.status_code == 422


def test_debug_provider_error_shape(client, monkeypatch):
    # Force provider failure via invalid Ollama settings by patching provider status path.
    from app.services.ai import factory
    from app.services.ai.base import AIProvider, AnalysisContext, AnalysisResult

    class Boom(AIProvider):
        name = "boom"
        is_local = False
        model_name = "boom"

        async def analyze_code(self, request: AnalysisContext) -> AnalysisResult:
            raise RuntimeError("provider down")

        async def explain_concept(self, request):
            raise RuntimeError("provider down")

    monkeypatch.setattr(factory, "get_provider", lambda: Boom())
    res = client.post(
        "/api/debug",
        json={"code": "int x;", "language": "cpp"},
    )
    assert res.status_code == 502
    body = res.json()
    assert body["error"]["code"] == "ai_provider_error"


def test_hint_endpoint(client):
    payload = {
        "code": "Node* head;\nhead->data = 1;",
        "language": "cpp",
        "error_message": "segfault",
    }
    created = client.post("/api/debug", json=payload)
    assert created.status_code == 200
    session_id = created.json()["session_id"]
    res = client.post("/api/hint", json={"session_id": session_id, "next_level": "hint"})
    assert res.status_code == 200
    assert res.json()["level"] == "hint"
    assert res.json()["content"]


def test_hint_missing_session(client):
    res = client.post("/api/hint", json={"session_id": "nope", "next_level": "hint"})
    assert res.status_code == 404

from __future__ import annotations


def test_explain_recursion(client):
    res = client.post("/api/explain", json={"query": "Explain recursion", "language": "python"})
    assert res.status_code == 200
    data = res.json()
    assert data["concept"]
    assert data["simple_explanation"]
    assert data["analogy"]
    assert data["mini_question"]
    assert data["session_id"]


def test_explain_validation(client):
    res = client.post("/api/explain", json={"query": "x"})
    assert res.status_code == 422

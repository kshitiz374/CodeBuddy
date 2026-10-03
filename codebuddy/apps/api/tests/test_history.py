from __future__ import annotations


def test_history_empty_then_populated(client):
    empty = client.get("/api/history")
    assert empty.status_code == 200
    assert empty.json()["items"] == []

    client.post(
        "/api/debug",
        json={"code": "Node* head;\nhead->data=1;", "language": "cpp", "error_message": "segfault"},
    )
    client.post("/api/explain", json={"query": "Explain arrays"})

    res = client.get("/api/history")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) >= 2
    kinds = {i["kind"] for i in items}
    assert kinds == {"debug", "explain"}


def test_history_debug_detail(client):
    created = client.post(
        "/api/debug",
        json={"code": "int x = ;", "language": "cpp", "error_message": "syntax error"},
    )
    session_id = created.json()["session_id"]
    res = client.get(f"/api/history/debug/{session_id}")
    assert res.status_code == 200
    assert res.json()["session_id"] == session_id

    missing = client.get("/api/history/debug/does-not-exist")
    assert missing.status_code == 404

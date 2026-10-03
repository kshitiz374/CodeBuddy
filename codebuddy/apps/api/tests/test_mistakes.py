from __future__ import annotations


def test_create_and_dashboard(client):
    res = client.post(
        "/api/mistakes",
        json={
            "topic": "Pointers",
            "problem_summary": "Dereferencing an uninitialized pointer",
            "cause": "Pointer used before memory was allocated",
            "lesson": "Always initialize/allocate before dereferencing",
            "language": "C++",
        },
    )
    assert res.status_code == 201
    mistake_id = res.json()["id"]

    dash = client.get("/api/mistakes")
    assert dash.status_code == 200
    data = dash.json()
    assert data["total"] >= 1
    assert any(p["topic"].lower() == "pointers" for p in data["patterns"])
    assert "not a scientifically validated" in data["note"].lower()
    assert any(item["id"] == mistake_id for item in data["items"])


def test_similar_mistake_after_debug(client):
    client.post(
        "/api/mistakes",
        json={
            "topic": "Pointers",
            "problem_summary": "Null pointer dereference in linked list",
            "cause": "Forgot to allocate node",
            "lesson": "Allocate before use",
            "language": "C++",
        },
    )
    res = client.post(
        "/api/debug",
        json={
            "code": "Node* head;\nhead->data = 5;",
            "language": "cpp",
            "error_message": "segmentation fault",
        },
    )
    assert res.status_code == 200
    prior = res.json()["prior_mistake"]
    assert prior["exists"] is True
    assert prior["connection"]

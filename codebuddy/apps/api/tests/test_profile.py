from __future__ import annotations


def test_get_profile_defaults(client):
    res = client.get("/api/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["level"] in {"beginner", "intermediate", "advanced"}
    assert isinstance(data["languages"], list)
    assert data["hint_first"] is True


def test_update_profile(client):
    res = client.put(
        "/api/profile",
        json={
            "level": "intermediate",
            "languages": ["C++", "Python", "Java"],
            "topics": ["pointers", "recursion"],
            "preferred_explanation": "example-first",
            "hint_first": True,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["level"] == "intermediate"
    assert "Java" in data["languages"]
    assert data["preferred_explanation"] == "example-first"


def test_update_profile_validation(client):
    res = client.put("/api/profile", json={"level": "wizard"})
    assert res.status_code == 422

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))

    from app.core.config import get_settings
    from app.core.database import init_db, reset_engine
    from app.services.ai.factory import reset_provider_cache

    get_settings.cache_clear()
    reset_provider_cache()
    reset_engine()
    init_db()

    from app.main import app

    with TestClient(app) as c:
        yield c

    reset_engine()
    get_settings.cache_clear()
    reset_provider_cache()

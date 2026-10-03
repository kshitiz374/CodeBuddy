from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.engine import Engine

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def _ensure_sqlite_parent(url: str) -> None:
    if not url.startswith("sqlite"):
        return
    raw = url.split("///", 1)[-1]
    if raw and raw != ":memory:":
        Path(raw).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def create_db_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_settings().database_url
    _ensure_sqlite_parent(url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_db_engine()
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


def get_session_factory() -> sessionmaker:
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


def reset_engine() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def init_db() -> None:
    from app.models import entities  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()

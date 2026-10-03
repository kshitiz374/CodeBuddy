from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return uuid4().hex


class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(80), default="Friend")
    level: Mapped[str] = mapped_column(String(32), default="beginner")
    languages: Mapped[str] = mapped_column(Text, default='["C++", "Python"]')
    topics: Mapped[str] = mapped_column(Text, default='["arrays", "recursion", "pointers"]')
    preferred_explanation: Mapped[str] = mapped_column(String(32), default="simple")
    hint_first: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class DebugSession(Base):
    __tablename__ = "debug_sessions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    language: Mapped[str] = mapped_column(String(32))
    code: Mapped[str] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    problem: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(32), default="error")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    explanation: Mapped[str] = mapped_column(Text)
    hint: Mapped[str] = mapped_column(Text)
    concept: Mapped[str] = mapped_column(Text)
    fix: Mapped[str] = mapped_column(Text)
    lesson: Mapped[str] = mapped_column(Text)
    deterministic_source: Mapped[str] = mapped_column(String(32), default="mock")
    findings_json: Mapped[str] = mapped_column(Text, default="[]")
    prior_mistake_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    mistakes: Mapped[list["Mistake"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class ExplainSession(Base):
    __tablename__ = "explain_sessions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    query: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    concept: Mapped[str] = mapped_column(Text)
    simple_explanation: Mapped[str] = mapped_column(Text)
    analogy: Mapped[str] = mapped_column(Text)
    example_code: Mapped[str] = mapped_column(Text)
    step_by_step: Mapped[str] = mapped_column(Text)
    common_mistake: Mapped[str] = mapped_column(Text)
    mini_question: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("debug_sessions.id"), nullable=True)
    topic: Mapped[str] = mapped_column(String(80))
    problem_summary: Mapped[str] = mapped_column(Text)
    cause: Mapped[str] = mapped_column(Text)
    lesson: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    session: Mapped[DebugSession | None] = relationship(back_populates="mistakes")

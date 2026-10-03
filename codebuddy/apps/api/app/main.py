from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import routes_debug, routes_explain, routes_health, routes_history, routes_mistakes, routes_profile
from app.core.config import get_settings
from app.core.database import init_db


def _json_safe(obj):
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="CodeBuddy API",
    version="0.1.0",
    description=(
        "Local-first AI coding companion backend. "
        "Uses a configurable AI provider (Ollama by default when enabled, mock for offline/tests)."
    ),
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_debug.router)
app.include_router(routes_explain.router)
app.include_router(routes_profile.router)
app.include_router(routes_mistakes.router)
app.include_router(routes_history.router)


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": {"errors": _json_safe(exc.errors())},
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        error_payload = {
            "code": str(detail.get("code", "http_error")),
            "message": str(detail.get("message", "Request failed")),
            "details": _json_safe(detail.get("details")),
        }
    else:
        error_payload = {
            "code": "http_error",
            "message": str(detail),
            "details": None,
        }
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error_payload},
        headers=getattr(exc, "headers", None),
    )


@app.get("/")
async def root() -> dict:
    return {
        "name": "CodeBuddy API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }

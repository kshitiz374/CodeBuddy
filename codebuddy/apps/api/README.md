# CodeBuddy API

Local-first AI coding companion backend (FastAPI + SQLite + pluggable AI provider).

## Quick start

```bash
cd apps/api
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
cp ../../.env.example ../../.env

# Offline/demo mode (no Ollama required)
# In .env set:
# AI_PROVIDER=mock

# Local open-weight mode (requires Ollama installed + model pulled)
# AI_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# MODEL_NAME=qwen2.5-coder:7b

uvicorn app.main:app --reload --port 8000
```

Open API docs: http://127.0.0.1:8000/docs

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Liveness |
| GET | `/api/model/status` | Provider/model status + privacy note |
| POST | `/api/debug` | Structured debug analysis |
| POST | `/api/hint` | Retrieve a progressive level from a session |
| POST | `/api/explain` | Concept explanation |
| GET | `/api/history` | Recent debug/explain sessions |
| GET | `/api/profile` | Learning profile |
| PUT | `/api/profile` | Update learning profile |
| GET | `/api/mistakes` | Mistake dashboard + items |
| POST | `/api/mistakes` | Record a mistake |

## Tests

```bash
cd apps/api
python -m pytest -q
```

Tests use `AI_PROVIDER=mock` and a temp SQLite database. They do not require Ollama.

## Deterministic analysis

`POST /api/debug` runs lightweight static heuristics (language-aware patterns) **before** the AI call.
Findings are returned in `deterministic.findings` and labeled clearly.

CodeBuddy does **not** execute arbitrary user code on the host in this MVP.
It does **not** invent compiler output when execution is disabled.

## Data

SQLite is stored under the path in `DATABASE_URL` (default `./data/codebuddy.db`).
No cloud database is required.

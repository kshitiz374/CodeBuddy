#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Starting CodeBuddy API..."
(cd apps/api && python -m uvicorn app.main:app --reload --port 8000) &
API_PID=$!

echo "Starting CodeBuddy Web..."
(cd apps/web && npm run dev) &
WEB_PID=$!

echo "API:  http://127.0.0.1:8000/docs"
echo "Web:  http://localhost:3000"
echo "For Ollama: set AI_PROVIDER=ollama in .env after pulling a model."

trap 'kill $API_PID $WEB_PID 2>/dev/null || true' EXIT
wait

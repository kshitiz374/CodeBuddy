@echo off
setlocal
cd /d "%~dp0"

echo Starting CodeBuddy API (mock provider unless .env says otherwise)...
start "CodeBuddy API" cmd /k "cd /d apps\api && python -m uvicorn app.main:app --reload --port 8000"

echo Starting CodeBuddy Web...
start "CodeBuddy Web" cmd /k "cd /d apps\web && npm run dev"

echo.
echo API:  http://127.0.0.1:8000/docs
echo Web:  http://localhost:3000
echo.
echo For local open-weight models:
echo   1. Install Ollama
echo   2. ollama pull qwen2.5-coder:7b
echo   3. Set AI_PROVIDER=ollama in .env
echo.
pause

# Contributing to CodeBuddy

Thanks for caring about a friend who is learning to program.

## Ground rules

1. **Keep it small.** CodeBuddy is a focused mentor tool, not an AI platform.
2. **Local-first.** Prefer solutions that work without cloud AI APIs.
3. **Progressive help.** New features should not make the app dump full answers immediately.
4. **Honesty.** Do not invent compiler output, user feedback, benchmarks, or "scientific" learning claims.
5. **Privacy.** Personal data stays local. If you add a cloud provider, label it clearly in UI and docs.

## Development setup

```bash
# Backend
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example ../../.env
uvicorn app.main:app --reload --port 8000

# Frontend
cd apps/web
npm install
npm run dev
```

Optional local model:

```bash
# Install Ollama, then:
ollama pull qwen2.5-coder:7b
```

Without Ollama, set `AI_PROVIDER=mock` in `.env`.

## Tests

```bash
cd apps/api
python -m pytest -q
```

```bash
cd apps/web
npm run lint
npm run typecheck
npm run build
```

## Pull requests

- Describe the user problem you are solving.
- Include tests for backend behavior changes.
- Update README/docs if behavior or setup changes.
- Do not commit secrets, real user code, or personal data.

## Reporting issues

Open an issue with:

- What you expected
- What happened
- OS, Python/Node versions
- `AI_PROVIDER` and model name (if relevant)
- Whether Ollama is running

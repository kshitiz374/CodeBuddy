# CodeBuddy Web

Next.js + TypeScript + Tailwind + Monaco Editor frontend for CodeBuddy.

## Quick start

```bash
cd apps/web
npm install
cp .env.example .env.local
# optional: API_BASE_URL=http://127.0.0.1:8000

npm run dev
```

Open http://localhost:3000

The app proxies `/api/*` to the FastAPI backend via Next.js rewrites
(`API_BASE_URL`, default `http://127.0.0.1:8000`).

## Pages

- `/` — Dashboard (counts, patterns, history, model status)
- `/debug` — Debug My Code (hint-first progressive reveal)
- `/explain` — Explain This
- `/mistakes` — Mistake Memory
- `/profile` — Learning profile editor

## Notes

- Monaco loads from CDN on first use in some environments; for fully offline demos,
  vendor Monaco locally if required.
- UI clearly shows whether the configured provider is local.

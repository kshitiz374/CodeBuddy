# CodeBuddy — Architecture & Implementation Plan

Hacktoberfest 2026 · "Build for a Friend"

## 1. Why this exists

A college friend learning DSA (C++, Python, Java) frequently gets stuck on debugging.
The pain is not "no answer exists" — it is not understanding **why** code fails.
CodeBuddy is a small local-first mentor tool: diagnose, hint, explain, fix, learn.

It is intentionally **not** a multi-agent AI platform. One product, one workflow, local data.

---

## 2. Product philosophy

```
Don't just give my friend the answer.
Help them understand why they are stuck.
```

### Progressive assistance levels

| Level | Name    | What the user gets                          |
|-------|---------|---------------------------------------------|
| 1     | Identify| Category of problem                         |
| 2     | Hint    | Point to the relevant part of the code      |
| 3     | Explain | Underlying programming concept              |
| 4     | Fix     | Corrected approach / code                   |
| 5     | Learn   | How to avoid the mistake next time          |

The UI must make it easy to stop at any level. Full solution is never the first output.

---

## 3. Target user (replaceable profile)

Example profile stored locally in `data/profile.json` (or SQLite):

- College student, beginner/intermediate
- Languages: C++, Python, Java
- Topics: arrays, linked lists, recursion, pointers
- Prefers simple explanations, hint-first
- No invented personal data about the real friend

Profile is user-editable via `PUT /api/profile`.

---

## 4. High-level architecture

```
┌─────────────────────────────┐
│  Next.js + TS + Tailwind    │
│  Monaco Editor              │
│  UI: Debug / Explain / ...  │
└──────────────┬──────────────┘
               │ HTTP JSON
┌──────────────▼──────────────┐
│  FastAPI + Pydantic         │
│  /api/debug /api/explain    │
│  /api/profile /api/mistakes │
│  /api/health /api/model/*   │
└──────┬──────────────┬───────┘
       │              │
┌──────▼──────┐ ┌─────▼──────────────┐
│ SQLite      │ │ AIProvider (ABC)   │
│ sessions,   │ │  ├─ LocalAIProvider│
│ mistakes,   │ │  │   (Ollama HTTP) │
│ profile     │ │  └─ MockProvider   │
└─────────────┘ │      (tests/demo)  │
                └────────────────────┘
```

### Key decisions

| Decision | Rationale |
|----------|-----------|
| FastAPI + SQLite | Simple, local, no cloud dependency |
| `AIProvider` interface | Swap Ollama model/runtime without touching business logic |
| MockProvider | App + tests run without Ollama installed |
| Deterministic static analysis | LLM is not the only judge; regex/AST-lite heuristics first |
| No code execution in MVP | Sandbox is hard to do safely on a weekend; static analysis + AI is enough |
| Data stays in `data/` on disk | Local-first privacy story is real, not marketing |

---

## 5. Backend layout

```
apps/api/
  app/
    main.py                 # FastAPI app, CORS, routers, lifespan
    core/
      config.py             # settings via pydantic-settings / env
      database.py           # SQLAlchemy engine/session
      security.py           # (optional) local auth stub — not required for MVP
    models/
      entities.py           # Session, Mistake, Profile tables
    schemas/
      debug.py              # DebugRequest, DebugResponse
      explain.py            # ExplainRequest, ExplainResponse
      profile.py            # Profile schemas
      mistakes.py           # Mistake schemas
      common.py             # Error envelope, HealthStatus
    api/
      routes_debug.py
      routes_explain.py
      routes_profile.py
      routes_mistakes.py
      routes_history.py
      routes_health.py
    services/
      ai/
        base.py             # AIProvider ABC
        ollama_provider.py  # LocalAIProvider
        mock_provider.py    # deterministic mock
        prompts.py          # system prompt + per-feature prompts
        factory.py          # select provider from config
      analysis/
        static_analysis.py  # language heuristics, error parsing
        language_map.py     # language normalization
      learning/
        profile_store.py
        mistake_memory.py   # similarity against past mistakes
        session_store.py
  tests/
    test_debug_api.py
    test_explain_api.py
    test_profile.py
    test_mistakes.py
    test_static_analysis.py
    test_provider.py
  requirements.txt
  pyproject.toml            # optional
```

---

## 6. Frontend layout

```
apps/web/
  app/
    layout.tsx              # sidebar + header (Local AI status)
    page.tsx                # Dashboard
    debug/page.tsx          # Debug My Code
    explain/page.tsx        # Explain This
    mistakes/page.tsx       # Mistake Memory + patterns
    profile/page.tsx        # Learning profile editor
  components/
    Sidebar.tsx
    Header.tsx
    CodeEditor.tsx          # Monaco wrapper
    ProgressiveSteps.tsx    # Identify → Hint → Concept → Fix → Learn
    ModelStatusBadge.tsx
    PatternBars.tsx
  lib/
    api.ts                  # typed fetch wrappers
    types.ts
```

---

## 7. API surface (MVP)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | API liveness |
| GET | `/api/model/status` | Ollama reachable? model name? provider type |
| POST | `/api/debug` | Full debug analysis |
| POST | `/api/hint` | Extra/next hint for an existing session |
| POST | `/api/explain` | Concept explanation |
| GET | `/api/history` | Recent sessions |
| GET | `/api/mistakes` | Mistake list + pattern counts |
| POST | `/api/mistakes` | Optionally record a mistake from a session |
| GET | `/api/profile` | Current learning profile |
| PUT | `/api/profile` | Update learning profile |

### Debug response (structured)

```json
{
  "problem": "...",
  "severity": "error",
  "location": "...",
  "explanation": "...",
  "hint": "...",
  "concept": "...",
  "fix": "...",
  "lesson": "...",
  "deterministic": {
    "source": "static_analysis|llm|both",
    "findings": ["..."],
    "compiler_output": null
  },
  "prior_mistake": {
    "exists": true,
    "summary": "...",
    "connection": "..."
  },
  "session_id": "..."
}
```

---

## 8. AI prompt contract

System prompt (always applied):

- You are CodeBuddy, a patient programming mentor.
- Prefer diagnosis → hint → concept → correct approach → corrected code → lesson.
- Never claim to have executed code unless the system did.
- Never invent compiler output.
- If info is insufficient, say what is missing.
- Adapt to the learning profile.
- Use prior mistake history only when relevant.

Implementation lives in `services/ai/prompts.py` so it can be tuned without touching routes.

---

## 9. Deterministic analysis (MVP)

Not a full compiler — practical heuristics:

1. **Language normalization**: `cpp`/`c++`/`cxx` → `cpp`, etc.
2. **Error message parsing**: extract file/line/token when present (g++, javac, Python traceback).
3. **Static patterns** (per language family):
   - C/C++: uninitialized pointer use (`->` after bare pointer decl), possible null deref patterns
   - Python: `IndentationError`, `NameError`, classic list/dict mistakes
   - Java: common beginner patterns where cheap to detect
4. **Code size / empty inputs**: reject empty code with a clear API error.
5. **No host execution** in MVP — documented limitation.

Deterministic findings are merged into the AI response as `deterministic.findings` and shown in the UI as "static analysis" vs "AI explanation".

---

## 10. Mistake memory

Stored fields:

- `topic` (e.g. Pointers)
- `problem_summary`
- `cause`
- `lesson`
- `language`
- `created_at`
- optional `session_id`

Dashboard shows **counts by topic** (bar chart). Copy must say these are records of encountered mistakes, not validated learning ability.

"Have I made this mistake before?" = simple keyword/tag overlap between current analysis topic and stored mistakes (no vector DB required for MVP). ChromaDB/FAISS only if retrieval quality becomes a real problem later.

---

## 11. Local-first & privacy

- Default inference: Ollama at `http://localhost:11434`, model from `MODEL_NAME`.
- `AI_PROVIDER=mock|ollama` (and room for future cloud providers clearly labeled).
- UI badge: `Local AI ●` when provider is local/mock-offline simulation; if cloud is configured later it must say so.
- Privacy copy in UI/README: "Your code stays on your machine when using local inference."
- Do **not** claim all configurations are private.
- Offline path: install app + pull model once → disconnect → debug locally.
- What requires internet: first install, `ollama pull`, optional model updates.

---

## 12. Security stance

- User code is untrusted input.
- MVP does **not** execute arbitrary user code on the host.
- If execution is added later: containers/sandbox, no network, CPU/mem/timeout limits, restricted FS, no host privileges.
- Do not fake compiler results when execution is disabled.

---

## 13. Development phases (incremental)

| Phase | Deliverable | Exit criteria |
|-------|-------------|---------------|
| 1 | Repo structure + docs skeleton + architecture | Files exist; plan reviewed |
| 2 | FastAPI skeleton, schemas, SQLite, health | `pytest` green for schema/db smoke |
| 3 | AIProvider + Ollama + Mock + prompts | Provider unit tests pass without Ollama |
| 4 | Debug/explain services + static analysis + mistake memory + profile | API tests pass |
| 5 | Next.js UI for all main pages | Manual walkthrough of workflow |
| 6 | History/profile/mistakes wired end-to-end | Data persists across restarts |
| 7 | UX polish, error states, offline notes | Checklist review |
| 8 | Full test run + docs + demo script | Definition of Done review |

Do not advance if the current phase is broken.

---

## 14. Testing strategy

- Backend: `pytest` + `httpx`/`fastapi.testclient`
- Provider tests use `MockProvider` (no network)
- Static analysis tests use known snippets
- API validation tests: empty code, bad language, profile update
- Frontend: manual QA for MVP; component tests optional later
- No fabricated benchmark numbers

---

## 15. Definition of Done (project)

- [x] Architecture plan (this doc)
- [x] Application runs locally (API + web build verified)
- [x] Local open-weight model path implemented (Ollama provider + configurable model)
- [x] User can submit code + language + error text
- [x] AI/debug analysis returns structured result
- [x] Hint-first progressive workflow in UI
- [x] Concept explanation works
- [x] Learning profile editable + used in prompts
- [x] Mistake history + pattern dashboard
- [x] Data stored locally (SQLite)
- [x] Clean UI
- [x] Error states handled
- [x] README complete
- [x] Offline demo path documented
- [ ] Friend has tested it (user must do this — no fabricated feedback)
- [ ] Feedback collected (real only)
- [ ] Demo video can be recorded from working app (script ready in `docs/DEMO.md`)
- [ ] Article can explain why open/local AI mattered (outline in `docs/ARTICLE_OUTLINE.md`)

### Environment status at implementation time

- Backend tests: **25 passed**
- Frontend: **`next build` succeeded**
- Ollama: **installed** (v0.35.0) with `qwen2.5-coder:7b` pulled
- `.env`: `AI_PROVIDER=ollama`, `MODEL_NAME=qwen2.5-coder:7b`
- Smoke test with real local model returned a mentor-style pointer-bug explanation
  (problem/hint/concept/lesson) plus static-analysis findings
- First Ollama request on this hardware took ~75s (model load); later calls are faster
- Friend feedback: still pending (must be real, not fabricated)

---

## 16. Environment notes (this machine)

- Python 3.14.3 available
- Node v24.18.0 available
- Ollama **not installed** in this environment at plan time
- Therefore: implement Ollama client properly, but default tests/demo use `MockProvider` until Ollama is installed and a model is pulled
- `.env.example` documents `MODEL_NAME` and `OLLAMA_BASE_URL`

Recommended models (configurable, not hardcoded as sole option):

- `qwen2.5-coder:7b` (coding-focused)
- `llama3.1:8b` (general)
- `phi3` (smaller machines)

---

## 17. Non-goals (MVP)

- Multi-agent orchestration
- VS Code extension
- Cloud SaaS
- RAG/vector store (until proven necessary)
- Sandboxed arbitrary code execution
- Gamified streaks that lie about learning science
- Invented friend testimonials or fake screenshots

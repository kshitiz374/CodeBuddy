# Demo Script (Hacktoberfest)

Record a short walkthrough. Do not fake UI or feedback.

## Setup on camera (brief)

1. Show `.env` with `AI_PROVIDER=mock` or `ollama`
2. Terminal 1: API (`uvicorn app.main:app --port 8000`)
3. Terminal 2: Web (`npm run dev`)
4. Open `http://localhost:3000`
5. Point to Local AI badge

## Story beat 1 — The friend problem

“CodeBuddy is for a friend learning DSA who gets stuck debugging. The goal is not another answer dump — it is helping them understand why the code is wrong.”

## Story beat 2 — Debug workflow

1. Open **Debug My Code**
2. Use the pointer demo (or paste the friend’s real stuck snippet after anonymizing)
3. Click **Analyze Code**
4. Show static analysis findings vs AI explanation labels
5. Reveal steps one by one: Problem → Why → Hint → Concept → Fix → Lesson
6. Save a mistake note
7. Open **Mistakes** and show the pattern bar

## Story beat 3 — Explain mode

Ask: “Explain recursion”
Show analogy + example + mini question.

## Story beat 4 — Why open/local AI

- Model is swappable via `MODEL_NAME`
- Works without cloud API keys (`AI_PROVIDER=mock` or Ollama)
- Data stays in local SQLite
- Be honest about model quality and limitations

## Story beat 5 — What is not done yet

- No arbitrary code execution in MVP
- Heuristic analysis is not a full compiler
- Friend feedback still pending (insert real quotes only)

## Recording tips

- Keep under 3–5 minutes
- Capture one full debug session without skipping the hint stage
- End on the privacy/local-first point

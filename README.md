CodeBuddy
Local-first AI coding companion — built for a friend who is learning programming and keeps getting stuck while debugging.

Don't just give my friend the answer. Help them understand why they are stuck.

CodeBuddy behaves like a patient coding mentor, not another generic chatbot:

Identify the problem
Hint first
Explain the concept
Show a corrected approach
Teach how to avoid the mistake next time
Why I built it for my friend
My friend is a college student learning DSA with C++, Python, and Java. They understand basic syntax, but compiler/runtime errors still slow them down. Asking people for help works — until those people are busy, or the answers arrive as finished code that gets copied without understanding.

CodeBuddy exists for that specific gap: structured help that stays on their machine, with a hint-first workflow that encourages thinking before revealing a fix.

This is intentionally a small tool for one real problem, not a multi-agent AI platform.

Features
Debug My Code — paste code + language + error/expected/actual behavior
Progressive assistance — unlock diagnosis → hint → concept → fix → lesson step by step
Explain This — concept explanations with analogy, example, steps, common mistake, mini question
Learning profile — local profile that personalizes explanations (level, languages, topics, style)
Mistake Memory — optional local log of mistakes + topic pattern dashboard
“Have I made this mistake before?” — compares new analysis with stored local history
Deterministic static analysis — language heuristics run before/independent of the LLM
Local-first AI — Ollama + configurable open-weight model; mock provider for offline/tests
Privacy-aware UI — shows local vs non-local provider status explicitly
Architecture
Next.js (UI)  →  FastAPI (API)  →  AIProvider interface
                         │              ├─ LocalAIProvider (Ollama)
                         │              └─ MockAIProvider (tests/offline)
                         └─ SQLite (sessions, mistakes, profile)
Layer	Tech
Frontend	Next.js, TypeScript, Tailwind, Monaco Editor
Backend	Python, FastAPI, Pydantic, SQLAlchemy
AI	Ollama HTTP API + configurable open-weight model
Database	SQLite (local file)
Details: docs/ARCHITECTURE.md

Open-source AI model
CodeBuddy does not hardcode a single model. Configure via .env:

AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=qwen2.5-coder:7b
Suggested open-weight options (pick what fits your machine):

qwen2.5-coder:7b — coding-focused
llama3.1:8b — general purpose
phi3 — smaller footprint
Pull a model once:

ollama pull qwen2.5-coder:7b
If you do not have Ollama, set AI_PROVIDER=mock — the full app still runs.

Why local inference matters here
Local/open models were useful for CodeBuddy specifically because:

Privacy — a friend’s learning code can stay on their own machine when using local inference.
Model flexibility — swap models by changing env vars, not by rewriting the app.
No cloud AI API required — the core debug/explain loop works without an OpenAI/Anthropic/Gemini key.
Cost — after the model download, inference does not require per-request API fees.
Customization — prompts, learning profile, and mentor behavior are editable in this repo.
Honest limits:

Local models can still be wrong, slow, or inconsistent on a small laptop.
“Local inference” is not the same as “private under every configuration.”
If a cloud provider is added later, the UI/docs must label it clearly.
Installation
Prerequisites
Python 3.11+ (developed/tested here with Python 3.14)
Node.js 18+ (developed/tested here with Node 24)
Optional: Ollama for local open-weight models
1) Clone and configure
git clone <your-repo-url> codebuddy
cd codebuddy
cp .env.example .env
2) Backend
cd apps/api
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
API docs: http://127.0.0.1:8000/docs

3) Frontend
cd apps/web
npm install
npm run dev
Open http://localhost:3000

4) Local model (recommended for the real mentor experience)
# Windows example path after winget install
ollama pull qwen2.5-coder:7b
Then set in .env (no BOM — save as plain UTF-8):

AI_PROVIDER=ollama
MODEL_NAME=qwen2.5-coder:7b
Restart the API. Check GET /api/model/status — it should say the model was found.

This machine’s smoke test used qwen2.5-coder:7b via Ollama successfully. First request loads the model (can take ~1 minute on modest hardware); later requests are faster.

Running locally (offline path)
Internet
   ↓
Download application + pull model once
   ↓
Disconnect internet
   ↓
Run CodeBuddy (API + web)
   ↓
Debug code locally
What requires internet:

Installing Python/Node packages and pulling the Ollama model (first time)
Optional Monaco CDN load (vendor it locally if you need a fully air-gapped UI)
What does not:

Using an already-pulled local model for debug/explain
SQLite history, profile, and mistake memory
Demo scenario
Submit this C++ snippet in Debug My Code:

struct Node {
    int data;
    Node* next;
};

int main() {
    Node* head;
    head->data = 10;
    return 0;
}
A good CodeBuddy session looks like:

Problem:
head does not point to a valid Node.

Hint:
Before accessing head->data, ask yourself:
"What object does head actually point to?"

Concept:
Pointers and dynamic memory allocation

Correct approach:
Allocate/create the node before dereferencing the pointer.

Lesson learned:
A pointer stores an address. It does not automatically create the object.
That story — understanding over answer-dumping — is the product.

Screenshots
No fake screenshots are shipped in this repository. Record real UI captures after you run the app locally and add them under screenshots/.

Suggested shots:

Dashboard with model status
Debug form + progressive steps
Mistake Memory pattern bars
Profile editor
Demo checklist (for your Hacktoberfest video)
Show the friend profile / problem statement
Start API with AI_PROVIDER=mock or ollama
Debug the pointer snippet
Reveal steps one at a time (do not jump to the fix)
Show Mistake Memory after saving a note
Toggle .env provider settings to explain model flexibility
Mention what stays local and what does not
Privacy
Local inference (Ollama/mock): your code is processed on your machine by the configured local provider.
History/profile/mistakes: stored in local SQLite under data/.
Not a blanket guarantee: if you later configure a cloud AI provider, those requests leave your machine unless your provider is otherwise private.
CodeBuddy does not upload code anywhere by default.
API overview
Method	Path	Purpose
GET	/api/health	API health
GET	/api/model/status	Provider/model/privacy status
POST	/api/debug	Structured debugging analysis
POST	/api/hint	Progressive level from a session
POST	/api/explain	Concept explanation
GET	/api/history	Recent sessions
GET/PUT	/api/profile	Learning profile
GET/POST	/api/mistakes	Mistake memory
Interactive docs: /docs

Tests
cd apps/api
python -m pytest -q
Frontend checks:

cd apps/web
npm run lint
npm run typecheck
npm run build
Current backend suite covers:

Debug/explain API happy paths
Validation errors
Provider failure shape
Mistake dashboard + prior-mistake similarity
Static analysis heuristics
Profile updates
History endpoints
Limitations
MVP does not execute arbitrary user code (no sandboxed run step yet)
Deterministic analysis is heuristic, not a full compiler/linter suite
Local model quality depends on hardware and model choice
Monaco editor may need CDN access unless vendored
Mistake similarity is simple keyword/topic overlap, not semantic RAG
No fabricated friend testimonials or benchmark numbers are included — get real feedback
Future improvements
Sandboxed C++/Python execution (only with strong isolation)
Better error parsing from real g++/javac/CPython output
Optional semantic retrieval for mistake memory (Chroma/FAISS) if it actually helps
VS Code extension
Richer dashboard trend charts (honestly labeled)
Model fallbacks and latency settings
Repository structure
codebuddy/
├── apps/
│   ├── web/          # Next.js UI
│   └── api/          # FastAPI backend
├── docs/             # Architecture & implementation plan
├── screenshots/      # Real screenshots only
├── .env.example
├── CONTRIBUTING.md
├── LICENSE
└── README.md
Contribution guide
See CONTRIBUTING.md.

Short version: keep it small, keep it local-first, keep hints progressive, do not invent data.

License
MIT — see LICENSE.

What my friend said
Pending. After you hand CodeBuddy to the real friend, record their honest answers here (did it solve the problem, was the explanation understandable, would they use it again). Do not fabricate a review.

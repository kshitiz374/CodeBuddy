# Offline / Local-First Guide

## What you need once (internet)

1. Install Python + Node dependencies
2. Install Ollama and pull one model

```bash
ollama pull qwen2.5-coder:7b
```

3. Start API + web app while online

## What you can do offline

- Debug and explain code using the pulled local model
- View dashboard, history, profile, mistakes
- Edit learning profile
- Record mistake notes

## What still needs internet (optional)

- Updating packages / pulling different models
- First-time Monaco editor CDN load (vendor locally if required)

## Provider modes

| `AI_PROVIDER` | Behavior |
|---------------|----------|
| `ollama` | Local open-weight model via Ollama |
| `mock` | Offline deterministic mentor stub (great for tests/demos without GPU) |

Mock mode is **not** a substitute for a real local model in quality, but it keeps the product runnable everywhere.

## Privacy

With `AI_PROVIDER=ollama`, code is sent only to your local Ollama process.
With a future cloud provider, code would leave your machine — UI must say so.

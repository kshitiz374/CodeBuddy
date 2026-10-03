# Hacktoberfest Article Outline

> Fill this in after you have real friend feedback and real screenshots.
> Do not invent quotes, metrics, or benchmark numbers.

## What I Built

CodeBuddy is a local-first AI coding companion for a friend learning programming.
It focuses on debugging and concept explanations with a hint-first mentor workflow.

## The Problem

My friend often asked for debugging help. The hard part was not finding an answer online —
it was understanding why the code failed and how to avoid the same mistake later.

## Why Open AI / Local Inference?

- Keep the friend’s code local when using Ollama
- Swap models with config, not rewrites
- Run without closed AI API keys
- Tune prompts and mentor behavior in the open

Be specific: open-weight models were useful here for privacy, flexibility, and offline demos —
not because they are magically “better” at everything.

## What I Learned

- Local inference ops (pull model, timeouts, failure states)
- Prompt design for progressive assistance
- Separating deterministic analysis from AI explanation
- Building for a real user instead of a hypothetical persona
- Saying “the model may be wrong” instead of overclaiming

## What My Friend Said

**[Pending real feedback]**

Ask:

1. Did this solve your original problem?
2. Was the explanation understandable?
3. Did the hint-first approach help?
4. Was anything confusing?
5. What would you change?
6. Would you actually use it again?

Include criticism verbatim. That is more valuable than a polished fake review.

## Screenshots

**[Add real screenshots only]**

## Links

- Repo
- Live demo notes (local)
- Architecture doc

# API Design

Base URL (local): `http://127.0.0.1:8000`

All error responses use:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": {}
  }
}
```

## GET /api/health

```json
{ "status": "ok", "provider": "mock", "model_name": null, "detail": "CodeBuddy API is running" }
```

## GET /api/model/status

Returns provider, model name, availability, privacy note, and configured Ollama URL.

## POST /api/debug

Request:

```json
{
  "code": "Node* head;\\nhead->data = 10;",
  "language": "cpp",
  "error_message": "Segmentation fault",
  "expected_behavior": "set data",
  "actual_behavior": "crash",
  "hint_level": "learn",
  "include_prior_mistakes": true
}
```

Response includes:

- `problem`, `severity`, `location`
- `explanation`, `hint`, `concept`, `fix`, `lesson`
- `deterministic.findings[]`, `deterministic.executed=false`
- `prior_mistake.exists` + connection text when a similar local mistake exists
- `session_id`, `provider`, `model_name`

## POST /api/hint

```json
{ "session_id": "...", "next_level": "hint" }
```

Levels: `hint`, `explain`, `fix`, `learn`.

## POST /api/explain

```json
{ "query": "Explain recursion", "language": "python", "depth": "standard" }
```

Response: `concept`, `simple_explanation`, `analogy`, `example_code`, `step_by_step`, `common_mistake`, `mini_question`.

## GET /api/profile · PUT /api/profile

Profile fields: `name`, `level`, `languages[]`, `topics[]`, `preferred_explanation`, `hint_first`.

## GET /api/mistakes · POST /api/mistakes

Dashboard returns `total`, `patterns[]`, `note`, `items[]`.

POST records:

```json
{
  "topic": "Pointers",
  "problem_summary": "...",
  "cause": "...",
  "lesson": "...",
  "language": "C++",
  "session_id": "optional"
}
```

## GET /api/history

Recent debug + explain sessions for the dashboard.

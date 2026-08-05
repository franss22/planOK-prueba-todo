# PlanOK Todo API

Lean backend plan for a Todo app.

## What We Are Building

- Django + Django REST Framework API for tasks
- Task report endpoint powered by LangChain + Grok

## Task Object

- `id`
- `title`
- `content`
- `completed` (bool)
- `created_at`

## API Direction

- `GET /api/v1/tasks/`
- `POST /api/v1/tasks/`
- `GET /api/v1/tasks/{id}/`
- `PATCH /api/v1/tasks/{id}/`
- `DELETE /api/v1/tasks/{id}/`
- `POST /api/v1/tasks/report/`

## Quick Start

```bash
uv sync
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py runserver
```

## Build Order

1. Finalize `Task` model and migrations.
2. Add serializer + viewset + router.
3. Add report service (LangChain + Grok).
4. Add basic tests for CRUD and report endpoint.

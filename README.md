# PlanOK Todo App

A small full-stack todo application with a Django REST API, a React/Vite frontend, PostgreSQL, and Docker Compose for local development.

## What is in this repo

- api/: Django + DRF backend
  - config/: project settings and URL wiring
  - tasks/: task model, serializer, views, URLs, and report generation service
  - manage.py: Django entrypoint
- frontend/: React + Vite app
  - src/: UI components, API client, and app entry point
- docker-compose.yml: local orchestration for api, frontend, and postgres

## Local development

### 1. Environment setup

Copy the API env example and adjust values if needed:

```bash
cp api/.env.example .env
```

### 2. Start the stack

```bash
docker compose up --build -d
```

### 3. Run database migrations

The API container is configured to run migrations on startup, but you can also run them manually:

```bash
docker compose exec api uv run python manage.py migrate
```

### 4. Seed demo data

```bash
docker compose exec api uv run python manage.py seed_tasks
```

### 5. Open the app

- Frontend: http://localhost:3000
- API root: http://localhost:8000/api/v1/
- Tasks endpoint: http://localhost:8000/api/v1/tasks/

## Where the important code lives

- Frontend app entry: frontend/src/App.jsx
- Frontend API client: frontend/src/api.js
- Backend routes: api/tasks/urls.py
- Backend task views: api/tasks/views.py
- Backend task serializer: api/tasks/serializers.py
- Backend task model: api/tasks/models.py
- Docker Compose config: docker-compose.yml

## Data flow

### Task CRUD flow

1. The React app loads tasks from the API client in frontend/src/api.js.
2. The API client calls Django endpoints under /api/v1/tasks/.
3. Django uses the TaskViewSet and TaskSerializer to read/write task data.
4. Task data is stored in PostgreSQL through Django ORM.

### Report generation flow

1. The frontend opens the report modal and sends a prompt to the backend.
2. The API endpoint /api/v1/tasks/report/ receives the request.
3. The view builds a payload from the current tasks and calls the Grok service.
4. The backend returns a generated report payload, which the frontend can display.

## Backend API shape

The backend currently exposes:

- GET /api/v1/tasks/
- POST /api/v1/tasks/
- GET /api/v1/tasks/:id/
- PATCH /api/v1/tasks/:id/
- DELETE /api/v1/tasks/:id/
- POST /api/v1/tasks/report/

## Notes

- The frontend is currently using the API client for task CRUD and report generation instead of relying on local mock state.
- The API environment file is expected at .env at the repository root.
- If you need to inspect logs, use:

```bash
docker compose logs -f api
```

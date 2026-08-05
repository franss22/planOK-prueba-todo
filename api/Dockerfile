FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy project files first so packaging metadata is available during build.
COPY pyproject.toml uv.lock .python-version README.md ./
COPY . .

RUN uv sync --frozen --no-dev --no-install-project

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

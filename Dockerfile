# ==========================================
# ETAPA 1: API (Django + DRF)
# ==========================================
FROM python:3.11-slim AS api-stage

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/

# ==========================================
# ETAPA 2: FRONTEND (React)
# ==========================================
FROM node:20-alpine AS frontend-stage

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
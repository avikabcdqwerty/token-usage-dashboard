# syntax=docker/dockerfile:1.4

# ---- Base Python image ----
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- System dependencies ----
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        && rm -rf /var/lib/apt/lists/*

# ---- Python dependencies ----
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---- Backend image ----
FROM base as backend

WORKDIR /app/backend

COPY backend/ ./backend/
COPY backend/models/ ./backend/models/
COPY backend/routes/ ./backend/routes/
COPY backend/services/ ./backend/services/
COPY backend/middleware/ ./backend/middleware/
COPY backend/db/ ./backend/db/
COPY backend/docs/ ./backend/docs/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---- Frontend image ----
FROM base as frontend

WORKDIR /app/frontend

COPY frontend/ ./frontend/

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# ---- Final multi-service image (for docker-compose or build target) ----
# Usage: docker build --target backend -t token-usage-backend .
#        docker build --target frontend -t token-usage-frontend .

# ---- Requirements file example ----
# (This section is not part of the Dockerfile, but requirements.txt should include:)
# fastapi
# uvicorn[standard]
# streamlit
# plotly
# httpx
# psycopg2-binary
# sqlalchemy
# python-jose
# streamlit-authenticator
# loguru
# pytest
# black
# isort
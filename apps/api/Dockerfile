FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_RELOAD=false

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 appuser

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
COPY scripts ./scripts

RUN pip install --upgrade pip \
    && pip install . \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
  CMD curl -f http://localhost:8000/health || exit 1

# Migrations then uvicorn (no host venv required)
CMD ["python", "scripts/entrypoint.py"]

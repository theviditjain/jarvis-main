# ── JARVIS Runtime — Dockerfile ───────────────────────────────────────────────
# Multi-stage build:
#   builder  — installs dependencies with Poetry
#   runtime  — production-ready slim image

ARG PYTHON_VERSION=3.12
ARG POETRY_VERSION=1.8.3

# ── Stage 1: Builder ───────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS builder

ARG POETRY_VERSION=1.8.3

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Configure Poetry to create virtual env inside project
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy dependency files first (Docker layer caching)
COPY pyproject.toml poetry.lock* ./

# Install production dependencies only
RUN poetry install --only=main --no-root && rm -rf ${POETRY_CACHE_DIR}

# ── Stage 2: Runtime ────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

LABEL maintainer="Vidit Jain <team@jarvis.dev>"
LABEL org.opencontainers.image.title="JARVIS AI Runtime"
LABEL org.opencontainers.image.description="AI reasoning engine for indexed code repositories"
LABEL org.opencontainers.image.version="0.1.0"

# Create non-root user for security
RUN groupadd --gid 1001 jarvis && \
    useradd --uid 1001 --gid jarvis --shell /bin/bash --create-home jarvis

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY --chown=jarvis:jarvis . .

# Create logs directory
RUN mkdir -p /app/logs && chown jarvis:jarvis /app/logs

# Switch to non-root user
USER jarvis

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

EXPOSE 8000

# Run with Uvicorn (main.py at repo root, imports from src/ via PYTHONPATH)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

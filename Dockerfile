# ========== ADVAITAM DJANGO DOCKERFILE ==========
# Multi-stage build: builder stage compiles dependencies, final stage is lean runtime image.
# Usage:
#   docker build -t advaitam .
#   docker run --env-file .env -p 8000:8000 advaitam
#
# For local dev with database + Redis, use docker-compose instead:
#   docker compose up

# ── Stage 1: Builder — install compiled dependencies ──────────────────────────
FROM python:3.12-slim AS builder

# Install OS-level build dependencies (needed to compile psycopg2, argon2-cffi)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (layer cache — only re-installs when requirements change)
COPY requirements-prod.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements-prod.txt


# ── Stage 2: Runtime — lean final image ──────────────────────────────────────
FROM python:3.12-slim AS runtime

# Runtime-only OS deps (libpq for psycopg2, no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root app user (never run as root in production)
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy project source
COPY --chown=appuser:appuser . .

# Create required directories
RUN mkdir -p logs staticfiles media

# Switch to non-root user
USER appuser

# Collect static files (requires SECRET_KEY env var at build time if USE_S3=False)
# Skipped here — run `python manage.py collectstatic` in deploy pipeline instead

EXPOSE 8000

# Health check — Docker daemon will mark container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fs http://localhost:8000/health/ || exit 1

# Default command: run Gunicorn using gunicorn.conf.py
CMD ["gunicorn", "--config", "gunicorn.conf.py", "webProject.wsgi:application"]


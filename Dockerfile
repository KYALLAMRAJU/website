# ========== ADVAITAM DJANGO DOCKERFILE ==========
# change this line according to your company (rename to your project)
# Multi-stage build: builder stage compiles dependencies, final stage is lean runtime image.
# Usage:
#   docker build -t advaitam .
#   # change this line according to your company (update image name)
#   docker run --env-file .env -p 8000:8000 advaitam
#   # change this line according to your company (update image name and port)
#
# For local dev with database + Redis, use docker-compose instead:
#   docker compose up

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# change this line according to your company (update Python version if needed)
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# change this line according to your company (update to your requirements file)
COPY requirements-prod.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements-prod.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
# change this line according to your company (update Python version if needed)
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root app user (never run as root in production)
# change this line according to your company (update username if needed)
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder /install /usr/local

COPY --chown=appuser:appuser . .

# change this line according to your company (add/remove directories as needed)
RUN mkdir -p logs staticfiles media

USER appuser

# change this line according to your company (update port if needed)
EXPOSE 8000

# change this line according to your company (update health check URL)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fs http://localhost:8000/health/ || exit 1

# change this line according to your company (update to your project name in wsgi:application)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "webProject.wsgi:application"]

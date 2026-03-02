# ========== ADVAITAM — MAKEFILE ==========
# Standard developer shortcuts. Run `make help` to see all targets.
#
# Usage:
#   make             → show help
#   make run         → start dev server
#   make test        → run all tests
#   make lint        → run ruff linter + formatter check
#   make migrate     → apply database migrations
#   make deploy      → trigger CI/CD deploy (push to main)

# ── Configuration ─────────────────────────────────────────────────────────────
PYTHON     := python
MANAGE     := $(PYTHON) manage.py
PIP        := pip
APP        := webapp
PORT       := 8000

.DEFAULT_GOAL := help

# ── Help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  Advaitam — Available Make Targets"
	@echo "  ─────────────────────────────────────────────────────────"
	@echo "  Dev Server"
	@echo "    make run           Start Django dev server on :$(PORT)"
	@echo "    make shell         Open Django shell"
	@echo "    make dbshell       Open PostgreSQL shell via Django"
	@echo ""
	@echo "  Database"
	@echo "    make migrate       Run pending migrations"
	@echo "    make makemigrations  Create new migration files"
	@echo "    make showmigrations  Show migration status"
	@echo "    make resetdb       ⚠️  Drop + recreate SQLite dev DB"
	@echo ""
	@echo "  Static Files"
	@echo "    make static        Run collectstatic"
	@echo ""
	@echo "  Testing"
	@echo "    make test          Run all tests (Django test runner)"
	@echo "    make test-cov      Run tests with coverage report"
	@echo "    make pytest        Run tests via pytest"
	@echo ""
	@echo "  Code Quality"
	@echo "    make lint          Run ruff linter (check only)"
	@echo "    make lint-fix      Run ruff linter + auto-fix"
	@echo "    make format        Run ruff formatter (check only)"
	@echo "    make format-fix    Run ruff formatter + auto-fix"
	@echo "    make check         Run lint + format checks"
	@echo ""
	@echo "  Deployment"
	@echo "    make deploy        Push to main → triggers GitHub Actions CI/CD"
	@echo "    make health        Check /health/ endpoint on localhost"
	@echo ""
	@echo "  Dependencies"
	@echo "    make install       Install dev dependencies (requirements.txt)"
	@echo "    make install-prod  Install prod dependencies (requirements-prod.txt)"
	@echo "    make freeze        Freeze current env to requirements.txt"
	@echo ""
	@echo "  Docker"
	@echo "    make docker-up     docker compose up (dev environment)"
	@echo "    make docker-down   docker compose down"
	@echo "    make docker-build  Rebuild Docker image"
	@echo "    make docker-logs   Tail app logs in Docker"
	@echo ""
	@echo "  Maintenance"
	@echo "    make backup        Run backup.sh (manual DB backup → S3)"
	@echo "    make logs          Tail Django log file"
	@echo "    make clean         Remove __pycache__, .pyc files, test artifacts"
	@echo "  ─────────────────────────────────────────────────────────"
	@echo ""

# ── Dev Server ────────────────────────────────────────────────────────────────
.PHONY: run
run:
	$(MANAGE) runserver $(PORT)

.PHONY: shell
shell:
	$(MANAGE) shell

.PHONY: dbshell
dbshell:
	$(MANAGE) dbshell

# ── Database ──────────────────────────────────────────────────────────────────
.PHONY: migrate
migrate:
	$(MANAGE) migrate --noinput

.PHONY: makemigrations
makemigrations:
	$(MANAGE) makemigrations

.PHONY: showmigrations
showmigrations:
	$(MANAGE) showmigrations

.PHONY: resetdb
resetdb:
	@echo "⚠️  This will DELETE your local SQLite database! Ctrl+C to cancel..."
	@sleep 3
	rm -f db.sqlite3
	$(MANAGE) migrate --noinput
	@echo "✅ Database reset complete"

# ── Static Files ──────────────────────────────────────────────────────────────
.PHONY: static
static:
	$(MANAGE) collectstatic --noinput

# ── Testing ───────────────────────────────────────────────────────────────────
.PHONY: test
test:
	$(MANAGE) test $(APP) --verbosity=2

.PHONY: test-cov
test-cov:
	coverage run --source=$(APP) $(MANAGE) test $(APP)
	coverage report -m
	coverage html
	@echo "✅ Coverage report generated in htmlcov/"

.PHONY: pytest
pytest:
	pytest --tb=short -q

# ── Code Quality ──────────────────────────────────────────────────────────────
.PHONY: lint
lint:
	ruff check .

.PHONY: lint-fix
lint-fix:
	ruff check . --fix

.PHONY: format
format:
	ruff format . --check

.PHONY: format-fix
format-fix:
	ruff format .

.PHONY: check
check: lint format
	@echo "✅ All code quality checks passed"

# ── Deployment ────────────────────────────────────────────────────────────────
.PHONY: deploy
deploy:
	@echo "Pushing to main branch → triggers GitHub Actions CI/CD..."
	git push origin main

.PHONY: health
health:
	curl -s http://localhost:$(PORT)/health/ | python -m json.tool

# ── Dependencies ──────────────────────────────────────────────────────────────
.PHONY: install
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: install-prod
install-prod:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-prod.txt

.PHONY: freeze
freeze:
	$(PIP) freeze > requirements.txt
	@echo "✅ requirements.txt updated"

# ── Docker ────────────────────────────────────────────────────────────────────
.PHONY: docker-up
docker-up:
	docker compose up

.PHONY: docker-up-d
docker-up-d:
	docker compose up -d

.PHONY: docker-down
docker-down:
	docker compose down

.PHONY: docker-build
docker-build:
	docker compose build --no-cache

.PHONY: docker-logs
docker-logs:
	docker compose logs -f web

# ── Maintenance ───────────────────────────────────────────────────────────────
.PHONY: backup
backup:
	bash backup.sh

.PHONY: logs
logs:
	tail -f logs/django.log

.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Cleaned up cache and artifact files"


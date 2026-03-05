# Contributing to webProject

Thank you for contributing! This guide covers branching strategy, commit conventions, and how to get a local dev environment running.

---

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Branching Strategy](#branching-strategy)
- [Commit Conventions](#commit-conventions)
- [Code Quality Standards](#code-quality-standards)
- [Pull Request Process](#pull-request-process)
- [Running Tests](#running-tests)
- [Environment Setup](#environment-setup)

---

## Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/KYALLAMRAJU/webProject.git
cd webProject

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Install dev dependencies
pip install -r requirements.txt

# 4. Set up environment file
cp .env.example .env
# Edit .env with your own values

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (for /admin/)
python manage.py createsuperuser

# 7. Start dev server
python manage.py runserver
# or: make run
```

---

## Branching Strategy

```
main                  ← production-ready code only (protected)
  └── feature/xyz     ← new features
  └── fix/bug-name    ← bug fixes
  └── chore/task      ← non-code changes (docs, deps, config)
  └── hotfix/urgent   ← emergency production fixes
```

### Rules
- **Never push directly to `main`** — always open a PR
- Branch from `main`, merge back to `main` via PR
- Delete branches after merging
- PRs require CI (lint + tests) to pass before merge

### Branch Naming Examples
```
feature/add-user-profile
feature/celery-task-queue
fix/cors-middleware-missing
fix/health-check-cache-error
chore/upgrade-django-5.3
chore/update-docs
hotfix/sql-injection-patch
```

---

## Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>

[optional body]

[optional footer: closes #issue-number]
```

### Types
| Type | When to use |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Dependency upgrades, config, tooling |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `refactor` | Code change that doesn't fix a bug or add a feature |
| `style` | Code formatting (no logic change) |
| `perf` | Performance improvement |
| `security` | Security fix (used by Dependabot PRs) |

### Examples
```
feat(auth): add JWT token refresh endpoint
fix(cors): add CorsMiddleware to MIDDLEWARE list
chore(deps): upgrade Django 5.2.9 → 5.2.11
docs(deploy): add nginx.conf to 13-NEW-FILES folder
test(views): add tests for contact_view
security(deps): bump requests from 2.32.3 to 2.32.4
```

---

## Code Quality Standards

This project uses **ruff** for linting and formatting.

```bash
# Check for lint errors
make lint
# or: ruff check .

# Auto-fix lint errors
make lint-fix
# or: ruff check . --fix

# Check formatting
make format
# or: ruff format . --check

# Auto-format code
make format-fix
# or: ruff format .

# Run both lint + format check (same as CI)
make check
```

**Rules enforced** (see `ruff.toml`):
- `E`, `W` — pycodestyle errors/warnings
- `F` — pyflakes (undefined names, unused imports)
- `I` — isort (import ordering)
- `UP` — pyupgrade (modern Python syntax)
- `B` — bugbear (common bugs)
- `DJ` — Django-specific checks

**Line length**: 100 characters
**Quote style**: double quotes

> ⚠️ CI will fail if ruff check or ruff format check fails. Run `make check` before pushing.

---

## Pull Request Process

1. **Create a branch** from `main`
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** and commit with conventional commit messages

3. **Run quality checks locally** before pushing:
   ```bash
   make check      # lint + format
   make pytest     # run tests
   ```

4. **Push and open a PR**:
   ```bash
   git push origin feature/my-new-feature
   ```
   Then open a PR on GitHub against `main`.

5. **CI runs automatically** (lint → test → deploy.check):
   - Job 1: `ruff check` + `ruff format --check`
   - Job 2: `pytest` + `manage.py check --deploy`
   - Job 3: Deploy (only on merge to `main`)

6. **PR is reviewed and merged** — CI must be green ✅

7. **Delete the branch** after merging

---

## Running Tests

```bash
# Run all tests via pytest
make pytest
# or: pytest

# Run with coverage report
make test-cov
# or: pytest --cov=webapp --cov-report=html

# Run a single test file
pytest webapp/tests/test_login_view.py -v

# Run a specific test
pytest webapp/tests/test_login_view.py::test_login_success -v

# Run Django test runner (alternative)
make test
# or: python manage.py test webapp
```

**Test files** are in `webapp/tests/`:
- `conftest.py` — shared fixtures (test users, authenticated client)
- `test_login_view.py` — login, auth, session tests
- `test_claude.py` — Claude AI integration tests (uses mocking)

---

## Environment Setup

### Option 1 — Local Python (simplest)
```bash
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### Option 2 — Docker (mirrors production)
```bash
cp .env.example .env
docker compose up
# Django runs on http://localhost:8000
# PostgreSQL on port 5432
# Redis on port 6379
```

### Option 3 — Makefile shortcuts
```bash
make run          # start dev server
make migrate      # apply migrations
make shell        # Django shell
make docker-up    # docker compose up -d
make docker-down  # docker compose down
```

---

## Questions?

Open an issue on GitHub or contact the maintainer directly.


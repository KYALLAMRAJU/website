# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `.env.example` — copy-paste template for new developer onboarding
- `CHANGELOG.md` — this file
- `CONTRIBUTING.md` — contributor guide with branching strategy and commit conventions
- `SECURITY.md` — responsible disclosure policy
- `nginx.conf` — production Nginx reverse proxy configuration
- `corsheaders.middleware.CorsMiddleware` wired into `MIDDLEWARE` in `settings.py` (bug fix — was installed but never active)
- DRF throttle classes (`AnonRateThrottle` 60/min, `UserRateThrottle` 300/min) in `REST_FRAMEWORK` settings
- `deploy/13-NEW-FILES/` documentation folder — detailed docs for all newly added files

### Fixed
- **CORS bug**: `django-cors-headers` was installed and configured but `CorsMiddleware` was missing from `MIDDLEWARE`, so CORS headers were never actually sent. Now fixed.

---

## [1.3.0] — 2026-03-01

### Added
- Content-Security-Policy (CSP) headers via `django-csp 3.8`
- Sentry error tracking with `DjangoIntegration` + `LoggingIntegration`
- `ruff` linter added as Job 1 gate in GitHub Actions CI pipeline
- Zero-downtime deploy: switched from `systemctl restart` to `systemctl reload`
- `dependabot.yml` — daily automated security scanning on `requirements-prod.txt`

### Changed
- `psycopg2-binary` → `psycopg2` (compiled) in `requirements-prod.txt`
- Django 5.2.8 → 5.2.9
- Gunicorn 22.0.0 → 23.0.0
- Requests 2.32.3 → 2.32.4

### Fixed
- 4 CVEs resolved in dependency upgrades

---

## [1.2.0] — 2026-02-22

### Added
- `backup.sh` — daily automated PostgreSQL backup to S3 with 30-day retention
- `docker-compose.yml` with full PostgreSQL 16 + Redis 7 local dev stack
- Multi-stage `Dockerfile` (builder + lean runtime, non-root user)
- Redis cache + session support in `settings.py` (auto-detects `REDIS_URL`)
- `LOGGING` configuration: rotating file handler, 15 MB / 10 backups
- `webapp/services/claude_service.py` — Anthropic Claude AI service layer
- `webapp/tests/` folder with `conftest.py`, `test_login_view.py`, `test_claude.py`
- `pytest.ini` and `pytest-django` integration

### Changed
- Local dev database switched to SQLite (no PostgreSQL setup needed in dev)
- Production database switched to PostgreSQL with `CONN_MAX_AGE=600` connection pooling

---

## [1.1.0] — 2026-02-10

### Added
- AWS SES email backend for production (console backend for dev)
- `HSTS`, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` for production
- `drf-spectacular` Swagger + ReDoc API documentation (dev-only URLs)
- `djangorestframework-simplejwt` JWT authentication endpoints
- `webapp/custompermission.py` — custom DRF permission class
- `webapp/pagination.py` — `PageNumberPagination` + `CursorPagination` classes
- `webapp/storages.py` — `StaticStorage` + `MediaStorage` for S3 + CloudFront
- `gunicorn.conf.py` tuned for `t4g.micro` (2 workers × 2 threads, preload_app)

---

## [1.0.0] — 2026-01-20

### Added
- Initial Django 5 project scaffold
- `webapp` app with `models.py`, `views.py`, `urls.py`, `forms.py`, `serializers.py`
- Django REST Framework (DRF) with `APIView`, CBVs, `ViewSet`, `ModelViewSet`
- `admin.py` — all models registered in Django admin
- `migrations/` — initial database schema
- `webProject/settings.py` — dev/prod split using `django-environ`
- `.gitignore` — protects `.env`, `db.sqlite3`, `staticfiles/`, `logs/`
- `Makefile` with 30+ developer shortcuts
- `.github/workflows/deploy.yml` — 3-job CI/CD: lint → test → deploy to EC2
- `deploy.sh` — automated EC2 deployment script
- `static/` — CSS, JS, images, audio, books (PDFs)
- `templates/` — HTML templates for all pages

---

[Unreleased]: https://github.com/KYALLAMRAJU/webProject/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/KYALLAMRAJU/webProject/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/KYALLAMRAJU/webProject/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/KYALLAMRAJU/webProject/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/KYALLAMRAJU/webProject/releases/tag/v1.0.0


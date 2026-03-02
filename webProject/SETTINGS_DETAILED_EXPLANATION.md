# 🚀 DJANGO SETTINGS.PY — COMPLETE LINE-BY-LINE EXPLANATION
## Advaitam Project · Updated March 1, 2026 · Matches actual settings.py (486 lines)

---

## TABLE OF CONTENTS
1.  [Architecture Overview & Deployment Pipeline](#1-architecture-overview)
2.  [Imports & Environment Setup](#2-imports--environment-setup)
3.  [DJANGO_ENV — How Dev vs Production is Detected](#3-django_env--dev-vs-production-detection)
4.  [Paths — BASE_DIR, TEMPLATE_DIR, STATIC_DIR](#4-paths)
5.  [SECRET_KEY](#5-secret_key)
6.  [DEBUG Mode](#6-debug-mode)
7.  [USE_S3 Flag](#7-use_s3-flag)
8.  [ALLOWED_HOSTS](#8-allowed_hosts)
9.  [CSRF_TRUSTED_ORIGINS](#9-csrf_trusted_origins)
10. [ANTHROPIC_API_KEY & CLOUDFRONT_SECRET](#10-anthropic_api_key--cloudfront_secret)
11. [INSTALLED_APPS — Including Conditional storages + csp](#11-installed_apps)
12. [MIDDLEWARE — Including Conditional WhiteNoise + CSPMiddleware](#12-middleware)
13. [Templates & Context Processors](#13-templates--context-processors)
14. [WSGI Application](#14-wsgi-application)
15. [Database — SQLite (dev) vs PostgreSQL (prod)](#15-database-configuration)
16. [Password Hashers](#16-password-hashers)
17. [Password Validators](#17-password-validators)
18. [Internationalization](#18-internationalization)
19. [Static & Media Files — Local vs S3/CloudFront](#19-static--media-files)
20. [Auth & Session Settings](#20-auth--session-settings)
21. [Email — Console (dev) vs AWS SES (prod)](#21-email-configuration)
22. [CSRF & Security Settings](#22-csrf--security-settings)
23. [Production Security Block (if not DEBUG)](#23-production-security-block)
24. [Sentry Error Tracking](#24-sentry-error-tracking)
25. [CORS Settings](#25-cors-settings)
26. [Content Security Policy (CSP)](#26-content-security-policy-csp)
27. [REST Framework](#27-rest-framework)
28. [DRF Spectacular (API Docs)](#28-drf-spectacular-api-docs)
29. [Logging Configuration](#29-logging-configuration)
30. [Quick Reference Table](#30-quick-reference-table)
31. [What Was Changed / Added (March 1, 2026)](#31-what-was-changed--added-march-1-2026)

---

## 1. Architecture Overview

### How the Advaitam application is deployed:

```
┌─────────────────────────────────────────────────────────────┐
│                      USER'S BROWSER                         │
│                  (Types advaitam.info)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
         ┌─────────────────────────────────────┐
         │     CloudFront CDN (advaitam.info)  │
         │   (Global edge servers, caching)    │
         └────────────────┬────────────────────┘
                          │
                    ┌─────┴──────┐
                    │            │
        ┌───────────▼──┐    ┌────▼──────────┐
        │ Static Files │    │ Dynamic Pages │
        │  (CSS/JS)    │    │  (HTML views) │
        │ → S3 Bucket  │    │ → EC2 Instance│
        └──────────────┘    └────┬──────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Nginx (Port 443 HTTPS)  │
                    │  (Reverse Proxy, SSL)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Unix Socket (/run/..)   │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────▼──────────────┐
                 │    Gunicorn (2 Workers)      │
                 │  (Django WSGI Application)   │
                 └───────────────┬──────────────┘
                                 │
                 ┌───────────────▼──────────────┐
                 │   Django Application         │
                 │   (views.py, models.py)      │
                 └───────────────┬──────────────┘
                                 │
                 ┌───────────────▼──────────────┐
                 │  PostgreSQL Database (EC2)   │
                 │  (NOT RDS — saves $15/month) │
                 └──────────────────────────────┘
```

### Request Flow (13 steps):
```
1.  User types "advaitam.info" in browser
2.  DNS → Points to CloudFront distribution
3.  CloudFront checks cache:
      Static file? → Serve from S3 directly (no EC2)
      Dynamic page? → Forward to origin.advaitam.info (EC2)
4.  Nginx on EC2 receives HTTPS request (port 443)
5.  Nginx verifies SSL certificate (Let's Encrypt)
6.  Nginx checks X-CloudFront-Secret header (blocks direct access)
7.  Nginx proxies request to Gunicorn via Unix socket
8.  Gunicorn picks an available worker process
9.  Django routes request via urls.py → view function
10. View queries PostgreSQL if needed
11. Template renders HTML response
12. Response: Django → Gunicorn → Nginx → CloudFront → Browser
13. CloudFront caches response at edge for next user ✅
```

---

## 2. Imports & Environment Setup

```python
from pathlib import Path
import os
import environ
import logging
```

| Import | Why it's needed |
|--------|----------------|
| `pathlib.Path` | Cross-platform file paths — works on Windows AND Linux without `/` vs `\` issues |
| `os` | Read system environment variables, check file existence |
| `environ` | `django-environ` package — reads `.env` files and type-casts values (`bool`, `list`, `int`) |
| `logging` | Used later in the Sentry block to pass `logging.WARNING` / `logging.ERROR` constants |

---

## 3. DJANGO_ENV — Dev vs Production Detection

```python
is_production = os.environ.get('DJANGO_ENV', '').lower() == 'production'

# Always load .env first (development default)
env_file = os.path.join(str(BASE_DIR), '.env')
if os.path.exists(env_file):
    env.read_env(env_file)
else:
    env_file = os.path.join(str(BASE_DIR), '.env.production.bak')
    if os.path.exists(env_file):
        env.read_env(env_file)

# Override with production config when DJANGO_ENV=production
if is_production:
    env_file = os.path.join(str(BASE_DIR), '.env.production.bak')
    if os.path.exists(env_file):
        env.read_env(env_file)
    else:
        import warnings
        warnings.warn(
            'DJANGO_ENV=production set, but .env.production.bak not found!',
            RuntimeWarning
        )
```

### Why this changed from the old version:

**OLD approach (before March 1):**
```
Load .env.production.bak first → fallback to .env
```
This was backwards — it loaded production secrets on every machine.

**NEW approach (current):**
```
Step 1: Load .env (development defaults — always available)
Step 2: If DJANGO_ENV=production → load .env.production.bak on top (overrides step 1)
Step 3: If production file missing → show a clear warning
```

**The key variable: `DJANGO_ENV`**

```bash
# In .env.prod.template / on EC2 server:
DJANGO_ENV=production

# Locally (not set = development mode)
# No need to set anything
```

**Loading priority:**
```
Development (DJANGO_ENV not set):
  .env loaded → DEBUG=True, SQLite, console emails, S3 off

Production (DJANGO_ENV=production on EC2):
  .env loaded first (base)
  .env.production.bak loaded second (overrides everything)
  Result: DEBUG=False, PostgreSQL, SES emails, S3 on
```

This means if `.env.production.bak` is missing on EC2, Django shows a `RuntimeWarning` immediately — you know exactly what's wrong instead of silently using wrong settings.

---

## 4. Paths

```python
BASE_DIR     = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR   = BASE_DIR / 'static'
```

| Variable | Resolves to | Used for |
|----------|------------|---------|
| `BASE_DIR` | `/home/advaitam/app/` (EC2) or `D:\webProject\` (Windows) | Root of project — all other paths are relative to this |
| `TEMPLATE_DIR` | `BASE_DIR/templates/` | Where Django finds your `.html` files |
| `STATIC_DIR` | `BASE_DIR/static/` | Your hand-written CSS, JS, images in dev mode |

The `/` operator on `Path` objects concatenates paths cross-platform — no hardcoded slashes.

---

## 5. SECRET_KEY

```python
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')
```

**What it does:**
- Signs CSRF tokens (prevents request forgery)
- Signs session cookies (prevents tampering)
- Signs password reset links (prevents forging reset URLs)
- Signs JWT tokens if used

**Rules:**
- Must be at least 50 random characters
- Must be different on every project
- NEVER commit to Git
- Always in `.env.production.bak` on EC2
- Rotating it logs out all users (invalidates all sessions)

**Generate one:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 6. DEBUG Mode

```python
DEBUG = env.bool('DEBUG', default=False)
```

**`env.bool()`** reads the `DEBUG` variable from `.env` file and converts it to a Python boolean.
`"True"` → `True`, `"False"` → `False`, `"0"` → `False`, `"1"` → `True`

| DEBUG=True (Development) | DEBUG=False (Production) |
|--------------------------|--------------------------|
| Full error page with traceback | Generic "500 Server Error" page |
| Shows local variables in errors | No variable exposure |
| Auto-reloads on code change | No auto-reload |
| Serves static files itself | Requires Nginx / WhiteNoise / S3 |
| No HTTPS enforcement | HTTPS enforced |
| Slower (extra checks) | Faster |

**Security:** With DEBUG=True, anyone who triggers a 500 error can see your entire codebase, settings, and local variables. NEVER run DEBUG=True in production.

---

## 7. USE_S3 Flag

```python
USE_S3 = env.bool('USE_S3', default=False)
```

**This single variable controls two entire branches of configuration:**

```
USE_S3=False (development):
  └─ INSTALLED_APPS: no 'storages'
  └─ MIDDLEWARE: WhiteNoiseMiddleware included
  └─ STATIC_URL: 'static/'
  └─ Files served from local disk

USE_S3=True (production):
  └─ INSTALLED_APPS: 'storages' added
  └─ MIDDLEWARE: WhiteNoiseMiddleware NOT included (S3 handles it)
  └─ STATIC_URL: 'https://xxxxx.cloudfront.net/static/'
  └─ Files served from S3 via CloudFront CDN
```

Set in `.env`:
```bash
USE_S3=True   # production
USE_S3=False  # development (default)
```

---

## 8. ALLOWED_HOSTS

```python
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '127.0.0.1',
    'localhost',
    'advaitam.info',
    'www.advaitam.info',
    'origin.advaitam.info',
])
```

**What it prevents:**
Host header injection attack — a hacker sends a request with a forged `Host:` header to get your Django app to generate URLs pointing to a malicious domain (e.g. in password reset emails).

**Each entry explained:**

| Host | Why it's needed |
|------|----------------|
| `127.0.0.1` | Local dev access by IP |
| `localhost` | Local dev by name |
| `advaitam.info` | Root production domain (what users type) |
| `www.advaitam.info` | WWW subdomain |
| `origin.advaitam.info` | EC2 direct access (used by CloudFront as origin) |

**In `.env.prod.template`** you also add your EC2 private IP:
```bash
ALLOWED_HOSTS=advaitam.info,www.advaitam.info,origin.advaitam.info,10.0.1.45
```

**If a request arrives for a host NOT in this list:** Django returns `400 Bad Request`.
This is the most common first-deploy error — always check this first.

---

## 9. CSRF_TRUSTED_ORIGINS

```python
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://advaitam.info',
    'https://www.advaitam.info',
    'https://origin.advaitam.info',
    'http://localhost',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://127.0.0.1:8000',
])
```

**What it does:**
CSRF (Cross-Site Request Forgery) protection. When a form submits a POST/PUT/DELETE request, Django checks that the request origin is in this list.

**Why both HTTP and HTTPS for localhost:**
During local development, Django dev server runs on `http://localhost:8000`. The CSRF check would fail if only `https://` was listed.

**Production-only domains use HTTPS:** A form on `https://advaitam.info` must be trusted. If this list is wrong, all your forms return `403 CSRF verification failed`.

---

## 10. ANTHROPIC_API_KEY & CLOUDFRONT_SECRET

```python
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')

CLOUDFRONT_SECRET = env('CLOUDFRONT_SECRET', default='')
```

**ANTHROPIC_API_KEY:**
- Used by `claude_chat.html` to call Claude AI
- Leave empty in development (Claude features won't work)
- Add real key (`sk-ant-api03-...`) in `.env.production.bak`

**CLOUDFRONT_SECRET (NEW — added March 1):**
- A random secret string you generate and set in two places:
  1. CloudFront → origin request → custom header `X-CloudFront-Secret: <value>`
  2. Nginx → `if ($http_x_cloudfront_secret != "<value>") { return 403; }`
- This blocks anyone from accessing your EC2 directly — they MUST go through CloudFront
- If someone finds your EC2 IP and tries to hit it directly, Nginx returns 403
- Only CloudFront knows the secret

Set in `.env`:
```bash
CLOUDFRONT_SECRET=uY3kLmN8vXpQ2rT5wZ9a  # generate a strong random string
```

---

## 11. INSTALLED_APPS

```python
INSTALLED_APPS = [
    # Django built-in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'drf_spectacular',
    'rest_framework.authtoken',
    'taggit',
    'csp',            # ← NEW: django-csp for Content-Security-Policy headers
    # Local
    'webapp',
]

# Conditional: only add when USE_S3=True
if USE_S3:
    INSTALLED_APPS.append('storages')
```

**Why `csp` is in INSTALLED_APPS:**
`django-csp` needs to be registered so Django discovers its template tags and signal handlers.

**Why `storages` is conditional:**
`django-storages` imports `boto3` at startup. If `boto3` is not installed (local dev uses `requirements.txt`, not `requirements-prod.txt`), Django would crash on startup. The conditional check `if USE_S3:` prevents this — in dev, `USE_S3=False`, so `storages` is never loaded.

**Built-in apps and what they do:**

| App | What it provides |
|-----|-----------------|
| `admin` | `/admin/` management interface |
| `auth` | User model, login, logout, permissions |
| `contenttypes` | Generic foreign keys, permission system backbone |
| `sessions` | Session storage (used with auth and messages) |
| `messages` | Flash messages (`messages.success(request, "Saved!")`) |
| `staticfiles` | `collectstatic` command, `{% static %}` template tag |

---

## 12. MIDDLEWARE

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',     # ← NEW: adds CSP header to every response
]

# WhiteNoise only in dev — S3 handles static in production
if not USE_S3:
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

MIDDLEWARE += [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### What is Middleware?

Middleware is code that runs on EVERY request and EVERY response — like a chain of filters.

```
REQUEST comes in:
SecurityMiddleware → CSPMiddleware → WhiteNoise → Sessions → Common → CSRF → Auth → Messages → XFrame
                                                                                                    ↓
                                                                                              Your View
                                                                                                    ↓
RESPONSE goes out (in reverse order):
SecurityMiddleware ← CSPMiddleware ← WhiteNoise ← Sessions ← Common ← CSRF ← Auth ← Messages ← XFrame
```

### Each middleware explained:

| Middleware | Runs on | What it does |
|-----------|---------|-------------|
| `SecurityMiddleware` | Request + Response | Sets security headers (`X-Content-Type-Options`, `Referrer-Policy`), redirects HTTP → HTTPS |
| `CSPMiddleware` ← NEW | Response | Adds `Content-Security-Policy` header to every response (blocks XSS attacks) |
| `WhiteNoiseMiddleware` | Request | Intercepts requests for static files, serves them directly — only active when `USE_S3=False` |
| `SessionMiddleware` | Request + Response | Loads session from DB/cache, saves it back after request |
| `CommonMiddleware` | Request | Appends trailing slashes, normalises URLs |
| `CsrfViewMiddleware` | Request | Checks CSRF token on POST/PUT/DELETE requests |
| `AuthenticationMiddleware` | Request | Reads session → sets `request.user` (the logged-in user object) |
| `MessageMiddleware` | Request + Response | Loads flash messages, clears them after display |
| `XFrameOptionsMiddleware` | Response | Adds `X-Frame-Options: DENY` header — prevents embedding your site in iframes (clickjacking) |

### Why WhiteNoise is conditional:

```
Production (USE_S3=True):
  CSS/JS are in S3 → served by CloudFront
  WhiteNoise would never match any request → pointless overhead
  Leave it out

Development (USE_S3=False):
  CSS/JS are in local static/ folder
  WhiteNoise intercepts /static/... requests → serves the file
  Django dev server doesn't need to handle them
```

---

## 13. Templates & Context Processors

```python
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [TEMPLATE_DIR],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'webapp.context_processors.contact_form',
        ],
    },
}]
```

**`DIRS: [TEMPLATE_DIR]`** — Django searches `templates/` folder first, then app `templates/` folders.

**Context processors** inject variables into EVERY template automatically:

| Processor | Variable available in templates | Example use |
|-----------|-------------------------------|-------------|
| `request` | `{{ request.user }}`, `{{ request.path }}` | Checking URL in nav |
| `auth` | `{{ user }}`, `{% if user.is_authenticated %}` | Login/logout UI |
| `messages` | `{% for msg in messages %}` | Flash message display |
| `contact_form` (custom) | `{{ contact_form }}` | Contact form on every page |

**`APP_DIRS: True`** — Also search `webapp/templates/` inside each installed app.

---

## 14. WSGI Application

```python
WSGI_APPLICATION = 'webProject.wsgi.application'
```

Points to `webProject/wsgi.py`. Gunicorn uses this to find your Django app:
```bash
gunicorn webProject.wsgi:application
```
The `application` object is the Django WSGI callable — the entry point Gunicorn calls on every request.

---

## 15. Database Configuration

```python
if DEBUG:
    # Development: SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Production: PostgreSQL on EC2
    _DB_HOST = env('DB_HOST', default='localhost')
    _DB_OPTIONS = {'connect_timeout': 10}
    if _DB_HOST not in ('localhost', '127.0.0.1'):
        _DB_OPTIONS['sslmode'] = 'require'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='advaitam_db'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': _DB_HOST,
            'PORT': env('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
            'OPTIONS': _DB_OPTIONS,
        }
    }
```

### Why SQLite in dev, PostgreSQL in production:

| | SQLite | PostgreSQL |
|--|--------|-----------|
| Setup | Zero setup — just a file | Needs install + user + DB creation |
| Multi-user | No — single writer | Yes — handles concurrent users |
| Performance | Fast for small data | Fast for large data |
| Features | Basic SQL | Full SQL + JSON + full-text search |
| Dev use | ✅ Perfect | Too heavy |
| Production | ❌ Not safe | ✅ Required |

### Key production settings explained:

| Setting | Value | Why |
|---------|-------|-----|
| `CONN_MAX_AGE: 600` | 10 minutes | Reuse DB connection instead of creating a new one per request — saves ~10ms per request |
| `connect_timeout: 10` | 10 seconds | If PostgreSQL doesn't respond in 10 seconds, fail fast instead of hanging forever |
| `sslmode: require` | Only for remote hosts | If using AWS RDS (remote), encrypt the DB connection. For local PostgreSQL on same EC2, SSL adds overhead with no benefit — so skipped for `localhost`/`127.0.0.1` |

### Why NOT using RDS:
AWS RDS costs ~$15–30/month minimum. Running PostgreSQL directly on the EC2 instance is free. For a project at this scale, it's the right cost-saving choice. You can always migrate to RDS later.

---

## 16. Password Hashers

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',     # ← Winner
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher', # ← Legacy fallback
]
```

**The list order matters:**
- First entry = algorithm used for all NEW passwords
- Other entries = algorithms that can still VERIFY old passwords

**Why Argon2 is first:**
- Won the 2015 Password Hashing Competition
- Designed specifically to resist GPU brute-force attacks
- Requires `argon2-cffi` package (in `requirements-prod.txt`)

**Automatic upgrade:** When a user logs in with an old BCrypt/PBKDF2 password, Django automatically re-hashes it with Argon2 and saves the new hash. Users don't notice. Old algorithm hashes slowly disappear.

---

## 17. Password Validators

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': '...UserAttributeSimilarityValidator'},  # Not similar to username/email
    {'NAME': '...MinimumLengthValidator'},            # At least 8 chars
    {'NAME': '...CommonPasswordValidator'},           # Not in 20,000 common passwords list
    {'NAME': '...NumericPasswordValidator'},          # Not entirely numbers
]
```

These run when a user sets or changes their password. If any validator fails, Django shows the error message and rejects the password.

---

## 18. Internationalization

```python
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
```

| Setting | Value | Meaning |
|---------|-------|---------|
| `LANGUAGE_CODE` | `en-us` | Default language for admin, error pages |
| `TIME_ZONE` | `UTC` | All datetimes stored in UTC (never in local time) |
| `USE_I18N` | `True` | Enable translation framework (`{% trans "Hello" %}`) |
| `USE_TZ` | `True` | All datetimes are timezone-aware — avoids DST bugs |

**Why UTC always:** Store in UTC, display in user's local time using JavaScript or Django's `{% timezone %}` tag. If you store in "local" time, your DB data is wrong whenever clocks change.

---

## 19. Static & Media Files

### Production path (USE_S3=True):

```python
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='advaitam-assets')
AWS_S3_REGION_NAME      = env('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN    = env('AWS_S3_CUSTOM_DOMAIN', ...)   # Your CloudFront domain

STATIC_URL           = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATICFILES_STORAGE  = 'webapp.storages.StaticStorage'   # → S3

MEDIA_URL            = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'    # → S3

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=31536000, immutable',  # 1-year cache
}
```

**`max-age=31536000, immutable`** — Tells browsers (and CloudFront) to cache CSS/JS files for 1 year. `immutable` tells the browser "don't even bother revalidating — this file NEVER changes." This is safe because Django's `collectstatic` adds a content hash to filenames (`app.abc123.css`) — whenever the file changes, the filename changes too.

**IAM credentials note:**
```python
AWS_ACCESS_KEY_ID     = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
```
Leave these EMPTY on EC2. Instead, attach an **IAM Instance Role** to the EC2. The SDK picks up credentials automatically. Role-based auth is more secure (no long-lived keys) and you never need to rotate credentials manually.

### Development path (USE_S3=False):

```python
STATIC_URL       = 'static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [STATIC_DIR]            # Where YOUR static files live
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
MEDIA_URL   = 'media/'
MEDIA_ROOT  = BASE_DIR / 'media'
```

**Audio files note (in the code comments):**
```
Audio files are uploaded separately via:
  aws s3 sync static/audio/ s3://advaitam-assets/static/audio/ --content-type audio/mpeg
They are NOT processed by collectstatic (too large for git / Django static pipeline)
```
This means audio files bypass Django's static file pipeline entirely.

---

## 20. Auth & Session Settings

```python
LOGIN_URL             = '/loginpage/'
LOGIN_REDIRECT_URL    = '/apimodelviewset/'
LOGOUT_REDIRECT_URL   = '/loginpage/'
SESSION_SAVE_EVERY_REQUEST    = True
SESSION_COOKIE_AGE            = env.int('SESSION_COOKIE_AGE', default=86400)
SESSION_EXPIRE_AT_BROWSER_CLOSE = env.bool('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=False)
```

| Setting | Value | Meaning |
|---------|-------|---------|
| `LOGIN_URL` | `/loginpage/` | Where `@login_required` redirects unauthenticated users |
| `LOGIN_REDIRECT_URL` | `/apimodelviewset/` | Where users go after successful login |
| `LOGOUT_REDIRECT_URL` | `/loginpage/` | Where users go after logout |
| `SESSION_SAVE_EVERY_REQUEST` | `True` | Refresh session expiry on every request — "last active" timeout |
| `SESSION_COOKIE_AGE` | `86400` (24 hours) | Session expires 24 hours after last activity |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE` | `False` | Session persists across browser restarts (remember me) |

**Why `SESSION_SAVE_EVERY_REQUEST=True`:**
Without this, a user active for 23 hours gets logged out. With it, the 24-hour timer resets on every request — you only get logged out if you're inactive for 24 hours.

---

## 21. Email Configuration

```python
if DEBUG:
    # Development: print emails to console — no real sending
    EMAIL_BACKEND = env('EMAIL_BACKEND',
        default='django.core.mail.backends.console.EmailBackend')
    EMAIL_HOST = env('EMAIL_HOST', default='')
    ...
else:
    # Production: AWS SES SMTP
    _ses_region = env('AWS_SES_REGION_NAME', default='us-east-1')
    EMAIL_BACKEND = env('EMAIL_BACKEND',
        default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = env('EMAIL_HOST',
        default=f'email-smtp.{_ses_region}.amazonaws.com')
    EMAIL_PORT     = env.int('EMAIL_PORT', default=587)
    EMAIL_USE_TLS  = env.bool('EMAIL_USE_TLS', default=True)
    EMAIL_USE_SSL  = env.bool('EMAIL_USE_SSL', default=False)  # TLS OR SSL — not both

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@advaitam.info')
ADMIN_EMAIL        = env('ADMIN_EMAIL', default='kalyan.py28@gmail.com')
```

### What changed from the old version:
- **OLD:** Used Gmail SMTP in production
- **NEW:** Uses **AWS SES** (Simple Email Service) in production

### AWS SES vs Gmail:

| | Gmail SMTP | AWS SES |
|--|-----------|---------|
| Cost | Free up to 500/day | $0.10 per 1,000 emails |
| Deliverability | Medium (often spam) | High (Amazon's reputation) |
| Setup | App password + 2FA | IAM user + SMTP credentials |
| Rate limit | 500/day | 62,000/day (from EC2, free) |
| Use for production | ❌ Not recommended | ✅ Recommended |

### AWS SES Setup:
1. Go to AWS SES Console → SMTP Settings → Create SMTP Credentials
2. This creates an IAM user + gives you SMTP username/password
3. Add to `.env.production.bak`:
```bash
EMAIL_HOST_USER=AKIAIOSFODNN7EXAMPLE    # SES SMTP username
EMAIL_HOST_PASSWORD=wJalrXUtnFEMI...   # SES SMTP password (different from AWS access key)
AWS_SES_REGION_NAME=us-east-1
```

### SES SMTP endpoints by region:
| Region | Endpoint |
|--------|---------|
| `us-east-1` | `email-smtp.us-east-1.amazonaws.com` |
| `us-west-2` | `email-smtp.us-west-2.amazonaws.com` |
| `eu-west-1` | `email-smtp.eu-west-1.amazonaws.com` |
| `ap-south-1`| `email-smtp.ap-south-1.amazonaws.com` |

**IMPORTANT:** In SES sandbox mode, you can only send to verified email addresses. Request production access to send to anyone.

**`EMAIL_USE_SSL=False` note:** Use TLS (port 587) OR SSL (port 465) — NEVER both. The code explicitly sets `EMAIL_USE_SSL=False` to prevent accidental misconfiguration.

---

## 22. CSRF & Security Settings

```python
CSRF_FAILURE_VIEW  = 'webapp.views.csrf_failure'
CSRF_COOKIE_HTTPONLY = False   # JS must read CSRF token for AJAX
CSRF_COOKIE_SAMESITE = 'Lax'
```

| Setting | Value | Why |
|---------|-------|-----|
| `CSRF_FAILURE_VIEW` | `webapp.views.csrf_failure` | Custom error page instead of Django's default 403 |
| `CSRF_COOKIE_HTTPONLY` | `False` | JavaScript needs to read the CSRF cookie to include it in AJAX requests. `True` would break all AJAX forms |
| `CSRF_COOKIE_SAMESITE` | `'Lax'` | Cookie is sent on same-origin requests AND on top-level navigation (clicking links). Blocks cross-site form submissions. `'Strict'` would break OAuth redirects |

---

## 23. Production Security Block

```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Cache & Session
    REDIS_URL = env('REDIS_URL', default='')
    if REDIS_URL:
        # Redis available → use it for cache + sessions
        CACHES = {'default': {'BACKEND': '...RedisCache', 'LOCATION': REDIS_URL, ...}}
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    else:
        # No Redis → local memory cache + database sessions
        CACHES = {'default': {'BACKEND': '...LocMemCache', ...}}
        SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

**Every security setting explained:**

| Setting | What it does | Analogy |
|---------|-------------|---------|
| `SECURE_SSL_REDIRECT=True` | Any HTTP request → auto-redirect to HTTPS | Bouncer at door: "HTTPS only" |
| `SESSION_COOKIE_SECURE=True` | Session cookie only sent over HTTPS | Session ID only travels in armored car |
| `CSRF_COOKIE_SECURE=True` | CSRF cookie only sent over HTTPS | Anti-forgery token stays on HTTPS highway |
| `SESSION_COOKIE_HTTPONLY=True` | JS cannot read session cookie | Session is locked in a vault JS can't open |
| `SECURE_BROWSER_XSS_FILTER=True` | Activates browser's built-in XSS scanner | Browser's extra guard layer |
| `X_FRAME_OPTIONS='DENY'` | Page cannot be put inside an `<iframe>` | Prevents clickjacking: fake button on top of your button |
| `SECURE_HSTS_SECONDS=31536000` | Browser must use HTTPS for 1 year | Tells browser: "Never visit this site over HTTP again" |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS=True` | HSTS applies to `api.advaitam.info` etc. too | All subdomains get the same HTTPS-only rule |
| `SECURE_HSTS_PRELOAD=True` | Submit to browser preload lists | Chrome/Firefox bake in "HTTPS only" before even first visit |
| `SECURE_PROXY_SSL_HEADER` | Trust `X-Forwarded-Proto: https` from Nginx | Nginx terminates SSL → tells Django "this was HTTPS" |

### Cache & Session Strategy:

```
Redis available (REDIS_URL set)?
  ├── CACHES: Redis (fast in-memory)
  └── SESSION_ENGINE: cache (session stored in Redis — sub-millisecond)

No Redis?
  ├── CACHES: LocMemCache (process-local RAM — doesn't survive restart, doesn't share between workers)
  └── SESSION_ENGINE: db (sessions stored in PostgreSQL — slightly slower but reliable)
```

**Current choice:** No Redis (saves ~$12/month ElastiCache cost). Sessions stored in PostgreSQL. Fast enough for this scale.

---

## 24. Sentry Error Tracking

```python
_SENTRY_DSN = env('SENTRY_DSN', default='')
if _SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    sentry_sdk.init(
        dsn=_SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style='url'),
            LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR),
        ],
        traces_sample_rate=0.1,    # Track 10% of requests for performance
        profiles_sample_rate=0.1,  # Profile 10% of requests
        environment='production',
        send_default_pii=False,    # Don't send emails/IPs to Sentry
    )
```

**What changed from the old version:**
- **OLD:** Sentry code was commented out — completely inactive
- **NEW:** Fully wired and active whenever `SENTRY_DSN` is set in `.env`

**What Sentry does:**
When your app throws an unhandled exception in production, Sentry:
1. Catches the full error + stack trace
2. Records the URL, user agent, and Django request data
3. Sends you an email (or Slack/PagerDuty alert) within seconds
4. Groups identical errors together
5. Tracks whether an error is new, recurring, or resolved

**Each integration explained:**

| Integration | What it captures |
|-------------|-----------------|
| `DjangoIntegration` | Unhandled exceptions in views, middleware, signals |
| `transaction_style='url'` | Groups performance traces by URL pattern (`/books/<id>/`) not specific ID |
| `LoggingIntegration` | Any `logger.error(...)` or `logger.critical(...)` call in your code |
| `level=logging.WARNING` | Attach WARNING+ logs as breadcrumbs (context) on errors |
| `event_level=logging.ERROR` | Create a Sentry issue for every `logger.error()` call |

**Key settings:**

| Setting | Value | Why |
|---------|-------|-----|
| `traces_sample_rate=0.1` | 10% | Don't track every request — just a sample is enough for performance insights. 100% would hit Sentry's quota fast |
| `profiles_sample_rate=0.1` | 10% | CPU profiling — which function is slowest |
| `send_default_pii=False` | Off | Don't send user emails, passwords, IP addresses to Sentry (GDPR compliance) |

**To activate:**
```bash
# In .env
SENTRY_DSN=https://abc123@o456.ingest.sentry.io/789
```
If `SENTRY_DSN` is empty → Sentry is silently skipped. App works fine without it.

---

## 25. CORS Settings

```python
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        'https://advaitam.info',
        'https://www.advaitam.info',
    ]
```

**What is CORS (Cross-Origin Resource Sharing)?**
A browser security feature. If JavaScript running on `site-a.com` tries to call `api.advaitam.info`, the browser blocks it — unless `api.advaitam.info` sends back a header saying "I allow site-a.com".

**Development:** Allow all origins — makes local dev and testing easy.
**Production:** Only allow your own domains — nobody else's JavaScript can call your API.

---

## 26. Content Security Policy (CSP)

```python
_csp_cloudfront = env('CSP_CLOUDFRONT_DOMAIN', default='')
_csp_cdn = (f"https://{_csp_cloudfront}",) if _csp_cloudfront else ()

_CSP_DIRECTIVES = {
    'default-src': ("'self'",),
    'script-src':  ("'self'",) + _csp_cdn + ("'unsafe-inline'",),
    'style-src':   ("'self'",) + _csp_cdn + ("'unsafe-inline'",),
    'img-src':     ("'self'",) + _csp_cdn + ("data:", "https:"),
    'font-src':    ("'self'",) + _csp_cdn + ("https://fonts.gstatic.com",),
    'connect-src': ("'self'", "https://sentry.io", "https://*.sentry.io"),
    'media-src':   ("'self'",) + _csp_cdn,
    'object-src':  ("'none'",),
    'base-uri':    ("'self'",),
    'frame-src':   ("'none'",),
}

if DEBUG:
    CONTENT_SECURITY_POLICY_REPORT_ONLY = {'DIRECTIVES': _CSP_DIRECTIVES}
else:
    CONTENT_SECURITY_POLICY = {'DIRECTIVES': _CSP_DIRECTIVES}
```

### ⚠️ django-csp 4.0 — Format Changed (Fixed March 1, 2026)

**What was wrong:**
The original code used the **old pre-4.0 flat settings** format:
```python
# OLD — broken with django-csp 4.0, causes SystemCheckError csp.E001
CSP_REPORT_ONLY = DEBUG
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC  = ("'self'", "'unsafe-inline'")
# ... etc
```
django-csp 4.0 (released 2024) changed the entire settings format. The old flat `CSP_*` variables are no longer recognised and raise `SystemCheckError: csp.E001` on startup.

**What was fixed:**
The new format uses a single `CONTENT_SECURITY_POLICY` dict with a `DIRECTIVES` key:
```python
# NEW — correct for django-csp 4.0+
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src':  ("'self'", "'unsafe-inline'"),
        # ... etc
    }
}
```

**Dev vs Production split:**
```python
if DEBUG:
    # Violations logged in browser console — nothing blocked
    CONTENT_SECURITY_POLICY_REPORT_ONLY = {'DIRECTIVES': _CSP_DIRECTIVES}
else:
    # Violations are enforced — browser blocks the resource
    CONTENT_SECURITY_POLICY = {'DIRECTIVES': _CSP_DIRECTIVES}
```

This replaces the old `CSP_REPORT_ONLY = DEBUG` boolean.

**What CSP does:**
CSP is an HTTP header added to every response by `CSPMiddleware`. It tells the browser:
"Only load resources (scripts, styles, images, fonts) from these approved sources. Block everything else."

**Without CSP:** If an attacker injects `<script src="https://evil.com/steal.js">` into your page (XSS), the browser runs it.
**With CSP:** Browser checks `script-src` — `evil.com` is not listed → blocked immediately.

**Each directive explained:**

| Directive | Value | Meaning |
|-----------|-------|---------|
| `default-src` | `'self'` | Default fallback — only load from your own domain |
| `script-src` | self + CloudFront + `unsafe-inline` | JS from your domain and CDN. `unsafe-inline` needed for Django admin |
| `style-src` | self + CloudFront + `unsafe-inline` | CSS from your domain and CDN |
| `img-src` | self + CloudFront + `data:` + `https:` | Images from anywhere (needed for avatars, external images) |
| `font-src` | self + CloudFront + Google Fonts | Web fonts sources |
| `connect-src` | self + Sentry domains | Where JavaScript can make fetch/XHR calls |
| `media-src` | self + CloudFront | Audio and video files |
| `object-src` | `none` | Block Flash, Java applets, plugins completely |
| `base-uri` | `self` | Blocks base-tag hijacking |
| `frame-src` | `none` | No iframes (extra clickjacking protection) |

**Required `.env` variable:**
```bash
CSP_CLOUDFRONT_DOMAIN=d1234abcd.cloudfront.net   # your CloudFront distribution domain
```
Without this, the CDN is not in the trusted list and your CSS/JS from CloudFront would be blocked in production.

---

## 27. REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'COERCE_DECIMAL_TO_STRING': False,
}
```

| Setting | Value | What it enables |
|---------|-------|----------------|
| `SearchFilter` | Default | `GET /api/books/?search=vedanta` — search across fields |
| `OrderingFilter` | Default | `GET /api/books/?ordering=-created_at` — sort results |
| `AutoSchema` | drf_spectacular | Auto-generate OpenAPI docs from your views |
| `PAGE_SIZE` | 20 | Return 20 records per page. Client uses `?page=2` for next page |
| `COERCE_DECIMAL_TO_STRING` | False | Return decimal numbers as numbers (not strings) |

---

## 28. DRF Spectacular (API Docs)

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Advaitam API',
    'DESCRIPTION': 'API documentation for Advaitam Django project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}
```

Auto-generates interactive API documentation.

| URL | What you see |
|-----|-------------|
| `/api/schema/swagger/` | Swagger UI — interactive docs, test API from browser |
| `/api/schema/redoc/` | ReDoc — alternative clean docs view |
| `/api/schema/` | Raw OpenAPI JSON/YAML schema |

`SERVE_INCLUDE_SCHEMA=False` — Don't include the schema endpoint itself in the docs (it would recursively document itself).

---

## 29. Logging Configuration

```python
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)   # ← Creates logs/ folder automatically

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}'
        },
        'simple': {'format': '{levelname} {asctime} {message}'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15 MB per file
            'backupCount': 10,             # Keep 10 files = 150MB total
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'] if DEBUG else ['file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'] if DEBUG else ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file'] if not DEBUG else [],
            'level': 'ERROR',   # Only DB errors (not every SQL query)
            'propagate': False,
        },
        'django.autoreload': {
            'level': 'WARNING',  # Suppress noisy autoreload INFO messages
        },
    },
}
```

**Rotating file handler explained:**
```
maxBytes=15MB, backupCount=10 means:
  django.log        (current, up to 15MB)
  django.log.1      (previous)
  django.log.2
  ...
  django.log.10     (oldest)
Total: max 165MB of logs before oldest are deleted
```

**Log levels (from lowest to highest severity):**

| Level | When used | Stored in file? |
|-------|----------|----------------|
| DEBUG | Detailed diagnostic — every SQL query | No (too noisy) |
| INFO | General operational messages | No |
| WARNING | Something unexpected but recoverable | ✅ Yes |
| ERROR | An error that needs attention | ✅ Yes |
| CRITICAL | System about to crash | ✅ Yes |

**`os.makedirs(LOGS_DIR, exist_ok=True)`** — Creates the `logs/` folder automatically if it doesn't exist. Without this, Django would crash on first startup on a new server because the log file path doesn't exist.

**In production — watching logs:**
```bash
tail -f logs/django.log          # Watch live
grep ERROR logs/django.log       # Find all errors
grep "2026-03-01" logs/django.log  # Filter by date
```

---

## 30. Quick Reference Table

| Setting | Development | Production | Purpose |
|---------|-------------|-----------|---------|
| `DJANGO_ENV` | (not set) | `production` | Which .env file to load |
| `DEBUG` | `True` | `False` | Error detail vs security |
| `USE_S3` | `False` | `True` | Local files vs S3+CloudFront |
| `ALLOWED_HOSTS` | `localhost, 127.0.0.1` | All production domains | Host header protection |
| `Database` | SQLite | PostgreSQL | Dev convenience vs production robustness |
| `STATIC_URL` | `static/` | `https://cloudfront.../static/` | File serving source |
| `EMAIL_BACKEND` | `console` | `smtp` (AWS SES) | Log emails vs send real emails |
| `SECURE_SSL_REDIRECT` | `False` | `True` | Force HTTPS |
| `SESSION_COOKIE_SECURE` | `False` | `True` | Cookie over HTTPS only |
| `CSRF_COOKIE_SECURE` | `False` | `True` | CSRF over HTTPS only |
| `SESSION_COOKIE_AGE` | `86400` (24h) | `86400` (24h) | Session timeout |
| `SECURE_HSTS_SECONDS` | `0` | `31536000` (1 year) | HTTPS preload |
| `CACHE` | `LocMemCache` | `Redis` (if set) or `LocMemCache` | Cache backend |
| `SESSION_ENGINE` | Default | `cache` (Redis) or `db` | Session storage |
| CSP setting | `CONTENT_SECURITY_POLICY_REPORT_ONLY` | `CONTENT_SECURITY_POLICY` | Log violations (dev) vs enforce and block (prod) — django-csp 4.0 format |
| `CORS_ALLOW_ALL` | `True` | `False` (own domains only) | API cross-origin policy |
| `SENTRY_DSN` | (empty) | Your DSN | Error tracking on/off |
| `Logging handler` | `console` | `RotatingFileHandler` | Where logs go |
| `WhiteNoise` | In MIDDLEWARE | Not in MIDDLEWARE | Static file fallback |

---

## 31. What Was Changed / Added (March 1, 2026)

This section documents exactly what changed from the original settings.py so you understand the full evolution:

| # | What changed | Old value / state | New value / state |
|---|-------------|-------------------|-------------------|
| 1 | **Environment detection** | Load `.env.production.bak` first, fallback to `.env` | Load `.env` always; load `.env.production.bak` on top only when `DJANGO_ENV=production` |
| 2 | **`DJANGO_ENV` variable** | Did not exist | Added — controls which env file is active |
| 3 | **`CLOUDFRONT_SECRET`** | Did not exist | Added — secret header that Nginx checks to block direct EC2 access |
| 4 | **`csp` in INSTALLED_APPS** | Not present | Added — required for `django-csp` package |
| 5 | **`USE_S3` flag** | Implicit in static config | Now explicit top-level variable controlling both INSTALLED_APPS and MIDDLEWARE |
| 6 | **`CSPMiddleware`** | Not present | Added as 2nd middleware (right after SecurityMiddleware) |
| 7 | **WhiteNoise conditional** | Always in MIDDLEWARE | Now only included when `USE_S3=False` (not needed in production) |
| 8 | **CSP configuration** | `SECURE_CONTENT_SECURITY_POLICY = True` (useless boolean) → then old flat `CSP_*` vars (caused `csp.E001` with django-csp 4.0) | **django-csp 4.0 format**: `CONTENT_SECURITY_POLICY = {'DIRECTIVES': {...}}` dict. Dev: `CONTENT_SECURITY_POLICY_REPORT_ONLY`. Prod: `CONTENT_SECURITY_POLICY`. |
| 9 | **`CSP_CLOUDFRONT_DOMAIN`** | Did not exist | New `.env` variable that builds CDN domain into all CSP directives |
| 10 | **`CSP_REPORT_ONLY`** (old) | Did not exist → used as boolean flag | Replaced by two separate dicts: `CONTENT_SECURITY_POLICY_REPORT_ONLY` (dev) and `CONTENT_SECURITY_POLICY` (prod) |
| 11 | **Sentry** | Commented out | Fully wired: `DjangoIntegration` + `LoggingIntegration`, activates via `SENTRY_DSN` env var |
| 12 | **`profiles_sample_rate`** | Did not exist | `0.1` — Sentry CPU profiling on 10% of requests |
| 13 | **Email backend** | Gmail SMTP in production | AWS SES SMTP in production (better deliverability, cheaper) |
| 14 | **`EMAIL_USE_SSL`** | Did not exist | Explicitly `False` — use TLS (port 587), not SSL (port 465) |
| 15 | **`ADMIN_EMAIL`** | Did not exist | `kalyan.py28@gmail.com` — admin notification address |
| 16 | **CORS settings** | Did not exist | `CORS_ALLOW_ALL_ORIGINS=True` in dev, explicit allowed origins in production |
| 17 | **`django.autoreload` logger** | Did not exist | Added to suppress noisy autoreload messages |
| 18 | **`os.makedirs(LOGS_DIR)`** | Not present | Auto-creates `logs/` folder — prevents crash on fresh server |
| 19 | **`storages` conditional** | Always in INSTALLED_APPS | Now only added `if USE_S3:` — prevents boto3 crash in dev |
| 20 | **`/health/` view** | Did not exist | Added `health_check` in `webapp/views.py`, wired to `path('health/', ...)` in `urls.py` |
| 21 | **Sentry import guard** | Bare `import sentry_sdk` — crashes server if package missing | Wrapped in `try/except ImportError` with `RuntimeWarning` — server starts safely even without `sentry-sdk` installed |
| 22 | **CSP `csp.E001` crash fix** | Old flat `CSP_*` vars caused `SystemCheckError: csp.E001` with django-csp 4.0 | Rewrote to `CONTENT_SECURITY_POLICY = {'DIRECTIVES': {...}}` (4.0 format) — `manage.py check` now passes with 0 issues |
---

*This document matches `webProject/settings.py` exactly as of March 1, 2026 — 486 lines.*
*Next time you open this project at any company, start here to understand the full configuration.*

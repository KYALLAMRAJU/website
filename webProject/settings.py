"""
Django settings for webProject project - PRODUCTION READY

Architecture:
  User Browser -> CloudFront CDN -> Nginx (EC2) -> Gunicorn -> Django -> PostgreSQL
  Static/Media files served via CloudFront -> S3
"""

import logging
import os
from pathlib import Path

import environ

# ========== ENVIRONMENT SETUP ==========
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))

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

# ========== PATHS ==========
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

# ========== SECURITY - SECRET KEY ==========
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')

# ========== DEBUG MODE ==========
DEBUG = env.bool('DEBUG', default=False)

# ========== STORAGE CONFIGURATION ==========
USE_S3 = env.bool('USE_S3', default=False)

# ========== ALLOWED HOSTS ==========
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '127.0.0.1',
    'localhost',
    'advaitam.info',
    'www.advaitam.info',
    'origin.advaitam.info',
])

# ========== CSRF TRUSTED ORIGINS ==========
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://advaitam.info',
    'https://www.advaitam.info',
    'https://origin.advaitam.info',
    'http://localhost',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://127.0.0.1:8000',
])

# ========== ANTHROPIC API KEY ==========
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')

# ========== CLOUDFRONT ORIGIN PROTECTION SECRET ==========
# Must match the X-CloudFront-Secret header value configured in Nginx
CLOUDFRONT_SECRET = env('CLOUDFRONT_SECRET', default='')

# ========== INSTALLED APPS ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
    'drf_spectacular',
    'rest_framework.authtoken',
    'taggit',
    'csp',
    # Local apps
    'webapp',
]

# Only add storages app when S3 is enabled (prevents crashes in dev without boto3)
if USE_S3:
    INSTALLED_APPS.append('storages')

# ========== MIDDLEWARE ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',   # Content-Security-Policy headers (blocks XSS)
]

# WhiteNoise only needed in dev/fallback mode — S3+CloudFront serves static in prod
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

ROOT_URLCONF = 'webProject.urls'

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = 'webProject.wsgi.application'

# ========== DATABASE CONFIGURATION ==========
if DEBUG:
    # Development: SQLite (no PostgreSQL needed)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Production: PostgreSQL on EC2 (local, no RDS)
    _DB_HOST = env('DB_HOST', default='localhost')
    _DB_OPTIONS = {'connect_timeout': 10}
    # Only require SSL for remote hosts (e.g. RDS), not for localhost
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

# ========== PASSWORD HASHERS ==========
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========== INTERNATIONALIZATION ==========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========== STATIC & MEDIA FILES CONFIGURATION ==========
if USE_S3:
    # ========== AWS S3 + CLOUDFRONT CONFIGURATION (PRODUCTION) ==========
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='advaitam-assets')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = env(
        'AWS_S3_CUSTOM_DOMAIN',
        default=f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    )
    # Leave blank to use EC2 IAM Instance Role (recommended)
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')

    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'webapp.storages.StaticStorage'

    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'

    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = 'virtual'
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = None
    # Default cache for CSS/JS/images — 1 year (immutable, versioned by collectstatic)
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=31536000, immutable',
    }
    # Audio files are uploaded separately via:
    #   aws s3 sync static/audio/ s3://advaitam-assets/static/audio/
    #       --exclude "*.md" --content-type audio/mpeg --cache-control "max-age=31536000"
    # They are NOT processed by collectstatic (too large for git / Django static pipeline)

else:
    # ========== LOCAL STORAGE (DEVELOPMENT) ==========
    STATIC_URL = 'static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [STATIC_DIR]
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    MEDIA_URL = 'media/'
    MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== AUTH & SESSION ==========
LOGIN_URL = '/loginpage/'
LOGIN_REDIRECT_URL = '/apimodelviewset/'
LOGOUT_REDIRECT_URL = '/loginpage/'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = env.int('SESSION_COOKIE_AGE', default=86400)
SESSION_EXPIRE_AT_BROWSER_CLOSE = env.bool('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=False)

# ========== EMAIL CONFIGURATION ==========
# Development: emails are printed to console (no real sending)
# Production: AWS SES via SMTP (TLS on port 587)
#
# AWS SES SMTP credentials (different from your AWS access keys!):
#   1. Go to AWS SES Console -> SMTP Settings -> Create SMTP Credentials
#   2. This creates an IAM user and gives you SMTP username/password
#   3. Add these to .env.production.bak:
#        EMAIL_HOST_USER=<SES SMTP username>
#        EMAIL_HOST_PASSWORD=<SES SMTP password>
#        AWS_SES_REGION_NAME=us-east-1           # your SES region
#
# SES SMTP endpoints by region:
#   us-east-1  -> email-smtp.us-east-1.amazonaws.com
#   us-west-2  -> email-smtp.us-west-2.amazonaws.com
#   eu-west-1  -> email-smtp.eu-west-1.amazonaws.com
#   ap-south-1 -> email-smtp.ap-south-1.amazonaws.com
#
# IMPORTANT: In SES sandbox mode only verified email addresses can receive mail.
#            Request production access to send to any address.
if DEBUG:
    # Development: dump emails to console, no real sending
    # EMAIL_BACKEND, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD,
    # EMAIL_PORT, EMAIL_USE_TLS can all be overridden in your .env file.
    EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
    EMAIL_HOST = env('EMAIL_HOST', default='')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
else:
    # Production: AWS SES SMTP
    _ses_region = env('AWS_SES_REGION_NAME', default='us-east-1')
    EMAIL_BACKEND = env(
        'EMAIL_BACKEND',
        default='django.core.mail.backends.smtp.EmailBackend',
    )
    EMAIL_HOST = env(
        'EMAIL_HOST',
        default=f'email-smtp.{_ses_region}.amazonaws.com',
    )
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
    EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)  # use TLS OR SSL, not both

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@advaitam.info')
ADMIN_EMAIL = env('ADMIN_EMAIL', default='kalyan.py28@gmail.com')

# ========== CSRF & SECURITY SETTINGS ==========
CSRF_FAILURE_VIEW = 'webapp.views.csrf_failure'
CSRF_COOKIE_HTTPONLY = False  # JS needs to read CSRF token for AJAX
CSRF_COOKIE_SAMESITE = 'Lax'

# ========== PRODUCTION SECURITY ==========
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = False
    SESSION_COOKIE_HTTPONLY = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Required when behind Nginx/CloudFront (they terminate SSL)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # ========== CACHE & SESSION (PRODUCTION) ==========
    REDIS_URL = env('REDIS_URL', default='')

    if REDIS_URL:
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': REDIS_URL,
                'OPTIONS': {
                    'socket_connect_timeout': 5,
                    'socket_timeout': 5,
                },
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
        SESSION_CACHE_ALIAS = 'default'
    else:
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'advaitam-cache',
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.db'

    # ========== SENTRY ERROR TRACKING ==========
    # Only activates when SENTRY_DSN is set in .env — safe to leave empty in dev.
    # Wrapped in try/except so a missing sentry-sdk package never crashes the server.
    _SENTRY_DSN = env('SENTRY_DSN', default='')
    if _SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration
            sentry_sdk.init(
                dsn=_SENTRY_DSN,
                integrations=[
                    DjangoIntegration(transaction_style='url'),
                    LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR),
                ],
                traces_sample_rate=0.1,   # 10% of transactions for performance monitoring
                profiles_sample_rate=0.1, # 10% of transactions for profiling
                environment='production',
                send_default_pii=False,   # Don't send personally identifiable information
            )
        except ImportError:
            import warnings
            warnings.warn(
                'SENTRY_DSN is set but sentry-sdk is not installed. '
                'Run: pip install sentry-sdk',
                RuntimeWarning,
            )

else:
    # Development: relax security settings
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

# ========== CORS SETTINGS ==========
# Only allow your own domain in production; allow all in dev
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        'https://advaitam.info',
        'https://www.advaitam.info',
    ]

# ========== REST FRAMEWORK ==========
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

# ========== DRF SPECTACULAR ==========
SPECTACULAR_SETTINGS = {
    'TITLE': 'Advaitam API',
    'DESCRIPTION': 'API documentation for Advaitam Django project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# ========== CONTENT SECURITY POLICY (CSP) ==========
# django-csp 4.0+ format — uses CONTENT_SECURITY_POLICY dict (not the old CSP_* flat settings).
# Protects against XSS attacks by controlling which resources browsers can load.
# django-csp docs: https://django-csp.readthedocs.io/en/latest/configuration.html
#
# In dev  (DEBUG=True)  → CONTENT_SECURITY_POLICY_REPORT_ONLY: violations logged, nothing blocked.
# In prod (DEBUG=False) → CONTENT_SECURITY_POLICY: violations are enforced and blocked.
#
# Set CSP_CLOUDFRONT_DOMAIN in .env to allow your CDN:
#   CSP_CLOUDFRONT_DOMAIN=d1234abcd.cloudfront.net

_csp_cloudfront = env('CSP_CLOUDFRONT_DOMAIN', default='')
_csp_cdn = (f"https://{_csp_cloudfront}",) if _csp_cloudfront else ()

_CSP_DIRECTIVES = {
    'default-src': ("'self'",),
    'script-src':  ("'self'",) + _csp_cdn + ("'unsafe-inline'",),  # unsafe-inline needed for Django admin
    'style-src':   ("'self'",) + _csp_cdn + ("'unsafe-inline'",),  # inline styles common in admin
    'img-src':     ("'self'",) + _csp_cdn + ("data:", "https:"),
    'font-src':    ("'self'",) + _csp_cdn + ("https://fonts.gstatic.com",),
    'connect-src': ("'self'", "https://sentry.io", "https://*.sentry.io"),
    'media-src':   ("'self'",) + _csp_cdn,
    'object-src':  ("'none'",),   # Block Flash, plugins
    'base-uri':    ("'self'",),   # Block base-tag hijacking
    'frame-src':   ("'none'",),   # No iframes
}

if DEBUG:
    # Report-only in dev: log violations in browser console, never block anything
    CONTENT_SECURITY_POLICY_REPORT_ONLY = {'DIRECTIVES': _CSP_DIRECTIVES}
else:
    # Enforce in production: violating resources are blocked by the browser
    CONTENT_SECURITY_POLICY = {'DIRECTIVES': _CSP_DIRECTIVES}

# ========== LOGGING ==========
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15 MB
            'backupCount': 10,
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
            'level': 'ERROR',
            'propagate': False,
        },
        'django.autoreload': {
            'level': 'WARNING',
            'handlers': ['console'] if DEBUG else ['file'],
        },
    },
}

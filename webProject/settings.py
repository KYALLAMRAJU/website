"""
Django settings for webProject project - PRODUCTION READY

Architecture:
  User Browser -> CloudFront CDN -> Nginx (EC2) -> Gunicorn -> Django -> PostgreSQL
  Static/Media files served via CloudFront -> S3
"""

import logging
import os
from pathlib import Path
from datetime import timedelta
import environ
import rest_framework
from rest_framework.authentication import *
from rest_framework.permissions import *

# ========== ENVIRONMENT SETUP ==========
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))

is_production = os.environ.get("DJANGO_ENV", "").lower() == "production"

# Always load .env first (development default)
env_file = os.path.join(str(BASE_DIR), ".env")
if os.path.exists(env_file):
    env.read_env(env_file)
else:
    env_file = os.path.join(str(BASE_DIR), ".env.production.bak")
    if os.path.exists(env_file):
        env.read_env(env_file)

# Override with production config when DJANGO_ENV=production
if is_production:
    env_file = os.path.join(str(BASE_DIR), ".env.production.bak")
    if os.path.exists(env_file):
        env.read_env(env_file)
    else:
        import warnings

        warnings.warn(
            "DJANGO_ENV=production set, but .env.production.bak not found!", RuntimeWarning
        )

# ========== PATHS ==========
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# ========== SECURITY - SECRET KEY ==========
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me-in-production")  # change this line according to your company

# ========== DEBUG MODE ==========
DEBUG = env.bool("DEBUG", default=False)

# ========== STORAGE CONFIGURATION ==========
USE_S3 = env.bool("USE_S3", default=False)

# ========== ALLOWED HOSTS ==========
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[
        "127.0.0.1",
        "localhost",
        "advaitam.info",          # change this line according to your company
        "www.advaitam.info",      # change this line according to your company
        "origin.advaitam.info",   # change this line according to your company
    ],
)

# ========== CSRF TRUSTED ORIGINS ==========
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://advaitam.info",           # change this line according to your company
        "https://www.advaitam.info",       # change this line according to your company
        "https://origin.advaitam.info",    # change this line according to your company
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
    ],
)


# ========== CLOUDFRONT ORIGIN PROTECTION SECRET ==========
# Must match the X-CloudFront-Secret header value configured in Nginx
CLOUDFRONT_SECRET = env("CLOUDFRONT_SECRET", default="")  # change this line according to your company

# ========== INSTALLED APPS ==========
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "drf_spectacular",
    "rest_framework.authtoken",
    "taggit",
    "csp",
    # ── django-allauth (OAuth2 / Social Login) ──────────────────────────────
    "django.contrib.sites",          # Required by allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.twitter_oauth2",
    # Local apps
    "webapp",  # change this line according to your company (rename/add your own apps)
]

# Only add storages app when S3 is enabled (prevents crashes in dev without boto3)
if USE_S3:
    INSTALLED_APPS.append("storages")

# ========== MIDDLEWARE ==========
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",  # Content-Security-Policy headers (blocks XSS)
    "corsheaders.middleware.CorsMiddleware",  # CORS headers — must be before CommonMiddleware
]

# WhiteNoise only needed in dev/fallback mode — S3+CloudFront serves static in prod
if not USE_S3:
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

MIDDLEWARE += [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # ── allauth: must come after AuthenticationMiddleware ──
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "webProject.urls"  # change this line according to your company (update to your project name)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "webapp.context_processors.contact_form",  # change this line according to your company (update to your app name)
            ],
        },
    },
]

WSGI_APPLICATION = "webProject.wsgi.application"  # change this line according to your company (update to your project name)

# ========== DATABASE CONFIGURATION ==========
if DEBUG:
    # Development: SQLite (no PostgreSQL needed)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Production: PostgreSQL on EC2 (local, no RDS)
    _DB_HOST = env("DB_HOST", default="localhost")
    _DB_OPTIONS: dict = {"connect_timeout": 10}
    # Only require SSL for remote hosts (e.g. RDS), not for localhost
    if _DB_HOST not in ("localhost", "127.0.0.1"):
        _DB_OPTIONS["sslmode"] = "require"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", default="advaitam_db"),        # change this line according to your company
            "USER": env("DB_USER", default="postgres"),           # change this line according to your company
            "PASSWORD": env("DB_PASSWORD", default=""),
            "HOST": _DB_HOST,
            "PORT": env("DB_PORT", default="5432"),
            "CONN_MAX_AGE": 600,
            "OPTIONS": _DB_OPTIONS,
        }
    }

# ========== PASSWORD HASHERS ==========
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========== INTERNATIONALIZATION ==========
LANGUAGE_CODE = "en-us"   # change this line according to your company (e.g. "en-gb", "fr", "de")
TIME_ZONE = "UTC"         # change this line according to your company (e.g. "Asia/Kolkata", "America/New_York")
USE_I18N = True
USE_TZ = True

# ========== STATIC & MEDIA FILES CONFIGURATION ==========
if USE_S3:
    # ========== AWS S3 + CLOUDFRONT CONFIGURATION (PRODUCTION) ==========
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="advaitam-assets")  # change this line according to your company
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")                  # change this line according to your company
    AWS_S3_CUSTOM_DOMAIN = env(
        "AWS_S3_CUSTOM_DOMAIN", default=f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"    # change this line according to your company
    )
    # Leave blank to use EC2 IAM Instance Role (recommended)
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")        # change this line according to your company
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")  # change this line according to your company

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_STORAGE = "webapp.storages.StaticStorage"  # change this line according to your company (update to your app name)

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    MEDIA_ROOT = BASE_DIR / "media"
    DEFAULT_FILE_STORAGE = "webapp.storages.MediaStorage"  # change this line according to your company (update to your app name)

    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_ADDRESSING_STYLE = "virtual"
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = None
    # Default cache for CSS/JS/images — 1 year (immutable, versioned by collectstatic)
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=31536000, immutable",
    }
    # Audio files are uploaded separately via:
    #   aws s3 sync static/audio/ s3://advaitam-assets/static/audio/  # change this line according to your company
    #       --exclude "*.md" --content-type audio/mpeg --cache-control "max-age=31536000"
    # They are NOT processed by collectstatic (too large for git / Django static pipeline)

else:
    # ========== LOCAL STORAGE (DEVELOPMENT) ==========
    STATIC_URL = "static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [STATIC_DIR]
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ========== DJANGO AUTH & SESSION ==========
LOGIN_URL = "/loginpage/"                        # change this line according to your company (update to your login URL)
LOGIN_REDIRECT_URL = "/home/"                    # change this line according to your company (update to your post-login landing page)
LOGOUT_REDIRECT_URL = "/loginpage/"             # change this line according to your company (update to your post-logout page)
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=86400)
SESSION_EXPIRE_AT_BROWSER_CLOSE = env.bool("SESSION_EXPIRE_AT_BROWSER_CLOSE", default=False)

# ========== DJANGO SITES FRAMEWORK (required by allauth) ==========
SITE_ID = 1  # Matches the first record in django_site table (domain = 127.0.0.1:8000 in dev)

# ========== AUTHENTICATION BACKENDS ==========
AUTHENTICATION_BACKENDS = [
    # Standard Django username/password login
    "django.contrib.auth.backends.ModelBackend",
    # allauth-specific: needed for social login and email-based login
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ========== ALLAUTH — ACCOUNT SETTINGS ==========
# allauth 65.x style (replaces old ACCOUNT_AUTHENTICATION_METHOD etc.)
ACCOUNT_LOGIN_METHODS = {"email"}              # login via email only (no username)
ACCOUNT_SIGNUP_FIELDS = [                      # fields shown on allauth's own signup form
    "email*",
    "password1*",
    "password2*",
]
ACCOUNT_EMAIL_VERIFICATION = "optional"        # change to "mandatory" in production
ACCOUNT_LOGIN_REDIRECT_URL = "/home/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/loginpage/"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_UNIQUE_EMAIL = True

# ========== ALLAUTH — SOCIAL ACCOUNT SETTINGS ==========
SOCIALACCOUNT_AUTO_SIGNUP = True                # auto-create Django user on first social login
SOCIALACCOUNT_LOGIN_ON_GET = False              # require POST to prevent CSRF on social login
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"       # provider already verified; skip extra email step

# ── OAuth2 Provider Credentials (set in .env) ──────────────────────────────
# Each provider needs its own Client ID & Secret from the provider's developer portal.
# See deploy/OAUTH2_COMPLETE_GUIDE.md for step-by-step instructions.
SOCIALACCOUNT_PROVIDERS = {
    # ── Google ───────────────────────────────────────────────────────────────
    # Create at: https://console.cloud.google.com/ → APIs & Services → Credentials
    # Callback URL: http://127.0.0.1:8000/accounts/google/login/callback/
    "google": {
        "APP": {
            "client_id": env("GOOGLE_OAUTH_CLIENT_ID", default=""),
            "secret":    env("GOOGLE_OAUTH_SECRET",    default=""),
            "key":       "",
        },
        "SCOPE":      ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,             # PKCE = extra security layer
    },
    # ── GitHub ───────────────────────────────────────────────────────────────
    # Create at: https://github.com/settings/developers → OAuth Apps → New OAuth App
    # Callback URL: http://127.0.0.1:8000/accounts/github/login/callback/
    "github": {
        "APP": {
            "client_id": env("GITHUB_OAUTH_CLIENT_ID", default=""),
            "secret":    env("GITHUB_OAUTH_SECRET",    default=""),
            "key":       "",
        },
        "SCOPE": ["user", "user:email"],
    },
    # ── Facebook ─────────────────────────────────────────────────────────────
    # Create at: https://developers.facebook.com/ → My Apps → Add a New App
    # Callback URL: http://127.0.0.1:8000/accounts/facebook/login/callback/
    "facebook": {
        "METHOD": "oauth2",
        "SDK_URL": "//connect.facebook.net/{locale}/sdk.js",
        "SCOPE":   ["email", "public_profile"],
        "AUTH_PARAMS": {"auth_type": "reauthenticate"},
        "FIELDS":  ["id", "email", "name", "first_name", "last_name", "verified", "locale", "picture"],
        "EXCHANGE_TOKEN": True,
        "VERIFIED_EMAIL": False,
        "VERSION":  "v19.0",
        "APP": {
            "client_id": env("FACEBOOK_APP_ID",     default=""),
            "secret":    env("FACEBOOK_APP_SECRET", default=""),
            "key":       "",
        },
    },
    # ── Twitter / X (OAuth 2.0) ───────────────────────────────────────────────
    # Create at: https://developer.twitter.com/en/portal/dashboard → New Project/App
    # Callback URL: http://127.0.0.1:8000/accounts/twitter_oauth2/login/callback/
    "twitter_oauth2": {
        "APP": {
            "client_id": env("TWITTER_OAUTH_CLIENT_ID", default=""),
            "secret":    env("TWITTER_OAUTH_SECRET",    default=""),
            "key":       "",
        },
        "SCOPE": ["tweet.read", "users.read", "offline.access"],
    },
}

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
#        AWS_SES_REGION_NAME=us-east-1           # your SES region  # change this line according to your company
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
    EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
    EMAIL_HOST = env("EMAIL_HOST", default="")
    EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
else:
    # Production: AWS SES SMTP
    _ses_region = env("AWS_SES_REGION_NAME", default="us-east-1")  # change this line according to your company
    EMAIL_BACKEND = env(
        "EMAIL_BACKEND",
        default="django.core.mail.backends.smtp.EmailBackend",
    )
    EMAIL_HOST = env(
        "EMAIL_HOST",
        default=f"email-smtp.{_ses_region}.amazonaws.com",  # change this line according to your company (update region)
    )
    EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")      # change this line according to your company
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")  # change this line according to your company
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
    EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)  # use TLS OR SSL, not both

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@advaitam.info")  # change this line according to your company
ADMIN_EMAIL = env("ADMIN_EMAIL", default="kalyan.py28@gmail.com")                # change this line according to your company

# ========== CSRF & SECURITY SETTINGS ==========
CSRF_FAILURE_VIEW = "webapp.views.csrf_failure"  # change this line according to your company (update to your app name)
CSRF_COOKIE_HTTPONLY = False  # JS needs to read CSRF token for AJAX
CSRF_COOKIE_SAMESITE = "Lax"

# ========== PRODUCTION SECURITY ==========
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = False
    SESSION_COOKIE_HTTPONLY = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"

    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Required when behind Nginx/CloudFront (they terminate SSL)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # ========== CACHE & SESSION (PRODUCTION) ==========
    REDIS_URL = env("REDIS_URL", default="")  # change this line according to your company (set your Redis URL)

    if REDIS_URL:
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": REDIS_URL,
                "OPTIONS": {
                    "socket_connect_timeout": 5,
                    "socket_timeout": 5,
                },
            }
        }
        SESSION_ENGINE = "django.contrib.sessions.backends.cache"
        SESSION_CACHE_ALIAS = "default"
    else:
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "advaitam-cache",  # change this line according to your company (rename to your project)
            }
        }
        SESSION_ENGINE = "django.contrib.sessions.backends.db"

    # ========== SENTRY ERROR TRACKING ==========
    # Only activates when SENTRY_DSN is set in .env — safe to leave empty in dev.
    # Wrapped in try/except so a missing sentry-sdk package never crashes the server.
    _SENTRY_DSN = env("SENTRY_DSN", default="")  # change this line according to your company (set your Sentry DSN)
    if _SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration

            sentry_sdk.init(
                dsn=_SENTRY_DSN,
                integrations=[
                    DjangoIntegration(transaction_style="url"),
                    LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR),
                ],
                traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
                profiles_sample_rate=0.1,  # 10% of transactions for profiling
                environment="production",  # change this line according to your company (e.g. "staging", "production")
                send_default_pii=False,  # Don't send personally identifiable information
            )
        except ImportError:
            sentry_sdk = None  # type: ignore[assignment]
            DjangoIntegration = None  # type: ignore[assignment]
            LoggingIntegration = None  # type: ignore[assignment]
            import warnings

            warnings.warn(
                "SENTRY_DSN is set but sentry-sdk is not installed. Run: pip install sentry-sdk",
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
        "https://advaitam.info",       # change this line according to your company
        "https://www.advaitam.info",   # change this line according to your company
    ]

# ================================================================== REST FRAMEWORK ========================================================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        # rest_framework.permissions.IsAdminUser,
        # rest_framework.permissions.IsAuthenticatedOrReadOnly,
        # rest_framework.permissions.AllowAny,
        # rest_framework.permissions.DjangoModelPermissions,
        # rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly,
    ),

    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    'SEARCH_PARAM': 'mysearch',# this is used for DRF seraching with our own search param name
    'ORDERING_PARAM': 'myordering', # THIS IS USED FOR DRF ORDERING WITH OUR OWN ORDERING PARAM NAME


    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,  # change this line according to your company (adjust page size as needed)
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "COERCE_DECIMAL_TO_STRING": False,

    # ── Rate Limiting (Throttling) ──────────────────────────────────────────
    # Protects the API from abuse / brute-force / DoS attacks.
    # anon: unauthenticated users (e.g. public API callers)
    # user: authenticated users (stricter limits possible per view)
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",   # change this line according to your company (adjust rate limit as needed)
        "user": "300/minute",  # change this line according to your company (adjust rate limit as needed)
    },
}

# ============================================ SIMPLE JWT SETTINGS ==================================================================================
# These settings control JWT token behaviour for all API endpoints that use
# JWTAuthentication (already set as DEFAULT_AUTHENTICATION_CLASSES above).
# TokenObtainPairView    → /jwt-token-get/      → returns access + refresh tokens
# TokenRefreshView       → /jwt-token-refresh/  → returns new access token using refresh token
# TokenVerifyView        → /jwt-token-verify/   → verifies token validity
# All three views read from this SIMPLE_JWT dict automatically — no code changes needed.

SIMPLE_JWT = {
    # ── Token lifetimes ───────────────────────────────────────────────────────
    # Access token expires quickly (short-lived) for security.
    # Refresh token lives longer — used to get a new access token without re-login.
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=env.int("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=60)),   # change this line according to your company
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_EXPIRE_DAYS", default=1)),         # change this line according to your company

    # ── Rotation & blacklist ──────────────────────────────────────────────────
    # ROTATE_REFRESH_TOKENS: issue a new refresh token every time the client refreshes.
    # BLACKLIST_AFTER_ROTATION: invalidate the old refresh token after rotation (requires 'rest_framework_simplejwt.token_blacklist' in INSTALLED_APPS).
    "ROTATE_REFRESH_TOKENS":  False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,  # updates User.last_login on every successful token obtain

    # ── Signing ───────────────────────────────────────────────────────────────
    "ALGORITHM":   "HS256",
    "SIGNING_KEY": SECRET_KEY,  # uses Django's SECRET_KEY to sign JWTs

    # ── Header format ─────────────────────────────────────────────────────────
    # Client must send:  Authorization: Bearer <access_token>
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME":  "HTTP_AUTHORIZATION",

    # ── Token claims ──────────────────────────────────────────────────────────
    "USER_ID_FIELD": "id",        # field from User model to include in token
    "USER_ID_CLAIM": "user_id",   # key name used in the JWT payload

    # ── Token classes ─────────────────────────────────────────────────────────
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM":   "token_type",
}

# ============================================ DRF SPECTACULAR ==================================================================================
SPECTACULAR_SETTINGS = {
    "TITLE": "Advaitam API",                                        # change this line according to your company
    "DESCRIPTION": (
        "Welcome to the **Advaitam API** documentation!\n\n"
        "Here you can explore all available API endpoints for the Advaitam Django project.\n\n"
        "- Use the endpoints below to interact with the system.\n"
        "- For help, contact [support@advaitam.com](mailto:support@advaitam.com).\n\n"
        "**Features:**\n"
        "- User authentication and JWT token management\n"
        "- CRUD operations for wishes, books, and more\n"
        "- Nested serializers and advanced API patterns\n\n"
        "_Enjoy using the API!_"
    ),
    "VERSION": "1.0.0",                                             # change this line according to your company
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    # "TAGS":[
    #     {
    #         "name":"apiviewset",
    #         "description":"This group provides CRUD operations for wishes. All endpoints require authentication."
    #     }
    # ]
}
#===========================================================================================================================
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

_csp_cloudfront = env("CSP_CLOUDFRONT_DOMAIN", default="")  # change this line according to your company (set your CloudFront domain)
_csp_cdn = (f"https://{_csp_cloudfront}",) if _csp_cloudfront else ()

_CSP_DIRECTIVES = {
    "default-src": ("'self'",),
    "script-src": ("'self'",)
    + _csp_cdn
    + (
        "'unsafe-inline'",              # Django admin inline scripts
        "https://accounts.google.com",  # Google Sign-In SDK
        "https://connect.facebook.net", # Facebook JS SDK
        "https://apis.google.com",      # Google API JS
    ),
    "style-src": ("'self'",) + _csp_cdn + ("'unsafe-inline'",),
    "img-src": (
        "'self'",
        "data:",
        "https:",
        "https://lh3.googleusercontent.com",   # Google profile pictures
        "https://avatars.githubusercontent.com", # GitHub avatars
        "https://graph.facebook.com",           # Facebook profile pictures
        "https://pbs.twimg.com",                # Twitter/X profile pictures
    ) + _csp_cdn,
    "font-src": ("'self'",) + _csp_cdn + ("https://fonts.gstatic.com",),
    "connect-src": (
        "'self'",
        "https://sentry.io",
        "https://*.sentry.io",
        "https://accounts.google.com",
        "https://oauth2.googleapis.com",
        "https://graph.facebook.com",
        "https://api.twitter.com",
        "https://api.github.com",
    ),
    "media-src":  ("'self'",) + _csp_cdn,
    "object-src": ("'none'",),
    "base-uri":   ("'self'",),
    "frame-src": (
        "'self'",
        "https://accounts.google.com",   # Google OAuth popup (if used)
        "https://staticxx.facebook.com", # Facebook SDK iframe
    ),
}

if DEBUG:
    # Report-only in dev: log violations in browser console, never block anything
    CONTENT_SECURITY_POLICY_REPORT_ONLY = {"DIRECTIVES": _CSP_DIRECTIVES}
else:
    # Enforce in production: violating resources are blocked by the browser
    CONTENT_SECURITY_POLICY = {"DIRECTIVES": _CSP_DIRECTIVES}

# ========== LOGGING ==========
LOGS_DIR = BASE_DIR / "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "django.log",
            "maxBytes": 1024 * 1024 * 15,  # 15 MB  # change this line according to your company (adjust log file size)
            "backupCount": 10,              # change this line according to your company (adjust number of backup log files)
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"] if DEBUG else ["file"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"] if DEBUG else ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["file"] if not DEBUG else [],
            "level": "ERROR",
            "propagate": False,
        },
        "django.autoreload": {
            "level": "WARNING",
            "handlers": ["console"] if DEBUG else ["file"],
        },
    },
}

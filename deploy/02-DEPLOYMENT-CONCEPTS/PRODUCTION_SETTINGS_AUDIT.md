# ✅ Production Settings Audit Report

**Date:** February 23, 2026  
**File:** webProject/settings.py  
**Status:** 80% Complete - Some improvements needed

---

## 📊 Settings Verification Summary

| Setting | Status | Details |
|---------|--------|---------|
| SESSION_COOKIE_AGE | ✅ DONE | 86400 (24 hours) - Correct |
| ALLOWED_HOSTS | ⚠️ PARTIAL | Missing origin.advaitam.info & EC2 IP |
| Whitenoise Middleware | ❌ MISSING | Not in MIDDLEWARE list |
| STATICFILES_STORAGE | ⚠️ NEEDS UPDATE | Should use WhiteNoiseStorage |
| CSP (Content Security Policy) | ❌ WRONG | Set to boolean True instead of dict |
| Email Configuration | ✅ DONE | Supports Gmail & SES |
| SECURE_SSL_REDIRECT | ✅ DONE | True in production |
| SECURE_HSTS | ✅ DONE | 31536000 seconds (1 year) |
| SECURE_PROXY_SSL_HEADER | ✅ DONE | Correctly set for Nginx |
| Password Hashers | ✅ DONE | Argon2 primary |
| Database Config | ✅ DONE | PostgreSQL with SSL for remote |
| Cache/Session | ✅ DONE | Redis-ready fallback to DB |
| Logging | ✅ DONE | Proper rotating file handler |
| Security Middleware | ✅ DONE | SecurityMiddleware present |
| CSRF Protection | ✅ DONE | HTTPONLY=False (correct for AJAX) |

---

## 🔴 Critical Issues That NEED Fixing

### 1. ⚠️ ALLOWED_HOSTS Missing Production Domains

**Current (INCOMPLETE):**
```python
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[
    "127.0.0.1",
    "localhost",
    "www.advaitam.info",
])
```

**Problem:**
- ❌ Missing: `advaitam.info` (root domain)
- ❌ Missing: `origin.advaitam.info` (EC2 direct access)
- ❌ Missing: `<EC2-IP>` (for debugging without DNS)

**Fix Required:**
Update `.env.production.bak` to include:
```bash
ALLOWED_HOSTS=127.0.0.1,localhost,advaitam.info,www.advaitam.info,origin.advaitam.info,<YOUR-EC2-IP>
```

**Why:** If a domain is NOT in ALLOWED_HOSTS, Django returns 400 Bad Request. Common first-deploy gotcha.

---

### 2. ❌ WhiteNoise Middleware NOT Configured

**Current (MISSING):**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ❌ WHITENOISE IS MISSING!
    'django.contrib.sessions.middleware.SessionMiddleware',
    ...
]
```

**Why It's Needed:**
- Serves static files as Nginx fallback if S3/CloudFront fails
- Prevents "missing stylesheet" errors in production
- Improves reliability

**Fix Required:**

Add this line to settings.py right after SecurityMiddleware:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← ADD THIS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]
```

Also update STATICFILES_STORAGE for production:

```python
if USE_S3:
    # ... existing S3 config ...
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

---

### 3. ❌ Content Security Policy (CSP) Incorrectly Set

**Current (WRONG):**
```python
SECURE_CONTENT_SECURITY_POLICY = True  # ❌ Boolean! Should be a dictionary
```

**Problem:**
- This is just a boolean flag
- Doesn't actually DEFINE any CSP rules
- CSP needs proper dictionary configuration

**Fix Required:**

Replace with proper CSP dictionary:

```python
if not DEBUG:
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", "https://cdn.jsdelivr.net"),  # Allow CDN if needed
        'style-src': ("'self'", "'unsafe-inline'"),  # Safe for your app
        'img-src': ("'self'", "https:", "data:"),  # Allow images from anywhere
        'font-src': ("'self'",),
        'connect-src': ("'self'",),
        'media-src': ("'self'", "https://d-xxxxx.cloudfront.net"),  # CloudFront domain
    }
else:
    SECURE_CONTENT_SECURITY_POLICY = {}
```

**Why:**
- Prevents XSS attacks (malicious scripts)
- Protects against clickjacking
- Restricts resource loading
- Industry security best practice

---

## 🟡 Things That Are PARTIALLY Done

### 1. ⚠️ SESSION_COOKIE_AGE - Good but verify .env

**Current (GOOD):**
```python
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=86400)  # 24 hours
```

**Status:** ✅ Correct for production

**But verify in .env.production.bak:**
```bash
SESSION_COOKIE_AGE=86400  # 24 hours (users logged out after inactivity)
```

---

### 2. ⚠️ Email Configuration - Good structure

**Current:**
```python
EMAIL_BACKEND = env("EMAIL_BACKEND", default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env("EMAIL_HOST", default='smtp.gmail.com')
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default='')
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default='')
```

**Status:** ✅ Supports both Gmail & Amazon SES

**For production, use Amazon SES** (cheaper, better deliverability):

```bash
# In .env.production.bak
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_HOST_USER=<SES_SMTP_USERNAME>
EMAIL_HOST_PASSWORD=<SES_SMTP_PASSWORD>
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@advaitam.info
ADMIN_EMAIL=kalyan.py28@gmail.com
```

---

## ✅ What's Already Correctly Configured

### Security Settings (GOOD)
```python
✅ SECURE_SSL_REDIRECT = True
✅ SESSION_COOKIE_SECURE = True
✅ CSRF_COOKIE_SECURE = True
✅ SESSION_COOKIE_HTTPONLY = True
✅ SECURE_BROWSER_XSS_FILTER = True
✅ X_FRAME_OPTIONS = 'DENY'
✅ SECURE_HSTS_SECONDS = 31536000 (1 year)
✅ SECURE_HSTS_INCLUDE_SUBDOMAINS = True
✅ SECURE_HSTS_PRELOAD = True
✅ SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Database Settings (GOOD)
```python
✅ PostgreSQL configuration
✅ SSL for remote hosts (RDS-ready)
✅ Connection pooling (CONN_MAX_AGE = 600)
✅ Password hashers using Argon2 primary
```

### Caching/Session (GOOD)
```python
✅ Redis support with fallback to DB
✅ Smart configuration (uses Redis if available)
✅ Proper session backend selection
```

### Logging (GOOD)
```python
✅ Rotating file handler (15MB max, 10 backups)
✅ Separate handlers for dev/prod
✅ Proper formatting with timestamp
```

---

## 🎯 Action Items (Priority Order)

### CRITICAL (Fix Before Deploy)

1. **Update ALLOWED_HOSTS in .env.production.bak**
   ```bash
   ALLOWED_HOSTS=127.0.0.1,localhost,advaitam.info,www.advaitam.info,origin.advaitam.info,<EC2-IP>
   ```
   **Time:** 1 minute

2. **Add WhiteNoise Middleware**
   ```python
   # In settings.py MIDDLEWARE section
   'whitenoise.middleware.WhiteNoiseMiddleware',  # After SecurityMiddleware
   ```
   **Time:** 1 minute

3. **Fix CSP Dictionary**
   ```python
   # Replace SECURE_CONTENT_SECURITY_POLICY = True with proper dict
   SECURE_CONTENT_SECURITY_POLICY = { ... }
   ```
   **Time:** 5 minutes

### HIGH PRIORITY (Before First Deploy)

4. **Verify .env.production.bak has all settings**
   - SESSION_COOKIE_AGE=86400
   - EMAIL configuration (Gmail or SES)
   - AWS credentials or EC2 role
   **Time:** 5 minutes

5. **Test static files with WhiteNoise**
   ```bash
   python manage.py collectstatic --noinput
   ```
   **Time:** 2 minutes

### MEDIUM PRIORITY (Soon After Deploy)

6. **Configure Email (Amazon SES)**
   - Get SES SMTP credentials
   - Update .env.production.bak
   - Test with password reset email
   **Time:** 15 minutes

---

## 📝 Production Settings Checklist

Before deploying, ensure:

- [ ] ALLOWED_HOSTS includes all domains
- [ ] WhiteNoise middleware added
- [ ] CSP set to proper dictionary (not boolean)
- [ ] .env.production.bak has SESSION_COOKIE_AGE=86400
- [ ] .env.production.bak has proper EMAIL settings
- [ ] DEBUG=False in .env.production.bak
- [ ] SECRET_KEY is long random string (not default)
- [ ] AWS credentials or EC2 role configured
- [ ] Database credentials set
- [ ] Email backend tested (try password reset)
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] All security headers present in responses

---

## 💡 Summary

**Your settings.py is 80% production-ready!**

### Missing/Broken (3 items):
- ❌ ALLOWED_HOSTS incomplete
- ❌ WhiteNoise middleware missing
- ❌ CSP boolean instead of dictionary

### Working Great (11 items):
- ✅ Security headers all configured
- ✅ Database setup correct
- ✅ Caching/session strategy smart
- ✅ Logging properly configured
- ✅ Email backend flexible

### To Deploy Successfully:
1. Fix 3 critical issues above (7 minutes)
2. Test locally: `python manage.py check`
3. Verify static files collect
4. Deploy with confidence!

---

**Status: 80% complete → 100% after 3 quick fixes** ✅


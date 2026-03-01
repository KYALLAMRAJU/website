# ⚡ storages.py - Quick Reference Guide

## One-Sentence Summary

**storages.py** = Custom S3 storage backend that tells Django how to save files to AWS S3 instead of your local disk.

---

## The 3 Key Links

```
┌──────────────────────┐
│   settings.py        │  ← Configuration
│   Line 263:          │
│   DEFAULT_FILE_      │
│   STORAGE =          │
│   'webapp.storages.' │
│   MediaStorage'      │
└──────────┬───────────┘
           │ (tells Django)
           ↓
┌──────────────────────┐
│  webapp/storages.py  │  ← Implementation
│  (2 classes)         │
│  - StaticStorage     │
│  - MediaStorage      │
└──────────┬───────────┘
           │ (inherits from)
           ↓
┌──────────────────────┐
│      AWS S3          │  ← Storage
│  advaitam-assets     │
│  bucket              │
└──────────────────────┘
```

---

## Where It's Used

| Scenario | File | Line | Usage |
|----------|------|------|-------|
| **Development** | settings.py | 237 | `USE_S3 = False` → NOT used |
| **Production** | settings.py | 237 | `USE_S3 = True` → LOADED |
| **Deployment** | deploy.sh | - | Installs `django-storages[s3]` |
| **Static Upload** | - | - | `python manage.py collectstatic` |
| **User Upload** | models.py | - | `ImageField.save()` (future) |

---

## File Content Summary

| Lines | Content | Purpose |
|-------|---------|---------|
| 1-32 | Docstring | Explains architecture |
| 33-34 | Imports | `S3Boto3Storage`, `settings` |
| 37-56 | StaticStorage class | For your app files (CSS, JS, audio, etc.) |
| 47 | `location = 'static'` | S3 folder: `s3://bucket/static/` |
| 59-80 | MediaStorage class | For user uploads (reserved) |
| 69 | `location = 'media'` | S3 folder: `s3://bucket/media/` |

---

## How It Works: 3 Steps

### Step 1: Activation (settings.py)
```python
# In .env.production.bak
USE_S3=True

# In settings.py (Line 263)
DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
# ↑ This string tells Django which class to use
```

### Step 2: Import (Django Runtime)
```python
# When Django needs to save a file:
import webapp.storages
MediaStorage = webapp.storages.MediaStorage
storage = MediaStorage()  # Create instance
```

### Step 3: Upload (S3 API)
```python
# storage.save() calls inherited method from S3Boto3Storage
# Which:
#   1. Reads self.location = 'media'
#   2. Builds S3 path: s3://advaitam-assets/media/filename
#   3. Connects to AWS API
#   4. Uploads file
#   5. Returns public URL
```

---

## StaticStorage vs MediaStorage

### StaticStorage

**What:** Your app files (you deploy them)

**Files:**
```
css/            ← Your stylesheets
js/             ← Your scripts
images/         ← Your images
audio/          ← Your audio files
books/          ← Your PDFs
admin/          ← Django admin CSS/JS
```

**Triggered by:**
```bash
python manage.py collectstatic --noinput
```

**S3 Location:**
```
s3://advaitam-assets/static/css/home.css
s3://advaitam-assets/static/audio/bhagavadgita/001.mp3
```

**Served as:**
```
https://xxxxx.cloudfront.net/static/css/home.css
```

---

### MediaStorage

**What:** User-uploaded files (users upload them)

**Files:**
```
profile_pics/   ← User profile pictures
uploads/        ← User-submitted files
```

**Triggered by:**
```python
# User uploads via form
profile_picture = models.ImageField(upload_to='profile_pics/')
# When saved, uses DEFAULT_FILE_STORAGE = MediaStorage
```

**S3 Location:**
```
s3://advaitam-assets/media/profile_pics/user123.jpg
```

**Served as:**
```
https://xxxxx.cloudfront.net/media/profile_pics/user123.jpg
```

**Current Status:** ❌ NOT USED (reserved for future)

---

## Configuration Chain

```
.env.production.bak
    ↓
    USE_S3=True
    AWS_STORAGE_BUCKET_NAME=advaitam-assets
    AWS_S3_CUSTOM_DOMAIN=xxxxx.cloudfront.net
    │
    └─→ settings.py reads these
        │
        ├─ Activates: DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
        ├─ Passes: AWS_S3_CUSTOM_DOMAIN to storages.py
        │
        └─→ storages.py
            │
            ├─ StaticStorage.location = 'static'
            │  └─ S3 path: s3://advaitam-assets/static/
            │
            └─ MediaStorage.location = 'media'
               └─ S3 path: s3://advaitam-assets/media/
               └─ custom_domain reads AWS_S3_CUSTOM_DOMAIN
                  └─ Returns: xxxxx.cloudfront.net
                     └─ Final URL: https://xxxxx.cloudfront.net/media/...
```

---

## Class Inheritance Diagram

```
S3Boto3Storage (from django-storages)
├── save(filename, content)      ← Uploads to S3
├── open(filename)               ← Reads from S3
├── delete(filename)             ← Deletes from S3
├── url(filename)                ← Returns S3 URL
└── exists(filename)             ← Checks if exists
    │
    └─ INHERITED BY
        │
        ├── StaticStorage (webapp/storages.py)
        │   ├── location = 'static'
        │   ├── file_overwrite = True
        │   └── custom_domain property
        │
        └── MediaStorage (webapp/storages.py)
            ├── location = 'media'
            ├── file_overwrite = False
            └── custom_domain property
```

---

## Quick Checklist

- [ ] `django-storages[s3]` installed? (in requirements-prod.txt)
- [ ] `USE_S3=True` in .env.production.bak?
- [ ] `AWS_STORAGE_BUCKET_NAME` set correctly?
- [ ] `AWS_S3_CUSTOM_DOMAIN` points to CloudFront?
- [ ] `DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'` in settings.py?
- [ ] `staticfiles/` directory exists for collectstatic?
- [ ] S3 bucket has OAC (Origin Access Control) configured?
- [ ] CloudFront distribution pointing to S3?

---

## Common Commands

### Deploy and Upload Static Files

```bash
# On EC2 server
python manage.py collectstatic --noinput

# This:
# 1. Finds all files in static/ and subdirectories
# 2. Imports StaticStorage from webapp/storages.py
# 3. Uploads each file to S3://advaitam-assets/static/
# 4. Result: All CSS, JS, images, audio on S3 ✅
```

### Check If storages.py Is Being Used

```bash
# Check if U
SE_S3 is True
grep "USE_S3" /home/advaitam/.env.production.bak

# Check S3 bucket
aws s3 ls s3://advaitam-assets/static/
```

### Troubleshoot

```bash
# Check if django-storages installed
python -c "from storages.backends.s3boto3 import S3Boto3Storage; print('OK')"

# Check if webapp.storages importable
python -c "from webapp.storages import MediaStorage; print('OK')"

# Check settings
python manage.py shell
>>> from django.conf import settings
>>> settings.DEFAULT_FILE_STORAGE
'webapp.storages.MediaStorage'
>>> settings.AWS_S3_CUSTOM_DOMAIN
'xxxxx.cloudfront.net'
```

---

## Real-World Example: User Uploads Profile Picture

```
User clicks upload button
    ↓
Form submitted to: POST /api/profile/
    ↓
Django view processes form:
    user.profile_picture = file
    user.save()
    ↓
    Django calls: profile_picture_field.save('profile.jpg', file_content)
    ↓
    Django checks: What is DEFAULT_FILE_STORAGE?
    
    In settings.py Line 263:
    DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
    ↓
    Django imports and instantiates:
    from webapp.storages import MediaStorage
    storage = MediaStorage()
    ↓
    Django calls:
    storage.save('profile_pics/user123.jpg', file_content)
    ↓
    S3Boto3Storage.save() does:
    - self.location = 'media'  ← From our class
    - Build path: s3://advaitam-assets/media/profile_pics/user123.jpg
    - Connect to AWS
    - Upload file
    - Return: https://advaitam-assets.s3.amazonaws.com/media/profile_pics/user123.jpg
             OR
             https://xxxxx.cloudfront.net/media/profile_pics/user123.jpg
    ↓
    Django saves URL to database:
    user.profile_picture = "media/profile_pics/user123.jpg"
    ↓
    In template: <img src="{{ user.profile_picture.url }}">
    ↓
    Browser displays: https://xxxxx.cloudfront.net/media/profile_pics/user123.jpg ✅
```

---

## File Size Reference

```
webapp/storages.py              83 lines
├── Docstring                   32 lines
├── Imports                     2 lines
├── StaticStorage class         20 lines
└── MediaStorage class          22 lines
```

Total: Very small file with big impact! 📦

---

## Key Takeaways

1. **Two Classes:** StaticStorage (your files) + MediaStorage (user uploads)

2. **One Connection:** settings.py → storages.py → S3

3. **One Trigger:** `collectstatic` for static files, file upload for media

4. **One Destination:** AWS S3 bucket (advaitam-assets)

5. **One Frontend:** CloudFront CDN serving files globally

**Everything flows through this 83-line file!** 🎯



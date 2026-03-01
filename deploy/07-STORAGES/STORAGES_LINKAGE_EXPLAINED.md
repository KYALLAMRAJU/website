# 🔗 How storages.py is Linked to Your Advaitam Project

## Overview: Connection Points

`storages.py` is connected to your Django project through **3 main linkage points**:

```
┌──────────────────────────────────────────────────────────────┐
│                    Your Django Project                        │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ (3 connections)
                            ↓
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ↓                   ↓                   ↓
    
  1️⃣ settings.py    2️⃣ deploy.sh         3️⃣ collectstatic
  (Configuration)   (Setup)              (Deployment)
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ↓
                    webapp/storages.py
                    (2 Custom Classes)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ↓                   ↓                   ↓
        
   StaticStorage    MediaStorage         S3 Bucket
   (Your files)     (User uploads)      (advaitam-assets)
```

---

## 📌 LINKAGE POINT #1: settings.py Configuration (Lines 237-291)

### The Connection:

In `webProject/settings.py`, when **`USE_S3=True`** in your `.env.production.bak`:

```python
# Line 237: Check if S3 is enabled
USE_S3 = env.bool('USE_S3', default=False)

if USE_S3:
    # Lines 239-291: AWS S3 Configuration
    
    # Line 263: Link to StaticStorage
    DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
```

### What This Means:

| Setting | Purpose | Links To |
|---------|---------|----------|
| `USE_S3=True` | Enables S3 storage mode | `webapp/storages.py` is loaded |
| `DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'` | User uploads use MediaStorage | `webapp/storages.py` line 67 |
| `AWS_S3_CUSTOM_DOMAIN` | CloudFront domain | Passed to `storages.py` via `settings` |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name | `'advaitam-assets'` |

### Code Flow:

```python
# In settings.py (Line 263)
DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
    └─ This tells Django to use MediaStorage class from webapp/storages.py
    └─ When a user uploads a file, Django calls MediaStorage to save it to S3

# In webapp/storages.py (Line 67-80)
class MediaStorage(S3Boto3Storage):
    location = 'media'
    # ... configuration ...
```

---

## 📌 LINKAGE POINT #2: deploy.sh Execution

### Where It's Used:

In `deploy.sh` (the deployment script), `storages.py` is indirectly linked through:

#### Step 1: Install Requirements
```bash
pip install -r requirements-prod.txt
```

**requirements-prod.txt includes:**
```
django-storages[s3]   # ← This is the package that provides S3Boto3Storage
boto3                 # ← AWS SDK that actually communicates with S3
```

#### Step 2: Set Environment Variables on EC2
```bash
echo "USE_S3=True" >> /home/advaitam/.env.production.bak
echo "AWS_STORAGE_BUCKET_NAME=advaitam-assets" >> /home/advaitam/.env.production.bak
echo "AWS_S3_CUSTOM_DOMAIN=xxxx.cloudfront.net" >> /home/advaitam/.env.production.bak
```

These env vars are read by `settings.py` → which activates `storages.py`.

#### Step 3: Run collectstatic
```bash
python manage.py collectstatic --noinput
```

**This is where storages.py is actually USED:**

```
python manage.py collectstatic
    ↓
Django reads settings.py
    ↓
Finds: DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
    ↓
Imports: from webapp.storages import MediaStorage
    ↓
Instantiates MediaStorage class
    ↓
Uses it to upload static files to S3!
    ↓
Files end up at: s3://advaitam-assets/static/
```

---

## 📌 LINKAGE POINT #3: collectstatic Command (Deployment Action)

### What Happens When You Deploy:

```bash
$ python manage.py collectstatic --noinput
```

This command:

1. **Scans your entire project** for static files:
   ```
   static/css/home.css
   static/js/audio.js
   static/images/adishankaracharya.jpg
   static/audio/bhagavadgita/001.mp3
   ... and so on
   ```

2. **Calls storages.py** for each file:
   ```python
   # Inside Django (using storages.py)
   for file in collected_files:
       storage = StaticStorage()  # ← Instantiates your custom class
       storage.save(file_path, file_content)  # ← Uploads to S3
   ```

3. **StaticStorage class handles S3 upload:**
   ```python
   class StaticStorage(S3Boto3Storage):
       location = 'static'  # ← All files go to s3://bucket/static/
       file_overwrite = True  # ← Replace old files
   ```

4. **Result: All files on S3**
   ```
   S3 Bucket: advaitam-assets
   ├── static/
   │   ├── css/home.css
   │   ├── js/audio.js
   │   ├── images/
   │   ├── audio/
   │   ├── books/
   │   ├── fonts/
   │   └── admin/  (auto-added by Django)
   └── media/  (reserved for future user uploads)
   ```

---

## 🗺️ Complete Architecture Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your Code                               │
│                     (Local Machine)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  webapp/                                                        │
│  ├── storages.py  ← 2 custom storage classes defined here      │
│  │   ├── StaticStorage (S3 location = 'static')                │
│  │   └── MediaStorage (S3 location = 'media')                  │
│  └── ...                                                        │
│                                                                 │
│  webProject/                                                    │
│  └── settings.py                                               │
│      ├── USE_S3 = True (from .env)                             │
│      ├── DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage' │
│      └── AWS_S3_CUSTOM_DOMAIN = 'xxxx.cloudfront.net'          │
│                                                                 │
│  deploy.sh  ← Runs on EC2 server                               │
│  ├── pip install django-storages[s3]                           │
│  ├── Set AWS credentials in .env                               │
│  └── python manage.py collectstatic                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ (deploy.sh runs on EC2)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Infrastructure                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  EC2 Instance (origin.advaitam.info)                           │
│  ├── /home/advaitam/app/webapp/storages.py (copied)            │
│  ├── /home/advaitam/app/webProject/settings.py (copied)        │
│  └── .env.production.bak (AWS credentials)                         │
│                                                                 │
│  CloudFront Distribution (advaitam.info)                       │
│  └── Origin: origin.advaitam.info (EC2)                        │
│  └── S3 Cache Behavior: /static/ → S3 bucket                   │
│                                                                 │
│  S3 Bucket: advaitam-assets                                    │
│  ├── /static/ (all your app files uploaded by collectstatic)   │
│  │   ├── css/home.css                                          │
│  │   ├── js/audio.js                                           │
│  │   ├── images/adishankaracharya.jpg                          │
│  │   ├── audio/bhagavadgita/001.mp3                            │
│  │   ├── books/Django.pdf                                      │
│  │   └── admin/ (Django admin static files)                    │
│  └── /media/ (reserved for future user uploads)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Real-World Request Flow (With storages.py)

### User Visits Your Site:

```
User types: https://advaitam.info
        │
        ↓
CloudFront CDN checks:
  "Is this a static file request?"
        │
        ├─ YES (e.g., /static/css/home.css)
        │   └─ Serve from: S3 bucket path configured in storages.py
        │      └─ StaticStorage.location = 'static'
        │         └─ Returns: https://xxxx.cloudfront.net/static/css/home.css
        │
        └─ NO (e.g., /api/, /audio/)
            └─ Forward to EC2 origin (Nginx → Gunicorn → Django)
               └─ Django returns HTML with:
                  <link rel="stylesheet" href="/static/css/home.css">
                  └─ Browser downloads from CloudFront (which has S3 as origin)
```

### When collectstatic Runs (Deployment):

```
$ python manage.py collectstatic --noinput

    ↓

Django reads settings.py:
  DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
  
    ↓

Imports webapp/storages.py
  from storages.backends.s3boto3 import S3Boto3Storage
  class MediaStorage(S3Boto3Storage):
      location = 'media'
      ...
  
    ↓

For each static file found:
  storage_instance = MediaStorage()
  storage_instance.save('audio/bhagavadgita/001.mp3', file_content)
  
    ↓

Files uploaded to S3:
  s3://advaitam-assets/media/audio/bhagavadgita/001.mp3
  (Note: Actually StaticStorage is used for collectstatic, not MediaStorage)
```

---

## 📋 storages.py Classes Explained

### Class 1: StaticStorage

```python
class StaticStorage(S3Boto3Storage):
    location = 'static'         # S3 path prefix: s3://bucket/static/
    default_acl = None          # No public ACL (CloudFront controls access)
    querystring_auth = False    # No signed URLs (public via CloudFront)
    file_overwrite = True       # Replace old files on collectstatic
```

**Used For:**
- CSS files
- JavaScript files
- Images you provide
- Audio files you provide
- PDF books you provide
- Fonts
- Django admin static files

**How It's Loaded:**
```python
# In settings.py (when USE_S3=True)
# (Currently uses WhiteNoise, but StaticStorage is the pattern)
```

**Upload Trigger:**
```bash
python manage.py collectstatic --noinput
```

### Class 2: MediaStorage

```python
class MediaStorage(S3Boto3Storage):
    location = 'media'          # S3 path prefix: s3://bucket/media/
    default_acl = None          # No public ACL (CloudFront controls access)
    querystring_auth = False    # No signed URLs (public via CloudFront)
    file_overwrite = False      # Keep all uploads (no overwrite)
```

**Used For:**
- User-uploaded profile pictures (if you add this feature)
- User-submitted audio files (if you add this feature)
- Any user-uploaded content

**How It's Loaded:**
```python
# In settings.py (Line 263)
DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
```

**Upload Trigger:**
```python
# In a Django form/model
class UserProfile(models.Model):
    profile_picture = models.ImageField(upload_to='profile_pics/')
    # When user uploads, Django uses MediaStorage (because DEFAULT_FILE_STORAGE)
```

---

## 🔑 Key AWS Configuration Variables

These are defined in `settings.py` and read by `storages.py`:

```python
# From .env.production.bak (read by settings.py)
AWS_STORAGE_BUCKET_NAME = 'advaitam-assets'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN = 'xxxxx.cloudfront.net'
AWS_ACCESS_KEY_ID = ''  # Empty = use EC2 IAM Role
AWS_SECRET_ACCESS_KEY = ''  # Empty = use EC2 IAM Role
```

**In storages.py:**
```python
@property
def custom_domain(self):
    # Reads AWS_S3_CUSTOM_DOMAIN from settings
    return getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
```

---

## 🚀 Deployment Sequence (How Everything Connects)

### Step 1: Local Development (storages.py NOT used)
```
USE_S3 = False (in .env)
    ↓
settings.py loads local storage config:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATIC_URL = 'static/'
    ↓
Files served from: /home/advaitam/app/staticfiles/
storages.py: NOT IMPORTED
```

### Step 2: Production Deployment (storages.py IS used)

```
Run: bash deploy.sh
    │
    ├─ pip install -r requirements-prod.txt
    │   └─ Installs django-storages[s3]
    │
    ├─ echo "USE_S3=True" >> .env.production.bak
    │   └─ Enables S3 mode
    │
    ├─ python manage.py collectstatic --noinput
    │   └─ Reads: settings.py
    │   └─ Imports: webapp/storages.py
    │   └─ Uploads all files to S3 using StaticStorage/MediaStorage
    │   └─ Result: s3://advaitam-assets/static/...
    │
    └─ systemctl restart advaitam
        └─ Django app starts
        └─ Whenever users access static URLs, they come from S3 via CloudFront
```

---

## ❓ FAQ

### Q: Is storages.py used in development?
**A:** No. During development (`USE_S3=False`), files are served from local disk. `storages.py` is only imported when `USE_S3=True` in production.

### Q: What happens if I don't have storages.py?
**A:** Django won't have a custom S3 storage backend. You'd need to define StaticStorage and MediaStorage somewhere else or use the default django-storages classes.

### Q: Can I use storages.py without CloudFront?
**A:** Yes. You can set `AWS_S3_CUSTOM_DOMAIN` to just the S3 URL (`advaitam-assets.s3.amazonaws.com`). But CloudFront gives you global edge caching for free.

### Q: What's the difference between StaticStorage and MediaStorage?
**A:** 
- **StaticStorage:** Your app files (CSS, JS, audio, PDFs) — use `file_overwrite=True`
- **MediaStorage:** User uploads (if added later) — use `file_overwrite=False`

### Q: Where are the actual AWS credentials?
**A:** In `.env.production.bak` on the EC2 server (not in storages.py). Or better: use EC2 IAM Role (empty credentials in settings, AWS SDK reads role automatically).

---

## 📊 Linkage Summary Table

| Connection | Location | What It Does | Links To |
|-----------|----------|-------------|----------|
| **settings.py** | `webProject/settings.py:263` | Imports `DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'` | `webapp/storages.py` |
| **deploy.sh** | `deploy.sh` | Installs `django-storages[s3]`, sets env vars | Enables `storages.py` usage |
| **collectstatic** | `python manage.py collectstatic` | Calls storage classes to upload files | Uses `StaticStorage` class |
| **User upload** | Form submission | Calls storage class to save upload | Uses `MediaStorage` class |
| **.env** | `.env.production.bak` | Provides AWS credentials & bucket name | Read by `settings.py` → passed to `storages.py` |
| **django-storages** | `pip install django-storages[s3]` | Provides `S3Boto3Storage` base class | Inherited by `storages.py` |

---

## 🎯 In Summary

1. **settings.py** = Configuration hub that enables storages.py
2. **storages.py** = Custom S3 storage classes
3. **deploy.sh** = Installs dependencies and triggers collectstatic
4. **collectstatic** = Actual command that uses storages.py to upload files to S3
5. **S3 bucket** = Final destination where files are stored
6. **CloudFront** = Serves files from S3 with global caching

All connected through environment variables and Django's storage backend system! 🔗



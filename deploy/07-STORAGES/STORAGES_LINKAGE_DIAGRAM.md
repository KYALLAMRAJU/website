# 🔗 storages.py Connection Diagram

## File Tree Showing Connections

```
webProject/
│
├── webProject/
│   ├── settings.py
│   │   ├── Line 237: USE_S3 = env.bool('USE_S3', default=False)
│   │   ├── Line 263: DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'  ← LINKS TO webapp/storages.py
│   │   ├── Line 298: STATICFILES_STORAGE = 'webapp.storages.StaticStorage'  ← LINKS TO webapp/storages.py
│   │   ├── Line 240: AWS_STORAGE_BUCKET_NAME = 'advaitam-assets'
│   │   ├── Line 241: AWS_S3_REGION_NAME = 'us-east-1'
│   │   ├── Line 245: AWS_S3_CUSTOM_DOMAIN = xxxx.cloudfront.net
│   │   └── Line 260: MEDIA_ROOT = BASE_DIR / 'media'
│   └── __init__.py
│
├── webapp/
│   ├── storages.py  ← THIS FILE IS THE LINK
│   │   ├── class StaticStorage(S3Boto3Storage):
│   │   │   ├── location = 'static'
│   │   │   ├── default_acl = None
│   │   │   ├── querystring_auth = False
│   │   │   └── file_overwrite = True
│   │   │
│   │   └── class MediaStorage(S3Boto3Storage):
│   │       ├── location = 'media'
│   │       ├── default_acl = None
│   │       ├── querystring_auth = False
│   │       └── file_overwrite = False
│   │
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── .env.production.bak  (on EC2 server)
│   ├── USE_S3=True
│   ├── AWS_STORAGE_BUCKET_NAME=advaitam-assets
│   ├── AWS_S3_CUSTOM_DOMAIN=xxxxx.cloudfront.net
│   └── AWS_ACCESS_KEY_ID=... (or empty for IAM Role)
│
└── deploy.sh
    ├── pip install django-storages[s3]  ← Installs base class for storages.py
    └── python manage.py collectstatic --noinput  ← Uses storages.py to upload files
```

---

## Flow Diagram: From Code to S3

```
DEVELOPMENT MODE (USE_S3=False)
═════════════════════════════════

settings.py
├─ USE_S3 = False
└─ STATIC_URL = 'static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   ↓
Files served from:
  /home/advaitam/app/staticfiles/
  
storages.py: NOT USED ❌


PRODUCTION MODE (USE_S3=True)
══════════════════════════════

settings.py
├─ USE_S3 = True
├─ AWS_STORAGE_BUCKET_NAME = 'advaitam-assets'
├─ AWS_S3_CUSTOM_DOMAIN = 'xxxxx.cloudfront.net'
└─ DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
   ↓
   Imports from webapp/storages.py:
   ├─ StaticStorage class
   └─ MediaStorage class
      ↓
      When collectstatic runs:
      ├─ For each static file:
      │  ├─ Creates StaticStorage instance
      │  ├─ Calls storage.save(filename, content)
      │  └─ Uploads to S3
      │     ↓
      │     S3 Bucket: advaitam-assets
      │     └─ /static/css/home.css
      │     └─ /static/js/audio.js
      │     └─ /static/audio/bhagavadgita/001.mp3
      │     └─ /static/admin/... (Django admin)
      │
      └─ When user uploads file:
         ├─ Creates MediaStorage instance
         ├─ Calls storage.save(filename, content)
         └─ Uploads to S3
            ↓
            S3 Bucket: advaitam-assets
            └─ /media/profile_pics/user123.jpg
            └─ /media/uploads/audio.mp3
               (Currently not used, reserved for future)
               
      ↓
      CloudFront CDN
      ├─ Caches files from S3
      └─ Serves to users globally
         ↓
         Browser receives:
         GET https://xxxxx.cloudfront.net/static/css/home.css
         ← Returns 200 (cached on edge server)
```

---

## Connection Points: 3 Main Links

```
┌─────────────────────────────────────┐
│         settings.py (Line 263)       │
│  DEFAULT_FILE_STORAGE =             │
│  'webapp.storages.MediaStorage'      │
└────────────────┬────────────────────┘
                 │ (String path)
                 ↓
┌─────────────────────────────────────┐
│      webapp/storages.py             │
│  ┌─────────────────────────────────┐│
│  │  class MediaStorage:            ││
│  │    location = 'media'           ││
│  │    default_acl = None           ││
│  │    querystring_auth = False     ││
│  │    file_overwrite = False       ││
│  └─────────────────────────────────┘│
└────────────────┬────────────────────┘
                 │ (Instantiated)
                 ↓
┌─────────────────────────────────────┐
│  S3Boto3Storage (base class)        │
│  (from django-storages)             │
└────────────────┬────────────────────┘
                 │ (Inherits from)
                 ↓
┌─────────────────────────────────────┐
│    AWS S3 Bucket API                │
│  PUT /advaitam-assets/media/...     │
└─────────────────────────────────────┘
```

---

## Call Stack When File Is Uploaded

```
User submits form with file
    ↓
Django form processes file
    ↓
model.save() → FileField.save()
    ↓
FileField calls:
  storage = DEFAULT_FILE_STORAGE  ← Looks at settings.py
    ↓
    'webapp.storages.MediaStorage'  ← Found!
    ↓
Django imports:
  from webapp.storages import MediaStorage
    ↓
Django creates instance:
  storage_instance = MediaStorage()
    ↓
Django calls:
  storage_instance.save(filename, file_content)
    ↓
MediaStorage.save() (from S3Boto3Storage):
  ├─ location = 'media'  ← From storages.py
  ├─ Creates S3 path: s3://advaitam-assets/media/{filename}
  ├─ Connects to AWS S3 API
  └─ Uploads file
      ↓
      S3 stores file
      ↓
      File URL generated:
      https://advaitam-assets.s3.amazonaws.com/media/{filename}
      OR (with CloudFront):
      https://xxxxx.cloudfront.net/media/{filename}
```

---

## Where storages.py Is Referenced

### 1. In settings.py

**File:** `webProject/settings.py`

```python
# Line 263
DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
  └─ When users upload files, use MediaStorage from webapp/storages.py
  
# Line 260
MEDIA_ROOT = BASE_DIR / 'media'
  └─ S3 destination configured in storages.py as location='media'
```

### 2. In deploy.sh

**File:** `deploy.sh` (not shown in this repo, but mentioned in DEPLOYMENT_CONCEPTS)

```bash
pip install -r requirements-prod.txt
  └─ Installs: django-storages[s3]  (provides S3Boto3Storage base class)
  
python manage.py collectstatic --noinput
  └─ Uses StaticStorage class from webapp/storages.py
  └─ Uploads all static files to S3
```

### 3. In requirements-prod.txt

**File:** `requirements-prod.txt`

```
django-storages[s3]  ← Dependency that storages.py inherits from
boto3                ← AWS SDK that actually communicates with S3
```

### 4. During Runtime

**When collectstatic runs:**
```bash
python manage.py collectstatic --noinput
  ↓
Loads settings.py
  ↓
Reads: USE_S3=True
  ↓
Imports: webapp.storages.StaticStorage
  ↓
For each file in static/:
  storage = StaticStorage()
  storage.save(file_path, file_content)
  ↓
Files uploaded to S3://advaitam-assets/static/
```

**When users upload files (future feature):**
```
User submits upload form
  ↓
Django model saves file
  ↓
Reads: DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
  ↓
Imports: webapp.storages.MediaStorage
  ↓
storage = MediaStorage()
storage.save(filename, file_content)
  ↓
File uploaded to S3://advaitam-assets/media/
```

---

## Environment Variables → storages.py

```
.env.production.bak (on EC2)
├─ USE_S3=True
│   └─ Enables S3 mode in settings.py
│      └─ Activates storages.py usage
│
├─ AWS_STORAGE_BUCKET_NAME=advaitam-assets
│   └─ Read by settings.py
│      └─ Passed to storages.py (via S3Boto3Storage base class)
│         └─ S3Boto3Storage.save() uses this bucket
│
├─ AWS_S3_REGION_NAME=us-east-1
│   └─ AWS region for the bucket
│
├─ AWS_S3_CUSTOM_DOMAIN=xxxxx.cloudfront.net
│   └─ CloudFront domain
│      └─ storages.py uses this in @property custom_domain()
│         └─ Returns: https://xxxxx.cloudfront.net/static/...
│
├─ AWS_ACCESS_KEY_ID=(empty for IAM Role)
│   └─ AWS credentials (or leave empty, use EC2 IAM Role)
│
└─ AWS_SECRET_ACCESS_KEY=(empty for IAM Role)
    └─ AWS credentials (or leave empty, use EC2 IAM Role)
```

---

## Data Flow: Complete Journey

```
STEP 1: DEVELOPER ACTION
═════════════════════════
$ git push origin main
  └─ Code pushed to GitHub, including webapp/storages.py

STEP 2: DEPLOYMENT START
═════════════════════════
$ bash deploy.sh (on EC2)
  ├─ Clones repo: git clone ... /home/advaitam/app
  │   └─ webapp/storages.py copied to EC2
  │
  ├─ pip install -r requirements-prod.txt
  │   └─ Installs django-storages[s3] package
  │      └─ Provides S3Boto3Storage base class
  │
  └─ Set environment variables in .env.production.bak
      └─ USE_S3=True
      └─ AWS credentials
      └─ S3 bucket name

STEP 3: COLLECTSTATIC EXECUTION
═════════════════════════════════
$ python manage.py collectstatic --noinput
  ├─ Django loads settings.py
  │  └─ Sees: USE_S3=True
  │  └─ Reads: DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
  │
  ├─ Imports webapp/storages.py
  │  ├─ Loads StaticStorage class
  │  └─ Loads MediaStorage class
  │
  ├─ Scans project for static files
  │  └─ static/css/home.css
  │  └─ static/js/audio.js
  │  └─ static/images/adishankaracharya.jpg
  │  └─ static/audio/bhagavadgita/...
  │  └─ ...
  │
  └─ For each file:
      storage_instance = StaticStorage()
      storage_instance.save(file_path, content)
      
STEP 4: S3 UPLOAD (storages.py Does This)
═════════════════════════════════════════════
MediaStorage.save() called:
  ├─ self.location = 'static'  ← From storages.py definition
  ├─ S3 path: s3://advaitam-assets/static/css/home.css
  ├─ Connects to AWS S3 API (via boto3)
  ├─ Uploads file content
  └─ Returns public URL:
      https://advaitam-assets.s3.amazonaws.com/static/css/home.css
      OR:
      https://xxxxx.cloudfront.net/static/css/home.css

STEP 5: RUNTIME (Live Server)
═══════════════════════════════
User visits: https://advaitam.info
  ├─ Django renders HTML:
  │  └─ <link rel="stylesheet" href="/static/css/home.css">
  │
  ├─ Browser makes request: GET /static/css/home.css
  │  └─ Nginx proxies to Django
  │  └─ Django sees /static/ URL
  │  └─ Django returns 302 redirect:
  │      Location: https://xxxxx.cloudfront.net/static/css/home.css
  │
  ├─ Browser requests: https://xxxxx.cloudfront.net/static/css/home.css
  │  └─ CloudFront checks cache
  │  └─ Not cached? Fetch from S3
  │  └─ Cache it for 1 year
  │  └─ Return to browser
  │
  └─ Browser receives CSS
      └─ Page styles applied ✅

STEP 6: FUTURE USER UPLOAD (When Feature Added)
═════════════════════════════════════════════════
User uploads profile picture
  ├─ Form submitted to Django
  │
  ├─ Django calls: profile_picture_field.save(filename, file)
  │  └─ Reads: DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
  │
  ├─ Creates: MediaStorage instance
  │
  ├─ Calls: storage.save(filename, file_content)
  │  └─ self.location = 'media'  ← From storages.py definition
  │  └─ S3 path: s3://advaitam-assets/media/profile_pics/user.jpg
  │  └─ Uploads to S3
  │
  └─ Stores URL in database:
      media/profile_pics/user.jpg
      └─ When displaying, Django generates:
         https://xxxxx.cloudfront.net/media/profile_pics/user.jpg
```

---

## Summary: Connection Points

| # | Component | Location | Links To | Purpose |
|---|-----------|----------|----------|---------|
| 1 | settings.py | `webProject/settings.py:263` | webapp/storages.py | Configures which storage class to use |
| 2 | storages.py | `webapp/storages.py` | S3Boto3Storage | Defines custom S3 behavior |
| 3 | deploy.sh | EC2 server | django-storages[s3] | Installs dependency |
| 4 | django-storages | pip package | AWS S3 API | Provides base class for S3 uploads |
| 5 | .env.production.bak | EC2 server | settings.py | AWS credentials & bucket config |
| 6 | S3 bucket | AWS | Web browsers | Final storage location |
| 7 | CloudFront | AWS | S3 & browsers | Global delivery network |

Everything is **connected through settings.py → storages.py → S3**! 🎯



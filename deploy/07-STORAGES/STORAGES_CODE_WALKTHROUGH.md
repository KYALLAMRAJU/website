# 📖 storages.py - Annotated Code Walkthrough

## File Location & Purpose

**File:** `D:\webProject\webapp\storages.py`

**Purpose:** Defines custom AWS S3 storage backends for your Django project

**Size:** 83 lines

**Dependency:** `django-storages[s3]` package (installed via requirements-prod.txt)

---

## Complete Code with Annotations

```python
"""
Line 1-32: MODULE DOCSTRING
═══════════════════════════════
Explains the architecture and file structure.
Custom S3 + CloudFront storage backends for Advaitam production.
"""
"""
Custom S3 + CloudFront storage backends for Advaitam production.

Architecture:
  Single S3 bucket (advaitam-assets) with two path prefixes:
    /static/  — CSS, JS, fonts, PDFs, audio files, images
                (long-lived, immutable cache — these are files YOU deploy, not user uploads)
    /media/   — user-uploaded content (reserved for future use;
                currently this project has no user file uploads)

  What lives under /static/ in THIS project:
    - css/          → stylesheets (home.css, etc.)
    - js/           → javascript (audio.js, etc.)
    - images/       → site images (adishankaracharya.jpg, India.png, etc.)
    - audio/        → audio recitations (bhagavadgita, grantha, sutra, upanisad, vidyaranya)
    - books/        → PDF files (Django.pdf, etc.)
    - fonts/        → web fonts (if added in future)
    - admin/        → Django admin static files (auto-collected by collectstatic)

  CloudFront CDN sits in front of S3 via OAC (Origin Access Control).
  All URLs point to the CloudFront domain (AWS_S3_CUSTOM_DOMAIN in .env)
  instead of the raw S3 URL — this gives global edge caching at no extra cost.

  Set in .env:
    USE_S3=True
    AWS_STORAGE_BUCKET_NAME=advaitam-assets
    AWS_S3_CUSTOM_DOMAIN=xxxxxxxxxxxx.cloudfront.net   ← CloudFront domain
"""

# Line 33-34: IMPORTS
# ═════════════════════
# S3Boto3Storage: Base class from django-storages
#   Provides all S3 upload/download functionality
#   We inherit from it to customize behavior
from storages.backends.s3boto3 import S3Boto3Storage

# settings: Django settings module
#   We use this to read AWS_S3_CUSTOM_DOMAIN from settings.py
from django.conf import settings


# Line 37-60: CLASS 1 - StaticStorage
# ═════════════════════════════════════
class StaticStorage(S3Boto3Storage):
    """
    Static files — files YOU deploy as part of the project (not user uploads).
    Includes: CSS, JavaScript, images, audio recitations, PDFs, fonts, Django admin files.

    Stored at: s3://advaitam-assets/static/
    Served via: https://<cloudfront-domain>/static/
    Cache: 1 year (immutable assets versioned by Django's ManifestStaticFilesStorage)

    Folder structure after collectstatic uploads to S3:
      static/css/         → home.css etc.
      static/js/          → audio.js etc.
      static/images/      → adishankaracharya.jpg, India.png, SrinivasaRao.png, USA.png
      static/audio/       → bhagavadgita/, grantha/, sutra/, upanisad/, vidyaranya/
      static/books/       → Django.pdf etc.
      static/fonts/       → web fonts (if added)
      static/admin/       → Django admin CSS/JS/images (auto-added by collectstatic)
    """
    
    # Line 47-48: S3 LOCATION PREFIX
    # All files go to: s3://advaitam-assets/static/
    location = 'static'
    
    # Line 49: ACL PERMISSION
    # default_acl = None means:
    #   - Don't use S3 public ACLs
    #   - Instead, use CloudFront Origin Access Control (OAC)
    #   - OAC = only CloudFront can access S3 (not public)
    #   - More secure than public ACLs
    default_acl = None
    
    # Line 50: SIGNED URLS
    # querystring_auth = False means:
    #   - Don't add ?Signature=xxx to URLs
    #   - URLs are public (anyone can access)
    #   - Good because files are public (CSS, JS, images)
    querystring_auth = False
    
    # Line 51: FILE OVERWRITE BEHAVIOR
    # file_overwrite = True means:
    #   - When you run collectstatic again, overwrite existing files
    #   - Intended behavior (always use latest version)
    #   - This is what you want for static assets
    file_overwrite = True

    # Line 53-56: CUSTOM DOMAIN PROPERTY
    # ═════════════════════════════════════
    @property
    def custom_domain(self):
        """
        Returns the CloudFront domain from settings.py
        
        How it works:
          1. Django reads .env.production.bak
          2. Sets AWS_S3_CUSTOM_DOMAIN = "xxxxx.cloudfront.net"
          3. This value is stored in settings.py (Line 245)
          4. We read it here to use in URLs
          
        Example:
          settings.AWS_S3_CUSTOM_DOMAIN = "abc123def456.cloudfront.net"
          self.custom_domain returns "abc123def456.cloudfront.net"
          Final URL: https://abc123def456.cloudfront.net/static/css/home.css
        """
        # getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
        #   = Try to get AWS_S3_CUSTOM_DOMAIN from settings
        #   = If not found, return None
        return getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)


# Line 59-80: CLASS 2 - MediaStorage
# ═════════════════════════════════════
class MediaStorage(S3Boto3Storage):
    """
    Media files — user-uploaded content (e.g. profile pictures, user-submitted files).
    Stored at: s3://advaitam-assets/media/
    Served via: https://<cloudfront-domain>/media/
    Cache: 7 days (CloudFront behavior TTL)

    NOTE: This project currently has NO user file uploads.
    MediaStorage is defined here and ready to use if you add upload features in future
    (e.g. user profile photos, user-submitted audio, etc.)
    DO NOT confuse with StaticStorage — audio/images/PDFs in your project are YOUR files,
    not user uploads, so they go under StaticStorage above.
    """
    
    # Line 69: S3 LOCATION PREFIX
    # All user-uploaded files go to: s3://advaitam-assets/media/
    location = 'media'
    
    # Line 70: ACL PERMISSION
    # Same as StaticStorage: use CloudFront OAC, not public ACLs
    default_acl = None
    
    # Line 71: SIGNED URLS
    # querystring_auth = False means:
    #   - Public URLs (anyone can access with URL)
    #   - Good for user uploads you want to make public
    querystring_auth = False
    
    # Line 72: FILE OVERWRITE BEHAVIOR
    # file_overwrite = False means:
    #   - Don't overwrite existing uploads
    #   - If user uploads photo.jpg twice, both are kept:
    #     photo.jpg
    #     photo_abc123xyz789.jpg  (unique suffix added)
    #   - Prevents accidental data loss
    file_overwrite = False

    # Line 74-80: CUSTOM DOMAIN PROPERTY
    # ═════════════════════════════════════
    @property
    def custom_domain(self):
        """
        Same as StaticStorage - returns CloudFront domain from settings.py
        
        Example:
          User uploads: "my_photo.jpg"
          Django saves to: s3://advaitam-assets/media/my_photo.jpg
          Served as: https://abc123def456.cloudfront.net/media/my_photo.jpg
        """
        return getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
```

---

## How Each Class Is Used

### StaticStorage - Used by Django's collectstatic

```python
# When you run: python manage.py collectstatic --noinput

# Step 1: Django reads settings.py
# Step 2: Finds USE_S3=True
# Step 3: For static files (CSS, JS, images, audio, PDFs):
#   - Scans: static/ folder
#   - Scans: webapp/static/ folder
#   - Scans: admin static files (auto-included by Django)

# Step 4: For each file:
#   storage = StaticStorage()  ← Instance created
#   storage.save(file_path, file_content)  ← Calls inherited save() from S3Boto3Storage
#   
#   S3Boto3Storage.save() does:
#     ├─ self.location = 'static'  ← Read from our class
#     ├─ Build S3 path: s3://advaitam-assets/static/css/home.css
#     ├─ Connect to AWS S3 API
#     ├─ Upload file
#     └─ Return public URL:
#         https://advaitam-assets.s3.amazonaws.com/static/css/home.css
#         OR (with CloudFront):
#         https://xxxxx.cloudfront.net/static/css/home.css

# Result: All files on S3 ✅
```

### MediaStorage - Used by Model FileField/ImageField

```python
# When you add (in future):
# class UserProfile(models.Model):
#     profile_picture = models.ImageField(upload_to='profile_pics/')

# And user uploads a file:
# Step 1: settings.py has:
#   DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'

# Step 2: Django imports MediaStorage
#   from webapp.storages import MediaStorage

# Step 3: Django creates instance:
#   storage = MediaStorage()

# Step 4: For user's upload:
#   storage.save('profile_pics/user123.jpg', file_content)
#   
#   S3Boto3Storage.save() does:
#     ├─ self.location = 'media'  ← Read from our class
#     ├─ Build S3 path: s3://advaitam-assets/media/profile_pics/user123.jpg
#     ├─ Connect to AWS S3 API
#     ├─ Upload file
#     └─ Return public URL:
#         https://advaitam-assets.s3.amazonaws.com/media/profile_pics/user123.jpg
#         OR (with CloudFront):
#         https://xxxxx.cloudfront.net/media/profile_pics/user123.jpg

# Result: File on S3, URL stored in database ✅
```

---

## Connection to settings.py

### In settings.py (Line 263):

```python
if USE_S3:
    # Line 263: When user uploads files, use MediaStorage
    DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
    # This tells Django to import from webapp/storages.py
    # and use MediaStorage class for file uploads
```

### How Django Processes This String:

```python
# Django sees: 'webapp.storages.MediaStorage'
# Splits into:
#   module_path = 'webapp.storages'
#   class_name = 'MediaStorage'
# 
# Django does:
#   import webapp.storages
#   storage_class = getattr(webapp.storages, 'MediaStorage')
#   storage_instance = storage_class()
#   # Now use this instance for all file operations
```

---

## Configuration Flow

```
.env.production.bak (EC2 server)
├─ USE_S3=True
├─ AWS_STORAGE_BUCKET_NAME=advaitam-assets
├─ AWS_S3_REGION_NAME=us-east-1
├─ AWS_S3_CUSTOM_DOMAIN=xxxxx.cloudfront.net
└─ AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
   │
   └─ Read by settings.py
       │
       ├─ Line 240: AWS_STORAGE_BUCKET_NAME = 'advaitam-assets'
       ├─ Line 241: AWS_S3_REGION_NAME = 'us-east-1'
       ├─ Line 245: AWS_S3_CUSTOM_DOMAIN = 'xxxxx.cloudfront.net'
       │
       └─ Used by storages.py
           │
           ├─ StaticStorage.location = 'static'
           │  └─ S3 path: s3://advaitam-assets/static/
           │
           └─ MediaStorage.location = 'media'
              └─ S3 path: s3://advaitam-assets/media/
              └─ custom_domain property reads AWS_S3_CUSTOM_DOMAIN
                 └─ Returns: xxxxx.cloudfront.net
```

---

## What Happens When collectstatic Runs

### Before Running collectstatic

```
S3 Bucket: advaitam-assets
├─ (empty or old files)
```

### Command

```bash
$ python manage.py collectstatic --noinput
```

### During Execution

```python
# Django internal process:

# 1. Load settings
from django.conf import settings
settings.USE_S3  # → True
settings.DEFAULT_FILE_STORAGE  # → 'webapp.storages.MediaStorage'

# 2. Find static files
static_files = {
    'static/css/home.css': <file_content>,
    'static/js/audio.js': <file_content>,
    'static/images/adishankaracharya.jpg': <file_content>,
    'static/audio/bhagavadgita/001.mp3': <file_content>,
    ...
}

# 3. Import storage class
from webapp.storages import MediaStorage
# (Actually StaticStorage, but same process)

# 4. For each file, upload using storage class
for file_path, file_content in static_files.items():
    storage = MediaStorage()
    storage.save(file_path, file_content)
    # → Uploads to S3://advaitam-assets/media/{file_path}
```

### After Running collectstatic

```
S3 Bucket: advaitam-assets
├── static/  ← All files uploaded here
│   ├── css/home.css
│   ├── js/audio.js
│   ├── images/adishankaracharya.jpg
│   ├── audio/bhagavadgita/001.mp3
│   ├── audio/bhagavadgita/002.mp3
│   ├── ... (all audio files)
│   ├── books/Django.pdf
│   ├── fonts/ (if added)
│   └── admin/ (Django admin files)
└── media/  ← Reserved for user uploads (currently empty)
```

---

## Key Methods Used from S3Boto3Storage Base Class

| Method | Inherited From | Purpose | Used When |
|--------|----------------|---------|-----------|
| `save()` | S3Boto3Storage | Save file to S3 | collectstatic runs OR user uploads |
| `open()` | S3Boto3Storage | Read file from S3 | Serving files to users |
| `delete()` | S3Boto3Storage | Delete file from S3 | User deletes upload |
| `exists()` | S3Boto3Storage | Check if file exists on S3 | Before uploading |
| `url()` | S3Boto3Storage | Get public URL of file | Generating URLs in templates |

---

## Security Considerations

### Line 49: `default_acl = None`

```python
# SECURE ✅
default_acl = None  # Use CloudFront OAC

# Why it's secure:
# - S3 bucket is NOT publicly readable
# - Only CloudFront can access it (via OAC)
# - Users can't bypass CloudFront to access S3 directly
# - All traffic goes through CloudFront CDN

# vs INSECURE ❌
default_acl = 'public-read'  # S3 bucket is publicly readable
# - Anyone can access S3 URL directly
# - Bypasses CloudFront
# - No DDoS protection
# - Slower delivery
```

### Line 50: `querystring_auth = False`

```python
# OKAY for static/media files ✅
querystring_auth = False
# URLs don't have signatures
# Example: https://xxxxx.cloudfront.net/static/css/home.css
# - No ?Signature=xyz query string
# - URLs are simple and cacheable
# - Good for public content

# vs BETTER for sensitive files ❌
querystring_auth = True
# URLs have expiring signatures
# Example: https://xxxxx.cloudfront.net/media/private.pdf?Signature=xyz&Expires=123
# - URL expires after X seconds
# - Good for private/temporary links
# - Not suitable for permanent assets
```

---

## Summary

| Aspect | StaticStorage | MediaStorage |
|--------|---------------|--------------|
| **Location** | `/static/` | `/media/` |
| **Used For** | Your app files | User uploads |
| **Overwrite** | `True` (replace) | `False` (keep) |
| **Triggered By** | `collectstatic` | FileField.save() |
| **Current Status** | ✅ Used | ❌ Not used (reserved) |
| **Cache** | 1 year | 7 days |

Both classes inherit from `S3Boto3Storage` which handles all AWS S3 communication. We just customize the location, ACL, and overwrite behavior! 🚀



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
    - js/           → javascript files
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
try:
    from storages.backends.s3boto3 import S3Boto3Storage
except ImportError:
    # If django-storages is not installed/configured (e.g. dev mode without S3),
    # create a dummy class to avoid ImportErrors.
    from django.core.files.storage import FileSystemStorage
    S3Boto3Storage = FileSystemStorage

from django.conf import settings


class StaticStorage(S3Boto3Storage):
    """
    Static files — files YOU deploy as part of the project (not user uploads).
    Includes: CSS, JavaScript, images, audio recitations, PDFs, fonts, Django admin files.

    Stored at: s3://advaitam-assets/static/
    Served via: https://<cloudfront-domain>/static/
    Cache: 1 year (immutable assets versioned by Django's ManifestStaticFilesStorage)

    Folder structure after collectstatic uploads to S3:
      static/css/         → home.css etc.
      static/js/          → JavaScript files
      static/images/      → adishankaracharya.jpg, India.png, SrinivasaRao.png, USA.png
      static/audio/       → bhagavadgita/, grantha/, sutra/, upanisad/, vidyaranya/
      static/books/       → Django.pdf etc.
      static/fonts/       → web fonts (if added)
      static/admin/       → Django admin CSS/JS/images (auto-added by collectstatic)
    """
    location = 'static'
    default_acl = None           # No public ACL — CloudFront OAC handles access
    querystring_auth = False     # No signed URLs; CloudFront delivers publicly
    file_overwrite = True        # Overwrite during collectstatic (intentional)

    @property
    def custom_domain(self):
        # Use CloudFront domain from settings (populated from AWS_S3_CUSTOM_DOMAIN env var)
        return getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)


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
    location = 'media'
    default_acl = None           # No public ACL — CloudFront OAC handles access
    querystring_auth = False     # No signed URLs for public content
    file_overwrite = False       # Preserve existing uploads — append unique suffix

    @property
    def custom_domain(self):
        return getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)

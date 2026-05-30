"""
Production settings for Platter to Purpose.

DEBUG is False, all secrets from environment variables.
Activated by setting DJANGO_SETTINGS_MODULE=config.settings.production.
"""

import os

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]


# Database — use dj-database-url if DATABASE_URL is set

try:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            default="sqlite:///db.sqlite3",
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
except ImportError:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405

        }
    }


# Email — SMTP via environment variables

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.sendgrid.net")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "apikey")
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_API_KEY", "")


# Static files — WhiteNoise

try:
    import whitenoise  # noqa: F401

    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
except ImportError:
    pass


# Media storage — S3/GCS via django-storages (if configured)

if os.environ.get("AWS_STORAGE_BUCKET_NAME"):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"


# Security hardening

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# Sentry error tracking (if configured)

SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    try:
        import sentry_sdk

        sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.1)
    except ImportError:
        pass


# Caching — Redis in production (if configured)

REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }

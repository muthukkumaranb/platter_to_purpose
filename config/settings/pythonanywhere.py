"""Settings for the free PythonAnywhere deployment.

This intentionally inherits only base settings. The production module may
enable Redis, external databases, S3, WhiteNoise manifests, and Sentry, none
of which are available on the free PythonAnywhere tier.
"""

import os

from .base import *  # noqa: F401, F403
from .base import BASE_DIR

DEBUG = False
DEMO_MODE = True

ALLOWED_HOSTS = ["muthukkumaranb.pythonanywhere.com"]
CSRF_TRUSTED_ORIGINS = ["https://muthukkumaranb.pythonanywhere.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "platter-pythonanywhere-cache",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
if not EMAIL_HOST_USER:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CELERY_BROKER_URL = "memory://"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Do not activate optional external monitoring or storage on this tier.
SENTRY_DSN = None

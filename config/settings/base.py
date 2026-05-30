"""
Base Django settings for Platter to Purpose.

Common settings shared across all environments.
Environment-specific overrides go in development.py or production.py.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# Load .env file if present
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Ensure apps/ is on the Python path
APPS_DIR = BASE_DIR / "apps"
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "The SECRET_KEY environment variable is not set. "
        "Create a .env file or set it in your environment."
    )


# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

PROJECT_APPS = [
    "apps.accounts",
    "apps.food",
    "apps.orders",
    "apps.dashboard",
    "apps.feedback",
    "apps.analytics",
    "apps.notifications",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_celery_results",
    "django_celery_beat",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.notifications.context_processors.unread_notifications",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Auth

AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"


# Email (base defaults — overridden per environment)

DEFAULT_FROM_EMAIL = "Platter to Purpose <noreply@plattertopurpose.com>"


# Caching

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "platter-cache",
    }
}


# Application-specific settings

# Duration (minutes) that new food posts are reserved exclusively
# for orphanages. Set to 0 to disable the priority window entirely.
PRIORITY_WINDOW_MINUTES = 30


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ═══════════════════════════════════════════════════════════════════
# Celery Configuration
# ═══════════════════════════════════════════════════════════════════
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "check-expiring-food-every-5-minutes": {
        "task": "apps.notifications.tasks.check_expiring_food_task",
        "schedule": 300.0,
    },
    "notify-priority-expiry-every-5-minutes": {
        "task": "apps.food.tasks.notify_priority_expiry_task",
        "schedule": 300.0,
    },
}

# ═══════════════════════════════════════════════════════════════════
# Django REST Framework Configuration
# ═══════════════════════════════════════════════════════════════════
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "config.exceptions.global_exception_handler",
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ═══════════════════════════════════════════════════════════════════
# Logging Configuration
# ═══════════════════════════════════════════════════════════════════
LOGS_DIR = BASE_DIR / "logs"
if not LOGS_DIR.exists():
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(BASE_DIR / "logs" / "app.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console"],
            "level": "WARNING",
        },
        "django.request": {
            "handlers": ["console", "file"]
            if os.environ.get("DEBUG", "True") != "True"
            else ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"]
            if os.environ.get("DEBUG", "True") != "True"
            else ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

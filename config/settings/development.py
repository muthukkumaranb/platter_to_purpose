"""
Development settings for Platter to Purpose.

DEBUG is True, SQLite database, console email backend.
Activated by default via manage.py and config/settings/__init__.py.
"""

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]


# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405

    }
}


# Email — print to console in development

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Django Debug Toolbar (if installed)

try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

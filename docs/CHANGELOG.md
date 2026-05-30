# Changelog
All notable changes to the Platter to Purpose project are documented in this file.

## Table of Contents
- [Unreleased](#unreleased)
- [1.0.0 - 2026-05-30](#100---2026-05-30)

## Unreleased
There are no unreleased modifications. The current production release contains all completed features.

## 1.0.0 - 2026-05-30
This is the initial public release of the Platter to Purpose application, a food rescue platform connecting hotels with surplus food to orphanages.

### Added
- **Monorepo architecture layout**:Grouped all applications under the `apps/` directory and centralized settings routing under the `config/` directory.
- **Service/Selector pattern**: Separated business logic into service components (`services.py`) and database query retrieval into selectors (`selectors.py`).
- **Celery background execution**: Built async task handling using Celery and Redis to handle phone verification OTP dispatches, food post expiry warnings, orphanage priority window checking, and monthly impact reports.
- **REST API with JSON Web Token (JWT) auth**: Exposed fully secure API endpoints under the `/api/v1/` prefix with simplejwt authentication.
- **Caching optimization**: Configured `django-redis` low-level caching for available food post lists, user badge collections, and platform metrics with automated invalidation hooks.
- **Standardized exceptions handling**: Configured standard exception definitions extending a core `AppException` class, combined with a global REST API view error handler.
- **Soft deletion models**: Built `SoftDeleteMixin`, `SoftDeleteQuerySet`, and `SoftDeleteManager` to prevent accidental loss of core entity data.
- **CI configuration**: Initialized a GitHub actions file running Ruff code style checks, security dependency validations via safety check, and pytest test suite checks.
- **Environment variables isolation**: Externalized secrets management to `.env` using `python-dotenv`.

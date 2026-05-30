# Security profile
This document describes the security controls, validation checks, environment isolation settings, and vulnerabilities protections implemented in the Platter to Purpose project.

## Table of Contents
- [Secrets management](#secrets-management)
- [HTTPS and session cookies hardening](#https-and-session-cookies-hardening)
- [Input validation and injection defenses](#input-validation-and-injection-defenses)
- [Cross-site scripting (XSS) and CSRF protection](#cross-site-scripting-xss-and-csrf-protection)
- [System vulnerabilities monitoring](#system-vulnerabilities-monitoring)

## Secrets management
All sensitive credentials (such as API keys, SMTP credentials, and signing keys) are externalized from the code:
- **Environment variables**: Configured locally in `.env` and loaded via `python-dotenv`.
- **Version control exclusion**: The `.env` file is excluded from repository tracking inside `.gitignore`.
- **Examples reference**: Safe placeholders are stored in `.env.example` to guide workspace setup without exposing actual values.
- **Production settings**: Loaded dynamically from environment variables, throwing errors if critical parameters (such as `SECRET_KEY`) are missing.

---

## HTTPS and session cookies hardening
In production environments (`config/settings/production.py`), the hosting stack enforces secure HTTP connections:
- **`SECURE_SSL_REDIRECT = True`**: Redirects all unencrypted HTTP traffic to HTTPS.
- **HSTS headers**: Enabled for 1 year (`SECURE_HSTS_SECONDS = 31536000`), enforcing browser-side HTTPS redirection across subdomains.
- **`SESSION_COOKIE_SECURE = True`**: Instructs browsers to transmit session cookies exclusively over secure TLS connections.
- **`CSRF_COOKIE_SECURE = True`**: Transmits CSRF verification cookies only over HTTPS.

---

## Input validation and injection defenses
Data sanitization is performed across input entry points:
- **Object-Relational Mapping (ORM)**: The Django ORM automatically parameterizes SQL queries, protecting the database against SQL injection. Raw queries are avoided across the project.
- **Django Form validations**: Form classes (e.g. `FoodPostForm`) enforce strict validations on field inputs, types, and ranges.
- **Serializer validations**: DRF serializers sanitize incoming JSON payloads prior to model updates or creations.

---

## Cross-site scripting (XSS) and CSRF protection
Defenses against scripting attacks are configured globally:
- **`CsrfViewMiddleware`**: Active on all web endpoints, requiring a valid token token header on every state-modifying request.
- **`X-Frame-Options`**: Set to `DENY` to prevent clickjacking attacks by blocking the site from rendering inside frames on external domains.
- **Ruff audits**: Automatic checks warn developers against using `mark_safe` or `safe` flags on unsanitized user inputs.

---

## System vulnerabilities monitoring
Automated checks are run regularly:
- **Safety check**: Executed in the CI pipeline to scan installed dependencies against databases of known software vulnerabilities:
  ```bash
  safety check -r requirements/production.txt
  ```
- **Ruff linter**: Warns against dangerous python code blocks or bare exceptions.

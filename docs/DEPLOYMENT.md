# Production deployment guide
This document provides specifications and environment variable configurations required to deploy Platter to Purpose to a production environment.

## Table of Contents
- [Required environment variables](#required-environment-variables)
- [Gunicorn and Nginx hosting stack](#gunicorn-and-nginx-hosting-stack)
- [Docker deployment setup](#docker-deployment-setup)
- [Static files and media storages](#static-files-and-media-storages)
- [Celery background workers](#celery-background-workers)

## Required environment variables
Ensure that all of the following environment variables are correctly configured in your hosting environment:

### Core settings
- **`SECRET_KEY`**: A long, random, secure string used by Django for signing keys.
- **`DEBUG`**: Must be set to `False` in production.
- **`ALLOWED_HOSTS`**: Comma-separated list of domains or IP addresses (e.g. `plattertopurpose.com,www.plattertopurpose.com`).

### Database configuration
- **`DATABASE_URL`**: Database connection URL parsed by `dj-database-url` (e.g. `postgres://user:pass@host:5432/db`). Defaults to local SQLite file path if not set.

### Celery & Redis
- **`CELERY_BROKER_URL`**: Connection URL for Redis queue (e.g. `redis://redis-host:6379/0`).
- **`REDIS_URL`**: Connection URL for Django caches backend (e.g. `redis://redis-host:6379/1`).

### Static files & AWS S3 storage (optional)
- **`AWS_STORAGE_BUCKET_NAME`**: Set to activate S3 media file hosting.
- **`AWS_S3_REGION_NAME`**: The AWS S3 region (defaults to `us-east-1`).

### Email SMTP configurations
- **`EMAIL_BACKEND`**: Defaults to `django.core.mail.backends.smtp.EmailBackend`.
- **`EMAIL_HOST`**: SMTP email host (e.g. `smtp.sendgrid.net`).
- **`EMAIL_PORT`**: SMTP port (defaults to `587`).
- **`EMAIL_USE_TLS`**: Defaults to `True`.
- **`EMAIL_HOST_USER`**: SMTP credentials user.
- **`SENDGRID_API_KEY`**: SendGrid API authorization password key.

### Twilio WhatsApp integration
- **`TWILIO_ACCOUNT_SID`**: Twilio account SID.
- **`TWILIO_AUTH_TOKEN`**: Twilio authentication token.
- **`TWILIO_WHATSAPP_NUMBER`**: Configured WhatsApp sender phone number (e.g. `whatsapp:+14155238886`).

### Monitoring
- **`SENTRY_DSN`**: Sentry URL for logging errors and monitoring performance.

---

## Gunicorn and Nginx hosting stack
We recommend serving the application behind Gunicorn and Nginx:

### 1. Gunicorn command
Run Gunicorn from the repository root:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 2. Nginx configuration
Configure Nginx as a reverse proxy, forwarding traffic to the Gunicorn port:
```nginx
server {
    listen 80;
    server_name plattertopurpose.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/project/staticfiles/;
    }
}
```

---

## Docker deployment setup
You can run the web server inside a Docker container. Here is an example `Dockerfile`:

```dockerfile
# Use official lightweight Python image
FROM python:3.11-slim

# Prevent write cache and buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements/production.txt /app/production.txt
RUN pip install --no-cache-dir -r production.txt

COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run container
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## Static files and media storages
- **Static assets**: WhiteNoise manages static asset compression. Static assets must be collected prior to startup:
  ```bash
  python manage.py collectstatic --noinput
  ```
- **Media assets**: Uploaded images are stored in `/media/` locally unless `AWS_STORAGE_BUCKET_NAME` is configured, which redirects uploads to AWS S3.

---

## Celery background workers
Launch background workers and periodic planners in separate system processes:

### Celery worker command
```bash
celery -A config worker --loglevel=info
```

### Celery beat scheduler
```bash
celery -A config beat --loglevel=info --scheduler=django_celery_beat.schedulers:DatabaseScheduler
```

# Platter to Purpose

Live demo: https://muthukkumaranb.pythonanywhere.com
No sign-up or OTP needed: open the login page and click "Try as Hotel" or "Try as Orphanage".
Note: hosted on a free tier, so the first load may take a few seconds.
Registration uses email OTP verification. The public demo skips it with one-click demo accounts.

Connecting Hotels with Surplus Food to Orphanages in Need

## Live Demo

### Demo accounts

The application currently has two RBAC roles:

| Role | What it can do |
|---|---|
| Hotel (donor) | Create and manage surplus food posts and verify pickups. |
| Orphanage (recipient) | Browse available food, claim donations, manage pickups, and submit feedback. |

The demo buttons use these real roles; no manager role exists in the current RBAC model.

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Deploying updates on PythonAnywhere

```bash
cd ~/platter_to_purpose && git pull
workon myenv
export DJANGO_SETTINGS_MODULE=config.settings.pythonanywhere
python manage.py migrate
python manage.py seed_demo
python manage.py collectstatic --noinput
```

Then press **Reload** on the Web tab.

[![CI Build Status](https://img.shields.io/github/actions/workflow/status/example/platter-to-purpose/ci.yml?branch=main)](https://github.com/example/platter-to-purpose/actions)
[![Coverage Status](https://img.shields.io/codecov/c/github/example/platter-to-purpose)](https://codecov.io/gh/example/platter-to-purpose)
[![License](https://img.shields.io/github/license/example/platter-to-purpose)](https://github.com/example/platter-to-purpose/blob/main/LICENSE)

## Table of Contents
- [Project tagline and mission](#project-tagline-and-mission)
- [Feature overview](#feature-overview)
- [Quickstart guide](#quickstart-guide)
- [Documentation directory maps](#documentation-directory-maps)
- [Technology stack](#technology-stack)
- [Contributing](#contributing)
- [License](#license)

## Project tagline and mission
Platter to Purpose is a community-driven surplus food rescue platform designed to bridge the gap between hospitality entities and local orphanages. By providing real-time listings, reservation priority windows, and secure pickup verification, we ensure excess food is rescued safely and efficiently, reducing environmental waste and supporting vulnerable communities.

## Feature overview
The platform implements these features:

| Feature | Description |

| **Monorepo apps structure** | Unified code architecture grouped inside the `apps/` folder namespace. |
| **Service-Selector design** | Separation of business logic (`services.py`) and read-heavy queries (`selectors.py`). |
| **Celery background queue** | Asynchronous email alerts, verification OTPs, and periodic tasks loops. |
| **REST API & JWT Auth** | Decoupled client endpoints with stateless JWT authentication. |
| **Caching optimization** | Caching layer for available food post lists, user badges, and metrics. |
| **Database soft deletion** | Soft deletion mixins to safeguard data integrity. |

## Quickstart guide
Get a local development environment running in 5 simple commands:

```bash
# 1. Clone the environment variables template
cp .env.example .env

# 2. Initialize and activate the virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install packages
pip install -r requirements/development.txt

# 4. Create and apply migrations
python manage.py migrate

# 5. Run the development server
python manage.py runserver
```

## Documentation directory maps
Refer to the following files in the `docs/` directory for detailed design and setup guides:

| Document | Relative Path | Purpose |
| :--- | :--- | :--- |
| **Architecture** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Component data flow and ASCII diagrams. |
| **REST API Reference** | [docs/API.md](./docs/API.md) | Full endpoint list with payload examples. |
| **Database Schema** | [docs/DATABASE.md](./docs/DATABASE.md) | Models definition, indexes, and mixins. |
| **Authentication** | [docs/AUTHENTICATION.md](./docs/AUTHENTICATION.md) | OTP flows, JWT tokens, and user role models. |
| **Security Profile** | [docs/SECURITY.md](./docs/SECURITY.md) | HTTPS policies, secrets rotation, and security headers. |
| **Developer Handbook** | [docs/DEVELOPER.md](./docs/DEVELOPER.md) | Quickstart guides, local testing, and Makefile targets. |
| **Production Deployment** | [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) | Serving guide using Docker, Gunicorn, and Nginx. |
| **Workflows & Journeys** | [docs/WORKFLOWS.md](./docs/WORKFLOWS.md) | End-to-end state machines for claims and pick-ups. |
| **Testing Strategy** | [docs/TESTING.md](./docs/TESTING.md) | Coverage expectations, factories, and pytest commands. |
| **Contributing** | [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) | Branch specifications, commits, and style constraints. |
| **Changelog** | [docs/CHANGELOG.md](./docs/CHANGELOG.md) | Historical logs of releases starting at v1.0.0. |

## Technology stack
- **Backend framework**: Django 5.2.14
- **API framework**: Django REST Framework 3.17.1
- **Background queue**: Celery 5.6.3 + Redis
- **Caching backend**: django-redis 6.0.0
- **Database engine**: SQLite (Development) / PostgreSQL (Production)
- **Formatting style**: Ruff 0.15.15

## Contributing
We welcome contributions to this project! Please read our [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) handbook for developer workflows and testing policies.

## License
Distributed under the MIT License. See [LICENSE](./LICENSE) for details.

# Developer handbook
This document provides guidelines for setting up the local development workspace, running tests, linting, code styles, and the pull request submission process.

## Table of Contents
- [Local environment setup](#local-environment-setup)
- [Makefile reference targets](#makefile-reference-targets)
- [Database migrations workflow](#database-migrations-workflow)
- [Coding standards and style check](#coding-standards-and-style-check)
- [Pull request submission flow](#pull-request-submission-flow)

## Local environment setup
Follow these steps to establish a running instance of the project on your local workstation:

### 1. Prerequisites
Verify you have the following installed:
- Python 3.10 or newer
- SQLite3 or PostgreSQL database engine
- Redis server (required for Celery queuing and caching)

### 2. Virtual environment creation
Clone the project and initialize a Python virtual environment:
```bash
python -m venv venv
```

Activate the environment (Windows):
```powershell
.\venv\Scripts\Activate.ps1
```

Activate the environment (macOS/Linux):
```bash
source venv/bin/activate
```

### 3. Dependencies installation
Install the development packages:
```bash
pip install -r requirements/development.txt
```

### 4. Configuration setup
Create a local `.env` file at the repository root by copying the template file:
```bash
cp .env.example .env
```
Ensure you generate a secure random value for `SECRET_KEY` inside `.env`.

---

## Makefile reference targets
We provide developer shortcuts inside the root `Makefile` to simplify command runs:

| Command | Description | Command Run under the Hood |
| :--- | :--- | :--- |
| `make run` | Runs Django local server | `python manage.py runserver` |
| `make migrate` | Applies pending database migrations | `python manage.py migrate` |
| `make migrations` | Generates new migrations from model changes | `python manage.py makemigrations` |
| `make test` | Runs the full test suite | `pytest --ds=config.settings.development` |
| `make shell` | Opens the Django interactive shell | `python manage.py shell` |
| `make lint` | Audits files for linting errors | `ruff check .` |
| `make format` | Formats all python files | `ruff format .` |
| `make collect` | Collects static files to deployment folder | `python manage.py collectstatic --noinput` |
| `make superuser` | Launches terminal superuser creation | `python manage.py createsuperuser` |
| `make check` | Runs Django internal configuration checks | `python manage.py check` |
| `make install-dev` | Installs local development environment packages | `pip install -r requirements/development.txt` |
| `make install-prod`| Installs production-ready environment packages | `pip install -r requirements/production.txt` |

---

## Database migrations workflow
Any changes made to models inside `apps/*/models.py` require database migrations:
1. Generate the migration layout:
   ```bash
   make migrations
   ```
2. Apply the schema change locally:
   ```bash
   make migrate
   ```
3. Commit both the models and migration files together.

---

## Coding standards and style check
To keep code quality high, the project enforces automated styling checks:
- **Lint rules**: Python files are checked using Ruff. Run `make lint` to verify.
- **Ruff configuration**: Rules are configured inside the `pyproject.toml` file at the root.
- **Auto-formatting**: Run `make format` before committing changes to format your code.
- **Architecture rules**: Views and controller layers must never execute direct model queries. Move all reads into `selectors.py` and writes into `services.py`.

---

## Pull request submission flow
The workflow for pushing modifications to the master repository is structured as follows:
1. Create a branch from `main` using branch naming conventions (e.g. `feature/claim-limits`).
2. Implement your features, and write unit/integration tests under the appropriate `tests/` directories.
3. Validate coding style checks and run tests locally:
   ```bash
   make lint
   make test
   ```
4. Push your branch to GitHub and open a pull request.
5. The GitHub Actions CI pipeline will run all tests and check format rules. Once approved, the branch will be merged into `main`.

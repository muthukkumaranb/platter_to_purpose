# Contributing guidelines
This document outlines the workflows, branching strategies, and conventions required to contribute to the Platter to Purpose project.

## Table of Contents
- [Branch naming strategy](#branch-naming-strategy)
- [Commit message conventions](#commit-message-conventions)
- [Pull request checklist](#pull-request-checklist)
- [Local development checks](#local-development-checks)
- [Coding style guidelines](#coding-style-guidelines)

## Branch naming strategy
All branch names must be prefixed with the type of work being done, followed by a slash and a short description:
- `feature/` for new features (e.g. `feature/jwt-auth-integration`)
- `fix/` for bug fixes (e.g. `fix/otp-expiration-ttl`)
- `chore/` for maintenance or dependencies (e.g. `chore/update-pillow-version`)
- `docs/` for documentation updates (e.g. `docs/add-api-examples`)

## Commit message conventions
Commit messages must follow the Conventional Commits specification. The message must begin with a type prefix, an optional scope, and a concise summary:
- `feat:` for adding a new feature
- `fix:` for fixing a bug
- `docs:` for modifying documentation
- `chore:` for updating tasks, dependencies, or configuration
- `refactor:` for rearranging code structure without altering behavior

Example commit message:
```bash
feat(accounts): add JWT registration endpoint and OTP generation
```

## Pull request checklist
Before opening a pull request (PR) for review, you must verify that:
- All automated unit and integration tests pass successfully.
- Code coverage is greater than or equal to 80% for each modified application.
- No new linting errors are introduced by the changes.
- All relevant documentation is updated to match the changes.

## Local development checks
You must run the linting, formatting, and testing checks locally before pushing your branch:

### Code linting
Verify that your changes conform to formatting requirements:
```bash
ruff check .
```

### Auto-formatting
Apply automated code formatting using Ruff:
```bash
ruff format .
```

### Run test suite
Execute the test suite locally:
```bash
python manage.py test
```

### Run test coverage
Measure test coverage using pytest:
```bash
pytest --ds=config.settings.development --cov=apps --cov-report=term-missing
```

## Coding style guidelines
Ensure your code complies with the project's formatting specifications:
- **Python formatting**: Ruff is used to enforce Python code style standards.
- **Line length**: The maximum allowed line length is 88 characters.
- **Docstrings**: Docstrings are required on all public modules, classes, and functions using standard Python conventions.
- **Service/Selector architecture**: Business logic must reside in `services.py` and reading logic must reside in `selectors.py`. Do not call ORM operations inside views or APIs.

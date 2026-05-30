.PHONY: run migrate migrations test shell lint format collect superuser check

# ──────────────────────────────────────────────────
# Development Shortcuts
# ──────────────────────────────────────────────────

run:
	python manage.py runserver

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

test:
	pytest --ds=config.settings.development

shell:
	python manage.py shell

lint:
	ruff check .

format:
	ruff format .

collect:
	python manage.py collectstatic --noinput

superuser:
	python manage.py createsuperuser

check:
	python manage.py check

install-dev:
	pip install -r requirements/development.txt

install-prod:
	pip install -r requirements/production.txt

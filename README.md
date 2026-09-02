# Result System

A university examination result management API built with Django REST
Framework. Handles the full result lifecycle — assessment entry, submission,
review, correction/resubmission, grading, and notifications — with
role-based access for lecturers, department result officers (DRO), faculty
result officers (FRO), and course officers (CO), plus JWT auth with optional
2FA.

## Features

- **Role-based access** — `Lecturer`, `DRO`, `FRO`, `CO` roles on a custom
  `User` model, enforced via DRF permission classes.
- **Result workflow** — CA scores per assessment slot, exam marks, automatic
  grading, submission, review, and a modification-log audit trail for
  corrections.
- **Result resubmission/correction** flow with per-status transitions
  (submitted → reviewed → corrected, etc).
- **CA slot max limits** — configurable max marks per CA slot, validated on
  entry.
- **Notifications** — in-app notifications on result submission/review
  events.
- **Auth** — JWT login (`djoser` + `djangorestframework-simplejwt`) with
  optional TOTP-based 2FA (`pyotp` + QR code provisioning).
- **API docs** — OpenAPI schema via `drf-spectacular`, with Swagger UI and
  Redoc.

## Tech stack

Django 5 · Django REST Framework · PostgreSQL · Simple JWT · djoser ·
drf-spectacular · Gunicorn · Whitenoise · Docker

## Getting started

### Option A — Docker (recommended)

```bash
cp .env.example .env
# edit .env: set SECRET_KEY, DB_* (DB_HOST should stay "db" for compose)
docker compose up --build
```

This starts Postgres and the Django app, waits for the DB, runs migrations,
collects static files, and serves on **http://localhost:8000**.

Create an admin user in the running container:

```bash
docker compose exec web python manage.py createsuperuser
```

### Option B — Local (no Docker)

Requires Python 3.12+ and a running PostgreSQL instance.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set SECRET_KEY, DB_NAME, DB_HOST, DB_USER, DB_PASSWORD

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

By default `manage.py` uses `examination_management_system.settings.dev`
(postgres via `DB_*` env vars). For production, set
`DJANGO_SETTINGS_MODULE=examination_management_system.settings.prod`, which
instead reads a single `DATABASE_URL` plus `ALLOWED_HOSTS`/`EMAIL_*` — see
`.env.example`.

## Environment variables

See [`.env.example`](.env.example) for the full list (dev vs. prod
settings pull different variables). Never commit a real `.env`.

## API documentation

Once running:

| Docs | URL |
|---|---|
| Swagger UI | `/api/schema/swagger-ui/` |
| Redoc | `/api/schema/redoc/` |
| Raw OpenAPI schema | `/api/schema/` |

## Project structure

```
core/               custom User model, auth-adjacent views
result_system/       courses, assessments, results, grading, permissions
notification/        in-app notifications
audit/                audit-log app
examination_management_system/   project settings, root urls
```

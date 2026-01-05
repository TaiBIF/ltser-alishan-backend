# 長期社會生態核心觀測｜阿里山站

## Long-Term Socio-Ecological Research | Alishan Backend

Django REST backend powering the LTSER Alishan site. Runs with PostgreSQL, Redis, Celery, and serves API + admin features.

-   Framework: Django 4.2 + DRF + Simple JWT
-   Services: PostgreSQL, Redis, Celery worker/beat, Nginx (proxy + static/media)
-   Frontend: https://ltsertw-alishan.org/

---

## Requirements

-   Docker + Docker Compose
-   (Optional for local venv) Python 3.11+, PostgreSQL 16+, Redis 7+

---

## Quick Start (Docker, development)

1. Create `.env` in the repo root:

    ```bash
    # Django
    SECRET_KEY=change-me
    DEBUG=1
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Database
    DB_HOST=db
    DB_NAME=ltser
    DB_USER=ltser
    DB_PASSWORD=ltser-password

    # Redis / Celery
    REDIS_HOST=redis
    REDIS_PORT=6379

    # CORS / CSRF
    CORS_ALLOWED_ORIGINS=http://localhost:5173
    CSRF_TRUSTED_ORIGINS=http://localhost:8000

    # Domains
    BACKEND_DOMAIN=http://localhost:8000
    FRONTEND_DOMAIN=http://localhost:5173

    # Auth / Google
    GOOGLE_CLIENT_ID=your-google-client-id

    # Email (SMTP)
    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=true
    EMAIL_HOST_USER=your-email@example.com
    EMAIL_HOST_PASSWORD=your-email-password
    DEFAULT_FROM_EMAIL=your-email@example.com

    # SEGIS data
    SEGIS_API_ID=your-segis-id
    SEGIS_API_KEY=your-segis-key
    ```

2. Start services (web, db, redis, celery, adminer):
    ```bash
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
    ```
    - Migrations run automatically before the server starts.
    - Dev API: http://localhost:8000
    - Adminer (DB UI): http://localhost:8080 (server: `db`, user/pass from `.env`)
3. Create a superuser (once containers are up):
    ```bash
    docker compose run --rm web python manage.py createsuperuser
    ```

---

## Common Commands

-   `docker compose logs -f web` — follow Django logs
-   `docker compose run --rm web python manage.py migrate` — run migrations manually
-   `docker compose run --rm web python manage.py collectstatic` — collect static files (for prod images)
-   `docker compose run --rm celery celery -A core inspect active` — inspect Celery
-   `docker compose down -v` — stop and remove containers + volumes (local data reset)

---

## Project Structure (Highlights)

-   `app/core/` — Django settings, URLs, WSGI/ASGI, Celery config
-   `app/api/` — API endpoints and pagination helpers
-   `app/account/` — authentication, JWT, Google login, user APIs
-   `app/dashboard/` — dashboard/management endpoints (downloads, forms, etc.)
-   `app/media/` & `app/static/` — uploaded files and collected static assets
-   `docker-compose*.yml` — service definitions for dev/prod
-   `nginx/django.conf` — Nginx reverse proxy + static/media paths
-   `requirements.txt` — Python dependencies

---

## Deployment (Docker, production)

1. Prepare `.env` with production values (set `DEBUG=0`, proper secrets, allowed hosts, TLS-ready domains).
2. Build and start:
    ```bash
    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    ```
    - Gunicorn serves Django; Nginx handles TLS/HTTP and static/media.
3. Issue/renew TLS certs using the bundled Certbot service (mounted at `/var/www/certbot` and `/etc/letsencrypt`); update `nginx/django.conf` server names if domains change.

---

## Notes

-   Static/media are persisted via named Docker volumes (`static_volume`, `media_volume`).
-   JWT auth uses access/refresh tokens; set `GOOGLE_CLIENT_ID` if Google login is needed.
-   CORS/CSRF origins must match your frontend domains to allow browser calls.

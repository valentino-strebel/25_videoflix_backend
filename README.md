Videoflix (Django + Docker)

A Django REST API for video streaming with JWT auth, Redis caching/queues, and HLS/FFmpeg support.

Stack

Python 3.12 (Alpine)

Django (4.2–5.x)

DRF + SimpleJWT

PostgreSQL

Redis (cache + RQ worker)

Gunicorn + WhiteNoise

FFmpeg (for video processing)

django-redis, django-rq, python-decouple, python-dotenv, Pillow

Services & Ports

web (Django API + Gunicorn): http://localhost:8000

Admin: /admin

RQ dashboard: /django-rq/

API namespaces: /api/ (apps: authentication, video)

db (Postgres): container port 5432 (internal)

redis: container port 6379 (internal)

Quick Start (Docker)

# 1) Copy env file and fill values

cp .env.example .env

# 2) Build & start

docker compose up -d --build

# 3) First run: entrypoint will

# - wait for Postgres

# - collect static files

# - makemigrations + migrate

# - create superuser from env:

# DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD

#

# 4) Visit the app

# API: http://localhost:8000/

# Admin: http://localhost:8000/admin

# RQ: http://localhost:8000/django-rq/

Data persists via Docker volumes: postgres_data, redis_data, videoflix_media, videoflix_static.

Development Workflow

Hot-reload is enabled via --reload in Gunicorn and a bind-mount of your source tree:

# view logs

docker compose logs -f web

# open a Django shell

docker compose exec web python manage.py shell

# run migrations manually (if needed)

docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# collect static (dev rarely needs it; prod does)

docker compose exec web python manage.py collectstatic --noinput

Redis / RQ

An RQ worker is launched by the entrypoint:

# see worker logs

docker compose logs -f web | grep rqworker

RQ admin is available at /django-rq/.

Environment Variables

These are read via python-decouple / dotenv and used in core/settings.py.

Variable Default (dev) Required Notes
SECRET_KEY generated/dev key Yes Strong, unique in prod
DEBUG True No Set False in prod
ALLOWED_HOSTS localhost,127.0.0.1 Yes Comma-separated
CSRF_TRUSTED_ORIGINS http://localhost:5500,http://127.0.0.1:5500 No Comma-separated full origins
DB_NAME — Yes Postgres database
DB_USER — Yes Postgres user
DB_PASSWORD — Yes Postgres password
DB_HOST db Yes Compose service name
DB_PORT 5432 Yes
REDIS_HOST redis No Hostname
REDIS_PORT 6379 No Port
REDIS_DB 0 No RQ queue DB
REDIS_LOCATION redis://redis:6379/1 No Cache URL (django-redis)
EMAIL_BACKEND console backend No SMTP backend in prod
EMAIL_HOST / EMAIL_PORT / EMAIL_USE_TLS / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD — No SMTP settings
DEFAULT_FROM_EMAIL no-reply@videoflix.local No Sender address
FRONTEND_URL http://localhost:3000 No For links in emails
EMAIL_VERIFICATION_PATH /verify-email No
PASSWORD_RESET_PATH /reset-password No
LOG_LEVEL INFO No Logging
DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD — Yes (first run) Used by entrypoint to auto-create superuser
VIDEO_ALLOWED_RESOLUTIONS 120p,360p,720p,1080p No HLS rendition list

A sample .env.example is included—rename to .env and update secrets.

Project Structure (relevant bits)
.
├── backend.Dockerfile
├── backend.entrypoint.sh
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── manage.py
├── core/
│ ├── settings.py
│ ├── urls.py
│ ├── asgi.py
│ └── wsgi.py
├── authentication/ # custom user model
├── video/ # video/HLS logic
└── media/ # persisted via volume

API & Auth

DRF installed; default permission is AllowAny (views can override).

JWT via rest_framework_simplejwt:

Access: 1 hour

Refresh: 7 days

Header: Authorization: Bearer <token>

Custom user model: authentication.User (set via AUTH_USER_MODEL).

Static & Media

Static served by WhiteNoise in the web container.

STATIC_ROOT=/app/static and MEDIA_ROOT=/app/media are mapped to named volumes.

On container start, collectstatic runs automatically.

Video / HLS

FFmpeg is installed in the image.

HLS root: <MEDIA_ROOT>/hls/<movie_id>/<resolution>/...

Allowed resolutions configurable via VIDEO_ALLOWED_RESOLUTIONS.

Example helper function (in settings context) shows 720p conversion with FFmpeg.

Production Notes

Set DEBUG=False, proper ALLOWED_HOSTS, strong SECRET_KEY.

Consider moving RQ worker to a separate container instead of backgrounding it in the web process.

Remove --reload from Gunicorn in production:

exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60

Configure reverse proxy (e.g., Nginx) for TLS and static caching, or use a platform’s ingress.

Set SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE to True behind TLS.

Use managed Postgres/Redis or persist volumes to durable storage.

Run regular DB backups and add health checks.

Common Commands

# bring everything down (keep volumes/data)

docker compose down

# bring everything down and wipe data/volumes

docker compose down -v

# rebuild after requirements change

docker compose build --no-cache

# open a shell inside the web container

docker compose exec web /bin/sh

Troubleshooting

“relation does not exist” / migration errors
Run makemigrations and migrate inside web, or wipe volumes and rebuild for a clean slate.

Admin user not created
Ensure all DJANGO*SUPERUSER*\* vars are set and that the first run wasn’t skipped (remove volumes and restart if needed).

Static files missing
Check collectstatic output in logs; verify videoflix_static volume is attached.

CORS errors from frontend
Add your frontend origin(s) to CORS_ALLOWED_ORIGINS and, if needed, to CSRF_TRUSTED_ORIGINS.

Port already in use
Change the host port in docker-compose.yml (e.g., "8001:8000").

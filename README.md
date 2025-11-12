Videoflix (Django + Docker)

Videoflix is a Django REST API for a video streaming platform.
It runs fully in Docker using PostgreSQL, Redis, and Gunicorn.

Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/valentino-strebel/25_videoflix_backend
cd core
```

## 2. Create Your Environment File

Copy the example and fill in your own values:

```bash
cp .env.example .env
```

At minimum, update:

```ini
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=yourpassword
SECRET_KEY=your_secret_key
```

## 3. Build and Start the Containers

```bash
docker compose up -d --build
```

This will:

- Start PostgreSQL and Redis
- Build the Django app image
- Run migrations automatically
- Collect static files
- Create a superuser (using DJANGO*SUPERUSER*\* variables)

## 4. Access the App

- API: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- RQ dashboard: http://localhost:8000/django-rq/

## Useful Commands

Run migrations manually:

```bash
docker compose exec web python manage.py migrate
```

Create a new superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Open a shell inside the web container:

```bash
docker compose exec web /bin/sh
```

Stop everything:

```bash
docker compose down
```

Rebuild after changes:

```bash
docker compose up -d --build
```

## Stack

- Django (Python 3.12)
- PostgreSQL
- Redis
- Gunicorn
- WhiteNoise
- FFmpeg

## Next Steps

After the containers are running and you can access the admin interface:

- Log in using your superuser credentials
- Add users, upload videos, and explore the API endpoints under /api/

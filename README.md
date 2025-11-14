Videoflix (Django + Docker)

Videoflix is a Django REST API for a video streaming platform.
It runs fully in Docker using PostgreSQL, Redis, and Gunicorn.

Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/valentino-strebel/25_videoflix_backend
cd core
```

## Install required dependencies

Run this command to install the project’s required Python dependencies.

```bash
pip install -r requirements.txt
```

## 2. Create Your Environment File

Copy the example and fill in your own values:

```bash
cp .env.template .env
```

## Docker Desktop

Start Docker Desktop before proceeding with the next steps.

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

## Email verification

After the Docker Container is running, run to read out logs:

```bash
docker compose logs -f web
```

## Troubleshooting: Backend Container Instantly Exits (“exited with code 1 / 2 / 255”)

If your videoflix_backend container starts and immediately stops, and you see errors like:

```
exec ./backend.entrypoint.sh: no such file or directory
```

or:

```
./backend.entrypoint.sh: set: line 3: illegal option -
```

or your container shows:

```
videoflix_backend exited with code 1
videoflix_backend exited with code 2
videoflix_backend exited with code 255
```

then the cause is almost always the same:

### Root Cause

Your backend.entrypoint.sh file was cloned with Windows line endings (CRLF).
Linux inside Docker requires Unix line endings (LF).
With CRLF, the shell sees invalid characters and crashes immediately.

This happens especially when cloning the repository on Windows with git or editing the file in VS Code.

### Fix: Convert the file to Unix line endings (LF)

1. Open: backend.entrypoint.sh
1. Look at the bottom-right corner of VS Code
1. → If it says CRLF, click it
1. Select LF
1. Save the file
1. Rebuild your container:

```bash
docker compose down
docker compose up --build
```

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

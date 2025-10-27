Clone the repository

bash git clone https://github.com/valentino-strebel/25_videoflix_backend
cd 25_videoflix_backend

Run with Docker (recommended)

Create a Dockerfile in the project root

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev netcat-openbsd && rm -rf /var/lib/apt/lists/\*
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app
WORKDIR /app/core
EXPOSE 8000

Create a docker-compose.yml file in the project root

version: "3.9"
services:
web:
build: .
command: sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
ports:

- "8000:8000"
  env_file:
- ./core/.env
  volumes:
- .:/app
- media_data:/app/core/media
- static_data:/app/core/static
  depends_on:
- db
- redis

worker:
build: .
command: python manage.py rqworker default
env_file:

- ./core/.env
  volumes:
- .:/app
  depends_on:
- db
- redis

db:
image: postgres:16
environment:
POSTGRES_DB: ${DB_NAME:-videoflix}
POSTGRES_USER: ${DB_USER:-videoflix_user}
POSTGRES_PASSWORD: ${DB_PASSWORD:-supersecretpassword}
volumes:

- pg_data:/var/lib/postgresql/data
  ports:
- "5432:5432"

redis:
image: redis:7
ports:

- "6379:6379"

volumes:
pg_data:
media_data:
static_data:

Create a .env file in the core directory

cp core/.env.template.docker core/.env

Build and start the containers

docker compose build
docker compose up

This will start the following services:
web: Django server (port 8000)
db: PostgreSQL database (port 5432)
redis: Redis cache (port 6379)
worker: Background RQ worker

Access the project

App: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

Create a superuser

docker compose exec web python manage.py createsuperuser

To stop the containers

docker compose down

To stop and remove all data volumes

docker compose down -v

Manual setup (without Docker)

Clone the repository

bash git clone https://github.com/valentino-strebel/25_videoflix_backend
cd 25_videoflix_backend/core

Create and activate a virtual environment

bash # On Linux/Mac python -m venv venv source venv/bin/activate # (optional) upgrade pip python -m pip install --upgrade pip

bash # On Windows (PowerShell) python -m venv venv venv\Scripts\Activate python -m pip install --upgrade pip

Install dependencies

bash pip install -r requirements.txt

Create your .env file

The project reads environment variables from core/.env (same folder as manage.py).

bash cp .env.template .env

Generate a secret key and set SECRET_KEY in .env

bash python - <<'PY' import secrets; print(secrets.token_urlsafe(64)) PY

PostgreSQL Database Setup

Make sure PostgreSQL is installed and running on your system.

Open PowerShell and log in as the default PostgreSQL user

bash psql -U postgres

Inside the PostgreSQL shell, create a new database and user

sql CREATE DATABASE videoflix; CREATE USER videoflix_user WITH PASSWORD 'yourpassword'; GRANT ALL PRIVILEGES ON DATABASE videoflix TO videoflix_user; ALTER DATABASE videoflix OWNER TO videoflix_user; \q

Configure your .env for PostgreSQL

DEBUG=True SECRET_KEY=your_generated_secret_key DB_NAME=videoflix DB_USER=videoflix_user DB_PASSWORD=yourpassword DB_HOST=127.0.0.1 DB_PORT=5432

Make sure PostgreSQL is running before continuing.

Apply database migrations

bash python manage.py migrate

Create a superuser (for admin access)

bash python manage.py createsuperuser

Run the development server

bash python manage.py runserver

The server starts at http://127.0.0.1:8000/

Access the project

App: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

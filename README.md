Clone the repository

```
bash git clone https://github.com/valentino-strebel/25_videoflix_backend cd 25_videoflix_backend/core
```

Create and activate a virtual environment

```
bash # On Linux/Mac python -m venv venv source venv/bin/activate # (optional) upgrade pip python -m pip install --upgrade pip
```

```
bash # On Windows (PowerShell) python -m venv venv venv\Scripts\Activate python -m pip install --upgrade pip
```

Install dependencies

```
bash pip install -r requirements.txt
```

Create your .env file

The project reads environment variables from core/.env (same folder as manage.py).

```
bash # from 25_videoflix_backend/core cp .env.template .env
```

Generate a secret key and set SECRET_KEY in .env:

```
bash python - <<'PY' import secrets; print(secrets.token_urlsafe(64)) PY
```

PostgreSQL Database Setup

Make sure PostgreSQL is installed and running on your system.

Open PowerShell and log in as the default PostgreSQL user:

```
bash psql -U postgres
```

Inside the PostgreSQL shell, create a new database and user:

```
sql CREATE DATABASE videoflix; CREATE USER videoflix_user WITH PASSWORD 'yourpassword'; GRANT ALL PRIVILEGES ON DATABASE videoflix TO videoflix_user; ALTER DATABASE videoflix OWNER TO videoflix_user; \q
```

Configure your .env for PostgreSQL

Open your .env and update these lines:

```
bash DEBUG=True SECRET_KEY=your_generated_secret_key DB_NAME=videoflix DB_USER=videoflix_user DB_PASSWORD=yourpassword DB_HOST=127.0.0.1 DB_PORT=5432
```

Make sure PostgreSQL is running before continuing.

Apply database migrations

```
bash python manage.py migrate
```

Create a superuser (for admin access)

```
bash python manage.py createsuperuser
```

Run the development server

```
bash python manage.py runserver
```

The server starts at http://127.0.0.1:8000/

Access the project

App: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

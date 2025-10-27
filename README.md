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

<pre> ```bash pip install -r requirements.txt ``` </pre>

Create your .env file

The project reads environment variables from core/.env (same folder as manage.py).

<pre> ```bash # from 25_videoflix_backend/core cp .env.template .env ``` </pre>

Generate a secret key and set SECRET_KEY in .env:

<pre> ```bash python - <<'PY' import secrets; print(secrets.token_urlsafe(64)) PY ``` </pre>

PostgreSQL Database Setup

Make sure PostgreSQL is installed and running on your system.

Open PowerShell and log in as the default PostgreSQL user:

<pre> ```bash psql -U postgres ``` </pre>

Inside the PostgreSQL shell, create a new database and user:

<pre> ```sql CREATE DATABASE videoflix; CREATE USER videoflix_user WITH PASSWORD 'yourpassword'; GRANT ALL PRIVILEGES ON DATABASE videoflix TO videoflix_user; ALTER DATABASE videoflix OWNER TO videoflix_user; \q ``` </pre>

Configure your .env for PostgreSQL

Open your .env and update these lines:

<pre> ```bash DEBUG=True SECRET_KEY=your_generated_secret_key DB_NAME=videoflix DB_USER=videoflix_user DB_PASSWORD=yourpassword DB_HOST=127.0.0.1 DB_PORT=5432 ``` </pre>

Make sure PostgreSQL is running before continuing.

Apply database migrations

<pre> ```bash python manage.py migrate ``` </pre>

Create a superuser (for admin access)

<pre> ```bash python manage.py createsuperuser ``` </pre>

Run the development server

<pre> ```bash python manage.py runserver ``` </pre>

The server starts at http://127.0.0.1:8000/

Access the project

App: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

#!/bin/sh
set -e

# -----------------------------------------------------------------------------
# Wait for PostgreSQL to become available
# -----------------------------------------------------------------------------
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."

while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
  echo "PostgreSQL unavailable – retrying in 1s..."
  sleep 1
done

echo "PostgreSQL is ready."

# -----------------------------------------------------------------------------
# Django Setup
# -----------------------------------------------------------------------------
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# -----------------------------------------------------------------------------
# Create superuser from environment variables (if not already existing)
# -----------------------------------------------------------------------------
python manage.py shell <<'EOF'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

identifier = (
    os.environ.get("DJANGO_SUPERUSER_EMAIL")
    or os.environ.get("DJANGO_SUPERUSER_USERNAME")
)
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "adminpassword")

lookup = {User.USERNAME_FIELD: identifier}

if not User.objects.filter(**lookup).exists():
    print(f"Creating superuser with {User.USERNAME_FIELD}='{identifier}'...")
    create_kwargs = {User.USERNAME_FIELD: identifier, "password": password}

    if (
        "email" in [f.name for f in User._meta.get_fields()]
        and User.USERNAME_FIELD != "email"
        and email
    ):
        create_kwargs["email"] = email

    User.objects.create_superuser(**create_kwargs)
    print("Superuser created.")
else:
    print("Superuser already exists.")
EOF

# -----------------------------------------------------------------------------
# Start RQ worker (background)
# -----------------------------------------------------------------------------
python manage.py rqworker default &

# -----------------------------------------------------------------------------
# Start Gunicorn application server
# -----------------------------------------------------------------------------
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --reload

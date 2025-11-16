#!/bin/sh
set -e

echo "Warte auf PostgreSQL auf $DB_HOST:$DB_PORT..."

# -q für "quiet" (keine Ausgabe außer Fehlern)
# Die Schleife läuft, solange pg_isready *nicht* erfolgreich ist (Exit-Code != 0)
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
  echo "PostgreSQL ist nicht erreichbar - schlafe 1 Sekunde"
  sleep 1
done

echo "PostgreSQL ist bereit - fahre fort..."

# Deine originalen Befehle (ohne wait_for_db)
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# Create a superuser using environment variables
# (Dein Superuser-Erstellungs-Code bleibt gleich)
python manage.py shell <<'EOF'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

# pull identifiers from env; prefer email if USERNAME_FIELD is 'email'
identifier = os.environ.get('DJANGO_SUPERUSER_EMAIL') or os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')

# build a lookup using the actual USERNAME_FIELD
lookup = {User.USERNAME_FIELD: identifier}

if not User.objects.filter(**lookup).exists():
    print(f"Creating superuser with {User.USERNAME_FIELD}='{identifier}'...")
    # create kwargs that match your manager signature
    create_kwargs = {User.USERNAME_FIELD: identifier, 'password': password}
    # include email if the model has it and it's not already the USERNAME_FIELD
    if 'email' in [f.name for f in User._meta.get_fields()] and User.USERNAME_FIELD != 'email' and email:
        create_kwargs['email'] = email
    User.objects.create_superuser(**create_kwargs)
    print("Superuser created.")
else:
    print("Superuser already exists.")
EOF

python manage.py rqworker default &

exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --reload
#!/usr/bin/env bash
set -e

# Ensure STATIC_ROOT and MEDIA_ROOT directories exist and have correct permissions
if [ -n "$STATIC_ROOT" ]; then
  echo "Ensuring static directory exists at $STATIC_ROOT"
  mkdir -p "$STATIC_ROOT"
  chmod -R 755 "$STATIC_ROOT"
fi

# Wait for Postgres if DATABASE_HOST is set
if [ -n "$DATABASE_HOST" ]; then
  echo "Waiting for Postgres at $DATABASE_HOST:${DATABASE_PORT:-5432}..."
  until pg_isready -h "$DATABASE_HOST" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USER:-}" >/dev/null 2>&1; do
    sleep 1
  done
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Finally execute the main command (e.g., gunicorn or runserver)
exec "$@"

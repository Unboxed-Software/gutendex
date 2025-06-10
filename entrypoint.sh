#!/usr/bin/env bash
set -e

# Wait for the database to be ready (optional but helpful)
if [ -n "$DATABASE_HOST" ]; then
  echo "Waiting for Postgres..."
  until pg_isready -h "$DATABASE_HOST" -p "${DATABASE_PORT:-5432}" -U "$DATABASE_USER"; do
    sleep 1
  done
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# You could also seed initial data, create superuser, etc., here if needed

# Finally execute the CMD
exec "$@"
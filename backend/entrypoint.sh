#!/bin/bash
set -e

# Function to check if postgres is ready
function postgres_ready() {
  python wait_for_db.py
  return $?
}

# Wait for postgres to be ready
echo "Waiting for PostgreSQL..."
until postgres_ready; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is available!"

# Apply migrations with explicit output and exit on error
echo "Making migrations..."
python manage.py makemigrations --noinput || { echo "Failed to make migrations"; exit 1; }

echo "Applying migrations..."
python manage.py migrate --noinput || { echo "Failed to apply migrations"; exit 1; }

echo "Migrations successfully applied!"

# Run the server
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000

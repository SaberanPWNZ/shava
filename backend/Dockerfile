FROM python:3.12-slim


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        curl \
        build-essential \
        libjpeg-dev \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt requirements-dev.txt ./

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN addgroup --system app && adduser --system --group app

RUN mkdir -p /app/static /app/media /app/logs && \
    chown -R app:app /app && \
    chmod +x /app/wait_for_db.py

USER app

EXPOSE 8000

# Run migrations with explicit error handling before starting the server
CMD bash -c "\
    echo 'Waiting for database...' && \
    python wait_for_db.py && \
    echo 'Database is available, running migrations...' && \
    python manage.py makemigrations --noinput || { echo 'Failed to make migrations!'; exit 1; } && \
    python manage.py migrate --noinput || { echo 'Failed to apply migrations!'; exit 1; } && \
    echo 'Migrations applied successfully!' && \
    python manage.py runserver 0.0.0.0:8000"

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1



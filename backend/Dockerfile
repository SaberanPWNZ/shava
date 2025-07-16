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


# Install poetry
RUN pip install poetry==1.7.1


# Copy only requirements files first to cache dependencies
COPY pyproject.toml poetry.lock* ./


# Install dependencies directly without virtualenv
RUN pip install django djangorestframework python-dotenv psycopg2-binary python-json-logger Pillow djangorestframework-simplejwt[crypto] django-debug-toolbar


# Copy the rest of the application
COPY . .

RUN addgroup --system app && adduser --system --group app


RUN mkdir -p /app/static /app/media && \
    chown -R app:app /app && \
    chmod +x /app/wait_for_db.py

USER app

EXPOSE 8000


HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Fix: remove duplicate CMD instruction
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
    CMD curl -f http://localhost:8000/admin/ || exit 1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

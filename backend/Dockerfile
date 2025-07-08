
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
        build-essential && \
    rm -rf /var/lib/apt/lists/*


RUN pip install poetry


ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache


COPY pyproject.toml poetry.lock* ./


RUN poetry install --only main && rm -rf $POETRY_CACHE_DIR


COPY . .

RUN addgroup --system app && adduser --system --group app


RUN mkdir -p /app/static /app/media && \
    chown -R app:app /app

USER app

EXPOSE 8000


HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

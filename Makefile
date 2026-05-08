
.PHONY: help up down migrate test test-backend test-frontend lint lint-backend lint-frontend typecheck typecheck-backend fmt fmt-backend fmt-frontend seed

COMPOSE ?= $(shell command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

up:
	# Pass .env.dev to docker compose via --env-file instead of sourcing it
	# in the shell (sourcing can fail if the file contains characters not
	# valid in POSIX shell assignments).
	$(COMPOSE) --env-file ./.env.dev up -d

down:
	$(COMPOSE) down

migrate:.
	$(COMPOSE) exec web python manage.py migrate

test: test-backend test-frontend

test-backend:
	cd backend && DJANGO_SECRET_KEY=test python manage.py test

test-frontend:
	cd frontend && npm run test

lint: lint-backend lint-frontend

lint-backend:
	cd backend && ruff check . && ruff format --check .

lint-frontend:
	cd frontend && npm run lint

typecheck: typecheck-backend

typecheck-backend:
	cd backend && DJANGO_SECRET_KEY=test mypy .

fmt: fmt-backend fmt-frontend

fmt-backend:
	cd backend && ruff format . && ruff check --fix .

fmt-frontend:
	cd frontend && npm run format

seed:
	@echo "No project-wide seed command yet — add one and wire it here."

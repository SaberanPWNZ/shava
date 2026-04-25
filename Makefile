# =============================================================================
# Shava — common developer commands.
#
# Most targets are thin wrappers around docker-compose, Django manage.py and
# the frontend npm scripts so newcomers don't have to memorize the exact
# invocation. Run `make help` to see the full list.
# =============================================================================

.PHONY: help up down migrate test test-backend test-frontend lint lint-backend lint-frontend fmt fmt-backend fmt-frontend seed

# Use docker compose v2 if available, fall back to legacy docker-compose.
COMPOSE ?= $(shell command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

up: ## Start the dev stack (docker compose up -d).
	$(COMPOSE) up -d

down: ## Stop the dev stack.
	$(COMPOSE) down

migrate: ## Apply Django database migrations inside the backend container.
	$(COMPOSE) exec backend python manage.py migrate

test: test-backend test-frontend ## Run all tests (backend + frontend).

test-backend: ## Run backend (Django) tests.
	cd backend && DJANGO_SECRET_KEY=test python manage.py test

test-frontend: ## Run frontend Playwright e2e tests.
	cd frontend && npm run test

lint: lint-backend lint-frontend ## Run all linters.

lint-backend: ## flake8 over the backend.
	cd backend && flake8 .

lint-frontend: ## Prettier + ESLint over the frontend.
	cd frontend && npm run lint

fmt: fmt-backend fmt-frontend ## Format backend and frontend.

fmt-backend: ## black + isort over the backend.
	cd backend && black . && isort .

fmt-frontend: ## prettier --write over the frontend.
	cd frontend && npm run format

seed: ## Run any registered seed management commands.
	@echo "No project-wide seed command yet — add one and wire it here."

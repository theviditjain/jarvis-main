# ─────────────────────────────────────────────────────────────────────────────
# JARVIS Runtime — Makefile
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help install dev lint format typecheck test test-unit test-integration \
        docker-build docker-up docker-down docker-logs clean docs

# Default target
.DEFAULT_GOAL := help

# ── Variables ─────────────────────────────────────────────────────────────────
PYTHON      := python3.12
POETRY      := poetry
DOCKER      := docker
COMPOSE     := docker compose
IMAGE_NAME  := jarvis-runtime
IMAGE_TAG   := latest
PYTEST_ARGS ?= -v

help: ## Show this help message
	@echo "JARVIS Runtime — Available Commands"
	@echo "════════════════════════════════════"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Installation ──────────────────────────────────────────────────────────────

install: ## Install all dependencies (including dev)
	$(POETRY) install

install-prod: ## Install production dependencies only
	$(POETRY) install --only=main

# ── Development ───────────────────────────────────────────────────────────────

dev: ## Start the development server with hot reload
	JARVIS_ENV=development PYTHONPATH=src $(POETRY) run uvicorn main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--reload \
		--reload-dir src \
		--log-level debug

# ── Code Quality ─────────────────────────────────────────────────────────────

lint: ## Run Ruff linter
	$(POETRY) run ruff check .

lint-fix: ## Run Ruff linter with auto-fix
	$(POETRY) run ruff check . --fix

format: ## Format code with Ruff
	$(POETRY) run ruff format .

format-check: ## Check formatting without writing
	$(POETRY) run ruff format . --check

typecheck: ## Run MyPy type checker
	$(POETRY) run mypy . --ignore-missing-imports

quality: lint format-check typecheck ## Run all quality checks

# ── Testing ───────────────────────────────────────────────────────────────────

test: ## Run all tests
	$(POETRY) run pytest $(PYTEST_ARGS)

test-unit: ## Run unit tests only
	$(POETRY) run pytest tests/unit/ $(PYTEST_ARGS)

test-integration: ## Run integration tests only (requires running services)
	$(POETRY) run pytest tests/integration/ $(PYTEST_ARGS)

test-e2e: ## Run end-to-end tests
	$(POETRY) run pytest tests/e2e/ $(PYTEST_ARGS)

test-cov: ## Run tests with coverage report
	$(POETRY) run pytest --cov=. --cov-report=html:coverage_html --cov-report=term-missing

# ── Docker ────────────────────────────────────────────────────────────────────

docker-build: ## Build the Docker image
	$(DOCKER) build --target runtime -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-up: ## Start all services with Docker Compose
	$(COMPOSE) up -d

docker-up-full: ## Start all services including Redis
	$(COMPOSE) --profile full up -d

docker-down: ## Stop all services
	$(COMPOSE) down

docker-down-volumes: ## Stop all services and remove volumes
	$(COMPOSE) down -v

docker-logs: ## Tail logs from all services
	$(COMPOSE) logs -f

docker-logs-jarvis: ## Tail logs from the JARVIS runtime only
	$(COMPOSE) logs -f jarvis

docker-restart: ## Restart the JARVIS runtime container
	$(COMPOSE) restart jarvis

docker-shell: ## Open a shell in the JARVIS runtime container
	$(COMPOSE) exec jarvis /bin/bash

docker-ps: ## Show running containers
	$(COMPOSE) ps

# ── Utilities ─────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf coverage_html/ .coverage 2>/dev/null || true
	@echo "✓ Clean complete"

pre-commit: ## Run pre-commit hooks on all files
	$(POETRY) run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	$(POETRY) run pre-commit install

# ── Database ──────────────────────────────────────────────────────────────────

neo4j-shell: ## Open Neo4j Cypher shell
	$(COMPOSE) exec neo4j cypher-shell -u neo4j -p devpassword

milvus-shell: ## Open Milvus admin shell (via python)
	$(POETRY) run python -c "from pymilvus import connections; connections.connect(); print('Connected to Milvus')"

# ── Documentation ─────────────────────────────────────────────────────────────

docs: ## Generate documentation (future: MkDocs)
	@echo "Documentation generation not yet configured."
	@echo "See docs/ directory for markdown documentation."

# Open Factory Agent — 100% Free & Open Source Local Workflow Platform
SHELL := /usr/bin/env bash
PYTHON ?= python3
PORT ?= 8765
DOCKER_IMAGE ?= open-factory-agent:latest

.PHONY: help setup install run start stop status restart test docker-build docker-up docker-down docker-logs build-pages clean

help: ## Show this help message
	@echo "Open Factory Agent — Automation & AI Platform"
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

setup: install ## Alias for install

install: ## Set up local dependencies, default workflows and permissions
	@echo "==> Preparing Open Factory Agent..."
	@mkdir -p assets
	@chmod +x start.sh stop.sh install.sh scripts/*.sh 2>/dev/null || true
	@if [ ! -f workflows.json ] && [ -f workflows.default.json ]; then \
		cp workflows.default.json workflows.json; \
		echo "==> Initialized workflows.json from default template."; \
	fi
	@echo "==> Setup completed successfully!"

start: run ## Alias for run

run: ## Start Open Factory Agent locally in background
	@./start.sh

dev: ## Run Open Factory Agent in foreground (interactive)
	@OPENFACTORY_PORT=$(PORT) $(PYTHON) server.py

stop: ## Stop running Open Factory Agent instance
	@./stop.sh

status: ## Check whether Open Factory Agent is running
	@if curl --noproxy '*' -fsS --max-time 2 http://127.0.0.1:$(PORT)/api/config >/dev/null 2>&1; then \
		echo "✓ Open Factory Agent is RUNNING at http://127.0.0.1:$(PORT)/"; \
	else \
		echo "✗ Open Factory Agent is STOPPED"; \
	fi

restart: stop run ## Restart local Open Factory Agent service

test: ## Run backend unit & integration tests
	@if [ -x .venv/bin/pytest ]; then \
		echo "==> Running pytest with .venv/bin/pytest..."; \
		.venv/bin/pytest backend/tests -v; \
	elif command -v pytest >/dev/null 2>&1; then \
		echo "==> Running pytest test suite..."; \
		pytest backend/tests -v; \
	else \
		echo "==> Validating server.py syntax..."; \
		$(PYTHON) -m py_compile server.py scheduler.py autostart.py; \
		echo "✓ Syntax valid!"; \
	fi

docker-build: ## Build Docker container image
	@echo "==> Building Docker image: $(DOCKER_IMAGE)..."
	docker build -t $(DOCKER_IMAGE) .

docker-up: ## Run Open Factory Agent via Docker Compose
	@echo "==> Starting Docker container in background..."
	docker compose up -d

docker-down: ## Stop Docker Compose services
	@echo "==> Stopping Docker container..."
	docker compose down

docker-logs: ## Follow Docker Compose logs
	docker compose logs -f

build-pages: ## Build frontend product landing page for GitHub Pages
	@echo "==> Building GitHub Pages landing page..."
	cd frontend && npm run build
	@echo "✓ Landing page built in frontend/dist/"

clean: ## Clean up temporary logs, pid files, and python caches
	@echo "==> Cleaning temporary files..."
	@rm -f *.pid .*.pid
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cleaned!"

.PHONY: help install dev test lint format type-check clean build docs docs-serve docs-deploy

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install KNL in development mode
	uv pip install -e .

dev: ## Install KNL with development dependencies
	uv pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=knl --cov-report=html --cov-report=term

lint: ## Run linter (ruff)
	ruff check src/knl tests/

lint-fix: ## Run linter and fix issues
	ruff check --fix src/knl tests/

format: ## Format code
	ruff format src/knl tests/

type-check: ## Run type checker (mypy)
	mypy src/knl

check-all: lint type-check test ## Run all checks (lint, type-check, test)

clean: ## Clean build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build distribution packages
	uv build

run: ## Run knl CLI
	uv run knl

# Development helpers
init-test-repo: ## Initialize a test repository
	@mkdir -p /tmp/knl-test-repo
	@cd /tmp/knl-test-repo && git init && knl init

watch-test: ## Run tests in watch mode (requires pytest-watch)
	ptw tests/ -- -v

# Documentation
docs: ## Build documentation
	mkdocs build --clean --strict

docs-serve: ## Serve documentation locally
	mkdocs serve

docs-deploy: ## Deploy documentation to GitHub Pages
	mkdocs gh-deploy --clean --force

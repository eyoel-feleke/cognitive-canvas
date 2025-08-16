# Makefile for ContentGraph MCP Server

.PHONY: help install install-dev sync test test-unit test-integration test-coverage test-fast clean lint format setup-dev add add-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install package and dependencies"
	@echo "  make install-dev  - Install package with development dependencies"
	@echo "  make sync         - Sync dependencies from lock file"
	@echo "  make test         - Run all tests with coverage"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-coverage - Run tests with detailed coverage"
	@echo "  make test-fast    - Run tests without coverage (faster)"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Clean up build artifacts"
	@echo "  make setup-dev    - Set up development environment"
	@echo "  make add          - Add a new dependency"
	@echo "  make add-dev      - Add a new development dependency"

# Installation
install:
	uv sync --no-dev

install-dev:
	uv sync

# Sync dependencies from lock file
sync:
	uv sync

# Testing
test:
	uv run python run_tests.py --mode all

test-file:
	@read -p "Enter test file name (e.g., test_models.py): " file; \
	uv run python run_tests.py --file $$file
test-unit:
	uv run python run_tests.py --mode unit

test-integration:
	uv run python run_tests.py --mode integration

test-coverage:
	uv run python run_tests.py --mode coverage

test-fast:
	uv run python run_tests.py --mode fast

# Code quality
lint:
	uv run flake8 src tests --max-line-length=100 --extend-ignore=E203,W503
	uv run mypy src --ignore-missing-imports

format:
	uv run black src tests
	uv run isort src tests

format-check:
	uv run black --check src tests
	uv run isort --check-only src tests

# Development setup
setup-dev: install-dev
	@echo "Development environment set up successfully!"
	@echo "Run 'make test' to verify everything works."

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .venv/

# Run specific test file
test-file:
	@read -p "Enter test file name (e.g., test_models.py): " file; \
	uv run python run_tests.py --file $$file

# Watch mode for tests (requires entr)
test-watch:
	find src tests -name "*.py" | entr -c make test-fast

# Add a new dependency
add:
	@read -p "Enter package name: " package; \
	uv add $$package

# Add a new development dependency
add-dev:
	@read -p "Enter dev package name: " package; \
	uv add --dev $$package
.PHONY: help install dev lint format test clean run

help:
	@echo "Available targets:"
	@echo "  install    - Install project dependencies with uv"
	@echo "  dev        - Install development dependencies"
	@echo "  run        - Run the script with uv"
	@echo "  lint       - Run linting checks (ruff)"
	@echo "  format     - Format code with black"
	@echo "  type-check - Run type checking with mypy"
	@echo "  test       - Run tests with pytest"
	@echo "  clean      - Remove build artifacts and cache files"
	@echo "  all        - Install, lint, format, and test"

install:
	uv sync

dev:
	uv sync --all-extras

run:
	uv run python mealie_toolkit/main.py --help

lint:
	ruff check .

format:
	black .

type-check:
	mypy .

test:
	pytest

all: install lint format test
	@echo "All tasks completed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true

.DEFAULT_GOAL := help

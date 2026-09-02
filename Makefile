.PHONY: help install lint test type-check format clean build docs docker-up docker-down

PYTHON := python3.12
VENV := .venv

help:
	@echo "NIGHTHAWK — Ethical Red-Team Platform"
	@echo ""
	@echo "Usage:"
	@echo "  make install    Install dependencies"
	@echo "  make lint      Run ruff linting"
	@echo "  make format    Auto-format code"
	@echo "  make test      Run tests"
	@echo "  make coverage  Run tests with coverage"
	@echo "  make type-check Run mypy"
	@echo "  make build     Build package"
	@echo "  make docs      Build documentation"
	@echo "  make docker-up Start services"
	@echo "  make docker-down Stop services"

install:
	@echo "Installing NIGHTHAWK..."
	pip install --upgrade pip
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

test:
	pytest -q --cov=nighthawk --cov-report=term-missing

type-check:
	mypy src/nighthawk --ignore-missing-imports --exclude tests/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

clean:
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/

build:
	python -m build

docs:
	@echo "Documentation available in docs/"

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

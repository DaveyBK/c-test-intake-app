.PHONY: help install install-dev test test-coverage lint format clean security pre-commit

help:
	@echo "C-Test Intake App - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make pre-commit       Set up pre-commit hooks"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run all linters (flake8, pylint)"
	@echo "  make format           Auto-format code (black, isort)"
	@echo "  make format-check     Check formatting without changing files"
	@echo "  make type-check       Run mypy type checking"
	@echo ""
	@echo "Security:"
	@echo "  make security         Run security checks (bandit, safety)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Remove build artifacts and cache"
	@echo "  make run              Run the application"
	@echo "  make demo             Run integration demo"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

pre-commit:
	pre-commit install
	@echo "Pre-commit hooks installed!"

test:
	python -m unittest discover tests/

test-coverage:
	coverage run -m unittest discover tests/
	coverage report
	coverage html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running flake8..."
	flake8 .
	@echo "Running pylint..."
	pylint *.py || true

format:
	@echo "Formatting with black..."
	black .
	@echo "Sorting imports with isort..."
	isort .

format-check:
	@echo "Checking formatting..."
	black --check --diff .
	isort --check-only --diff .

type-check:
	@echo "Running mypy..."
	mypy --ignore-missing-imports . || true

security:
	@echo "Running bandit security scan..."
	bandit -r . -ll || true
	@echo "Checking dependencies with safety..."
	pip install -r requirements.txt
	safety check || true

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/ 2>/dev/null || true
	rm -rf .pytest_cache/ .mypy_cache/ .tox/ 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true
	rm -f bandit-report.json safety-report.json 2>/dev/null || true
	@echo "Clean complete!"

run:
	python main.py

demo:
	python demo_integration.py

all: clean install-dev format lint test
	@echo "All checks complete!"

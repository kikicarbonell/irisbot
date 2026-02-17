.PHONY: help install install-dev pre-commit-install pre-commit-run pre-commit-update test test-cov test-html test-watch test-fast lint format clean coverage-check ci-local

help:
	@echo "🤖 Irisbot Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install              Install dependencies"
	@echo "  make install-dev          Install dev dependencies"
	@echo "  make pre-commit-install   Install pre-commit hooks"
	@echo ""
	@echo "Running:"
	@echo "  make run                  Run the catalog scraper"
	@echo ""
	@echo "Pre-commit Hooks:"
	@echo "  make pre-commit-run       Run pre-commit on all files"
	@echo "  make pre-commit-update    Update pre-commit hooks"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 Run all tests"
	@echo "  make test-fast            Run tests (quick, no capture)"
	@echo "  make test-watch           Run tests in watch mode"
	@echo "  make test-cov             Run tests with coverage"
	@echo "  make test-cov-html        Generate HTML coverage report"
	@echo "  make coverage-check       Verify 90% coverage threshold"
	@echo ""
	@echo "Linting & Code Quality:"
	@echo "  make lint                 Run code style checks"
	@echo "  make format               Format code automatically"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci-local             Simulate GitHub Actions locally"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                Remove build artifacts"
	@echo "  make clean-all            Remove build + test artifacts"
	@echo ""

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .
	python -m playwright install chromium firefox

install-dev:
	pip install -r requirements-dev.txt
	python -m playwright install --with-deps chromium firefox webdriver
	@echo "✅ Dev dependencies installed. Run 'make pre-commit-install' to setup git hooks."

pre-commit-install:
	. .venv/bin/activate && pre-commit install --hook-type pre-commit
	@echo "✅ Pre-commit hooks installed. They will run automatically on 'git commit'."

pre-commit-run:
	. .venv/bin/activate && pre-commit run --all-files

pre-commit-update:
	. .venv/bin/activate && pre-commit autoupdate
	@echo "✅ Pre-commit hooks updated."

run:
	@echo "🚀 Running catalog scraper..."
	python src/scrape_catalog_phase1.py

test:
	pytest tests/ -v --tb=short

test-fast:
	pytest tests/ -v -s --tb=line

test-watch:
	@command -v ptw >/dev/null || pip install pytest-watch
	ptw tests/ -- -v

test-cov:
	pytest --cov=src --cov-report=term-missing tests/ -v

test-cov-html:
	pytest --cov=src --cov-report=html --cov-report=term tests/ -v
	@echo ""
	@echo "📊 Coverage report generated: htmlcov/index.html"
	@echo "🌐 Opening in browser..."
	@command -v open >/dev/null && open htmlcov/index.html || xdg-open htmlcov/index.html || start htmlcov/index.html

coverage-check:
	@echo "Verifying 90% coverage threshold..."
	coverage report --fail-under=90

lint:
	@echo "🔍 Running linters..."
	@command -v pylint >/dev/null && pylint irisbot/ --disable=C0111,C0103,C0301 || echo "pylint not installed"
	@command -v flake8 >/dev/null && flake8 irisbot/ --max-line-length=120 --ignore=E501,W503 || echo "flake8 not installed"
	@command -v mypy >/dev/null && mypy irisbot/ --ignore-missing-imports || echo "mypy not installed"

format:
	@echo "🎨 Formatting code..."
	@command -v black >/dev/null && black irisbot/ tests/ || echo "black not installed"
	@command -v isort >/dev/null && isort irisbot/ tests/ || echo "isort not installed"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/ dist/ .eggs/ *.egg-info/
	rm -rf .pytest_cache/ .coverage coverage.xml
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	@echo "✅ Clean complete"

clean-all: clean
	@echo "🧹 Cleaning test artifacts..."
	rm -rf htmlcov/ .hypothesis/
	rm -f test_*.db catalog_projects.db
	@echo "✅ Full clean complete"

ci-local:
	@echo "🔄 Simulating GitHub Actions locally..."
	@echo ""
	@echo "Step 1: Installing dependencies..."
	pip install -r requirements.txt pytest-cov
	@echo ""
	@echo "Step 2: Installing Playwright..."
	python -m playwright install --with-deps chromium
	@echo ""
	@echo "Step 3: Running tests with coverage..."
	pytest --cov=. --cov-report=xml --cov-report=term --cov-report=html tests/ -v
	@echo ""
	@echo "Step 4: Verifying coverage (90% minimum)..."
	coverage report --fail-under=90
	@echo ""
	@echo "✅ CI simulation complete - all checks passed!"
	@echo ""
	@echo "📊 HTML Report: htmlcov/index.html"
	@echo "🐍 Coverage File: coverage.xml"

.PHONY: help build clean deptree format lint ruff setup test all

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup    - Set up development environment"
	@echo "  make build    - Build the package"
	@echo "  make test     - Run all tests"
	@echo "  make test-unit - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-e2e - Run end-to-end tests only"
	@echo "  make test-verbose - Run tests with verbose output"
	@echo "  make test-fast - Run tests without coverage"
	@echo "  make lint     - Run linting"
	@echo "  make ruff     - Run ruff linter and formatter"
	@echo "  make format   - Format code"
	@echo "  make clean    - Clean build artifacts and caches"
	@echo "  make clean-all - Deep clean (removes .venv and all artifacts)"
	@echo "  make deptree  - Analyze dependency tree"
	@echo "  make all      - Run setup, lint, test, and build"

# Setup development environment
setup:
	@./scripts/setup.sh

# Build the package
build:
	@./scripts/build.sh

# Run tests
test:
	@./scripts/test.sh --all

# Run unit tests only
test-unit:
	@./scripts/test.sh --unit

# Run integration tests only
test-integration:
	@./scripts/test.sh --integration

# Run end-to-end tests only
test-e2e:
	@./scripts/test.sh --e2e

# Run tests with verbose output
test-verbose:
	@./scripts/test.sh --all --verbose

# Run tests without coverage
test-fast:
	@./scripts/test.sh --all --no-cov

# Run linting
lint:
	@./scripts/lint.sh

# Run ruff linter and formatter
ruff:
	@./scripts/ruff.sh

# Format code
format:
	@./scripts/format.sh

# Clean build artifacts (keeps .venv)
clean:
	@./scripts/clean.sh --keep-venv

# Deep clean (removes .venv and all artifacts)
clean-all:
	@echo "Performing deep clean (removes .venv)..."
	@./scripts/clean.sh
	@echo "Deep clean completed!"

# Analyze dependency tree
deptree:
	@./scripts/deptree.sh

# Run all main tasks
all: setup lint test-fast build
	@echo "All tasks completed successfully!"

#!/bin/bash
set -e

echo "Linting tensym code..."

# Check if flake8 is available, install if not
if ! uv run flake8 --version &> /dev/null; then
    echo "Installing flake8..."
    uv add flake8 --dev
fi

# Check if mypy is available, install if not
if ! uv run mypy --version &> /dev/null; then
    echo "Installing mypy..."
    uv add mypy --dev
fi

echo "Running flake8 linter..."
uv run flake8

echo "Running mypy type checker..."
uv run mypy tensym/

echo "Linting completed successfully!"

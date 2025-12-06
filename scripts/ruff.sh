#!/bin/bash
set -e

echo "Running ruff on tensym..."

# Check if ruff is available, install if not
if ! uv run ruff --version &> /dev/null; then
    echo "Installing ruff..."
    uv add ruff --dev
fi

echo "Running ruff linter..."
uv run ruff check .

echo "Running ruff formatter..."
uv run ruff format .

echo "Ruff completed successfully!"

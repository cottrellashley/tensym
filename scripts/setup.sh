#!/bin/bash
set -e

echo "Setting up tensym development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Sync all dependencies from pyproject.toml
echo "Syncing dependencies..."
uv sync

echo "Setup completed successfully!"
echo "Virtual environment is ready at .venv/"
echo "Run 'source .venv/bin/activate' to activate it manually, or use 'uv run' commands."

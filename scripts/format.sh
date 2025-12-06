#!/bin/bash
set -e

echo "Formatting tensym code..."

# Check if black is available, install if not
if ! uv run black --version &> /dev/null; then
    echo "Installing black..."
    uv add black --dev
fi

# Check if isort is available, install if not
if ! uv run isort --version &> /dev/null; then
    echo "Installing isort..."
    uv add isort --dev
fi

echo "Running black formatter..."
uv run black tensym/ tests/ pocs/ --line-length 88

echo "Running isort import sorter..."
uv run isort tensym/ tests/ pocs/ --profile black

echo "Code formatting completed successfully!"

#!/bin/bash
set -e

echo "Building tensym..."

# Create build directory if it doesn't exist
mkdir -p build

# Install dependencies
echo "Installing dependencies..."
uv sync

# Ensure build tool is available
if ! uv run python -c "import build" &> /dev/null; then
    echo "Installing build tool..."
    uv add build --dev
fi

# Build the package
echo "Building package..."
uv run python -m build

echo "Build completed successfully!"

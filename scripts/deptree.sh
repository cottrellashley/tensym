#!/bin/bash
set -e

echo "Analyzing dependency tree for tensym..."

# Check if pipdeptree is installed, install if not
if ! uv run pipdeptree --version &> /dev/null; then
    echo "Installing pipdeptree..."
    uv add pipdeptree --dev
fi

echo "Dependency tree:"
uv run pipdeptree

echo ""
echo "Checking for security vulnerabilities..."
if uv run safety --version &> /dev/null; then
    uv run safety check
else
    echo "Installing safety..."
    uv add safety --dev
    uv run safety check
fi

echo "Dependency analysis completed!"

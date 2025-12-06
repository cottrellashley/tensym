#!/bin/bash
set -e

echo "Cleaning tensym..."

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [--keep-venv] [--help]"
    echo ""
    echo "Options:"
    echo "  --keep-venv    Keep the .venv directory (default for 'make clean')"
    echo "  --help, -h     Show this help message"
    echo ""
    echo "This script removes:"
    echo "  - Python cache files (*.pyc, __pycache__, etc.)"
    echo "  - Build artifacts (build/, dist/, *.egg-info/)"
    echo "  - Test artifacts (.pytest_cache/, htmlcov/, .coverage)"
    echo "  - Linter caches (.ruff_cache, .mypy_cache, .flake8, etc.)"
    echo "  - IDE files (.idea/, .vscode/)"
    echo "  - Temporary files (*.tmp, *.log, *.bak)"
    echo "  - Virtual environments (.venv unless --keep-venv is used)"
    exit 0
fi

# Function to safely remove directories/files
safe_remove() {
    if [ -e "$1" ]; then
        echo "  Removing $1"
        rm -rf "$1"
    fi
}

# Remove Python cache files (excluding .venv)
echo "Removing Python cache files..."
find . -path "./.venv" -prune -o -type f -name "*.pyc" -delete 2>/dev/null || true
find . -path "./.venv" -prune -o -type f -name "*.pyo" -delete 2>/dev/null || true
find . -path "./.venv" -prune -o -type f -name "*.pyd" -delete 2>/dev/null || true
find . -path "./.venv" -prune -o -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove virtual environments and package managers
echo "Removing virtual environments..."
if [ "$1" = "--keep-venv" ]; then
    echo "  Keeping .venv (--keep-venv flag specified)"
else
    rm -r .venv
fi
safe_remove "venv"
safe_remove "env"
safe_remove ".env"

# Remove linter and formatter caches
echo "Removing linter and formatter caches..."
safe_remove ".ruff_cache"
safe_remove ".mypy_cache"
safe_remove ".pylint.d"
safe_remove ".black"
safe_remove ".isort.cfg"
safe_remove ".flake8"

# Remove build artifacts
echo "Removing build artifacts..."
safe_remove "build/"
safe_remove "dist/"
safe_remove "*.egg-info/"
safe_remove ".eggs/"
safe_remove "wheels/"

# Remove test artifacts
echo "Removing test artifacts..."
safe_remove ".pytest_cache/"
safe_remove ".coverage"
safe_remove ".coverage.*"
safe_remove "htmlcov/"
safe_remove ".tox/"
safe_remove ".nox/"
safe_remove "coverage.xml"
safe_remove "*.cover"
safe_remove ".hypothesis/"

# Remove documentation build artifacts
echo "Removing documentation artifacts..."
safe_remove ".doctrees/"

# Remove Jupyter notebook checkpoints
echo "Removing Jupyter artifacts..."
find . -path "./.venv" -prune -o -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

# Remove temporary and log files
echo "Removing temporary files..."
find . -path "./.venv" -prune -o -name "*.tmp" -delete 2>/dev/null || true
find . -path "./.venv" -prune -o -name "*.log" -delete 2>/dev/null || true
find . -path "./.venv" -prune -o -name "*.bak" -delete 2>/dev/null || true
find . -path "./.venv" -prune -o -name "*.orig" -delete 2>/dev/null || true

# Remove OS-specific files
echo "Removing OS-specific files..."
find . -path "./.venv" -prune -o -name ".DS_Store" -delete 2>/dev/null || true
find . -path "./.venv" -prune -o -name "Thumbs.db" -delete 2>/dev/null || true
find . -path "./.venv" -prune -o -name "desktop.ini" -delete 2>/dev/null || true

# Remove profiling and debugging artifacts
echo "Removing profiling artifacts..."
safe_remove "*.prof"
safe_remove ".profile"
safe_remove "cachegrind.out.*"

echo "Clean completed successfully!"
echo "Removed all development artifacts, caches, and temporary files."

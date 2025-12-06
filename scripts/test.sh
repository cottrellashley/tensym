#!/bin/bash
set -e

echo "Running tests for tensym..."

# Check if pytest is available, install if not
if ! uv run pytest --version &> /dev/null; then
    echo "Installing pytest..."
    uv add pytest pytest-cov --dev
fi

# Parse command line arguments
TEST_TYPE=""
VERBOSE=""
COVERAGE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --e2e)
            TEST_TYPE="e2e"
            shift
            ;;
        --all)
            TEST_TYPE="all"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        --no-cov)
            COVERAGE="--no-cov"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--unit|--integration|--e2e|--all] [-v|--verbose] [--no-cov]"
            exit 1
            ;;
    esac
done

# Set default test type if none specified
if [ -z "$TEST_TYPE" ]; then
    TEST_TYPE="all"
fi

# Build pytest command
PYTEST_CMD="uv run pytest"

# Add test path based on type
case $TEST_TYPE in
    unit)
        PYTEST_CMD="$PYTEST_CMD tests/unit/"
        echo "Running unit tests..."
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD tests/integration/"
        echo "Running integration tests..."
        ;;
    e2e)
        PYTEST_CMD="$PYTEST_CMD tests/e2e/"
        echo "Running end-to-end tests..."
        ;;
    all)
        PYTEST_CMD="$PYTEST_CMD tests/"
        echo "Running all tests..."
        ;;
esac

# Add verbose flag if requested
if [ -n "$VERBOSE" ]; then
    PYTEST_CMD="$PYTEST_CMD $VERBOSE"
fi

# Add coverage unless disabled
if [ -z "$COVERAGE" ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=tensym --cov-report=html --cov-report=term"
fi

# Run the tests
echo "Command: $PYTEST_CMD"
eval $PYTEST_CMD

if [ -z "$COVERAGE" ]; then
    echo "Test coverage report generated in htmlcov/"
fi
echo "Tests completed successfully!"

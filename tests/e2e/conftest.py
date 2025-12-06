# tests/e2e/conftest.py
"""Configuration for end-to-end tests.

E2E tests should test complete user workflows from input to output.
"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_tensym_file():
    """Create a temporary TenSym file for testing."""

    def _create_file(content: str, suffix: str = ".tensym"):
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    return _create_file


@pytest.fixture
def fixtures_dir():
    """Path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def simple_math_example():
    """Simple mathematical expression example."""
    return """
# Basic arithmetic
let a = 10
let b = 20
let sum = a + b
let product = a * b

print("Sum:", sum)
print("Product:", product)
"""


@pytest.fixture
def tensor_example():
    """Tensor calculation example."""
    return """
# Tensor operations
with metric η:
    # Minkowski metric
    η_{00} = -1
    η_{11} = 1
    η_{22} = 1
    η_{33} = 1
    
    # Four-vector
    x^μ = [t, x, y, z]
    
    # Invariant interval
    ds² = η_{μν} * x^μ * x^ν
"""


@pytest.fixture
def function_example():
    """Function definition example."""
    return """
# Function definitions
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

# Usage
let fact_5 = factorial(5)
let fib_10 = fibonacci(10)
"""

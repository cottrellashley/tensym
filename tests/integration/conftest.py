# tests/integration/conftest.py
"""Configuration for integration tests.

Integration tests should test component interactions with real dependencies.
"""

import pytest


@pytest.fixture
def lexer():
    """Real lexer instance for integration testing."""
    from tensym.interpreter.lexer._lexer import Lexer

    return Lexer()


@pytest.fixture
def sample_tensym_code():
    """Sample TenSym code for integration testing."""
    return """
# Simple mathematical expression
let x = 42
let y = 3.14

# Tensor notation
T_{ij} = g^{mu nu} * R_{mu nu}

# Function definition
def calculate(a, b):
    return a + b * pi

# Greek letters and Unicode
result = α + β ≤ γ → δ
"""


@pytest.fixture
def complex_tensym_code():
    """More complex TenSym code for integration testing."""
    return """
# Einstein summation with tensor operations
with metric g:
    # Define Riemann tensor
    R^{mu}_{nu rho sigma} = ∂_rho Γ^mu_{nu sigma} - ∂_sigma Γ^mu_{nu rho}
    
    # Calculate Ricci tensor
    R_{mu nu} = R^rho_{mu rho nu}
    
    # Compute scalar curvature
    R = g^{mu nu} * R_{mu nu}

# Function with tensor arguments
def einstein_tensor(g, R):
    return R - (1/2) * g * R
"""

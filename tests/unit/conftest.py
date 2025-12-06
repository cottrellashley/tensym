# tests/unit/conftest.py
"""Configuration for unit tests.

Unit tests should test individual components in isolation with mocked dependencies.
"""

from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_lexer():
    """Mock lexer for testing parser components."""
    lexer = Mock()
    lexer.tokenize.return_value = []
    return lexer


@pytest.fixture
def mock_parser():
    """Mock parser for testing AST components."""
    parser = Mock()
    parser.parse.return_value = None
    return parser


@pytest.fixture
def sample_tokens():
    """Sample tokens for testing."""
    from tensym.interpreter.sourcecode import Position
    from tensym.interpreter.token._kind import TokenKind
    from tensym.interpreter.token._token import Token

    return [
        Token(TokenKind.KW_LET, "let", Position(1, 1)),
        Token(TokenKind.ID, "x", Position(1, 5)),
        Token(TokenKind.OP_EQUATE, "=", Position(1, 7)),
        Token(TokenKind.INTEGER, "42", Position(1, 9)),
    ]


@pytest.fixture
def sample_source_code():
    """Sample source code for testing."""
    return "let x = 42\nlet y = x + 1"

"""Minimal parser stub for tensym.

Produces a very small AST for testing the pipeline.
"""

from typing import Iterable

from .ast_nodes import Module
from .lexer import Token


def parse(tokens: Iterable[Token]) -> Module:
    """Parse tokens into a Module AST. This is a placeholder for the real parser."""
    # For now produce an empty module
    return Module(body=[])

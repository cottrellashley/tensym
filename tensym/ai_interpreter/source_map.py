"""Source map utilities: attach source spans to AST / HIR nodes (minimal).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceSpan:
    filename: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int


def attach_span(node, span: Optional[SourceSpan]):
    setattr(node, "_span", span)
    return node


def get_span(node) -> Optional[SourceSpan]:
    return getattr(node, "_span", None)


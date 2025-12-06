"""Simple tokenizer stub for tensym language.

This is a minimal placeholder; replace with a full lexer later.
"""

from dataclasses import dataclass
from typing import Iterator


@dataclass
class Token:
    type: str
    value: str
    line: int = 0
    col: int = 0


def tokenize(source: str) -> Iterator[Token]:
    """Yield a very small set of tokens for testing front-end plumbing."""
    # naive split by whitespace for placeholder purposes
    for i, part in enumerate(source.split()):
        yield Token(
            type="IDENT" if part.isidentifier() else "SYM",
            value=part,
            line=1,
            col=i + 1,
        )

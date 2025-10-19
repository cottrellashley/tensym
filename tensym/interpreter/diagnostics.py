"""Diagnostics and error reporting helpers."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceSpan:
    filename: str
    start_line: int
    start_pos: int
    end_line: int
    end_pos: int

    @classmethod
    def from_filepath(cls, filepath, strat_index, end_index: Optional[int] = None):
        with open(filepath, 'r') as f:
            raw_code = f.read()
        return cls.from_raw_code(raw_code, strat_index, end_index, filepath)

    @classmethod
    def from_raw_code(cls, raw_code, strat_index, end_index: Optional[int] = None, filename: str = "<string>"):
        if end_index is None:
            end_index = strat_index + 1
        start_line = raw_code.count('\n', 0, strat_index) + 1
        start_pos = strat_index - raw_code.rfind('\n', 0, strat_index)
        end_line = raw_code.count('\n', 0, end_index) + 1
        end_pos = end_index - raw_code.rfind('\n', 0, end_index)
        return cls(filename, start_line, start_pos, end_line, end_pos)


@dataclass
class Diagnostic:
    message: str
    span: Optional[SourceSpan] = None
    level: str = "error"  # or 'warning', 'info'


class InvalidSyntaxError(Exception):
    """Raised when the syntax of the input is invalid."""
    def __init__(self, message: str, location: tuple[int, int]) -> None:
        super().__init__(message)
        self.message = message


def error(message: str, span: Optional[SourceSpan] = None) -> Diagnostic:
    return Diagnostic(message=message, span=span, level="error")


def warn(message: str, span: Optional[SourceSpan] = None) -> Diagnostic:
    return Diagnostic(message=message, span=span, level="warning")


def raise_invalid_syntax(iterable):
    from .iterator import CodeIterator, IterBoundary
    assert isinstance(iterable, CodeIterator)
    
    # Handle the case where current is not a valid character
    if isinstance(iterable.current, int):
        char_repr = f"'{chr(iterable.current)}'"
    else:
        char_repr = str(iterable.current)
    
    raise SyntaxError(
        f"Invalid syntax at line:{iterable.current_line} pos:{iterable.current_pos} char:{char_repr} at:\n"
        f"{iterable.printable_current_position_underlined()}"
    )

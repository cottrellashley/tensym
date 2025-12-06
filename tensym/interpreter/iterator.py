from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Generic, Optional, TypeVar, Union

from tensym.interpreter.sourcecode import SourceCode

from .diagnostics import SourceSpan

if TYPE_CHECKING:
    from .token import Token

T = TypeVar("T")


class IterBoundary(Enum):
    EOI = "END_OF_ITER"
    SOI = "START_OF_ITER"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Iterator(Generic[T]):
    boundary = IterBoundary

    def __init__(self, iterable):
        # Ensure the input is iterable
        if not hasattr(iterable, "__len__"):
            raise ValueError("Argument must be an iterable")
        if not hasattr(iterable, "__getitem__"):
            raise ValueError("Argument must be an iterable")

        # If it's not indexable, convert it to a list
        self.__object = iterable
        self._index = -1
        self.__len = len(iterable)

    @property
    def length(self) -> int:
        return self.__len

    @property
    def index(self) -> int:
        return self._index

    @property
    def current(self) -> Union[T, IterBoundary]:
        if self._index == -1:
            return IterBoundary.SOI
        if 0 <= self._index < self.length:
            return self.__object[self._index]
        return IterBoundary.EOI

    def __repr__(self):
        return repr([_ for _ in self.__object])

    def __str__(self):
        return str(self)

    def __next__(self) -> Union[T, IterBoundary]:
        next_object = self.advance()
        if next_object == IterBoundary.EOI:
            raise StopIteration
        return next_object

    def __iter__(self):
        return self

    def advance(self) -> Union[T, IterBoundary]:
        """Advance to the next item and return it. Returns None if at the end."""
        self._index += 1
        return self.current

    def peek(self, n: int = 1, default: Optional[T] = None) -> Optional[T]:
        """Return the nth item ahead without advancing, or default if out of range."""
        next_index = self.index + n
        if next_index < self.length:
            return self.__object[next_index]
        return default

    def reset(self):
        """Reset the iterator."""
        self._index = -1

    def __len__(self) -> int:
        return self.length

    @property
    def original(self) -> str:
        """
        Return the original string if the underlying iterable is a string.
        Raises an AttributeError otherwise.
        """
        return str(self.__object)


class CodeIterator(Iterator[int]):
    def __init__(self, raw_code: Optional[str] = None, filepath: Optional[str] = None):
        if raw_code is None and filepath is None:
            raise ValueError("Either 'code' or 'filepath' must be provided.")
        if raw_code is not None and filepath is not None:
            raise ValueError("Only one of 'code' or 'filepath' should be provided.")
        if filepath is not None:
            sc = SourceCode.from_file(filepath)
            self.raw_code = sc.as_string
            self.__filepath = filepath
        else:
            sc = SourceCode.from_string(raw_code)
            self.raw_code = sc.as_string
            self.__filepath = "<string>"
        # Convert string to Unicode code points instead of UTF-8 bytes
        unicode_codepoints = [ord(c) for c in sc.as_string]
        super().__init__(unicode_codepoints)

    @property
    def filepath(self) -> str:
        return self.__filepath

    @property
    def is_file(self) -> bool:
        return self.__filepath != "<string>"

    @property
    def current_line(self) -> int:
        if self._index < 0 or self._index >= self.length:
            return -1
        return self.raw_code.count("\n", 0, self._index) + 1

    @property
    def current_pos(self) -> int:
        if self._index < 0 or self._index >= self.length:
            return -1
        return self._index - self.raw_code.rfind("\n", 0, self._index)

    def build_source_span(self, start_index: int, end_index: int = None) -> SourceSpan:
        """
        Get the substring of the source code from start to end indices.
        :return: The substring from start to end.
        """
        if end_index is None:
            end_index = start_index + 1
        if start_index < 0 or end_index > self.length or start_index >= end_index:
            raise IndexError(
                f"Invalid span range {start_index}:{end_index} for source code of length {self.length}."
            )
        return SourceSpan.from_raw_code(
            self.raw_code, start_index, end_index, self.filepath
        )

    def get_source_span_from_current(self) -> SourceSpan:
        if self.index < 0 or self.index >= self.length:
            raise IndexError(
                f"Current index {self.index} is out of range for source code of length {self.length}."
            )
        return self.build_source_span(self.index, self.index + 1)

    def printable_current_position_underlined(self) -> str:
        span = self.get_source_span_from_current()
        lines = self.raw_code.splitlines()
        if span.start_line - 1 < 0 or span.start_line - 1 >= len(lines):
            return ""
        line_content = lines[span.start_line - 1]
        underline = " " * (span.start_pos - 1) + "^"
        return f"{line_content}\n{underline}"

    def pprint_token(self, token: "Token") -> str:
        end = token.end_index
        start = end - len(token)
        span = self.build_source_span(start, end)
        lines = self.raw_code.splitlines()
        if span.start_line - 1 < 0 or span.start_line - 1 >= len(lines):
            return ""
        line_content = lines[span.start_line - 1]
        underline = " " * (span.start_pos - 1) + "^"
        return f"{line_content}\n{underline}"

    def pprint_source_span(self, span: SourceSpan) -> str:
        lines = self.raw_code.splitlines()
        # Handle case when end pos is a newline character at the end of the line
        if span.start_line - 1 < 0 or span.start_line - 1 >= len(lines):
            return ""
        line_content = lines[span.start_line - 1]

        pointers = "^" * (span.end_pos - span.start_pos)
        underline = " " * (span.start_pos - 1) + pointers
        return f"{line_content}\n{underline}"

    def source_span_from_token(
        self, start_token: "Token", end_token: "Token" = None
    ) -> SourceSpan:
        if end_token is not None:
            end = end_token.end_index
            start = start_token.end_index - len(start_token)
        else:
            end = start_token.end_index
            start = start_token.end_index - len(start_token)
        return self.build_source_span(start, end)

    def __str__(self):
        return self.raw_code

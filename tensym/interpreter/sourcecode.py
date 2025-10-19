from typing import List, ByteString, Optional


class SourceCode:
    """
    A class to read source code in various formats and return all into a list of UTF-8 encoded integers.

    The idea is lexer takes in a list of integers and produces tokens from it. So raw code can come in from various
    sources, but the lexer only needs to deal with one format.

    Supported input formats:
    str -> UTF-8 encoded integers
    bytes -> UTF-8 encoded integers
    file content -> UTF-8 encoded integers
    stream content -> UTF-8 encoded integers

    Provides methods to access the source code as a string, bytes, or list of integers.
    Supports concatenation, length retrieval, and iteration.
    Can be used as a context manager.
    """
    def __init__(self, sc_bytes: ByteString):
        self.__sc_bytes = sc_bytes
        self.filename = None

    @property
    def as_byte_list(self) -> List[int]:
        """Return the source code as a list of integer UTF-8 byte values."""
        return list(self.__sc_bytes)

    @property
    def as_unicode(self) -> List[int]:
        return list(self.__sc_bytes)

    @property
    def as_string(self) -> str:
        """Return the source code as a decoded UTF-8 string."""
        return self.__sc_bytes.decode('utf-8')

    @property
    def as_byte_string(self) -> ByteString:
        """Return the source code as raw UTF-8 encoded bytes."""
        return self.__sc_bytes

    @classmethod
    def from_string(cls, s: str):
        """Create a SourceCode object from a string."""
        return cls(s.encode('utf-8'))

    @classmethod
    def from_file(cls, file_path: str):
        """Create a SourceCode object from a UTF-8 encoded file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            source_code = file.read()
        return cls(source_code.encode('utf-8'))

    @classmethod
    def from_stream(cls, stream):
        """Create a SourceCode object from a stream (e.g., a file-like object)."""
        source_code = stream.read()
        return cls(source_code.encode('utf-8'))

    @classmethod
    def from_bytes(cls, b: bytes):
        """Create a SourceCode object from raw bytes."""
        return cls(b)

    def __str__(self):
        return self.as_string

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        """Concatenate two SourceCode objects."""
        return SourceCode.from_string(self.as_string + other.as_string)

    def __len__(self) -> int:
        """Return the length of the source code in characters."""
        return len(self.as_string)

    def __iter__(self):
        """Iterate over the integer representation of each UTF-8 character."""
        return iter(self.as_byte_list)

    def __enter__(self):
        """Enter a context manager."""
        # Return self to allow access to the SourceCode object in the `with` block.
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager."""
        # No resources to clean up, but this ensures compatibility with `with`.
        pass

    def __getitem__(self, item):
        """Return the integer representation of each UTF-8 character."""
        return self.as_byte_list[item]

    def char_at(self, position: int) -> str:
        """
        Get the character at a specific position in the source code.
        :param position: The index of the character (0-based).
        :return: The character at the specified position.
        """
        if position < 0 or position >= len(self):
            raise IndexError(f"Position {position} is out of range for source code of length {len(self)}.")
        return self.as_string[position]

    def peek(self, position: int, count: int = 1) -> str:
        """
        Peek ahead to view characters starting at a specific position.
        :param position: The starting position (0-based).
        :param count: The number of characters to preview.
        :return: A substring of the specified length starting from the position.
        """
        if position < 0 or position >= len(self):
            raise IndexError(f"Position {position} is out of range for source code of length {len(self)}.")
        return self.as_string[position:position + count]

    def slice(self, start: int, end: Optional[int] = None) -> str:
        """
        Get a substring of the source code.
        :param start: The starting index (0-based, inclusive).
        :param end: The ending index (0-based, exclusive). If None, goes to the end of the string.
        :return: The sliced substring.
        """
        if start < 0 or start >= len(self) or (end is not None and (end < start or end > len(self))):
            raise IndexError(f"Invalid slice range {start}:{end} for source code of length {len(self)}.")
        return self.as_string[start:end]

    def is_empty(self) -> bool:
        """Check if the source code is empty."""
        return len(self.__sc_bytes) == 0

    def remaining_bytes(self, start: int) -> List[int]:
        """
        Get the remaining bytes in the source code starting from a given position.
        :param start: The starting position.
        :return: A list of remaining byte values.
        """
        if start < 0 or start >= len(self.as_byte_list):
            raise IndexError(f"Position {start} is out of range for source code of length {len(self)}.")
        return self.as_byte_list[start:]

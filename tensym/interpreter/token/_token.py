from typing import List, Tuple, Union
from tensym.interpreter.token._kind import TokenKind


class Token:

    def __init__(
            self,
            *,
            kind: TokenKind,
            lexeme_unicode: List[int] = None,
            end_index: int = -1,
    ):
        self.__index = end_index
        self.__kind = kind
        self.__lexeme_unicode = lexeme_unicode

    def __repr__(self):
        return f"(loc {self.__index}: {self.__kind}, {self.lexeme_repr})"

    def as_tuple(self) -> Tuple[TokenKind, str]:
        return self.kind, self.lexeme

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.kind == other.kind and self.lexeme_unicode == other.lexeme_unicode

    def __hash__(self):
        return hash((self.kind, tuple(self.lexeme_unicode) if self.lexeme_unicode is not None else None))

    def __len__(self):
        if self.__lexeme_unicode is not None:
            return len(self.__lexeme_unicode)
        return 0

    @property
    def end_index(self) -> int:
        return self.__index

    @property
    def kind(self) -> TokenKind:
        return self.__kind

    @property
    def lexeme_unicode(self):
        return self.__lexeme_unicode

    @property
    def lexeme(self):
        if self.__lexeme_unicode is not None:
            return "".join([chr(_) for _ in self.__lexeme_unicode])
        return None

    @property
    def lexeme_repr(self):
        if self.__lexeme_unicode is not None:
            return "'" + "".join([repr(chr(_))[1:-1] for _ in self.__lexeme_unicode]) + "'"
        return None

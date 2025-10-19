from __future__ import annotations
from enum import Enum, auto


# ─────────────────────────── Token kinds ────────────────────────────

class TokenKind(Enum):
    ID             = auto()
    LATEX_ID       = auto()
    TENSOR_ID      = auto()
    FUNC_ID        = auto()
    INTEGER        = auto()
    FLOAT          = auto()
    STRING         = auto()

    # Keywords / language
    KW_LET         = auto()
    KW_DEF         = auto()
    KW_WITH        = auto()
    KW_CONST       = auto()
    KW_PRINT       = auto()
    KW_DECLARE     = auto()
    KW_CONSTANT    = auto()
    KW_METRIC      = auto()

    # Logical / control
    KW_NOT         = auto()
    KW_AND         = auto()
    KW_OR          = auto()
    KW_IF          = auto()
    KW_THEN        = auto()
    KW_ELSE        = auto()
    KW_ELIF        = auto()

    # Math words / constants
    KW_INFTY       = auto()  # infty, oo
    KW_PI          = auto()  # pi
    KW_E           = auto()  # e
    KW_D           = auto()  # d

    # LaTeX-like words
    KW_NEWLINE     = auto()
    KW_SUM         = auto()
    KW_LIM         = auto()
    KW_FRAC        = auto()
    KW_BEGIN       = auto()
    KW_END         = auto()
    KW_DOSUM       = auto()
    KW_TO          = auto()
    KW_RIGHTARROW  = auto()
    KW_LEFTARROW   = auto()
    KW_PROD        = auto()
    KW_DOPROD      = auto()
    KW_EQUIV       = auto()
    KW_PDV         = auto()
    KW_DV          = auto()
    KW_INT         = auto()
    KW_PARTIAL     = auto()
    KW_SQRT        = auto()

    # Greek (names or single glyphs)
    KW_GREEK       = auto()

    # Operators / punctuation
    ASSIGNMENT     = auto()  # :=
    OP_PLUS        = auto()
    OP_MINUS       = auto()
    OP_MUL         = auto()
    OP_DIV         = auto()
    OP_MOD         = auto()

    OP_PLUSEQUAL   = auto()
    OP_MINUSEQUAL  = auto()
    OP_MULEQUAL    = auto()
    OP_DIVEQUAL    = auto()

    OP_EQUATE      = auto()  # =
    OP_EQ          = auto()  # ==
    OP_NE          = auto()  # !=, ≠
    OP_LT          = auto()
    OP_LE          = auto()  # <=, ≤
    OP_GT          = auto()
    OP_GE          = auto()  # >=, ≥
    OP_SHL         = auto()  # <<
    OP_SHR         = auto()  # >>
    OP_SHL_EQUAL   = auto()  # <<=
    OP_SHR_EQUAL   = auto()  # >>=
    OP_AND         = auto()  # &&
    OP_OR          = auto()  # ||
    OP_BAND        = auto()  # &
    OP_BOR         = auto()  # |
    OP_BXOR        = auto()  # ^
    OP_NOT         = auto()  # !
    OP_TILDE       = auto()  # ~
    OP_PRIME       = auto()  # ', ′, ″, ‴

    # Encapsulators / misc
    LBRACKET       = auto()  # [
    RBRACKET       = auto()  # ]
    LPAREN         = auto()  # (
    RPAREN         = auto()  # )
    LBRACE         = auto()  # {
    RBRACE         = auto()  # }
    COLON          = auto()  # :
    SEMICOLON      = auto()  # ;
    COMMA          = auto()  # ,
    BACKSLASH      = auto()  # \
    DOT            = auto()  # .
    UNDERSCORE     = auto()  # _ (for tensor index syntax)
    HASHTAG        = auto()  # # (comment)
    STRING_DELIM   = auto()  # "

    NEWLINE        = auto()
    INDENT         = auto()
    DEDENT         = auto()

    EOF            = auto()
    ERROR          = auto()

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.name
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.name)
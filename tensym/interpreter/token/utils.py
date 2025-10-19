# tensym/interpreter/token/utils.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional, Iterable, List, TYPE_CHECKING

from tensym.interpreter.token._kind import TokenKind

if TYPE_CHECKING:
    from tensym.interpreter.iterator import Iterator, IterBoundary


# ───────────────────────────── helpers ──────────────────────────────

def _ordt(s: str) -> Tuple[int, ...]:
    return tuple(map(ord, s))

def ord_tuple(s: str) -> Tuple[int, ...]:
    return tuple(map(ord, s))

def from_ord_tuple(t: Iterable[int]) -> str:
    return "".join(map(chr, t))

def word_lookup(word: str, WORD_TOKEN_MAP: Dict[Tuple[int, ...], TokenKind]) -> Optional[TokenKind]:
    return WORD_TOKEN_MAP.get(ord_tuple(word))

def _cp_is_int(x) -> bool:
    return isinstance(x, int)

def _cur_int(it: Iterator[int]) -> Optional[int]:
    c = it.current
    return c if _cp_is_int(c) else None   # SOI/EOI → None

def _peek_int(it: Iterator[int], k: int) -> Optional[int]:
    c = it.peek(k)
    return c if _cp_is_int(c) else None

def is_end_of_iteration(current_value) -> bool:
    """Check if the current iterator value indicates end of iteration.
    
    Args:
        current_value: The current value from an iterator
        
    Returns:
        True if this represents end of iteration (None or IterBoundary.EOI)
    """
    from tensym.interpreter.iterator import IterBoundary
    return current_value is None or current_value == IterBoundary.EOI


# ───────────────────────── 1) WORD-STARTING MAP ─────────────────────

WORD_TOKEN_MAP: Dict[Tuple[int, ...], TokenKind] = {
    # language
    _ordt("let"): TokenKind.KW_LET,
    _ordt("def"): TokenKind.KW_DEF,
    _ordt("with"): TokenKind.KW_WITH,
    _ordt("const"): TokenKind.KW_CONST,
    _ordt("print"): TokenKind.KW_PRINT,
    _ordt("declare"): TokenKind.KW_DECLARE,
    _ordt("constant"): TokenKind.KW_CONSTANT,
    _ordt("metric"): TokenKind.KW_METRIC,

    # logic / control
    _ordt("not"): TokenKind.KW_NOT,
    _ordt("and"): TokenKind.KW_AND,
    _ordt("or"):  TokenKind.KW_OR,
    _ordt("if"):  TokenKind.KW_IF,
    _ordt("then"):TokenKind.KW_THEN,
    _ordt("else"):TokenKind.KW_ELSE,
    _ordt("elif"):TokenKind.KW_ELIF,

    # math words / constants
    _ordt("d"):    TokenKind.KW_D,
    _ordt("pi"):   TokenKind.KW_PI,
    _ordt("e"):    TokenKind.KW_E,
    _ordt("oo"):   TokenKind.KW_INFTY,
    _ordt("infty"):TokenKind.KW_INFTY,

    # LaTeX-like words
    _ordt("newline"):     TokenKind.KW_NEWLINE,
    _ordt("sum"):         TokenKind.KW_SUM,
    _ordt("lim"):         TokenKind.KW_LIM,
    _ordt("frac"):        TokenKind.KW_FRAC,
    _ordt("begin"):       TokenKind.KW_BEGIN,
    _ordt("end"):         TokenKind.KW_END,
    _ordt("dosum"):       TokenKind.KW_DOSUM,
    _ordt("to"):          TokenKind.KW_TO,
    _ordt("rightarrow"):  TokenKind.KW_RIGHTARROW,
    _ordt("leftarrow"):   TokenKind.KW_LEFTARROW,
    _ordt("prod"):        TokenKind.KW_PROD,
    _ordt("doprod"):      TokenKind.KW_DOPROD,
    _ordt("equiv"):       TokenKind.KW_EQUIV,
    _ordt("pdv"):         TokenKind.KW_PDV,
    _ordt("dv"):          TokenKind.KW_DV,
    _ordt("int"):         TokenKind.KW_INT,
    _ordt("partial"):     TokenKind.KW_PARTIAL,
    _ordt("sqrt"):        TokenKind.KW_SQRT,

    # Greek names (map to KW_GREEK except 'pi' which is KW_PI above)
    _ordt("alpha"):TokenKind.KW_GREEK, _ordt("Alpha"):TokenKind.KW_GREEK,
    _ordt("beta"): TokenKind.KW_GREEK, _ordt("Beta"): TokenKind.KW_GREEK,
    _ordt("gamma"):TokenKind.KW_GREEK, _ordt("Gamma"):TokenKind.KW_GREEK,
    _ordt("delta"):TokenKind.KW_GREEK, _ordt("Delta"):TokenKind.KW_GREEK,
    _ordt("epsilon"):TokenKind.KW_GREEK, _ordt("Epsilon"):TokenKind.KW_GREEK,
    _ordt("zeta"): TokenKind.KW_GREEK,  _ordt("Zeta"): TokenKind.KW_GREEK,
    _ordt("eta"):  TokenKind.KW_GREEK,  _ordt("Eta"):  TokenKind.KW_GREEK,
    _ordt("theta"):TokenKind.KW_GREEK,  _ordt("Theta"):TokenKind.KW_GREEK,
    _ordt("iota"): TokenKind.KW_GREEK,  _ordt("Iota"): TokenKind.KW_GREEK,
    _ordt("kappa"):TokenKind.KW_GREEK,  _ordt("Kappa"):TokenKind.KW_GREEK,
    _ordt("lambda"):TokenKind.KW_GREEK, _ordt("Lambda"):TokenKind.KW_GREEK,
    _ordt("mu"):   TokenKind.KW_GREEK,  _ordt("Mu"):   TokenKind.KW_GREEK,
    _ordt("nu"):   TokenKind.KW_GREEK,  _ordt("Nu"):   TokenKind.KW_GREEK,
    _ordt("xi"):   TokenKind.KW_GREEK,  _ordt("Xi"):   TokenKind.KW_GREEK,
    _ordt("omicron"):TokenKind.KW_GREEK,_ordt("Omicron"):TokenKind.KW_GREEK,
    _ordt("Pi"):   TokenKind.KW_GREEK,  # capital word 'Pi'
    _ordt("rho"):  TokenKind.KW_GREEK,  _ordt("Rho"):  TokenKind.KW_GREEK,
    _ordt("sigma"):TokenKind.KW_GREEK,  _ordt("Sigma"):TokenKind.KW_GREEK,
    _ordt("tau"):  TokenKind.KW_GREEK,  _ordt("Tau"):  TokenKind.KW_GREEK,
    _ordt("upsilon"):TokenKind.KW_GREEK,_ordt("Upsilon"):TokenKind.KW_GREEK,
    _ordt("phi"):  TokenKind.KW_GREEK,  _ordt("Phi"):  TokenKind.KW_GREEK,
    _ordt("chi"):  TokenKind.KW_GREEK,  _ordt("Chi"):  TokenKind.KW_GREEK,
    _ordt("psi"):  TokenKind.KW_GREEK,  _ordt("Psi"):  TokenKind.KW_GREEK,
    _ordt("omega"):TokenKind.KW_GREEK,  _ordt("Omega"):TokenKind.KW_GREEK,
}

# ───────────────────────── 2) OP/GLYPH MAP ──────────────────────────
# NOTE: No NEWLINE_INDENT here; only '\n' → NEWLINE. INDENT/DEDENT emitted by Indenter.

OP_TOKEN_MAP: Dict[Tuple[int, ...], TokenKind] = {
    # assignment / comparison
    _ordt(":="): TokenKind.ASSIGNMENT,
    _ordt("="):  TokenKind.OP_EQUATE,
    _ordt("=="): TokenKind.OP_EQ,
    _ordt("!="): TokenKind.OP_NE,
    _ordt("<"):  TokenKind.OP_LT,
    _ordt("<="): TokenKind.OP_LE,
    _ordt(">"):  TokenKind.OP_GT,
    _ordt(">="): TokenKind.OP_GE,

    # arithmetic
    _ordt("+"): TokenKind.OP_PLUS,
    _ordt("-"): TokenKind.OP_MINUS,
    _ordt("*"): TokenKind.OP_MUL,
    _ordt("/"): TokenKind.OP_DIV,
    _ordt("%"): TokenKind.OP_MOD,

    # compound assigns
    _ordt("+="): TokenKind.OP_PLUSEQUAL,
    _ordt("-="): TokenKind.OP_MINUSEQUAL,
    _ordt("*="): TokenKind.OP_MULEQUAL,
    _ordt("/="): TokenKind.OP_DIVEQUAL,

    # shifts
    _ordt("<<"):  TokenKind.OP_SHL,
    _ordt(">>"):  TokenKind.OP_SHR,
    _ordt("<<="): TokenKind.OP_SHL_EQUAL,
    _ordt(">>="): TokenKind.OP_SHR_EQUAL,

    # logical / bitwise
    _ordt("&&"): TokenKind.OP_AND,
    _ordt("||"): TokenKind.OP_OR,
    _ordt("&"):  TokenKind.OP_BAND,
    _ordt("|"):  TokenKind.OP_BOR,
    _ordt("^"):  TokenKind.OP_BXOR,
    _ordt("!"):  TokenKind.OP_NOT,
    _ordt("~"):  TokenKind.OP_TILDE,

    # arrows (ASCII)
    _ordt("->"): TokenKind.KW_RIGHTARROW,
    _ordt("<-"): TokenKind.KW_LEFTARROW,

    # punctuation / encapsulators
    _ordt("["): TokenKind.LBRACKET,
    _ordt("]"): TokenKind.RBRACKET,
    _ordt("("): TokenKind.LPAREN,
    _ordt(")"): TokenKind.RPAREN,
    _ordt("{"): TokenKind.LBRACE,
    _ordt("}"): TokenKind.RBRACE,
    _ordt(":"): TokenKind.COLON,
    _ordt(";"): TokenKind.SEMICOLON,
    _ordt(","): TokenKind.COMMA,
    _ordt("\\"):TokenKind.BACKSLASH,
    _ordt("."): TokenKind.DOT,
    _ordt("_"): TokenKind.UNDERSCORE,
    _ordt("#"): TokenKind.HASHTAG,
    _ordt("\""):TokenKind.STRING_DELIM,

    # NEWLINE (only) — indentation handled separately
    _ordt("\n"):TokenKind.NEWLINE,

    # Unicode arithmetic
    _ordt("×"): TokenKind.OP_MUL,
    _ordt("·"): TokenKind.OP_MUL,
    _ordt("⋅"): TokenKind.OP_MUL,
    _ordt("÷"): TokenKind.OP_DIV,
    _ordt("−"): TokenKind.OP_MINUS,  # U+2212

    # Unicode comparison / logic
    _ordt("≤"): TokenKind.OP_LE,
    _ordt("≥"): TokenKind.OP_GE,
    _ordt("≠"): TokenKind.OP_NE,
    _ordt("≡"): TokenKind.KW_EQUIV,
    _ordt("∧"): TokenKind.OP_AND,
    _ordt("∨"): TokenKind.OP_OR,
    _ordt("¬"): TokenKind.OP_NOT,

    # Unicode arrows
    _ordt("→"): TokenKind.KW_RIGHTARROW,
    _ordt("⇒"): TokenKind.KW_RIGHTARROW,
    _ordt("↦"): TokenKind.KW_RIGHTARROW,
    _ordt("←"): TokenKind.KW_LEFTARROW,
    _ordt("⇐"): TokenKind.KW_LEFTARROW,

    # calculus / operators
    _ordt("∂"): TokenKind.KW_PARTIAL,
    _ordt("∇"): TokenKind.KW_PDV,
    _ordt("∑"): TokenKind.KW_SUM,
    _ordt("∏"): TokenKind.KW_PROD,
    _ordt("∫"): TokenKind.KW_INT,
    _ordt("√"): TokenKind.KW_SQRT,
    _ordt("∞"): TokenKind.KW_INFTY,

    # primes
    _ordt("'"):  TokenKind.OP_PRIME,
    _ordt("′"):  TokenKind.OP_PRIME,
    _ordt("″"):  TokenKind.OP_PRIME,
    _ordt("‴"):  TokenKind.OP_PRIME,

    # single-letter Greek GLYPHS
    _ordt("Γ"): TokenKind.KW_GREEK, _ordt("γ"): TokenKind.KW_GREEK, _ordt("Δ"): TokenKind.KW_GREEK,
    _ordt("δ"): TokenKind.KW_GREEK, _ordt("Λ"): TokenKind.KW_GREEK, _ordt("λ"): TokenKind.KW_GREEK,
    _ordt("Π"): TokenKind.KW_GREEK, _ordt("π"): TokenKind.KW_GREEK, _ordt("Σ"): TokenKind.KW_GREEK,
    _ordt("σ"): TokenKind.KW_GREEK, _ordt("ς"): TokenKind.KW_GREEK, _ordt("ϕ"): TokenKind.KW_GREEK,
    _ordt("Φ"): TokenKind.KW_GREEK, _ordt("φ"): TokenKind.KW_GREEK, _ordt("Ψ"): TokenKind.KW_GREEK,
    _ordt("ψ"): TokenKind.KW_GREEK, _ordt("Ω"): TokenKind.KW_GREEK, _ordt("ω"): TokenKind.KW_GREEK,
    _ordt("Θ"): TokenKind.KW_GREEK, _ordt("θ"): TokenKind.KW_GREEK, _ordt("ϑ"): TokenKind.KW_GREEK,
    _ordt("Ξ"): TokenKind.KW_GREEK, _ordt("ξ"): TokenKind.KW_GREEK, _ordt("Υ"): TokenKind.KW_GREEK,
    _ordt("υ"): TokenKind.KW_GREEK, _ordt("Ρ"): TokenKind.KW_GREEK, _ordt("ρ"): TokenKind.KW_GREEK,
    _ordt("ϱ"): TokenKind.KW_GREEK, _ordt("Χ"): TokenKind.KW_GREEK, _ordt("χ"): TokenKind.KW_GREEK,
    _ordt("Τ"): TokenKind.KW_GREEK, _ordt("τ"): TokenKind.KW_GREEK, _ordt("Η"): TokenKind.KW_GREEK,
    _ordt("η"): TokenKind.KW_GREEK, _ordt("Ζ"): TokenKind.KW_GREEK, _ordt("ζ"): TokenKind.KW_GREEK,
    _ordt("Ε"): TokenKind.KW_GREEK, _ordt("ε"): TokenKind.KW_GREEK, _ordt("ϵ"): TokenKind.KW_GREEK,
    _ordt("Ι"): TokenKind.KW_GREEK, _ordt("ι"): TokenKind.KW_GREEK, _ordt("Κ"): TokenKind.KW_GREEK,
    _ordt("κ"): TokenKind.KW_GREEK, _ordt("Ν"): TokenKind.KW_GREEK, _ordt("ν"): TokenKind.KW_GREEK,
    _ordt("Μ"): TokenKind.KW_GREEK, _ordt("μ"): TokenKind.KW_GREEK, _ordt("Β"): TokenKind.KW_GREEK,
    _ordt("β"): TokenKind.KW_GREEK, _ordt("Α"): TokenKind.KW_GREEK, _ordt("α"): TokenKind.KW_GREEK,
    _ordt("Ο"): TokenKind.KW_GREEK, _ordt("ο"): TokenKind.KW_GREEK,
}

# Useful sets
SET_OF_LOWER_LETTERS = {ord(c) for c in "abcdefghijklmnopqrstuvwxyz"}
SET_OF_UPPER_LETTERS = {ord(c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
SET_OF_DIGITS = {ord(c) for c in "0123456789"}

# Extended character sets for tokenization
LETTERS = SET_OF_LOWER_LETTERS | SET_OF_UPPER_LETTERS
IDENTIFIERS = LETTERS | SET_OF_DIGITS | {ord('_')}
NUMERIC_CHARACTERS = SET_OF_DIGITS | {ord('.'), ord('e'), ord('E')}
WHITESPACE_CHARS = {ord(' '), ord('\t')}
NEWLINE = ord('\n')
HASHTAG = ord('#')
BACKSLASH = ord('\\')
STRING_DELIM = ord('"')

# Bracket sets
BRACKETS = {ord('['), ord(']')}
PARENTHESES = {ord('('), ord(')')}
BRACES = {ord('{'), ord('}')}
ENCAPSULATORS = BRACKETS | PARENTHESES | BRACES

# Utility functions for character classification
def unicode_to_string(lexeme_unicode: List[int]) -> str:
    """Convert a list of Unicode code points to a string."""
    return ''.join([chr(cp) for cp in lexeme_unicode])

def is_letter_or_underscore(cp: Optional[int]) -> bool:
    """Check if a code point is a letter or underscore."""
    return not is_end_of_iteration(cp) and (cp in LETTERS or cp == ord('_'))

def is_digit_or_dot(cp: Optional[int]) -> bool:
    """Check if a code point is a digit or dot."""
    return not is_end_of_iteration(cp) and (cp in SET_OF_DIGITS or cp == ord('.'))

def is_wordlike(cp: Optional[int]) -> bool:
    """Check if a code point can be part of an identifier."""
    return not is_end_of_iteration(cp) and cp in IDENTIFIERS

# ───────────────────────── Token Building Functions ─────────────────────────

def build_token_from_digit(iterable):
    """Build a numeric token (INTEGER or FLOAT) from the current position."""
    from tensym.interpreter.token._token import Token
    from tensym.interpreter.token._kind import TokenKind
    
    unicodes = [iterable.current]
    
    # Consume all numeric characters
    while True:
        next_char = iterable.peek(1)
        if next_char is None or next_char not in NUMERIC_CHARACTERS:
            break
        iterable.advance()
        unicodes.append(iterable.current)
        
        # Special handling for signs after 'e' or 'E'
        if chr(iterable.current).lower() == 'e':
            sign_char = iterable.peek(1)
            if sign_char in {ord('+'), ord('-')}:
                iterable.advance()
                unicodes.append(iterable.current)
    
    # Analyze the token to determine type and validate
    num_of_dots = unicodes.count(ord('.'))
    num_of_es = unicodes.count(ord('e')) + unicodes.count(ord('E'))
    
    # Check for invalid formats
    if num_of_dots > 1:
        raise SyntaxError(f"Invalid number format: {unicode_to_string(unicodes)}")
    if num_of_es > 1:
        raise SyntaxError(f"Invalid number format: {unicode_to_string(unicodes)}")
    
    # Simple integer
    if num_of_es == 0 and num_of_dots == 0:
        return Token(
            kind=TokenKind.INTEGER,
            lexeme_unicode=unicodes,
            end_index=iterable.index,
        )
    
    # Validate scientific notation
    if num_of_es == 1:
        # Find the 'e' position
        number_str = unicode_to_string(unicodes)
        e_pos = number_str.lower().find('e')
        
        # Check if there are digits after 'e' (and optional sign)
        after_e = number_str[e_pos + 1:]
        if not after_e:
            raise SyntaxError(f"Invalid number format: {unicode_to_string(unicodes)}")
        
        # If starts with sign, check there are digits after
        if after_e[0] in '+-':
            if len(after_e) == 1 or not after_e[1:].isdigit():
                raise SyntaxError(f"Invalid number format: {unicode_to_string(unicodes)}")
        elif not after_e.isdigit():
            raise SyntaxError(f"Invalid number format: {unicode_to_string(unicodes)}")
    
    # Valid float (with or without scientific notation)
    if num_of_es <= 1 and num_of_dots <= 1:
        return Token(
            kind=TokenKind.FLOAT,
            lexeme_unicode=unicodes,
            end_index=iterable.index,
        )
    
    # Invalid number format
    raise SyntaxError(f"Invalid number format: {unicode_to_string(unicodes)}")

def build_token_from_word(iterable):
    """Build an identifier or keyword token from the current position."""
    from tensym.interpreter.token._token import Token
    from tensym.interpreter.token._kind import TokenKind
    
    unicodes = []
    
    # Collect all word-like characters, but stop at underscore if followed by {
    while not is_end_of_iteration(iterable.current) and is_wordlike(iterable.current):
        # Special case: stop at underscore if followed by { (tensor notation)
        if (iterable.current == ord('_') and 
            iterable.peek(1) == ord('{')):
            break
        unicodes.append(iterable.current)
        iterable.advance()
    
    # Check if it's a keyword
    word_tuple = tuple(unicodes)
    keyword_kind = WORD_TOKEN_MAP.get(word_tuple)
    if keyword_kind is not None:
        return Token(
            kind=keyword_kind,
            lexeme_unicode=unicodes,
            end_index=iterable.index,
        )
    
    # Determine identifier type based on context
    # Check if followed by parentheses (function call)
    if iterable.current == ord('('):
        return Token(
            kind=TokenKind.FUNC_ID,
            lexeme_unicode=unicodes,
            end_index=iterable.index,
        )
    
    # Check if followed by tensor notation (_ or ^ with {)
    if iterable.current in [ord('_'), ord('^')] and iterable.peek(1) == ord('{'):
        # If unicodes is empty, this means we're at a standalone _ or ^ 
        # that should be treated as a separate token, not as a TENSOR_ID
        if not unicodes:
            return None  # Let the caller handle this as a separate token
        return Token(
            kind=TokenKind.TENSOR_ID,
            lexeme_unicode=unicodes,
            end_index=iterable.index,
        )
    
    # Special case: standalone underscore should be treated as operator
    if len(unicodes) == 1 and unicodes[0] == ord('_'):
        # Rewind the iterator to before the underscore so the caller can process it
        iterable._index -= 1
        return None  # Let the caller handle this as an operator
    
    # Regular identifier
    return Token(
        kind=TokenKind.ID,
        lexeme_unicode=unicodes,
        end_index=iterable.index,
    )

def build_encapsulation_token(iterable):
    """Build a bracket, parenthesis, or brace token."""
    from tensym.interpreter.token._token import Token
    from tensym.interpreter.token._kind import TokenKind
    from tensym.interpreter.diagnostics import raise_invalid_syntax
    
    char = iterable.current
    
    # Map characters to token kinds
    char_to_kind = {
        ord('['): TokenKind.LBRACKET,
        ord(']'): TokenKind.RBRACKET,
        ord('('): TokenKind.LPAREN,
        ord(')'): TokenKind.RPAREN,
        ord('{'): TokenKind.LBRACE,
        ord('}'): TokenKind.RBRACE,
    }
    
    kind = char_to_kind.get(char)
    if kind is None:
        raise_invalid_syntax(iterable)
    
    return Token(
        kind=kind,
        lexeme_unicode=[char],
        end_index=iterable.index,
    )

def build_token_from_latex(iterable):
    """Build a LaTeX-style token starting with backslash."""
    from tensym.interpreter.token._token import Token
    from tensym.interpreter.token._kind import TokenKind
    
    assert iterable.current == BACKSLASH, "Character must be '\\\\' to build latex token."
    
    unicodes = [iterable.current]  # Include the backslash
    iterable.advance()
    
    # Collect letters after the backslash
    while not is_end_of_iteration(iterable.current) and iterable.current in LETTERS:
        unicodes.append(iterable.current)
        iterable.advance()
    
    return Token(
        kind=TokenKind.LATEX_ID,
        lexeme_unicode=unicodes,
        end_index=iterable.index,
    )

def build_string_token(iterable):
    """Build a string token."""
    from tensym.interpreter.token._token import Token
    from tensym.interpreter.token._kind import TokenKind
    from tensym.interpreter.iterator import IterBoundary
    
    assert iterable.current == STRING_DELIM, 'Character must be \'"\' to build string token.'
    
    unicodes = [iterable.current]  # Include opening quote
    iterable.advance()
    
    # Collect characters until closing quote or end of input
    while (not is_end_of_iteration(iterable.current) and 
           iterable.current != STRING_DELIM):
        if iterable.current == NEWLINE:
            raise SyntaxError("Unterminated string literal")
        unicodes.append(iterable.current)
        iterable.advance()
    
    # Check if we found the closing quote
    if iterable.current == STRING_DELIM:
        unicodes.append(iterable.current)
        # Don't advance here - let the caller handle it
    else:
        # We reached EOI or None without finding closing quote
        raise SyntaxError("Unterminated string literal")
    
    return Token(
        kind=TokenKind.STRING,
        lexeme_unicode=unicodes,
        end_index=iterable.index,
    )

# ──────────────────────────── prefix stuff ──────────────────────────

def _build_prefix_set(op_map: Dict[Tuple[int, ...], TokenKind]) -> set[Tuple[int, ...]]:
    prefixes: set[Tuple[int, ...]] = set()
    for key in op_map.keys():
        for k in range(1, len(key) + 1):
            prefixes.add(key[:k])
    return prefixes

OP_PREFIX_SET: set[Tuple[int, ...]] = _build_prefix_set(OP_TOKEN_MAP)
OP_HEAD_SET: set[int] = {key[0] for key in OP_TOKEN_MAP}
OP_MAX_TOKEN_LEN: int = max((len(k) for k in OP_TOKEN_MAP), default=0)

def advance_n(iterator: Iterator[int], n: int) -> None:
    for _ in range(max(0, n)):
        iterator.advance()

# ───────────────────────── longest-match (advancing) ────────────────

def longest_token_match_and_consume(
    iterator: Iterator[int],
    *,
    token_map: Dict[Tuple[int, ...], TokenKind] = None,
    prefix_set: set[Tuple[int, ...]] = None,
    head_set: set[int] = None,
    max_len: int = OP_MAX_TOKEN_LEN,
    prime_if_needed: bool = True,
    advance_to: str = "after",  # "after" or "last"
) -> Optional[TokenKind]:
    """
    Prefix-aware, bounded longest-match that *consumes* exactly the matched length.
    Sentinel-safe for Iterator.current (SOI/EOI). Returns TokenKind or None.
    """
    if token_map is None:
        token_map = OP_TOKEN_MAP
    if prefix_set is None:
        prefix_set = OP_PREFIX_SET
    if head_set is None:
        head_set = OP_HEAD_SET
    assert max_len >= OP_MAX_TOKEN_LEN

    head = _cur_int(iterator)
    if head is None and prime_if_needed:
        iterator.advance()
        head = _cur_int(iterator)

    if head is None or head not in head_set:
        return None

    cand: List[int] = []
    best_kind: Optional[TokenKind] = None
    best_len = 0

    for offset in range(max_len):
        cp = head if offset == 0 else _peek_int(iterator, offset)
        if cp is None:
            break
        cand.append(cp)
        t = tuple(cand)

        k = token_map.get(t)
        if k is not None:
            best_kind = k
            best_len = len(t)

        if t in prefix_set:
            continue
        break

    if best_kind is None:
        return None

    # consume exactly matched length
    if advance_to == "after":
        advance_n(iterator, best_len)
    else:
        advance_n(iterator, best_len - 1)

    return best_kind


# ───────────────────── Indentation + Paren-depth engine ─────────────

TAB_WIDTH = 4
ENFORCE_MULTIPLE = 4  # None to disable “multiple of N” enforcement

@dataclass
class Indenter:
    tab_width: int = TAB_WIDTH
    enforce_multiple: Optional[int] = ENFORCE_MULTIPLE
    stack: List[int] = field(default_factory=lambda: [0])  # indentation levels
    paren_depth: int = 0                                   # (), [], {}

    def _expand_tab(self, col: int) -> int:
        w = self.tab_width - (col % self.tab_width)
        return col + w

    def update_paren_depth(self, tok: TokenKind) -> None:
        if tok in (TokenKind.LPAREN, TokenKind.LBRACKET, TokenKind.LBRACE):
            self.paren_depth += 1
        elif tok in (TokenKind.RPAREN, TokenKind.RBRACKET, TokenKind.RBRACE):
            if self.paren_depth > 0:
                self.paren_depth -= 1

    def _measure_indent_after_newline(self, iterator: Iterator[int]) -> tuple[int, int, Optional[int]]:
        """
        Measure visual indent width from current position (assumed just after '\n').
        Returns (width, consumed_chars, first_non_ws_codepoint_or_None).
        """
        width = 0
        consumed = 0

        while True:
            cp = _cur_int(iterator) if consumed == 0 else _peek_int(iterator, consumed)
            if cp is None:
                return width, consumed, None
            if cp == ord(' '):
                width += 1
                consumed += 1
                continue
            if cp == ord('\t'):
                width = self._expand_tab(width)
                consumed += 1
                continue
            break

        next_cp = _cur_int(iterator) if consumed == 0 else _peek_int(iterator, consumed)
        return width, consumed, next_cp

    def _compute_indent_tokens(self, new_width: int) -> List[TokenKind]:
        toks: List[TokenKind] = []
        cur = self.stack[-1]
        if new_width == cur:
            return toks

        if new_width > cur:
            if self.enforce_multiple is not None and (new_width % self.enforce_multiple) != 0:
                raise ValueError(f"Indent {new_width} is not a multiple of {self.enforce_multiple}")
            self.stack.append(new_width)
            toks.append(TokenKind.INDENT)
            return toks

        # dedent(s)
        while len(self.stack) > 1 and self.stack[-1] > new_width:
            self.stack.pop()
            toks.append(TokenKind.DEDENT)

        if self.stack[-1] != new_width:
            raise ValueError(f"Inconsistent dedent to column {new_width}; stack={self.stack}")
        return toks

    def flush_eof(self) -> List[TokenKind]:
        toks: List[TokenKind] = []
        while len(self.stack) > 1:
            self.stack.pop()
            toks.append(TokenKind.DEDENT)
        return toks


def scan_newline_and_indent(
    iterator: Iterator[int],
    indenter: Indenter,
    *,
    treat_hash_as_comment: bool = True,
    consume_ws_on_blank: bool = True,
    emit_newline_inside_parens: bool = False,
) -> List[TokenKind]:
    """
    Assumes iterator.current == ord('\n') BEFORE calling.
    Inside parens: consume newline + following ws, emit [] (or [NEWLINE] if emit_newline_inside_parens=True).
    Outside parens: emit [NEWLINE] + optional [INDENT]/[DEDENT...], consume leading ws of the next line.
    """
    # consume '\n'
    iterator.advance()

    # inside implicit line-join context → ignore indentation
    if indenter.paren_depth > 0:
        while True:
            cp = _cur_int(iterator)
            if cp is None:
                break
            if cp in (ord(' '), ord('\t')):
                iterator.advance()
                continue
            break
        return [TokenKind.NEWLINE] if emit_newline_inside_parens else []

    # outside parens → measure indent
    width, consumed, next_cp = indenter._measure_indent_after_newline(iterator)
    is_blank = (next_cp is None) or (next_cp == ord('\n'))
    is_comment_only = (treat_hash_as_comment and next_cp == ord('#'))

    out: List[TokenKind] = [TokenKind.NEWLINE]

    # Only compute indent/dedent tokens for non-blank, non-comment-only lines
    # Blank lines and comment-only lines should not affect indentation
    if is_blank or is_comment_only:
        if consume_ws_on_blank:
            advance_n(iterator, consumed)
        return out

    # For actual content lines, compute and emit indent/dedent tokens
    toks = indenter._compute_indent_tokens(width)
    advance_n(iterator, consumed)
    out.extend(toks)
    return out


# ────────────────────────────── tests ────────────────────────────────

if __name__ == "__main__":
    # minimalist scanner for ops + indent, to validate the machinery
    def _is_wordlike(cp: Optional[int]) -> bool:
        return (
            not is_end_of_iteration(cp) and (
                cp in SET_OF_LOWER_LETTERS
                or cp in SET_OF_UPPER_LETTERS
                or cp in SET_OF_DIGITS
                or cp == ord('_')
                or cp == ord('\\')  # treat \Gamma etc. as wordlike for this harness
            )
        )

    def scan(src: str, *, tabw=4, enforce_mult=4, emit_nl_in_parens=False) -> List[TokenKind]:
        from tensym.interpreter.iterator import Iterator
        it = Iterator(list(map(ord, src)))  # sentinel-based
        ind = Indenter(tab_width=tabw, enforce_multiple=enforce_mult)
        out: List[TokenKind] = []

        # prime to first element
        it.advance()

        while True:
            cp = _cur_int(it)
            if cp is None:
                break

            # comments: skip to EOL (do not consume the newline)
            if cp == ord('#'):
                while True:
                    it.advance()
                    c2 = _cur_int(it)
                    if c2 is None or c2 == ord('\n'):
                        break
                continue

            # newline → let the indenter handle it
            if cp == ord('\n'):
                out.extend(scan_newline_and_indent(
                    it, ind,
                    treat_hash_as_comment=True,
                    consume_ws_on_blank=True,
                    emit_newline_inside_parens=emit_nl_in_parens
                ))
                continue

            # operators / glyphs
            kind = longest_token_match_and_consume(it)
            if kind is not None:
                # maintain paren depth
                ind.update_paren_depth(kind)
                if kind != TokenKind.NEWLINE:
                    out.append(kind)
                continue

            # identifiers / numbers: skip run
            if _is_wordlike(cp):
                it.advance()
                while _is_wordlike(_cur_int(it)):
                    it.advance()
                continue

            # stray spaces/tabs mid-line: skip
            if cp in (ord(' '), ord('\t')):
                it.advance()
                continue

            # fallback: consume one
            it.advance()

        out.extend(ind.flush_eof())
        return out

    def names(seq: List[TokenKind]) -> List[str]:
        return [t.name for t in seq]

    # A) Simple block
    srcA = "with X:\n    a\n    b\nc\n"
    gotA = names(scan(srcA))
    expA = [TokenKind.COLON, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.NEWLINE, TokenKind.NEWLINE, TokenKind.DEDENT, TokenKind.NEWLINE]
    assert gotA == expA, f"A mismatch: {gotA}"

    # B) Nested block with multi-dedent
    srcB = "with X:\n    a\n        x\n    b\nc\n"
    gotB = names(scan(srcB))
    print(gotB)
    expB = [TokenKind.COLON, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.NEWLINE, TokenKind.DEDENT, TokenKind.NEWLINE, TokenKind.DEDENT, TokenKind.NEWLINE]
    assert gotB == expB, f"B mismatch: {gotB}"

    # C) Implicit line joining in parens
    srcC = "f(\n    x,\n    y\n)\nnext\n"
    gotC = names(scan(srcC))
    expC = [TokenKind.LPAREN, TokenKind.RPAREN, TokenKind.NEWLINE, TokenKind.NEWLINE]
    assert gotC == expC, f"C mismatch: {gotC}"

    # D) Blank + comment-only lines don't change indentation
    srcD = "with X:\n    # comment\n\n    a\n"
    gotD = names(scan(srcD))
    expD = [TokenKind.COLON, TokenKind.NEWLINE, TokenKind.NEWLINE, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.NEWLINE, TokenKind.DEDENT]
    assert gotD == expD, f"D mismatch: {gotD}"

    # E) Tabs vs spaces: tabwidth=4; '\t' and 4 spaces both mean width 4
    srcE = "X:\n\tline1\n    line2\n"
    gotE = names(scan(srcE, tabw=4))
    expE = [TokenKind.COLON, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.NEWLINE, TokenKind.NEWLINE, TokenKind.DEDENT]
    assert gotE == expE, f"E mismatch: {gotE}"

    # F) Enforce multiple-of-4: bad indent (2 spaces) should error
    try:
        _ = scan("hdr:\n  oops\n", enforce_mult=4)
        raise AssertionError("Expected ValueError for non-multiple indent, but none raised")
    except ValueError as ex:
        assert "multiple of 4" in str(ex)

    # G) Operator longest match: >>=
    srcG = "a >>=\n"
    gotG = [t for t in scan(srcG) if t in (TokenKind.OP_SHR_EQUAL, TokenKind.NEWLINE)]
    assert names(gotG) == [TokenKind.OP_SHR_EQUAL, TokenKind.NEWLINE], f"G mismatch: {names(gotG)}"

    # H) Unicode operators and arrows
    srcH = "a ≤ b → c\n"
    gotH = [t for t in scan(srcH) if t in (TokenKind.OP_LE, TokenKind.KW_RIGHTARROW, TokenKind.NEWLINE)]
    assert names(gotH) == [TokenKind.OP_LE, TokenKind.KW_RIGHTARROW, TokenKind.NEWLINE], f"H mismatch: {names(gotH)}"

    # I) Mixed [], {} implicit join
    srcI = "with T:\n    A = [\n        1,\n        2\n    ]\n    B\nC\n"
    keep = {TokenKind.COLON, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.DEDENT, TokenKind.LBRACKET, TokenKind.RBRACKET}
    gotI = [t for t in scan(srcI) if t in keep]
    expI = [TokenKind.COLON, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.LBRACKET, TokenKind.RBRACKET, TokenKind.NEWLINE, TokenKind.NEWLINE, TokenKind.DEDENT, TokenKind.NEWLINE]
    assert names(gotI) == expI, f"I mismatch: {names(gotI)}"

    print("All sentinel-safe INDENT/DEDENT + operator longest-match tests passed ✅")

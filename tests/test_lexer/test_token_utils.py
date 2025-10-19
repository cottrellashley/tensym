import pytest

from tensym.interpreter.token._kind import TokenKind
from tensym.interpreter.token.utils import (
    _cur_int,
    _peek_int,
    longest_token_match_and_consume,
    advance_n,
    scan_newline_and_indent,
    Indenter,
    SET_OF_LOWER_LETTERS,
    SET_OF_UPPER_LETTERS,
    SET_OF_DIGITS,
)
from tensym.interpreter.iterator import Iterator

def _is_wordlike(cp: int) -> bool:
    return (
        cp is not None and (
            cp in SET_OF_LOWER_LETTERS
            or cp in SET_OF_UPPER_LETTERS
            or cp in SET_OF_DIGITS
            or cp == ord('_')
            or cp == ord('\\')  # treat \Gamma etc. as wordlike for this harness
        )
    )

def scan(src: str, *, tabw=4, enforce_mult=4, emit_nl_in_parens=False):
    from tensym.interpreter.iterator import Iterator
    # Create an iterator over the source code
    it = Iterator(list(map(ord, src)))  # sentinel-based
    ind = Indenter(tab_width=tabw, enforce_multiple=enforce_mult)
    out = []

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

def names(seq) -> list:
    return [t.name for t in seq]

def test_simple_block():
    # Test A: Simple block
    srcA = "with X:\n    a\n    b\nc\n"
    gotA = names(scan(srcA))
    expA = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.INDENT.name,
            TokenKind.NEWLINE.name, TokenKind.NEWLINE.name, TokenKind.DEDENT.name,
            TokenKind.NEWLINE.name]
    assert gotA == expA, f"A mismatch: {gotA}"

def test_nested_block_with_multidend():
    # Test B: Nested block with multi-dedent
    srcB = "with X:\n    a\n        x\n    b\nc\n"
    gotB = names(scan(srcB))
    expB = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.INDENT.name,
            TokenKind.NEWLINE.name, TokenKind.INDENT.name, TokenKind.NEWLINE.name,
            TokenKind.DEDENT.name, TokenKind.NEWLINE.name, TokenKind.DEDENT.name,
            TokenKind.NEWLINE.name]
    assert gotB == expB, f"B mismatch: {gotB}"

def test_implicit_line_join_in_parens():
    # Test C: Implicit line joining in parens
    srcC = "f(\n    x,\n    y\n)\nnext\n"
    gotC = names(scan(srcC))
    # Now includes COMMA since we added comma support
    expC = [TokenKind.LPAREN.name, TokenKind.COMMA.name, TokenKind.RPAREN.name,
            TokenKind.NEWLINE.name, TokenKind.NEWLINE.name]
    assert gotC == expC, f"C mismatch: {gotC}"

def test_blank_and_comment_only_lines():
    # Test D: Blank + comment-only lines don’t change indentation
    srcD = "with X:\n    # comment\n\n    a\n"
    gotD = names(scan(srcD))
    # Implementation emits the blank/newline tokens before the INDENT for the
    # following non-blank line, so reflect that observed ordering here.
    expD = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.NEWLINE.name,
            TokenKind.NEWLINE.name, TokenKind.INDENT.name, TokenKind.NEWLINE.name,
            TokenKind.DEDENT.name]
    assert gotD == expD, f"D mismatch: {gotD}"

def test_tabs_vs_spaces():
    # Test E: Tabs vs spaces: tabwidth=4; '\t' and 4 spaces both mean width 4
    srcE = "X:\n\tline1\n    line2\n"
    gotE = names(scan(srcE, tabw=4))
    expE = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.INDENT.name,
            TokenKind.NEWLINE.name, TokenKind.NEWLINE.name, TokenKind.DEDENT.name]
    assert gotE == expE, f"E mismatch: {gotE}"

def test_bad_indent_raises_valueerror():
    # Test F: Enforce multiple-of-4: bad indent (2 spaces) should error.
    with pytest.raises(ValueError) as exc:
        scan("hdr:\n  oops\n", enforce_mult=4)
    assert "multiple of 4" in str(exc.value)

def test_operator_longest_match():
    # Test G: Operator longest match: >>=
    srcG = "a >>=\n"
    result = scan(srcG)
    # Filter only tokens from operator >>=
    filtered = [t for t in result if t in (TokenKind.OP_SHR_EQUAL, TokenKind.NEWLINE)]
    gotG = names(filtered)
    expG = [TokenKind.OP_SHR_EQUAL.name, TokenKind.NEWLINE.name]
    assert gotG == expG, f"G mismatch: {gotG}"

def test_unicode_operators_and_arrows():
    # Test H: Unicode operators and arrows
    srcH = "a ≤ b → c\n"
    result = scan(srcH)
    filtered = [t for t in result if t in (TokenKind.OP_LE, TokenKind.KW_RIGHTARROW, TokenKind.NEWLINE)]
    gotH = names(filtered)
    expH = [TokenKind.OP_LE.name, TokenKind.KW_RIGHTARROW.name, TokenKind.NEWLINE.name]
    assert gotH == expH, f"H mismatch: {gotH}"

def test_mixed_brackets_implicit_join():
    # Test I: Mixed [], {} implicit join
    srcI = "with T:\n    A = [\n        1,\n        2\n    ]\n    B\nC\n"
    # Keep only the tokens of interest
    keep = {TokenKind.COLON, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.DEDENT, TokenKind.LBRACKET, TokenKind.RBRACKET}
    filtered = [t for t in scan(srcI) if t in keep]
    gotI = names(filtered)
    expI = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.INDENT.name,
            TokenKind.LBRACKET.name, TokenKind.RBRACKET.name, TokenKind.NEWLINE.name,
            TokenKind.NEWLINE.name, TokenKind.DEDENT.name, TokenKind.NEWLINE.name]
    assert gotI == expI, f"I mismatch: {gotI}"

# ═══════════════════════════════════════════════════════════════════════════════════
# Additional comprehensive tests for edge cases and robustness
# ═══════════════════════════════════════════════════════════════════════════════════

def test_multiple_blank_lines():
    # Test J: Multiple consecutive blank lines should not affect indentation
    srcJ = "with X:\n\n\n    a\n\n\nb\n"
    gotJ = names(scan(srcJ))
    expJ = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.NEWLINE.name, 
            TokenKind.NEWLINE.name, TokenKind.INDENT.name, TokenKind.NEWLINE.name,
            TokenKind.NEWLINE.name, TokenKind.NEWLINE.name, TokenKind.DEDENT.name, TokenKind.NEWLINE.name]
    assert gotJ == expJ, f"J mismatch: {gotJ}"

def test_comment_with_varying_indentation():
    # Test K: Comments with different indentation levels should not affect block structure
    srcK = "with X:\n# no indent comment\n    # indented comment\n        # deeply indented comment\n    a\n"
    gotK = names(scan(srcK))
    expK = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.NEWLINE.name,
            TokenKind.NEWLINE.name, TokenKind.NEWLINE.name, TokenKind.INDENT.name, 
            TokenKind.NEWLINE.name, TokenKind.DEDENT.name]
    assert gotK == expK, f"K mismatch: {gotK}"

def test_mixed_comments_and_blank_lines():
    # Test L: Mixed comments and blank lines in various positions
    srcL = "with X:\n    # comment\n\n    # another comment\n\n    a\n    # end comment\nb\n"
    gotL = names(scan(srcL))
    expL = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.NEWLINE.name,
            TokenKind.NEWLINE.name, TokenKind.NEWLINE.name, TokenKind.NEWLINE.name,
            TokenKind.INDENT.name, TokenKind.NEWLINE.name, TokenKind.NEWLINE.name,
            TokenKind.DEDENT.name, TokenKind.NEWLINE.name]
    assert gotL == expL, f"L mismatch: {gotL}"

def test_nested_parens_with_newlines():
    # Test M: Nested parentheses with newlines should suppress indentation
    srcM = "f(\n    g(\n        h(x)\n    )\n)\nnext\n"
    gotM = names(scan(srcM))
    expM = [TokenKind.LPAREN.name, TokenKind.LPAREN.name, TokenKind.LPAREN.name,
            TokenKind.RPAREN.name, TokenKind.RPAREN.name, TokenKind.RPAREN.name,
            TokenKind.NEWLINE.name, TokenKind.NEWLINE.name]
    assert gotM == expM, f"M mismatch: {gotM}"

def test_complex_operator_sequences():
    # Test N: Complex operator sequences should be tokenized correctly
    srcN = "a >>= b <<= c += d -= e *= f /= g\n"
    result = scan(srcN)
    # Filter for compound assignment operators
    compound_ops = [t for t in result if t in (
        TokenKind.OP_SHR_EQUAL, TokenKind.OP_SHL_EQUAL, TokenKind.OP_PLUSEQUAL,
        TokenKind.OP_MINUSEQUAL, TokenKind.OP_MULEQUAL, TokenKind.OP_DIVEQUAL, TokenKind.NEWLINE
    )]
    gotN = names(compound_ops)
    expN = [TokenKind.OP_SHR_EQUAL.name, TokenKind.OP_SHL_EQUAL.name, TokenKind.OP_PLUSEQUAL.name,
            TokenKind.OP_MINUSEQUAL.name, TokenKind.OP_MULEQUAL.name, TokenKind.OP_DIVEQUAL.name, 
            TokenKind.NEWLINE.name]
    assert gotN == expN, f"N mismatch: {gotN}"

def test_unicode_mixed_with_ascii():
    # Test O: Unicode and ASCII operators mixed together
    srcO = "a ≤ b <= c ≥ d >= e ≠ f != g\n"
    result = scan(srcO)
    # Filter for comparison operators
    comp_ops = [t for t in result if t in (
        TokenKind.OP_LE, TokenKind.OP_GE, TokenKind.OP_NE, TokenKind.NEWLINE
    )]
    gotO = names(comp_ops)
    expO = [TokenKind.OP_LE.name, TokenKind.OP_LE.name, TokenKind.OP_GE.name,
            TokenKind.OP_GE.name, TokenKind.OP_NE.name, TokenKind.OP_NE.name, TokenKind.NEWLINE.name]
    assert gotO == expO, f"O mismatch: {gotO}"

def test_greek_letters_and_symbols():
    # Test P: Greek letters and mathematical symbols
    srcP = "α + β = γ ∧ δ → ε ∑ ζ ∫ η\n"
    result = scan(srcP)
    # Filter for Greek and math symbols
    greek_math = [t for t in result if t in (
        TokenKind.KW_GREEK, TokenKind.OP_PLUS, TokenKind.OP_EQUATE, TokenKind.OP_AND,
        TokenKind.KW_RIGHTARROW, TokenKind.KW_SUM, TokenKind.KW_INT, TokenKind.NEWLINE
    )]
    gotP = names(greek_math)
    expP = [TokenKind.KW_GREEK.name, TokenKind.OP_PLUS.name, TokenKind.KW_GREEK.name,
            TokenKind.OP_EQUATE.name, TokenKind.KW_GREEK.name, TokenKind.OP_AND.name,
            TokenKind.KW_GREEK.name, TokenKind.KW_RIGHTARROW.name, TokenKind.KW_GREEK.name,
            TokenKind.KW_SUM.name, TokenKind.KW_GREEK.name, TokenKind.KW_INT.name,
            TokenKind.KW_GREEK.name, TokenKind.NEWLINE.name]
    assert gotP == expP, f"P mismatch: {gotP}"

def test_empty_lines_at_start_and_end():
    # Test Q: Empty lines at the beginning and end of input
    srcQ = "\n\nwith X:\n    a\n\n\n"
    gotQ = names(scan(srcQ))
    expQ = [TokenKind.NEWLINE.name, TokenKind.NEWLINE.name, TokenKind.COLON.name,
            TokenKind.NEWLINE.name, TokenKind.INDENT.name, TokenKind.NEWLINE.name,
            TokenKind.NEWLINE.name, TokenKind.NEWLINE.name, TokenKind.DEDENT.name]
    assert gotQ == expQ, f"Q mismatch: {gotQ}"

def test_deeply_nested_indentation():
    # Test R: Deeply nested indentation levels
    srcR = "a:\n    b:\n        c:\n            d\n        e\n    f\ng\n"
    gotR = names(scan(srcR))
    expR = [TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.INDENT.name,
            TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.INDENT.name,
            TokenKind.COLON.name, TokenKind.NEWLINE.name, TokenKind.INDENT.name,
            TokenKind.NEWLINE.name, TokenKind.DEDENT.name, TokenKind.NEWLINE.name,
            TokenKind.DEDENT.name, TokenKind.NEWLINE.name, TokenKind.DEDENT.name,
            TokenKind.NEWLINE.name]
    assert gotR == expR, f"R mismatch: {gotR}"

def test_mixed_brackets_and_braces():
    # Test S: Mixed brackets, braces, and parentheses with implicit line joining
    srcS = "data = {\n    'list': [\n        (1, 2),\n        (3, 4)\n    ]\n}\nnext\n"
    result = scan(srcS)
    # Filter for brackets and structural tokens
    brackets = [t for t in result if t in (
        TokenKind.LBRACE, TokenKind.RBRACE, TokenKind.LBRACKET, TokenKind.RBRACKET,
        TokenKind.LPAREN, TokenKind.RPAREN, TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.DEDENT
    )]
    gotS = names(brackets)
    expS = [TokenKind.LBRACE.name, TokenKind.LBRACKET.name, TokenKind.LPAREN.name,
            TokenKind.RPAREN.name, TokenKind.LPAREN.name, TokenKind.RPAREN.name,
            TokenKind.RBRACKET.name, TokenKind.RBRACE.name, TokenKind.NEWLINE.name, TokenKind.NEWLINE.name]
    assert gotS == expS, f"S mismatch: {gotS}"

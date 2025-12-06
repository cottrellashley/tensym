"""Integration tests for lexer and parser interaction."""

import pytest

from tensym.interpreter.token._kind import TokenKind


class TestLexerParserIntegration:
    """Test integration between lexer and parser components."""

    def test_simple_expression_tokenization(self, lexer):
        """Test tokenizing a simple mathematical expression."""
        code = "x + y * 2"
        tokens = list(lexer.tokenize(raw_code=code))

        expected_kinds = [
            TokenKind.ID,  # x
            TokenKind.OP_PLUS,  # +
            TokenKind.ID,  # y
            TokenKind.OP_MUL,  # *
            TokenKind.INTEGER,  # 2
        ]

        assert len(tokens) == len(expected_kinds)
        for token, expected_kind in zip(tokens, expected_kinds):
            assert token.kind == expected_kind

    def test_assignment_statement_tokenization(self, lexer):
        """Test tokenizing an assignment statement."""
        code = "let result = calculate(x, y)"
        tokens = list(lexer.tokenize(raw_code=code))

        expected_kinds = [
            TokenKind.KW_LET,  # let
            TokenKind.ID,  # result
            TokenKind.OP_EQUATE,  # =
            TokenKind.FUNC_ID,  # calculate
            TokenKind.LPAREN,  # (
            TokenKind.ID,  # x
            TokenKind.COMMA,  # ,
            TokenKind.ID,  # y
            TokenKind.RPAREN,  # )
        ]

        assert len(tokens) == len(expected_kinds)
        for token, expected_kind in zip(tokens, expected_kinds):
            assert token.kind == expected_kind

    def test_tensor_notation_tokenization(self, lexer):
        """Test tokenizing tensor notation."""
        code = "T_{ij} = g^{mu nu} * R_{mu nu}"
        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain tensor identifiers
        tensor_tokens = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        assert len(tensor_tokens) >= 2  # T, g, and possibly R

        # Should contain proper punctuation
        brace_tokens = [
            t for t in tokens if t.kind in (TokenKind.LBRACE, TokenKind.RBRACE)
        ]
        assert len(brace_tokens) >= 4  # At least 2 pairs of braces

    def test_function_definition_tokenization(self, lexer):
        """Test tokenizing a function definition."""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)
"""
        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain function definition keywords
        def_tokens = [t for t in tokens if t.kind == TokenKind.KW_DEF]
        assert len(def_tokens) == 1

        # Should contain control flow keywords
        if_tokens = [t for t in tokens if t.kind == TokenKind.KW_IF]
        else_tokens = [t for t in tokens if t.kind == TokenKind.KW_ELSE]
        assert len(if_tokens) == 1
        assert len(else_tokens) == 1

        # Should handle indentation
        indent_tokens = [t for t in tokens if t.kind == TokenKind.INDENT]
        dedent_tokens = [t for t in tokens if t.kind == TokenKind.DEDENT]
        assert len(indent_tokens) >= 1
        assert len(dedent_tokens) >= 1

    def test_unicode_mathematical_expression(self, lexer):
        """Test tokenizing Unicode mathematical expressions."""
        code = "α + β ≤ γ → δ"
        tokens = list(lexer.tokenize(raw_code=code))

        expected_kinds = [
            TokenKind.KW_GREEK,  # α
            TokenKind.OP_PLUS,  # +
            TokenKind.KW_GREEK,  # β
            TokenKind.OP_LE,  # ≤
            TokenKind.KW_GREEK,  # γ
            TokenKind.KW_RIGHTARROW,  # →
            TokenKind.KW_GREEK,  # δ
        ]

        assert len(tokens) == len(expected_kinds)
        for token, expected_kind in zip(tokens, expected_kinds):
            assert token.kind == expected_kind

    def test_complex_nested_expression(self, lexer):
        """Test tokenizing complex nested expressions."""
        code = "result = sqrt(x^2 + y^2) * sin(θ)"
        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain function calls
        func_tokens = [t for t in tokens if t.kind == TokenKind.FUNC_ID]
        assert len(func_tokens) >= 2  # sqrt and sin

        # Should contain Greek letters
        greek_tokens = [t for t in tokens if t.kind == TokenKind.KW_GREEK]
        assert len(greek_tokens) >= 1  # θ

        # Should handle parentheses correctly
        lparen_tokens = [t for t in tokens if t.kind == TokenKind.LPAREN]
        rparen_tokens = [t for t in tokens if t.kind == TokenKind.RPAREN]
        assert len(lparen_tokens) == len(rparen_tokens)

    def test_string_and_comment_handling(self, lexer):
        """Test handling of strings and comments together."""
        code = """
# This is a comment
let message = "Hello, World!"  # Another comment
print(message)
"""
        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain string token
        string_tokens = [t for t in tokens if t.kind == TokenKind.STRING]
        assert len(string_tokens) == 1
        assert string_tokens[0].lexeme == '"Hello, World!"'

        # Comments should be filtered out
        lexemes = [t.lexeme for t in tokens]
        assert "This" not in lexemes
        assert "comment" not in lexemes
        assert "Another" not in lexemes

    def test_error_recovery_invalid_tokens(self, lexer):
        """Test lexer behavior with invalid tokens."""
        code = "let x = @invalid_char"

        with pytest.raises(SyntaxError):
            list(lexer.tokenize(raw_code=code))

    def test_multiline_indented_code(self, lexer, sample_tensym_code):
        """Test tokenizing multiline indented code."""
        tokens = list(lexer.tokenize(raw_code=sample_tensym_code))

        # Should handle indentation properly
        indent_tokens = [t for t in tokens if t.kind == TokenKind.INDENT]
        dedent_tokens = [t for t in tokens if t.kind == TokenKind.DEDENT]

        # Should have matching indents and dedents
        assert len(indent_tokens) == len(dedent_tokens)

        # Should contain various token types
        token_kinds = {t.kind for t in tokens}
        expected_kinds = {
            TokenKind.KW_LET,
            TokenKind.ID,
            TokenKind.OP_EQUATE,
            TokenKind.INTEGER,
            TokenKind.FLOAT,
            TokenKind.TENSOR_ID,
            TokenKind.KW_DEF,
            TokenKind.FUNC_ID,
            TokenKind.KW_GREEK,
        }

        # Should contain most expected token types
        assert len(token_kinds.intersection(expected_kinds)) >= 5

    def test_position_tracking_accuracy(self, lexer):
        """Test that token positions are tracked accurately."""
        code = """line1 = 42
line2 = "hello"
line3 = x + y"""

        tokens = list(lexer.tokenize(raw_code=code))

        # Check that positions increase appropriately
        line_numbers = [t.position.line for t in tokens if t.kind != TokenKind.NEWLINE]

        # Should have tokens on lines 1, 2, and 3
        assert 1 in line_numbers
        assert 2 in line_numbers
        assert 3 in line_numbers

        # Column positions should be reasonable
        for token in tokens:
            assert token.position.column >= 1

"""Integration tests for the complete compilation pipeline."""

import pytest

from tensym.interpreter.token._kind import TokenKind


class TestFullPipeline:
    """Test the complete pipeline from source code to tokens."""

    def test_simple_arithmetic_pipeline(self, lexer):
        """Test complete pipeline for simple arithmetic."""
        code = "let result = 2 + 3 * 4"

        # Tokenize
        tokens = list(lexer.tokenize(raw_code=code))

        # Verify token sequence
        expected_sequence = [
            (TokenKind.KW_LET, "let"),
            (TokenKind.ID, "result"),
            (TokenKind.OP_EQUATE, "="),
            (TokenKind.INTEGER, "2"),
            (TokenKind.OP_PLUS, "+"),
            (TokenKind.INTEGER, "3"),
            (TokenKind.OP_MUL, "*"),
            (TokenKind.INTEGER, "4"),
        ]

        assert len(tokens) == len(expected_sequence)
        for token, (expected_kind, expected_lexeme) in zip(tokens, expected_sequence):
            assert token.kind == expected_kind
            assert token.lexeme == expected_lexeme

    def test_function_definition_pipeline(self, lexer):
        """Test pipeline for function definition."""
        code = """
def add(x, y):
    return x + y
"""

        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain proper structure
        token_kinds = [t.kind for t in tokens]

        # Check for key elements
        assert TokenKind.KW_DEF in token_kinds
        assert TokenKind.FUNC_ID in token_kinds
        assert TokenKind.LPAREN in token_kinds
        assert TokenKind.RPAREN in token_kinds
        assert TokenKind.COLON in token_kinds
        assert TokenKind.INDENT in token_kinds
        assert TokenKind.DEDENT in token_kinds

    def test_tensor_calculation_pipeline(self, lexer):
        """Test pipeline for tensor calculations."""
        code = """
with metric g:
    T^{mu}_{nu} = R^{mu}_{nu} - (1/2) * g^{mu}_{nu} * R
"""

        tokens = list(lexer.tokenize(raw_code=code))

        # Should handle tensor notation
        tensor_ids = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        assert len(tensor_ids) >= 2  # T, R, g

        # Should handle braces
        lbraces = [t for t in tokens if t.kind == TokenKind.LBRACE]
        rbraces = [t for t in tokens if t.kind == TokenKind.RBRACE]
        assert len(lbraces) == len(rbraces)
        assert len(lbraces) >= 3  # Multiple tensor indices

    def test_mathematical_expression_pipeline(self, lexer):
        """Test pipeline for complex mathematical expressions."""
        code = "result = √(α² + β²) ≤ ∑_{i=1}^{n} x_i"

        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain mathematical symbols
        token_kinds = {t.kind for t in tokens}
        expected_math_kinds = {
            TokenKind.KW_SQRT,  # √
            TokenKind.KW_GREEK,  # α, β
            TokenKind.OP_LE,  # ≤
            TokenKind.KW_SUM,  # ∑
        }

        # Should contain most mathematical symbols
        assert len(token_kinds.intersection(expected_math_kinds)) >= 3

    def test_error_handling_pipeline(self, lexer):
        """Test error handling in the pipeline."""
        invalid_codes = [
            "let x = @",  # Invalid character
            'let s = "unterminated string',  # Unterminated string
            "let x = 1.2.3",  # Invalid number
        ]

        for code in invalid_codes:
            with pytest.raises(SyntaxError):
                list(lexer.tokenize(raw_code=code))

    def test_unicode_support_pipeline(self, lexer):
        """Test Unicode support throughout pipeline."""
        code = "∀x ∈ ℝ: f(x) = ∫_{-∞}^{∞} e^{-t²} dt"

        tokens = list(lexer.tokenize(raw_code=code))

        # Should handle various Unicode symbols
        unicode_lexemes = {t.lexeme for t in tokens}
        expected_unicode = {"∀", "∈", "ℝ", "∫", "∞", "²"}

        # Should contain some Unicode symbols
        assert len(unicode_lexemes.intersection(expected_unicode)) >= 3

    def test_complex_nested_structure_pipeline(self, lexer, complex_tensym_code):
        """Test pipeline with complex nested structures."""
        tokens = list(lexer.tokenize(raw_code=complex_tensym_code))

        # Should handle indentation correctly
        indent_count = len([t for t in tokens if t.kind == TokenKind.INDENT])
        dedent_count = len([t for t in tokens if t.kind == TokenKind.DEDENT])
        assert indent_count == dedent_count

        # Should contain various token types
        token_kinds = {t.kind for t in tokens}
        expected_variety = {
            TokenKind.KW_WITH,
            TokenKind.KW_DEF,
            TokenKind.TENSOR_ID,
            TokenKind.KW_GREEK,
            TokenKind.OP_EQUATE,
            TokenKind.FUNC_ID,
        }

        # Should have good token variety
        assert len(token_kinds.intersection(expected_variety)) >= 4

    def test_performance_pipeline(self, lexer):
        """Test pipeline performance with larger input."""
        # Generate a moderately large input
        lines = []
        for i in range(100):
            lines.append(f"let var_{i} = {i} + {i + 1} * {i + 2}")

        code = "\n".join(lines)

        # Should handle without issues
        tokens = list(lexer.tokenize(raw_code=code))

        # Should produce expected number of tokens (roughly)
        # Each line has ~7 tokens, so ~700 total
        assert len(tokens) >= 600  # Allow for some variation
        assert len(tokens) <= 800

    def test_whitespace_and_comment_handling_pipeline(self, lexer):
        """Test whitespace and comment handling in pipeline."""
        code = """
        # Header comment
        
        let x = 42    # Inline comment
        
        # Another comment
        let y = x + 1
        
        """

        tokens = list(lexer.tokenize(raw_code=code))

        # Comments should be filtered out
        lexemes = [t.lexeme for t in tokens]
        comment_words = ["Header", "comment", "Inline", "Another"]
        for word in comment_words:
            assert word not in lexemes

        # Should still have the actual code
        assert any(t.lexeme == "x" for t in tokens)
        assert any(t.lexeme == "42" for t in tokens)
        assert any(t.lexeme == "y" for t in tokens)

    def test_position_information_pipeline(self, lexer):
        """Test that position information is preserved through pipeline."""
        code = """line 1
    line 2 indented
line 3"""

        tokens = list(lexer.tokenize(raw_code=code))

        # Filter out newlines for easier testing
        content_tokens = [
            t
            for t in tokens
            if t.kind not in (TokenKind.NEWLINE, TokenKind.INDENT, TokenKind.DEDENT)
        ]

        # Should have tokens from different lines
        line_numbers = {t.position.line for t in content_tokens}
        assert 1 in line_numbers
        assert 2 in line_numbers
        assert 3 in line_numbers

        # Indented line should have higher column numbers
        line2_tokens = [t for t in content_tokens if t.position.line == 2]
        line1_tokens = [t for t in content_tokens if t.position.line == 1]

        if line2_tokens and line1_tokens:
            # Indented tokens should start at higher column
            assert min(t.position.column for t in line2_tokens) > min(
                t.position.column for t in line1_tokens
            )

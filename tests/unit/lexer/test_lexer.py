import pytest

from tensym.interpreter.lexer._lexer import Lexer, tokenize_string
from tensym.interpreter.token._kind import TokenKind


class TestLexerBasicFunctionality:
    """Test basic lexer functionality."""

    def test_lexer_initialization(self):
        """Test lexer can be initialized."""
        lexer = Lexer()
        assert lexer is not None

        # Test debug mode
        debug_lexer = Lexer(debug=True)
        assert debug_lexer is not None

    def test_empty_input(self):
        """Test lexer handles empty input."""
        lexer = Lexer()
        tokens = lexer.tokenize(raw_code="")
        token_list = list(tokens)
        assert len(token_list) == 0

    def test_whitespace_only(self):
        """Test lexer handles whitespace-only input."""
        lexer = Lexer()
        tokens = lexer.tokenize(raw_code="   \t  \n  ")
        token_list = list(tokens)
        # Should only contain newline tokens
        assert all(token.kind == TokenKind.NEWLINE for token in token_list)


class TestLexerIdentifiers:
    """Test identifier tokenization."""

    def test_simple_identifier(self):
        """Test simple identifier tokenization."""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code="variable"))
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.ID
        assert tokens[0].lexeme == "variable"

    def test_identifier_with_underscore(self):
        """Test identifier with underscore."""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code="var_name"))
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.ID
        assert tokens[0].lexeme == "var_name"

    def test_identifier_with_numbers(self):
        """Test identifier with numbers."""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code="var123"))
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.ID
        assert tokens[0].lexeme == "var123"

    def test_function_identifier(self):
        """Test function identifier (followed by parentheses)."""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code="func("))
        assert len(tokens) == 2
        assert tokens[0].kind == TokenKind.FUNC_ID
        assert tokens[0].lexeme == "func"
        assert tokens[1].kind == TokenKind.LPAREN

    def test_tensor_identifier(self):
        """Test tensor identifier (followed by _ or ^ and {)."""
        lexer = Lexer()

        # Test with underscore
        tokens = list(lexer.tokenize(raw_code="tensor_{"))
        assert len(tokens) == 3
        assert tokens[0].kind == TokenKind.TENSOR_ID
        assert tokens[0].lexeme == "tensor"
        assert tokens[1].kind == TokenKind.UNDERSCORE
        assert tokens[2].kind == TokenKind.LBRACE

        # Test with caret
        tokens = list(lexer.tokenize(raw_code="tensor^{"))
        assert len(tokens) == 3
        assert tokens[0].kind == TokenKind.TENSOR_ID
        assert tokens[0].lexeme == "tensor"
        assert tokens[1].kind == TokenKind.OP_BXOR  # ^ is bitwise XOR operator
        assert tokens[2].kind == TokenKind.LBRACE

    def test_latex_identifier(self):
        """Test LaTeX-style identifier."""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code="\\alpha"))
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.LATEX_ID
        assert tokens[0].lexeme == "\\alpha"


class TestLexerKeywords:
    """Test keyword tokenization."""

    def test_language_keywords(self):
        """Test language keywords."""
        test_cases = [
            ("let", TokenKind.KW_LET),
            ("def", TokenKind.KW_DEF),
            ("with", TokenKind.KW_WITH),
            ("const", TokenKind.KW_CONST),
            ("print", TokenKind.KW_PRINT),
        ]

        lexer = Lexer()
        for keyword, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=keyword))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == keyword

    def test_control_flow_keywords(self):
        """Test control flow keywords."""
        test_cases = [
            ("if", TokenKind.KW_IF),
            ("then", TokenKind.KW_THEN),
            ("else", TokenKind.KW_ELSE),
            ("elif", TokenKind.KW_ELIF),
        ]

        lexer = Lexer()
        for keyword, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=keyword))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == keyword

    def test_logical_keywords(self):
        """Test logical keywords."""
        test_cases = [
            ("not", TokenKind.KW_NOT),
            ("and", TokenKind.KW_AND),
            ("or", TokenKind.KW_OR),
        ]

        lexer = Lexer()
        for keyword, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=keyword))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == keyword

    def test_mathematical_keywords(self):
        """Test mathematical keywords."""
        test_cases = [
            ("pi", TokenKind.KW_PI),
            ("e", TokenKind.KW_E),
            ("infty", TokenKind.KW_INFTY),
            ("oo", TokenKind.KW_INFTY),
            ("sum", TokenKind.KW_SUM),
            ("prod", TokenKind.KW_PROD),
            ("sqrt", TokenKind.KW_SQRT),
        ]

        lexer = Lexer()
        for keyword, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=keyword))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == keyword

    def test_greek_letter_keywords(self):
        """Test Greek letter keywords."""
        test_cases = [
            ("alpha", TokenKind.KW_GREEK),
            ("beta", TokenKind.KW_GREEK),
            ("gamma", TokenKind.KW_GREEK),
            ("delta", TokenKind.KW_GREEK),
            ("Alpha", TokenKind.KW_GREEK),
            ("Beta", TokenKind.KW_GREEK),
        ]

        lexer = Lexer()
        for keyword, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=keyword))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == keyword


class TestLexerNumbers:
    """Test number tokenization."""

    def test_integers(self):
        """Test integer tokenization."""
        test_cases = ["0", "42", "123", "999"]

        lexer = Lexer()
        for number in test_cases:
            tokens = list(lexer.tokenize(raw_code=number))
            assert len(tokens) == 1
            assert tokens[0].kind == TokenKind.INTEGER
            assert tokens[0].lexeme == number

    def test_floats(self):
        """Test float tokenization."""
        test_cases = ["3.14", "0.5", "123.456", "0.0"]

        lexer = Lexer()
        for number in test_cases:
            tokens = list(lexer.tokenize(raw_code=number))
            assert len(tokens) == 1
            assert tokens[0].kind == TokenKind.FLOAT
            assert tokens[0].lexeme == number

    def test_scientific_notation(self):
        """Test scientific notation."""
        test_cases = ["1e10", "2.5e-3", "1E+5", "3.14e0"]

        lexer = Lexer()
        for number in test_cases:
            tokens = list(lexer.tokenize(raw_code=number))
            assert len(tokens) == 1
            assert tokens[0].kind == TokenKind.FLOAT
            assert tokens[0].lexeme == number

    def test_invalid_numbers(self):
        """Test invalid number formats raise errors."""
        invalid_cases = ["1.2.3", "1e", "1e+"]

        lexer = Lexer()
        for invalid_number in invalid_cases:
            with pytest.raises(SyntaxError):
                list(lexer.tokenize(raw_code=invalid_number))


class TestLexerOperators:
    """Test operator tokenization."""

    def test_arithmetic_operators(self):
        """Test arithmetic operators."""
        test_cases = [
            ("+", TokenKind.OP_PLUS),
            ("-", TokenKind.OP_MINUS),
            ("*", TokenKind.OP_MUL),
            ("/", TokenKind.OP_DIV),
            ("%", TokenKind.OP_MOD),
        ]

        lexer = Lexer()
        for op, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=op))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == op

    def test_comparison_operators(self):
        """Test comparison operators."""
        test_cases = [
            ("=", TokenKind.OP_EQUATE),
            ("==", TokenKind.OP_EQ),
            ("!=", TokenKind.OP_NE),
            ("<", TokenKind.OP_LT),
            ("<=", TokenKind.OP_LE),
            (">", TokenKind.OP_GT),
            (">=", TokenKind.OP_GE),
        ]

        lexer = Lexer()
        for op, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=op))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == op

    def test_assignment_operators(self):
        """Test assignment operators."""
        test_cases = [
            (":=", TokenKind.ASSIGNMENT),
            ("+=", TokenKind.OP_PLUSEQUAL),
            ("-=", TokenKind.OP_MINUSEQUAL),
            ("*=", TokenKind.OP_MULEQUAL),
            ("/=", TokenKind.OP_DIVEQUAL),
        ]

        lexer = Lexer()
        for op, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=op))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == op

    def test_shift_operators(self):
        """Test shift operators."""
        test_cases = [
            ("<<", TokenKind.OP_SHL),
            (">>", TokenKind.OP_SHR),
            ("<<=", TokenKind.OP_SHL_EQUAL),
            (">>=", TokenKind.OP_SHR_EQUAL),
        ]

        lexer = Lexer()
        for op, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=op))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == op

    def test_logical_operators(self):
        """Test logical operators."""
        test_cases = [
            ("&&", TokenKind.OP_AND),
            ("||", TokenKind.OP_OR),
            ("!", TokenKind.OP_NOT),
            ("~", TokenKind.OP_TILDE),
        ]

        lexer = Lexer()
        for op, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=op))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == op


class TestLexerUnicodeSupport:
    """Test Unicode operator and symbol support."""

    def test_unicode_arithmetic(self):
        """Test Unicode arithmetic operators."""
        test_cases = [
            ("×", TokenKind.OP_MUL),
            ("·", TokenKind.OP_MUL),
            ("⋅", TokenKind.OP_MUL),
            ("÷", TokenKind.OP_DIV),
            ("−", TokenKind.OP_MINUS),  # U+2212
        ]

        lexer = Lexer()
        for op, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=op))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == op

    def test_unicode_comparison(self):
        """Test Unicode comparison operators."""
        test_cases = [
            ("≤", TokenKind.OP_LE),
            ("≥", TokenKind.OP_GE),
            ("≠", TokenKind.OP_NE),
            ("≡", TokenKind.KW_EQUIV),
        ]

        lexer = Lexer()
        for op, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=op))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == op

    def test_unicode_logic(self):
        """Test Unicode logical operators."""
        test_cases = [
            ("∧", TokenKind.OP_AND),
            ("∨", TokenKind.OP_OR),
            ("¬", TokenKind.OP_NOT),
        ]

        lexer = Lexer()
        for op, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=op))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == op

    def test_unicode_arrows(self):
        """Test Unicode arrows."""
        test_cases = [
            ("→", TokenKind.KW_RIGHTARROW),
            ("⇒", TokenKind.KW_RIGHTARROW),
            ("↦", TokenKind.KW_RIGHTARROW),
            ("←", TokenKind.KW_LEFTARROW),
            ("⇐", TokenKind.KW_LEFTARROW),
        ]

        lexer = Lexer()
        for arrow, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=arrow))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == arrow

    def test_unicode_mathematical_symbols(self):
        """Test Unicode mathematical symbols."""
        test_cases = [
            ("∂", TokenKind.KW_PARTIAL),
            ("∇", TokenKind.KW_PDV),
            ("∑", TokenKind.KW_SUM),
            ("∏", TokenKind.KW_PROD),
            ("∫", TokenKind.KW_INT),
            ("√", TokenKind.KW_SQRT),
            ("∞", TokenKind.KW_INFTY),
        ]

        lexer = Lexer()
        for symbol, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=symbol))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == symbol

    def test_unicode_greek_letters(self):
        """Test Unicode Greek letters."""
        test_cases = [
            ("α", TokenKind.KW_GREEK),
            ("β", TokenKind.KW_GREEK),
            ("γ", TokenKind.KW_GREEK),
            ("δ", TokenKind.KW_GREEK),
            ("Γ", TokenKind.KW_GREEK),
            ("Δ", TokenKind.KW_GREEK),
            ("π", TokenKind.KW_GREEK),
            ("Π", TokenKind.KW_GREEK),
        ]

        lexer = Lexer()
        for letter, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=letter))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == letter


class TestLexerPunctuation:
    """Test punctuation tokenization."""

    def test_brackets_and_parentheses(self):
        """Test brackets and parentheses."""
        test_cases = [
            ("[", TokenKind.LBRACKET),
            ("]", TokenKind.RBRACKET),
            ("(", TokenKind.LPAREN),
            (")", TokenKind.RPAREN),
            ("{", TokenKind.LBRACE),
            ("}", TokenKind.RBRACE),
        ]

        lexer = Lexer()
        for punct, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=punct))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == punct

    def test_other_punctuation(self):
        """Test other punctuation marks."""
        test_cases = [
            (":", TokenKind.COLON),
            (";", TokenKind.SEMICOLON),
            (",", TokenKind.COMMA),
            (".", TokenKind.DOT),
            ("_", TokenKind.UNDERSCORE),
            # Note: # starts comments and is handled specially, not tokenized as HASHTAG
        ]

        lexer = Lexer()
        for punct, expected_kind in test_cases:
            tokens = list(lexer.tokenize(raw_code=punct))
            assert len(tokens) == 1
            assert tokens[0].kind == expected_kind
            assert tokens[0].lexeme == punct


class TestLexerStrings:
    """Test string tokenization."""

    def test_simple_string(self):
        """Test simple string."""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code='"hello"'))
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.STRING
        assert tokens[0].lexeme == '"hello"'

    def test_empty_string(self):
        """Test empty string."""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code='""'))
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.STRING
        assert tokens[0].lexeme == '""'

    def test_string_with_spaces(self):
        """Test string with spaces."""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code='"hello world"'))
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.STRING
        assert tokens[0].lexeme == '"hello world"'

    def test_unterminated_string(self):
        """Test unterminated string raises error."""
        lexer = Lexer()
        with pytest.raises(SyntaxError, match="Unterminated string literal"):
            list(lexer.tokenize(raw_code='"hello'))

    def test_string_with_newline(self):
        """Test string with newline raises error."""
        lexer = Lexer()
        with pytest.raises(SyntaxError, match="Unterminated string literal"):
            list(lexer.tokenize(raw_code='"hello\nworld"'))


class TestLexerIndentation:
    """Test indentation handling."""

    def test_simple_indentation(self):
        """Test simple indentation."""
        code = """with X:
    a = 1
b = 2"""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Find indentation tokens
        indent_tokens = [
            t for t in tokens if t.kind in (TokenKind.INDENT, TokenKind.DEDENT)
        ]
        assert len(indent_tokens) == 2
        assert indent_tokens[0].kind == TokenKind.INDENT
        assert indent_tokens[1].kind == TokenKind.DEDENT

    def test_nested_indentation(self):
        """Test nested indentation."""
        code = """with X:
    with Y:
        a = 1
    b = 2
c = 3"""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Find indentation tokens
        indent_tokens = [
            t for t in tokens if t.kind in (TokenKind.INDENT, TokenKind.DEDENT)
        ]
        assert len(indent_tokens) == 4  # 2 INDENTs, 2 DEDENTs
        assert indent_tokens[0].kind == TokenKind.INDENT
        assert indent_tokens[1].kind == TokenKind.INDENT
        assert indent_tokens[2].kind == TokenKind.DEDENT
        assert indent_tokens[3].kind == TokenKind.DEDENT

    def test_comments_dont_affect_indentation(self):
        """Test that comments don't affect indentation."""
        code = """with X:
    # This is a comment
    
    a = 1"""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should have proper indentation despite comments and blank lines
        indent_tokens = [
            t for t in tokens if t.kind in (TokenKind.INDENT, TokenKind.DEDENT)
        ]
        assert len(indent_tokens) == 2  # 1 INDENT, 1 DEDENT
        assert indent_tokens[0].kind == TokenKind.INDENT
        assert indent_tokens[1].kind == TokenKind.DEDENT


class TestLexerComments:
    """Test comment handling."""

    def test_line_comment(self):
        """Test line comments are skipped."""
        code = "a = 1  # This is a comment"
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should not contain any comment content
        lexemes = [t.lexeme for t in tokens]
        assert "This" not in lexemes
        assert "comment" not in lexemes

        # Should contain the actual code
        assert any(t.lexeme == "a" for t in tokens)
        assert any(t.lexeme == "=" for t in tokens)
        assert any(t.lexeme == "1" for t in tokens)

    def test_comment_only_line(self):
        """Test comment-only lines."""
        code = """a = 1
# This is a comment
b = 2"""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain variables and operators but no comment text
        lexemes = [t.lexeme for t in tokens]
        assert "a" in lexemes
        assert "b" in lexemes
        assert "This" not in lexemes


class TestLexerComplexExpressions:
    """Test complex expressions."""

    def test_mathematical_expression(self):
        """Test complex mathematical expression."""
        code = "result = α + β * 2.5e-3 ≤ γ → δ"
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        expected_kinds = [
            TokenKind.ID,  # result
            TokenKind.OP_EQUATE,  # =
            TokenKind.KW_GREEK,  # α
            TokenKind.OP_PLUS,  # +
            TokenKind.KW_GREEK,  # β
            TokenKind.OP_MUL,  # *
            TokenKind.FLOAT,  # 2.5e-3
            TokenKind.OP_LE,  # ≤
            TokenKind.KW_GREEK,  # γ
            TokenKind.KW_RIGHTARROW,  # →
            TokenKind.KW_GREEK,  # δ
        ]

        assert len(tokens) == len(expected_kinds)
        for token, expected_kind in zip(tokens, expected_kinds):
            assert token.kind == expected_kind

    def test_function_definition(self):
        """Test function definition."""
        code = "def calculate(x, y): return x * y"
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        expected_kinds = [
            TokenKind.KW_DEF,  # def
            TokenKind.FUNC_ID,  # calculate
            TokenKind.LPAREN,  # (
            TokenKind.ID,  # x
            TokenKind.COMMA,  # ,
            TokenKind.ID,  # y
            TokenKind.RPAREN,  # )
            TokenKind.COLON,  # :
            TokenKind.ID,  # return
            TokenKind.ID,  # x
            TokenKind.OP_MUL,  # *
            TokenKind.ID,  # y
        ]

        assert len(tokens) == len(expected_kinds)
        for token, expected_kind in zip(tokens, expected_kinds):
            assert token.kind == expected_kind

    def test_tensor_notation(self):
        """Test tensor notation."""
        code = "T_{ij} = g^{mu nu}"
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should recognize tensor identifiers
        tensor_tokens = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        assert len(tensor_tokens) == 2
        assert tensor_tokens[0].lexeme == "T"
        assert tensor_tokens[1].lexeme == "g"


class TestLexerErrorHandling:
    """Test error handling."""

    def test_invalid_character(self):
        """Test invalid character raises error."""
        lexer = Lexer()
        # Using a character that's not in any token map
        with pytest.raises(SyntaxError):
            list(lexer.tokenize(raw_code="@"))  # @ is not defined in token maps

    def test_debug_mode_error_reporting(self):
        """Test debug mode provides better error reporting."""
        debug_lexer = Lexer(debug=True)
        with pytest.raises(RuntimeError):  # Debug mode wraps in RuntimeError
            list(debug_lexer.tokenize(raw_code="@"))


class TestLexerUtilityFunctions:
    """Test utility functions."""

    def test_tokenize_string_function(self):
        """Test the standalone tokenize_string function."""
        tokens = tokenize_string(raw_code="let x = 42")
        token_list = list(tokens)

        assert len(token_list) == 4
        assert token_list[0].kind == TokenKind.KW_LET
        assert token_list[1].kind == TokenKind.ID
        assert token_list[2].kind == TokenKind.OP_EQUATE
        assert token_list[3].kind == TokenKind.INTEGER

    def test_tokenize_from_filepath(self):
        """Test tokenizing from a file path."""
        # Create a temporary file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("let x = 42")
            temp_path = f.name

        try:
            lexer = Lexer()
            tokens = list(lexer.tokenize(filepath=temp_path))

            assert len(tokens) == 4
            assert tokens[0].kind == TokenKind.KW_LET
            assert tokens[1].kind == TokenKind.ID
            assert tokens[2].kind == TokenKind.OP_EQUATE
            assert tokens[3].kind == TokenKind.INTEGER
        finally:
            os.unlink(temp_path)


class TestLexerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_infinite_loop_protection(self):
        """Test that the lexer has infinite loop protection."""
        lexer = Lexer()

        # Test normal operation doesn't trigger protection
        tokens = list(lexer.tokenize(raw_code="x + y"))
        assert len(tokens) == 3  # ID, OP_PLUS, ID

        # Test with longer input to verify protection scales
        long_input = "a" * 100
        tokens = list(lexer.tokenize(raw_code=long_input))
        assert len(tokens) == 1  # Should be one long ID token

        # The protection mechanism is internal and would raise RuntimeError
        # if triggered, but we can't easily test that without creating an
        # actual infinite loop condition

    def test_very_long_identifier(self):
        """Test very long identifier."""
        long_name = "a" * 1000
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=long_name))

        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.ID
        assert tokens[0].lexeme == long_name

    def test_many_operators_in_sequence(self):
        """Test many operators in sequence."""
        code = "+ - * / % == != <= >= << >> += -= *= /="
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should tokenize all operators correctly
        assert len(tokens) == 15
        assert all(
            t.kind.name.startswith("OP_") or t.kind == TokenKind.OP_EQUATE
            for t in tokens
        )

    def test_mixed_unicode_and_ascii(self):
        """Test mixed Unicode and ASCII in same expression."""
        code = "α + beta ≤ 42 → result"
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should handle both Unicode and ASCII correctly
        assert len(tokens) == 7
        assert tokens[0].kind == TokenKind.KW_GREEK  # α
        assert tokens[1].kind == TokenKind.OP_PLUS  # +
        assert tokens[2].kind == TokenKind.KW_GREEK  # beta
        assert tokens[3].kind == TokenKind.OP_LE  # ≤
        assert tokens[4].kind == TokenKind.INTEGER  # 42
        assert tokens[5].kind == TokenKind.KW_RIGHTARROW  # →
        assert tokens[6].kind == TokenKind.ID  # result

    def test_tensor_assignment_expression(self):
        """Test tensor assignment expression that may cause infinite loop."""
        test_one = """
A_{a} := x + y
"""
        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=test_one))

        # Filter out newline tokens for easier testing
        non_newline_tokens = [t for t in tokens if t.kind != TokenKind.NEWLINE]

        # Expected tokens: A (TENSOR_ID), _ (UNDERSCORE), { (LBRACE), a (ID), } (RBRACE),
        # := (ASSIGNMENT), x (ID), + (OP_PLUS), y (ID)
        expected_kinds = [
            TokenKind.TENSOR_ID,  # A
            TokenKind.UNDERSCORE,  # _
            TokenKind.LBRACE,  # {
            TokenKind.ID,  # a
            TokenKind.RBRACE,  # }
            TokenKind.ASSIGNMENT,  # :=
            TokenKind.ID,  # x
            TokenKind.OP_PLUS,  # +
            TokenKind.ID,  # y
        ]

        assert len(non_newline_tokens) == len(expected_kinds), (
            f"Expected {len(expected_kinds)} tokens, got {len(non_newline_tokens)}: {[t.kind for t in non_newline_tokens]}"
        )
        for i, (token, expected_kind) in enumerate(
            zip(non_newline_tokens, expected_kinds)
        ):
            assert token.kind == expected_kind, (
                f"Token {i}: expected {expected_kind}, got {token.kind} (lexeme: {token.lexeme})"
            )


if __name__ == "__main__":
    pytest.main([__file__])

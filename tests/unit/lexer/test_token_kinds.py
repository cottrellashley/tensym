"""Unit tests for token kinds and definitions."""

from tensym.interpreter.token._kind import TokenKind


class TestTokenKindDefinitions:
    """Test token kind definitions and properties."""

    def test_all_token_kinds_have_unique_values(self):
        """Test that all token kinds have unique values."""
        values = [kind.value for kind in TokenKind]
        assert len(values) == len(set(values)), "Token kinds should have unique values"

    def test_token_kind_categories(self):
        """Test token kind categorization."""
        # Operators
        operator_kinds = [
            TokenKind.OP_PLUS,
            TokenKind.OP_MINUS,
            TokenKind.OP_MUL,
            TokenKind.OP_DIV,
            TokenKind.OP_MOD,
        ]
        for kind in operator_kinds:
            assert kind.name.startswith("OP_"), f"{kind} should be an operator"

        # Keywords
        keyword_kinds = [
            TokenKind.KW_LET,
            TokenKind.KW_DEF,
            TokenKind.KW_IF,
            TokenKind.KW_THEN,
            TokenKind.KW_ELSE,
        ]
        for kind in keyword_kinds:
            assert kind.name.startswith("KW_"), f"{kind} should be a keyword"

        # Literals
        literal_kinds = [TokenKind.INTEGER, TokenKind.FLOAT, TokenKind.STRING]
        for kind in literal_kinds:
            assert kind in TokenKind, f"{kind} should be a valid token kind"

    def test_identifier_kinds(self):
        """Test identifier token kinds."""
        identifier_kinds = [
            TokenKind.ID,
            TokenKind.FUNC_ID,
            TokenKind.TENSOR_ID,
            TokenKind.LATEX_ID,
        ]
        for kind in identifier_kinds:
            assert "ID" in kind.name, f"{kind} should be an identifier type"

    def test_punctuation_kinds(self):
        """Test punctuation token kinds."""
        punctuation_kinds = [
            TokenKind.LPAREN,
            TokenKind.RPAREN,
            TokenKind.LBRACE,
            TokenKind.RBRACE,
            TokenKind.LBRACKET,
            TokenKind.RBRACKET,
            TokenKind.COMMA,
            TokenKind.DOT,
            TokenKind.COLON,
            TokenKind.SEMICOLON,
        ]
        for kind in punctuation_kinds:
            assert kind in TokenKind, f"{kind} should be a valid punctuation token"

    def test_special_tokens(self):
        """Test special token kinds."""
        special_kinds = [
            TokenKind.NEWLINE,
            TokenKind.INDENT,
            TokenKind.DEDENT,
            TokenKind.EOF,
        ]
        for kind in special_kinds:
            assert kind in TokenKind, f"{kind} should be a valid special token"

    def test_greek_letter_token(self):
        """Test Greek letter token kind."""
        assert TokenKind.KW_GREEK in TokenKind
        assert "GREEK" in TokenKind.KW_GREEK.name

    def test_mathematical_symbols(self):
        """Test mathematical symbol token kinds."""
        math_kinds = [
            TokenKind.KW_PI,
            TokenKind.KW_E,
            TokenKind.KW_INFTY,
            TokenKind.KW_SUM,
            TokenKind.KW_PROD,
            TokenKind.KW_SQRT,
            TokenKind.KW_INT,
            TokenKind.KW_PARTIAL,
        ]
        for kind in math_kinds:
            assert kind in TokenKind, f"{kind} should be a valid mathematical token"

    def test_assignment_operators(self):
        """Test assignment operator token kinds."""
        assignment_kinds = [
            TokenKind.ASSIGNMENT,
            TokenKind.OP_PLUSEQUAL,
            TokenKind.OP_MINUSEQUAL,
            TokenKind.OP_MULEQUAL,
            TokenKind.OP_DIVEQUAL,
        ]
        for kind in assignment_kinds:
            assert kind in TokenKind, f"{kind} should be a valid assignment operator"

    def test_comparison_operators(self):
        """Test comparison operator token kinds."""
        comparison_kinds = [
            TokenKind.OP_EQ,
            TokenKind.OP_NE,
            TokenKind.OP_LT,
            TokenKind.OP_LE,
            TokenKind.OP_GT,
            TokenKind.OP_GE,
            TokenKind.OP_EQUATE,
        ]
        for kind in comparison_kinds:
            assert kind in TokenKind, f"{kind} should be a valid comparison operator"

    def test_token_kind_string_representation(self):
        """Test string representation of token kinds."""
        for kind in TokenKind:
            str_repr = str(kind)
            assert str_repr.startswith("TokenKind."), (
                f"String representation should start with 'TokenKind.': {str_repr}"
            )
            assert kind.name in str_repr, (
                f"Token name should be in string representation: {str_repr}"
            )

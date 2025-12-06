"""End-to-end tests for mathematical expressions."""

import pytest

from tensym.interpreter.lexer._lexer import Lexer


class TestMathematicalExpressions:
    """Test complete mathematical expression processing."""

    def test_simple_arithmetic_file(self, fixtures_dir):
        """Test processing simple arithmetic from file."""
        simple_math_file = fixtures_dir / "simple_math.tensym"

        if not simple_math_file.exists():
            pytest.skip("simple_math.tensym fixture not found")

        lexer = Lexer()
        tokens = list(lexer.tokenize(filepath=str(simple_math_file)))

        # Should successfully tokenize without errors
        assert len(tokens) > 0

        # Should contain expected identifiers
        lexemes = {t.lexeme for t in tokens}
        expected_vars = {"a", "b", "c", "sum", "product", "square_root"}
        assert len(lexemes.intersection(expected_vars)) >= 4

    def test_mathematical_constants(self):
        """Test mathematical constants processing."""
        code = """
let pi_val = pi
let e_val = e
let infinity = ∞
let result = pi_val * e_val
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain mathematical constants
        from tensym.interpreter.token._kind import TokenKind

        pi_tokens = [t for t in tokens if t.kind == TokenKind.KW_PI]
        e_tokens = [t for t in tokens if t.kind == TokenKind.KW_E]
        infty_tokens = [t for t in tokens if t.kind == TokenKind.KW_INFTY]

        assert len(pi_tokens) >= 1
        assert len(e_tokens) >= 1
        assert len(infty_tokens) >= 1

    def test_complex_mathematical_functions(self):
        """Test complex mathematical function expressions."""
        code = """
let result1 = sin(π/2)
let result2 = cos(0)
let result3 = tan(π/4)
let result4 = log(e)
let result5 = sqrt(4)
let result6 = exp(1)
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain function identifiers
        func_tokens = [t for t in tokens if t.kind == TokenKind.FUNC_ID]
        func_names = {t.lexeme for t in func_tokens}

        expected_funcs = {"sin", "cos", "tan", "log", "sqrt", "exp"}
        assert len(func_names.intersection(expected_funcs)) >= 4

    def test_scientific_notation_expressions(self):
        """Test scientific notation in expressions."""
        code = """
let avogadro = 6.022e23
let planck = 6.626e-34
let speed_of_light = 2.998e8
let result = avogadro * planck * speed_of_light
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain float tokens with scientific notation
        float_tokens = [t for t in tokens if t.kind == TokenKind.FLOAT]
        scientific_notation = [t for t in float_tokens if "e" in t.lexeme]

        assert len(scientific_notation) >= 3

    def test_greek_letter_expressions(self):
        """Test expressions with Greek letters."""
        code = """
let α = 1.0
let β = 2.0
let γ = α + β
let δ = α * β
let Δ = γ - δ
let π_approx = 22/7
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain Greek letter tokens
        greek_tokens = [t for t in tokens if t.kind == TokenKind.KW_GREEK]
        greek_letters = {t.lexeme for t in greek_tokens}

        expected_letters = {"α", "β", "γ", "δ", "Δ"}
        assert len(greek_letters.intersection(expected_letters)) >= 4

    def test_unicode_mathematical_operators(self):
        """Test Unicode mathematical operators."""
        code = """
let result1 = a × b
let result2 = c ÷ d
let result3 = e ≤ f
let result4 = g ≥ h
let result5 = i ≠ j
let result6 = k ≡ l
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should contain Unicode operators
        unicode_ops = {t.lexeme for t in tokens}
        expected_ops = {"×", "÷", "≤", "≥", "≠", "≡"}

        assert len(unicode_ops.intersection(expected_ops)) >= 4

    def test_summation_and_product_notation(self):
        """Test summation and product notation."""
        code = """
let sum_result = ∑_{i=1}^{n} x_i
let prod_result = ∏_{j=0}^{m} y_j
let integral = ∫_{a}^{b} f(x) dx
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain summation/product symbols
        sum_tokens = [t for t in tokens if t.kind == TokenKind.KW_SUM]
        prod_tokens = [t for t in tokens if t.kind == TokenKind.KW_PROD]
        int_tokens = [t for t in tokens if t.kind == TokenKind.KW_INT]

        assert len(sum_tokens) >= 1
        assert len(prod_tokens) >= 1
        assert len(int_tokens) >= 1

    def test_complex_nested_expressions(self):
        """Test complex nested mathematical expressions."""
        code = """
let result = √((α + β)² + (γ - δ)²)
let quadratic = (-b ± √(b² - 4ac)) / (2a)
let exponential = e^{iπ} + 1
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should tokenize without errors
        assert len(tokens) > 0

        # Should handle nested parentheses and braces
        from tensym.interpreter.token._kind import TokenKind

        lparen_count = len([t for t in tokens if t.kind == TokenKind.LPAREN])
        rparen_count = len([t for t in tokens if t.kind == TokenKind.RPAREN])
        lbrace_count = len([t for t in tokens if t.kind == TokenKind.LBRACE])
        rbrace_count = len([t for t in tokens if t.kind == TokenKind.RBRACE])

        # Should have balanced parentheses and braces
        assert lparen_count == rparen_count
        assert lbrace_count == rbrace_count

    def test_error_handling_invalid_expressions(self):
        """Test error handling for invalid mathematical expressions."""
        invalid_expressions = [
            "let x = 1.2.3.4",  # Invalid number
            "let y = sin(",  # Unmatched parenthesis
            "let z = @invalid",  # Invalid character
            'let s = "unterminated string',  # Unterminated string
        ]

        lexer = Lexer()

        for expr in invalid_expressions:
            with pytest.raises(SyntaxError):
                list(lexer.tokenize(raw_code=expr))

    def test_whitespace_tolerance(self):
        """Test tolerance for various whitespace patterns."""
        code = """
        let    x   =   42
        let y=43
        let z = 44
        
        let    result    =    x    +    y    *    z
        """

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should handle various whitespace patterns
        from tensym.interpreter.token._kind import TokenKind

        # Should contain expected variables
        id_tokens = [t for t in tokens if t.kind == TokenKind.ID]
        var_names = {t.lexeme for t in id_tokens}

        expected_vars = {"x", "y", "z", "result"}
        assert expected_vars.issubset(var_names)

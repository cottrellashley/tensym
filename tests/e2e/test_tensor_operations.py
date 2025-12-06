"""End-to-end tests for tensor operations."""

import pytest

from tensym.interpreter.lexer._lexer import Lexer


class TestTensorOperations:
    """Test complete tensor operation processing."""

    def test_tensor_file_processing(self, fixtures_dir):
        """Test processing tensor calculations from file."""
        tensor_file = fixtures_dir / "tensor_calc.tensym"

        if not tensor_file.exists():
            pytest.skip("tensor_calc.tensym fixture not found")

        lexer = Lexer()
        tokens = list(lexer.tokenize(filepath=str(tensor_file)))

        # Should successfully tokenize without errors
        assert len(tokens) > 0

        from tensym.interpreter.token._kind import TokenKind

        # Should contain tensor identifiers
        tensor_tokens = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        assert len(tensor_tokens) >= 3  # Multiple tensors

    def test_simple_tensor_notation(self):
        """Test simple tensor index notation."""
        code = """
T_{ij} = A_{ik} * B_{kj}
S^{ij} = g^{ik} * g^{jl} * T_{kl}
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain tensor identifiers
        tensor_tokens = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        tensor_names = {t.lexeme for t in tensor_tokens}

        expected_tensors = {"T", "A", "B", "S", "g"}
        assert len(tensor_names.intersection(expected_tensors)) >= 3

    def test_einstein_summation_notation(self):
        """Test Einstein summation convention."""
        code = """
# Contraction
trace = T^i_i

# Matrix multiplication
C_{ij} = A_{ik} B_{kj}

# Metric operations
length_squared = g_{μν} x^μ x^ν
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should handle repeated indices correctly
        tensor_tokens = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        assert len(tensor_tokens) >= 4

        # Should contain Greek indices
        greek_tokens = [t for t in tokens if t.kind == TokenKind.KW_GREEK]
        assert len(greek_tokens) >= 2  # μ, ν

    def test_riemann_curvature_tensor(self):
        """Test Riemann curvature tensor notation."""
        code = """
R^ρ_{σμν} = ∂_μ Γ^ρ_{νσ} - ∂_ν Γ^ρ_{μσ} + Γ^ρ_{μλ} Γ^λ_{νσ} - Γ^ρ_{νλ} Γ^λ_{μσ}
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain partial derivative symbols
        partial_tokens = [t for t in tokens if t.kind == TokenKind.KW_PARTIAL]
        assert len(partial_tokens) >= 2

        # Should contain Christoffel symbols (Γ)
        gamma_tokens = [t for t in tokens if t.lexeme == "Γ"]
        assert len(gamma_tokens) >= 4

    def test_metric_tensor_operations(self):
        """Test metric tensor operations."""
        code = """
with metric g:
    # Minkowski metric
    g_{00} = -1
    g_{11} = 1
    g_{22} = 1
    g_{33} = 1
    
    # Raise index
    x^μ = g^{μν} x_ν
    
    # Lower index
    x_μ = g_{μν} x^ν
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain 'with' keyword
        with_tokens = [t for t in tokens if t.kind == TokenKind.KW_WITH]
        assert len(with_tokens) >= 1

        # Should handle mixed upper/lower indices
        tensor_tokens = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        assert len(tensor_tokens) >= 3

    def test_electromagnetic_field_tensor(self):
        """Test electromagnetic field tensor."""
        code = """
# Field strength tensor
F_{μν} = ∂_μ A_ν - ∂_ν A_μ

# Dual tensor
F̃^{μν} = (1/2) ε^{μνρσ} F_{ρσ}

# Maxwell equations
∂_μ F^{μν} = J^ν
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain field tensors
        tensor_tokens = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        tensor_names = {t.lexeme for t in tensor_tokens}

        expected_tensors = {"F", "A", "J", "ε"}
        assert len(tensor_names.intersection(expected_tensors)) >= 2

    def test_tensor_contractions(self):
        """Test various tensor contractions."""
        code = """
# Trace
trace_T = T^i_i

# Double contraction
double_trace = T^{ij} S_{ij}

# Ricci tensor from Riemann
R_{μν} = R^ρ_{μρν}

# Ricci scalar
R = g^{μν} R_{μν}
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should handle repeated indices for contractions
        tensor_tokens = [t for t in tokens if t.kind == TokenKind.TENSOR_ID]
        assert len(tensor_tokens) >= 6

    def test_tensor_symmetries(self):
        """Test tensor symmetry operations."""
        code = """
# Symmetric tensor
S_{(μν)} = (1/2)(T_{μν} + T_{νμ})

# Antisymmetric tensor
A_{[μν]} = (1/2)(T_{μν} - T_{νμ})

# Symmetrization
symmetric_part = T_{(ij)}

# Antisymmetrization
antisymmetric_part = T_{[ij]}
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should tokenize symmetry notation correctly
        from tensym.interpreter.token._kind import TokenKind

        # Should contain parentheses and brackets for symmetry
        lparen_count = len([t for t in tokens if t.kind == TokenKind.LPAREN])
        lbracket_count = len([t for t in tokens if t.kind == TokenKind.LBRACKET])

        assert lparen_count >= 4
        assert lbracket_count >= 2

    def test_covariant_derivatives(self):
        """Test covariant derivative notation."""
        code = """
# Covariant derivative
∇_μ T^ν = ∂_μ T^ν + Γ^ν_{μλ} T^λ

# Covariant derivative of vector
∇_μ V_ν = ∂_μ V_ν - Γ^λ_{μν} V_λ

# Laplacian
□φ = ∇^μ ∇_μ φ
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        from tensym.interpreter.token._kind import TokenKind

        # Should contain nabla (∇) symbols
        nabla_tokens = [t for t in tokens if t.kind == TokenKind.KW_PDV]
        assert len(nabla_tokens) >= 3

    def test_tensor_products(self):
        """Test tensor product operations."""
        code = """
# Outer product
T_{ij} = u_i ⊗ v_j

# Tensor product
S_{ijkl} = A_{ij} ⊗ B_{kl}

# Wedge product
ω = dx ∧ dy

# Cross product
c_i = ε_{ijk} a^j b^k
"""

        lexer = Lexer()
        tokens = list(lexer.tokenize(raw_code=code))

        # Should handle various product symbols
        lexemes = {t.lexeme for t in tokens}
        product_symbols = {"⊗", "∧"}

        assert len(lexemes.intersection(product_symbols)) >= 1

    def test_complex_tensor_file(self, fixtures_dir):
        """Test processing complex tensor example file."""
        complex_file = fixtures_dir / "complex_example.tensym"

        if not complex_file.exists():
            pytest.skip("complex_example.tensym fixture not found")

        lexer = Lexer()
        tokens = list(lexer.tokenize(filepath=str(complex_file)))

        # Should successfully process complex notation
        assert len(tokens) > 0

        from tensym.interpreter.token._kind import TokenKind

        # Should contain various tensor and mathematical elements
        token_kinds = {t.kind for t in tokens}
        expected_kinds = {
            TokenKind.TENSOR_ID,
            TokenKind.KW_GREEK,
            TokenKind.KW_SUM,
            TokenKind.KW_INT,
            TokenKind.KW_PARTIAL,
            TokenKind.FUNC_ID,
        }

        # Should contain most expected token types
        assert len(token_kinds.intersection(expected_kinds)) >= 4

    def test_tensor_error_handling(self):
        """Test error handling in tensor notation."""
        invalid_tensor_codes = [
            "T_{unclosed",  # Unclosed brace
            "S^{mixed}_{notation",  # Mixed notation error
            "R^{too{many{braces}}}",  # Nested braces incorrectly
        ]

        lexer = Lexer()

        for code in invalid_tensor_codes:
            with pytest.raises(SyntaxError):
                list(lexer.tokenize(raw_code=code))

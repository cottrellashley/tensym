"""Unit tests for AST node construction and manipulation."""

import pytest

from tensym.interpreter.diagnostics import SourceSpan

# Import NodeType separately to avoid Python 3.9 compatibility issues
try:
    from tensym.interpreter.ast_nodes import NodeType
except TypeError:
    # Handle Python 3.9 compatibility issue with union types
    import sys

    if sys.version_info < (3, 10):
        pytest.skip(
            "AST nodes require Python 3.10+ for union type syntax",
            allow_module_level=True,
        )
    else:
        raise


class TestNodeType:
    """Test AST node type enumeration."""

    def test_node_type_values(self):
        """Test node type enum values."""
        # Test some basic node types exist
        assert NodeType.ADD.value == "+"
        assert NodeType.SUB.value == "-"
        assert NodeType.MUL.value == "*"
        assert NodeType.DIV.value == "/"

    def test_comparison_operators(self):
        """Test comparison operator node types."""
        assert NodeType.EQEQUAL.value == "=="
        assert NodeType.NOTEQUAL.value == "!="
        assert NodeType.LESS.value == "<"
        assert NodeType.GREATER.value == ">"

    def test_literal_types(self):
        """Test literal node types."""
        assert NodeType.INT.value == "int"
        assert NodeType.FLOAT.value == "float"
        assert NodeType.SYMBOL.value == "symbol"

    def test_control_structures(self):
        """Test control structure node types."""
        assert NodeType.ASSIGNMENT.value == "="
        assert NodeType.DEFINITION.value == ":="
        assert NodeType.PRINT.value == "print"


class TestSourceSpanIntegration:
    """Test source span integration with AST nodes."""

    def test_source_span_creation(self):
        """Test source span creation for AST context."""
        span = SourceSpan("test.py", 1, 1, 1, 5)

        assert span.filename == "test.py"
        assert span.start_line == 1
        assert span.start_pos == 1
        assert span.end_line == 1
        assert span.end_pos == 5


class TestLiteralNode:
    """Test literal node functionality."""

    def test_literal_node_types(self):
        """Test literal node type constants."""
        # Test that literal node types are available
        assert NodeType.INT
        assert NodeType.FLOAT
        assert NodeType.CONSTANT
        assert NodeType.SYMBOL

    def test_literal_values(self):
        """Test literal node type values."""
        assert NodeType.INT.value == "int"
        assert NodeType.FLOAT.value == "float"
        assert NodeType.CONSTANT.value == "constant"
        assert NodeType.SYMBOL.value == "symbol"


class TestOperatorNodes:
    """Test operator node type definitions."""

    def test_binary_operators(self):
        """Test binary operator node types."""
        binary_ops = [
            NodeType.ADD,
            NodeType.SUB,
            NodeType.MUL,
            NodeType.DIV,
            NodeType.POW,
        ]

        for op in binary_ops:
            assert op.value in ["+", "-", "*", "/", "^"]

    def test_comparison_operators(self):
        """Test comparison operator node types."""
        comparison_ops = [
            NodeType.EQEQUAL,
            NodeType.NOTEQUAL,
            NodeType.LESS,
            NodeType.LESSEQUAL,
            NodeType.GREATER,
            NodeType.GREATEREQUAL,
        ]

        for op in comparison_ops:
            assert op.value in ["==", "!=", "<", "<=", ">", ">="]

    def test_unary_operators(self):
        """Test unary operator node types."""
        unary_ops = [NodeType.POS, NodeType.NEG, NodeType.NOT]

        for op in unary_ops:
            assert op.value in ["+", "-", "not"]


class TestMathematicalNodes:
    """Test mathematical construct node types."""

    def test_tensor_node_type(self):
        """Test tensor node type."""
        assert NodeType.TENSOR.value == "tensor"

    def test_array_node_type(self):
        """Test array node type."""
        assert NodeType.ARRAY.value == "array"

    def test_mathematical_constructs(self):
        """Test various mathematical node types exist."""
        # These should be available in the NodeType enum
        math_types = [NodeType.TENSOR, NodeType.ARRAY]

        for node_type in math_types:
            assert isinstance(node_type, NodeType)

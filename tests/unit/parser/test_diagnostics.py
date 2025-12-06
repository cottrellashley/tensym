"""Unit tests for diagnostic and error handling functionality."""

from tensym.interpreter.diagnostics import Diagnostic, InvalidSyntaxError, SourceSpan


class TestDiagnostic:
    """Test diagnostic message functionality."""

    def test_diagnostic_creation(self):
        """Test diagnostic creation."""
        span = SourceSpan("test.py", 1, 5, 1, 10)
        diagnostic = Diagnostic(message="Unexpected token", span=span, level="error")

        assert diagnostic.level == "error"
        assert diagnostic.message == "Unexpected token"
        assert diagnostic.span == span

    def test_diagnostic_levels(self):
        """Test different diagnostic levels."""
        span = SourceSpan("test.py", 1, 1, 1, 5)

        levels = ["info", "warning", "error"]

        for level in levels:
            diagnostic = Diagnostic("Test message", span, level)
            assert diagnostic.level == level

    def test_diagnostic_without_span(self):
        """Test diagnostic without source span."""
        diagnostic = Diagnostic(message="General error", level="error")

        assert diagnostic.message == "General error"
        assert diagnostic.span is None
        assert diagnostic.level == "error"

    def test_diagnostic_default_level(self):
        """Test diagnostic with default level."""
        diagnostic = Diagnostic(message="Test message")

        assert diagnostic.level == "error"  # Default level


class TestSourceSpan:
    """Test source span functionality."""

    def test_source_span_creation(self):
        """Test source span creation."""
        span = SourceSpan("test.py", 1, 5, 1, 10)

        assert span.filename == "test.py"
        assert span.start_line == 1
        assert span.start_pos == 5
        assert span.end_line == 1
        assert span.end_pos == 10

    def test_source_span_from_raw_code(self):
        """Test creating source span from raw code."""
        code = "line 1\nline 2\nline 3"
        span = SourceSpan.from_raw_code(code, 7, 13, "test.py")  # "line 2"

        assert span.filename == "test.py"
        assert span.start_line == 2
        assert span.end_line == 2

    def test_source_span_single_character(self):
        """Test source span for single character."""
        code = "hello world"
        span = SourceSpan.from_raw_code(code, 6, None, "test.py")  # "w"

        assert span.start_pos == 7  # Position of 'w'
        assert (
            span.end_pos == 8
        )  # End position is exclusive (start + 1 for single char)


class TestInvalidSyntaxError:
    """Test invalid syntax error functionality."""

    def test_invalid_syntax_error_creation(self):
        """Test invalid syntax error creation."""
        error = InvalidSyntaxError("Unexpected token", (1, 5))

        assert str(error) == "Unexpected token"
        assert error.message == "Unexpected token"
        # Note: location is passed to constructor but not stored as attribute

    def test_invalid_syntax_error_inheritance(self):
        """Test that InvalidSyntaxError is an Exception."""
        error = InvalidSyntaxError("Test error", (1, 1))

        assert isinstance(error, Exception)

    def test_placeholder_for_future_manager(self):
        """Placeholder test for future diagnostic manager implementation."""
        # This test serves as a placeholder for when DiagnosticManager is implemented
        assert True  # Always passes

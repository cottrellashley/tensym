"""Unit tests for iterator functionality."""

from tensym.interpreter.iterator import Iterator


class TestIterator:
    """Test iterator functionality."""

    def test_iterator_initialization(self):
        """Test iterator can be initialized."""
        data = [1, 2, 3, 4, 5]
        iterator = Iterator(data)
        assert iterator is not None

    def test_iterator_with_empty_data(self):
        """Test iterator with empty data."""
        iterator = Iterator([])
        assert iterator is not None

    def test_iterator_advance(self):
        """Test iterator advance functionality."""
        data = [1, 2, 3]
        iterator = Iterator(data)

        # Initial state - should be at sentinel
        iterator.advance()  # Move to first element
        assert iterator.current == 1

        iterator.advance()  # Move to second element
        assert iterator.current == 2

        iterator.advance()  # Move to third element
        assert iterator.current == 3

        iterator.advance()  # Move past end
        assert iterator.current == Iterator.boundary.EOI

    def test_iterator_peek(self):
        """Test iterator peek functionality."""
        data = [1, 2, 3]
        iterator = Iterator(data)
        iterator.advance()  # Move to first element

        # Peek should show next element without advancing
        assert iterator.peek() == 2
        assert iterator.current == 1  # Should still be at first element

        # Peek multiple times should return same value
        assert iterator.peek() == 2
        assert iterator.peek() == 2

    def test_iterator_peek_at_end(self):
        """Test peek behavior at end of data."""
        data = [1, 2]
        iterator = Iterator(data)
        iterator.advance()  # Move to first element
        iterator.advance()  # Move to second element

        # Peek past end should return None (default)
        assert iterator.peek() is None
        assert iterator.current == 2

    def test_iterator_current_before_advance(self):
        """Test current() before any advance() calls."""
        data = [1, 2, 3]
        iterator = Iterator(data)

        # Should be at sentinel position initially
        assert iterator.current == Iterator.boundary.SOI

    def test_iterator_with_string_data(self):
        """Test iterator with string data (character codes)."""
        text = "hello"
        data = [ord(c) for c in text]
        iterator = Iterator(data)

        iterator.advance()
        assert iterator.current == ord("h")

        iterator.advance()
        assert iterator.current == ord("e")

    def test_iterator_multiple_advances(self):
        """Test multiple consecutive advances."""
        data = list(range(10))
        iterator = Iterator(data)

        for i in range(10):
            iterator.advance()
            assert iterator.current == i

        # One more advance should go past end
        iterator.advance()
        assert iterator.current == Iterator.boundary.EOI

    def test_iterator_peek_sequence(self):
        """Test peeking through a sequence."""
        data = [1, 2, 3, 4, 5]
        iterator = Iterator(data)
        iterator.advance()  # Start at first element

        # Peek should always show next element
        assert iterator.peek() == 2
        iterator.advance()
        assert iterator.peek() == 3
        iterator.advance()
        assert iterator.peek() == 4
        iterator.advance()
        assert iterator.peek() == 5
        iterator.advance()
        assert iterator.peek() is None

    def test_iterator_position_tracking(self):
        """Test that iterator maintains position correctly."""
        data = [10, 20, 30]
        iterator = Iterator(data)

        # Track position through advances
        positions = []
        for _ in range(4):  # One past the end
            iterator.advance()
            positions.append(iterator.current)

        assert positions == [10, 20, 30, Iterator.boundary.EOI]

    def test_iterator_with_none_values(self):
        """Test iterator with None values in data."""
        data = [1, None, 3, None, 5]
        iterator = Iterator(data)

        iterator.advance()
        assert iterator.current == 1

        iterator.advance()
        assert iterator.current is None  # Actual None value

        iterator.advance()
        assert iterator.current == 3

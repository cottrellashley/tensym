import os

from tensym.interpreter.diagnostics import raise_invalid_syntax
from tensym.interpreter.iterator import CodeIterator, Iterator
from tensym.interpreter.token._kind import TokenKind
from tensym.interpreter.token._token import Token
from tensym.interpreter.token.utils import (
    BACKSLASH,
    ENCAPSULATORS,
    HASHTAG,
    NEWLINE,
    SET_OF_DIGITS,
    STRING_DELIM,
    WHITESPACE_CHARS,
    Indenter,
    build_encapsulation_token,
    build_string_token,
    build_token_from_digit,
    build_token_from_latex,
    build_token_from_word,
    is_end_of_iteration,
    is_letter_or_underscore,
    longest_token_match_and_consume,
    scan_newline_and_indent,
)


class Lexer:
    def __init__(self, debug: bool = False):
        self.__debug = os.environ.get("TENSYM_LEXER_DEBUG_MODE", "0") == "1" or debug
        self.tokens = []

    def scanner(self):
        pass

    def tokenize(self, *, raw_code: str = None, filepath: str = None, iterable=None):
        if iterable is None:
            iterable = CodeIterator(raw_code=raw_code, filepath=filepath)
        assert isinstance(iterable, CodeIterator)

        # Reset tokens for each tokenization
        self.tokens = []

        if iterable.index != -1:
            iterable.reset()
        iterable.advance()

        # Infinite loop protection: calculate maximum allowed iterations
        # Use input length * 3 as safety margin (should be more than enough for any valid input)
        input_length = iterable.length
        max_iterations = max(
            input_length * 3, 1000
        )  # At least 1000 iterations for small inputs
        iteration_count = 0

        if not self.__debug:
            while iterable.current != iterable.boundary.EOI:
                iteration_count += 1
                if iteration_count > max_iterations:
                    raise RuntimeError(
                        f"Lexer infinite loop detected: exceeded {max_iterations} iterations "
                        f"for input of length {input_length}. This is a language implementation bug, "
                        f"not a user input error. Please report this issue."
                    )

                token = self.build_token(iterable)
                if token is not None:
                    self.tokens.append(token)
        else:
            while iterable.current != iterable.boundary.EOI:
                iteration_count += 1
                if iteration_count > max_iterations:
                    raise RuntimeError(
                        f"Lexer infinite loop detected: exceeded {max_iterations} iterations "
                        f"for input of length {input_length}. This is a language implementation bug, "
                        f"not a user input error. Please report this issue."
                    )

                try:
                    token = self.build_token(iterable)
                except Exception as e:
                    # Try to get current position for error reporting, but handle edge cases
                    try:
                        current = iterable.printable_current_position_underlined()
                    except (IndexError, AttributeError):
                        current = f"<position unavailable, index: {iterable.index}>"
                    raise RuntimeError(
                        f"Error while tokenizing at line:\n{current}\n{e}"
                    ) from e
                if token is not None:
                    self.tokens.append(token)

        # Add any remaining dedent tokens at EOF
        if hasattr(self, "_indenter"):
            eof_tokens = self._indenter.flush_eof()
            for token_kind in eof_tokens:
                self.tokens.append(
                    Token(
                        kind=token_kind,
                        lexeme_unicode=[],
                        end_index=iterable.index,
                    )
                )

        return Iterator(self.tokens)

    def build_token(self, iterable):
        """Build a single token from the current position in the iterable."""
        # Initialize indenter if not exists
        if not hasattr(self, "_indenter"):
            self._indenter = Indenter()

        cp = iterable.current

        # Skip whitespace (but not newlines)
        if cp in WHITESPACE_CHARS:
            while iterable.current in WHITESPACE_CHARS:
                iterable.advance()
            return None  # Skip whitespace

        # Handle comments
        if cp == HASHTAG:
            while (
                not is_end_of_iteration(iterable.current)
                and iterable.current != NEWLINE
            ):
                iterable.advance()
            return None  # Skip comments

        # Handle newlines and indentation
        if cp == NEWLINE:
            tokens = scan_newline_and_indent(
                iterable,
                self._indenter,
                treat_hash_as_comment=True,
                consume_ws_on_blank=True,
                emit_newline_inside_parens=False,
            )
            # Return the first token, store the rest for later
            if tokens:
                if len(tokens) > 1:
                    # Store remaining tokens for next calls
                    if not hasattr(self, "_pending_tokens"):
                        self._pending_tokens = []
                    self._pending_tokens.extend(tokens[1:])
                return Token(
                    kind=tokens[0],
                    lexeme_unicode=[NEWLINE] if tokens[0] == TokenKind.NEWLINE else [],
                    end_index=iterable.index,
                )
            return None

        # Check for pending tokens from indentation processing
        if hasattr(self, "_pending_tokens") and self._pending_tokens:
            token_kind = self._pending_tokens.pop(0)
            return Token(
                kind=token_kind,
                lexeme_unicode=[],
                end_index=iterable.index,
            )

        # Handle identifiers and keywords
        if is_letter_or_underscore(cp):
            token = build_token_from_word(iterable)
            if token is not None:
                return token
            # If build_token_from_word returns None, fall through to operator handling

        # Handle numbers (but not standalone dots)
        if cp in SET_OF_DIGITS or (
            cp == ord(".") and iterable.peek(1) in SET_OF_DIGITS
        ):
            token = build_token_from_digit(iterable)
            iterable.advance()
            return token

        # Handle strings
        if cp == STRING_DELIM:
            token = build_string_token(iterable)
            iterable.advance()
            return token

        # Handle LaTeX tokens
        if cp == BACKSLASH:
            return build_token_from_latex(iterable)

        # Handle encapsulators (brackets, parentheses, braces)
        if cp in ENCAPSULATORS:
            token = build_encapsulation_token(iterable)
            # Update parentheses depth for indentation
            self._indenter.update_paren_depth(token.kind)
            iterable.advance()
            return token

        # Handle operators and other symbols
        # Use the longest_token_match_and_consume function directly on the main iterator
        from tensym.interpreter.iterator import Iterator as UtilsIterator

        # Create a temporary iterator starting from current position
        remaining_chars = []
        # start_index = iterable.index  # Unused variable
        for i in range(min(10, iterable.length - iterable.index)):
            char = iterable.peek(i)
            if not is_end_of_iteration(char):
                remaining_chars.append(char)
            else:
                break

        if remaining_chars:
            temp_iter = UtilsIterator(remaining_chars)
            temp_iter.advance()  # Prime it to point to first character

            # Find the match without consuming from temp_iter
            op_token_kind = longest_token_match_and_consume(
                temp_iter, advance_to="last"
            )
            if op_token_kind is not None:
                # temp_iter.index now points to the last character of the match
                # So the length is temp_iter.index + 1 (since it started at -1, advanced to 0, then to match end)
                match_length = temp_iter.index + 1

                # Collect the matched characters from the main iterator
                lexeme_chars = []
                for i in range(match_length):
                    if iterable.current != iterable.boundary.EOI:
                        lexeme_chars.append(iterable.current)
                        iterable.advance()
                    else:
                        break

                # Update parentheses depth if needed
                self._indenter.update_paren_depth(op_token_kind)

                return Token(
                    kind=op_token_kind,
                    lexeme_unicode=lexeme_chars,
                    end_index=iterable.index,
                )

        # If we get here, it's an unrecognized character
        raise_invalid_syntax(iterable)

    def skip_comment(self, iterable):
        while iterable.current not in {NEWLINE, iterable.boundary.EOI}:
            iterable.advance()
        if iterable.current == NEWLINE:
            iterable.advance()

    def skip_whitespace(self, iterable):
        while iterable.current in WHITESPACE_CHARS:
            iterable.advance()


def tokenize_string(raw_code: str = None, filepath: str = None):
    lexer = Lexer()
    tokens = lexer.tokenize(raw_code=raw_code, filepath=filepath)
    # Returns the list of tokens
    return tokens

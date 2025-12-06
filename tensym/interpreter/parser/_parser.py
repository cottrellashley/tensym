# ##############################################################################
# ######################## RELATIVITY PARSER GRAMMAR ###########################
# ##############################################################################
#
# statements:
#     NEWLINE* statement (NEWLINE* statement)
#
# statement:
#     KEYWORD:print? expr
#
# expr:
#     (ID | TENSORID) EQUAL expr
#   | bool-expr ((KEYWORD:and | KEYWORD:or) bool-expr)*
#
# bool-expr:
#     NOT bool-expr
#   | arith-expr ((EQEQUAL | LESS | GREATER | LESSEQUAL | GREATEREQUAL) arith-expr)*
#
# arith-expr:
#     term ((PLUS | MINUS) term)*
#
# term:
#     factor ((MUL | DIV) factor)*
#
# factor:
#     (PLUS | MINUS) factor
#   | power
#
# power:
#     atom ((CIRCUMFLEX | DOUBLESTAR) atom)*
#
# atom:
#     INT | FLOAT | STRING | BOOL | ID | TENSORID | FUNCTIONID | LATEXID
#   | LPAR expr RPAR
#   | array
#   | func-def
#   | tensor
#
# tensor:
#     TENSORID ((UNDER | CIRCUMFLEX) LBRACE ID ((EQUAL | COLON) (INT | atom))? RBRACE )*
#
# array:
#     LPAR (expr ((COMMA) expr*)? RPAR)
#
# func-def:
#     FUNCTIONID? LPAR (ID (COMMA ID)*)? RPAR (EQUAL expr NEWLINE)
#
# statement:
#     KEYWORD:print? expr
#   | if-stmt
#
# if-stmt:
#     KW_IF boolean_expression ':' block
#       (KW_ELIF boolean_expression ':' block)*
#       (KW_ELSE ':' block)?
#
# block:
#     NEWLINE INDENT statements DEDENT
#   | statement        # single-line suite
# ##############################################################################

import os
from typing import Iterable, Optional

from tensym.interpreter.ast_nodes import (
    ArrayNode,
    AstNode,
    BinaryNode,
    Call,
    ConstantNode,
    Definition,
    Equation,
    ExprStmt,
    FloatNode,
    IfNode,
    IntNode,
    Module,
    NegNode,
    NodeType,
    NotNode,
    PosNode,
    PrintNode,
    StringNode,
    SymbolNode,
    TensorNode,
)
from tensym.interpreter.diagnostics import SourceSpan
from tensym.interpreter.iterator import CodeIterator, Iterator, IterBoundary
from tensym.interpreter.lexer import tokenize_string
from tensym.interpreter.token import Token, TokenKind


class TokenEnd(Token):
    """Special token to represent end of token stream."""

    def __init__(self, end_index: int = -1):
        super().__init__(kind=TokenKind.EOI, lexeme_unicode=[], end_index=end_index)


class Parser:
    """Recursive descent parser for the tensor/mathematical language."""

    def __init__(
        self,
        tokens: Iterable[Token],
        debug_code_iter: CodeIterator,
        debug: bool = False,
    ):
        self.debug_code_iter = debug_code_iter
        self.debug = os.environ.get("TENSYM_PARSER_DEBUG_MODE", "0") == "1" or debug
        self.tokens = Iterator(list(tokens))
        self.__current_token: Optional[Token] = None
        self.advance()

    @property
    def end_of_iteration(self) -> None:
        """Advance past any NOT tokens."""
        eoi = self.__current_token == IterBoundary.EOI
        non = self.__current_token is None
        eoi_token = self.match_kind(TokenKind.EOI)
        return eoi or non or eoi_token

    @property
    def current_token(self) -> Token:
        if self.end_of_iteration:
            return TokenEnd()
        return self.__current_token

    def advance(self) -> None:
        """Move to the next token."""
        try:
            next_token = self.tokens.advance()
            if next_token == IterBoundary.EOI:
                self.__current_token = TokenEnd()
            else:
                self.__current_token = next_token
        except StopIteration:
            self.__current_token = TokenEnd()

    def peek(self, n: int = 1) -> Optional[Token]:
        """Look ahead n tokens without consuming them."""
        peeked = self.tokens.peek(n)
        if peeked == IterBoundary.EOI:
            return TokenEnd()
        return peeked

    def match_kind(self, *kinds: TokenKind, **token) -> bool:
        """Check if current token matches any of the given kinds."""
        return token.get("token", self.__current_token).kind in kinds

    def match_lexeme(self, *lexemes: str) -> bool:
        """Check if current token matches any of the given lexemes."""
        if self.__current_token is None:
            return False
        return self.__current_token.lexeme in lexemes

    def consume(self, kind: TokenKind, error_msg: str = None) -> Token:
        """Consume a token of the given kind or raise an error.
        We only compute a pretty code location when we *actually* error out, and we
        guard against zero-width/span issues for INDENT/DEDENT/etc.
        """
        if not self.match_kind(kind):
            code_loc = ""
            try:
                code_loc = self.debug_code_iter.pprint_token(self.current_token)
            except Exception:
                # Some layout tokens (INDENT/DEDENT) may have zero-width spans; fall back silently
                code_loc = ""
            if error_msg is None:
                kind_str = self.current_token.kind if self.current_token else "EOF"
                error_msg = f"Expected {kind}, got {kind_str}"
            if code_loc:
                error_msg += f"\n{code_loc}"
            raise SyntaxError(error_msg)
        token = self.current_token
        self.advance()
        return token

    def throw_error(self, message: str) -> None:
        """Raise a syntax error with the given message."""
        code_loc = self.debug_code_iter.pprint_token(self.current_token)
        full_message = f"{message}\n{code_loc}"
        raise SyntaxError(full_message)

    def get_source_span(
        self, start_token: Token, end_token: Token = None
    ) -> SourceSpan:
        """Get current source span for AST nodes."""
        if end_token is not None:
            if self.match_kind(TokenKind.EOI):
                end_token = self.peek(-1)
            return self.debug_code_iter.source_span_from_token(start_token, end_token)
        return self.debug_code_iter.source_span_from_token(start_token=start_token)

    def skip_newlines(self) -> None:
        """Skip over newline tokens."""
        while self.match_kind(TokenKind.NEWLINE, TokenKind.KW_NEWLINE):
            self.advance()

    def skip_indents(self):
        """Skip over indent tokens."""
        while self.match_kind(TokenKind.INDENT, TokenKind.DEDENT):
            self.advance()

    def parse(self) -> Module:
        """Parse tokens into a Module AST."""
        statements = []

        # Skip initial newlines
        self.skip_newlines()
        self.skip_indents()

        start_token = self.current_token
        end_token = None

        while not self.end_of_iteration:
            if self.match_kind(TokenKind.NEWLINE, TokenKind.KW_NEWLINE):
                self.advance()
                continue

            start_token = self.current_token
            stmt = self.statement()
            end_token = self.current_token

            if not self.end_of_iteration:
                if self.match_kind(TokenKind.NEWLINE):
                    self.consume(TokenKind.NEWLINE)
                elif self.match_kind(TokenKind.DEDENT):
                    self.consume(TokenKind.DEDENT)
                elif self.match_kind(TokenKind.INDENT):
                    self.consume(TokenKind.INDENT)

            if stmt:
                statements.append(stmt)

            self.skip_newlines()
            self.skip_indents()

        end_token = self.current_token if end_token is None else end_token
        source_span = self.get_source_span(start_token, end_token)
        return Module(source_span=source_span, body=statements)

    def statement(self) -> Optional[AstNode]:
        """Parse a statement."""
        if self.end_of_iteration:
            return None

        # Handle print statements
        if self.match_kind(TokenKind.KW_PRINT):
            return self.print_statement()
        elif self.match_kind(TokenKind.KW_LET):
            return self.declaration()
        elif self.match_kind(TokenKind.KW_IF):
            return self.if_statement()
        elif self.match_kind(TokenKind.KW_WHILE):
            self.throw_error("While statements are not yet implemented.")
        elif self.match_kind(TokenKind.KW_FOR):
            self.throw_error("For statements are not yet implemented.")
        # Otherwise it's an expression statement

        start_token = self.current_token
        expr = self.expression()
        end_token = self.current_token
        source_span = self.get_source_span(start_token, end_token)

        return ExprStmt(source_span, expr) if expr else None

    def print_statement(self) -> AstNode:
        """Parse print statement."""
        start_token = self.current_token
        self.consume(TokenKind.KW_PRINT)  # consume 'print'
        expr = self.expression()
        end_token = self.current_token
        source_span = self.get_source_span(start_token, end_token)
        return PrintNode(source_span, expr)

    def if_statement(self) -> IfNode:
        """Parse if/elif/else as a single IfNode with elif list + optional else body."""
        start_token = self.current_token
        self.consume(TokenKind.KW_IF)

        condition = self.boolean_expression()
        then_body = self.block()

        elifs: list[tuple[AstNode, list[AstNode]]] = []
        while self.match_kind(TokenKind.KW_ELIF):
            self.advance()
            elif_cond = self.boolean_expression()
            elif_body = self.block()
            elifs.append((elif_cond, elif_body))

        else_body: list[AstNode] | None = None
        if self.match_kind(TokenKind.KW_ELSE):
            self.advance()
            else_body = self.block()

        end_token = self.current_token
        source_span = self.get_source_span(start_token, end_token)
        return IfNode(
            source_span, condition, then_body, elifs=elifs, else_body=else_body
        )

    def block(self) -> list[AstNode]:
        """Parse a suite after ':'; either indented multi-line or single-line."""
        self.consume(TokenKind.COLON, "Expected ':' after condition")

        # Multi-line: ':' NEWLINE INDENT ... DEDENT
        if self.match_kind(TokenKind.NEWLINE, TokenKind.KW_NEWLINE):
            self.advance()
            self.consume(TokenKind.INDENT, "Expected an indented block after ':'")

            body: list[AstNode] = []
            while not self.match_kind(TokenKind.DEDENT, TokenKind.EOI):
                # Allow blank lines inside the block
                while self.match_kind(TokenKind.NEWLINE, TokenKind.KW_NEWLINE):
                    self.advance()
                if self.match_kind(TokenKind.DEDENT, TokenKind.EOI):
                    break

                stmt = self.statement()
                if stmt is not None:
                    body.append(stmt)

                # Optional newline after a statement within the block
                if self.match_kind(TokenKind.NEWLINE, TokenKind.KW_NEWLINE):
                    self.advance()

            self.consume(TokenKind.DEDENT, "Expected block to be closed by DEDENT")
            return body

        # Single-line: ':' <statement>
        stmt = self.statement()
        return [stmt] if stmt is not None else []

    def declaration(self) -> Optional[AstNode]:
        """Parse a declaration (definition or equation)."""
        start_token = self.current_token
        self.consume(TokenKind.KW_LET)

        assert self.match_kind(TokenKind.ID, TokenKind.TENSOR_ID), (
            "Expected identifier after 'let'"
        )
        if self.match_kind(TokenKind.ID):
            var = self.atom()
        else:
            var = self.tensor()

        if self.match_kind(TokenKind.ASSIGNMENT, TokenKind.COLON):
            self.advance()
            value = self.expression()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)
            return Definition(source_span, var, value)

        return self.expression()

    def expression(self) -> Optional[AstNode]:
        """Parse an expression (assignment or boolean expression)."""
        # Check for assignment tokens: (ID, =)
        start_token = self.current_token
        if self.match_kind(TokenKind.ID, TokenKind.KW_GREEK) and self.match_kind(
            TokenKind.OP_EQUATE, token=self.peek()
        ):
            assert self.match_kind(TokenKind.ID, TokenKind.KW_GREEK), (
                "Expected identifier on left side of assignment."
            )
            var_token = self.current_token
            self.advance()  # consume ID
            self.consume(TokenKind.OP_EQUATE)  # consume =
            var_expr = SymbolNode(
                self.get_source_span(start_token=var_token), var_token.lexeme
            )
            value = self.boolean_expression()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)
            assert isinstance(var_expr, (SymbolNode, TensorNode)), (
                "Left side of assignment must be a variable or tensor."
            )
            return Equation(source_span, var_expr, value)
        return self.boolean_expression()

    def boolean_expression(self) -> Optional[AstNode]:
        """Parse boolean expressions with and/or."""
        start_token = self.current_token
        left = self.comparison()

        while self.match_kind(TokenKind.OP_AND, TokenKind.OP_OR):
            # hit = True  # Unused variable
            op_token = self.current_token
            self.advance()
            right = self.comparison()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)

            if self.match_kind(TokenKind.OP_AND, token=op_token):
                left = BinaryNode(NodeType.AND, source_span, left, right)
            else:
                left = BinaryNode(NodeType.OR, source_span, left, right)

        return left

    def comparison(self) -> Optional[AstNode]:
        """Parse comparison expressions."""
        start_token = self.current_token
        left = self.arithmetic()

        while self.match_kind(
            TokenKind.OP_EQ,
            TokenKind.OP_NE,
            TokenKind.OP_LT,
            TokenKind.OP_LE,
            TokenKind.OP_GT,
            TokenKind.OP_GE,
        ):
            op_token = self.current_token
            self.advance()
            right = self.arithmetic()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)
            if self.match_kind(TokenKind.OP_EQ, token=op_token):
                left = BinaryNode(NodeType.EQEQUAL, source_span, left, right)
            elif self.match_kind(TokenKind.OP_NE, token=op_token):
                left = BinaryNode(NodeType.NOTEQUAL, source_span, left, right)
            elif self.match_kind(TokenKind.OP_LT, token=op_token):
                left = BinaryNode(NodeType.LESS, source_span, left, right)
            elif self.match_kind(TokenKind.OP_LE, token=op_token):
                left = BinaryNode(NodeType.LESSEQUAL, source_span, left, right)
            elif self.match_kind(TokenKind.OP_GT, token=op_token):
                left = BinaryNode(NodeType.GREATER, source_span, left, right)
            elif self.match_kind(TokenKind.OP_GE, token=op_token):
                left = BinaryNode(NodeType.GREATEREQUAL, source_span, left, right)
        return left

    def arithmetic(self) -> Optional[AstNode]:
        """Parse arithmetic expressions (addition and subtraction)."""
        start_token = self.current_token
        left = self.term()

        while self.match_kind(TokenKind.OP_PLUS, TokenKind.OP_MINUS):
            op_token = self.current_token
            self.advance()
            right = self.term()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)

            if self.match_kind(TokenKind.OP_PLUS, token=op_token):
                left = BinaryNode(NodeType.ADD, source_span, left, right)
            else:  # MINUS
                left = BinaryNode(NodeType.SUB, source_span, left, right)

        return left

    def term(self) -> Optional[AstNode]:
        """Parse multiplication and division."""
        start_token = self.current_token
        left = self.factor()

        while self.match_kind(TokenKind.OP_MUL, TokenKind.OP_DIV):
            op_token = self.current_token
            self.advance()
            right = self.factor()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)

            if self.match_kind(TokenKind.OP_MUL, token=op_token):
                left = BinaryNode(NodeType.MUL, source_span, left, right)
            else:  # DIV
                left = BinaryNode(NodeType.DIV, source_span, left, right)

        return left

    def factor(self) -> Optional[AstNode]:
        """Parse unary operators and powers."""
        # Handle unary operators
        start_token = self.current_token
        if self.match_kind(TokenKind.OP_PLUS):
            self.advance()
            factor = self.factor()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)
            return PosNode(source_span, factor)

        if self.match_kind(TokenKind.OP_MINUS):
            self.advance()
            factor = self.factor()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)
            return NegNode(source_span, factor)

        if self.match_kind(TokenKind.OP_NOT):
            self.advance()
            factor = self.factor()
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)
            return NotNode(source_span, factor)

        return self.power()

    def power(self) -> Optional[AstNode]:
        """Parse exponentiation."""
        start_token = self.current_token
        left = self.atom()

        if self.match_kind(
            TokenKind.OP_BXOR, TokenKind.OP_STARSTAR
        ):  # ^ or ** operator subject to change
            self.advance()
            right = self.factor()  # Right associative
            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)
            left = BinaryNode(NodeType.POW, source_span, left, right)

        return left

    def atom(self) -> Optional[AstNode]:
        """Parse atomic expressions."""
        if self.end_of_iteration:
            return None

        # Numbers
        if self.match_kind(TokenKind.INTEGER):
            token = self.current_token
            self.advance()
            return IntNode(self.get_source_span(start_token=token), token.lexeme)

        if self.match_kind(TokenKind.FLOAT):
            token = self.current_token
            self.advance()
            return FloatNode(self.get_source_span(start_token=token), token.lexeme)

        # Parenthesized expressions
        if self.match_kind(TokenKind.LPAREN):
            self.advance()
            expr = self.expression()
            self.consume(TokenKind.RPAREN, "Expected ')' after expression")
            return expr

        # Arrays
        if self.match_kind(TokenKind.LBRACKET):
            return self.array()

        # Function calls and tensors
        if self.match_kind(TokenKind.FUNC_ID):
            return self.function_call()

        if self.match_kind(TokenKind.STRING):
            token = self.current_token
            self.advance()
            return StringNode(self.get_source_span(token), token.lexeme)

        if self.match_kind(TokenKind.TENSOR_ID):
            return self.tensor()

        # LaTeX identifiers
        if self.match_kind(TokenKind.LATEX_ID):
            token = self.current_token
            self.advance()
            return SymbolNode(self.get_source_span(token), token.lexeme)

        # Regular atoms/identifiers
        if self.match_kind(TokenKind.ID):
            token = self.current_token
            self.advance()

            # Check for constants
            if token.lexeme in ["pi", "e", "oo", "infty"]:
                return ConstantNode(self.get_source_span(token), token.lexeme)

            return SymbolNode(self.get_source_span(token), token.lexeme)

        # If we can't match anything, return None
        return None

    def array(self) -> ArrayNode:
        """Parse array literals [1, 2, 3]."""
        start_token = self.current_token
        self.consume(TokenKind.LBRACKET)
        elements = []

        self.skip_newlines()
        self.skip_indents()

        if not self.match_kind(TokenKind.RBRACKET):
            elements.append(self.expression())

            while self.match_kind(TokenKind.COMMA):
                self.advance()  # consume comma

                # Skip any newlines/indents between elements
                self.skip_newlines()
                self.skip_indents()

                elements.append(self.expression())

                # Skip any newlines/indents after elements
                self.skip_newlines()
                self.skip_indents()

        end_token = self.current_token
        self.consume(TokenKind.RBRACKET, "Expected ']' after array elements")
        source_span = self.get_source_span(
            start_token, end_token
        )  # Get source span from [ to ]

        return ArrayNode(source_span, elements)

    def function_call(self) -> Call:
        """Parse function calls like sin(x)."""
        start_token = self.current_token
        func_token = self.consume(TokenKind.FUNC_ID)
        self.consume(TokenKind.LPAREN)

        args = []
        if not self.match_kind(TokenKind.RPAREN):
            args.append(self.expression())

            while self.match_kind(TokenKind.COMMA):
                self.advance()  # consume comma
                args.append(self.expression())

        end_token = self.current_token
        self.consume(TokenKind.RPAREN, "Expected ')' after function arguments")
        source_span = self.get_source_span(
            start_token, end_token
        )  # Get source span from func name to ) i.e. sin(x) from s to )
        return Call(func_token.lexeme, source_span, args)

    def tensor(self) -> TensorNode:
        """Parse tensor expressions like T_{mu nu}."""
        start_token = self.current_token
        tensor_token = self.consume(TokenKind.TENSOR_ID)
        tensor_node = TensorNode(self.get_source_span(start_token=start_token))
        tensor_node.identifier = tensor_token.lexeme

        # Parse indices
        while self.match_kind(TokenKind.UNDERSCORE, TokenKind.OP_BXOR):
            is_covariant = self.match_kind(TokenKind.UNDERSCORE)
            self.advance()  # consume _ or ^

            self.consume(TokenKind.LBRACE, "Expected '{' after tensor index marker")

            # Parse index identifiers
            while self.match_kind(
                TokenKind.ID,
                TokenKind.KW_GREEK,
            ):
                index_token = self.current_token  # consume ID or KW_GREEK
                self.advance()
                value = None

                # Check for index assignment like {mu: 0}
                if self.match_kind(TokenKind.COLON):
                    self.advance()  # consume :
                    value = self.atom()

                tensor_node.add_index(index_token.lexeme, is_covariant, value)

            end_token = self.current_token
            source_span = self.get_source_span(start_token, end_token)

            tensor_node.source_span = source_span
            self.consume(TokenKind.RBRACE, "Expected '}' after tensor indices")

        return tensor_node


def parse_string(code: str = None, *, filepath: str = None) -> Module:
    """Parse tokens into a Module AST."""
    tokens = tokenize_string(raw_code=code, filepath=filepath)
    iter = CodeIterator(raw_code=code, filepath=filepath)
    parser = Parser(tokens=tokens, debug_code_iter=iter)
    return parser.parse()


if __name__ == "__main__":
    code = """
        let Eq1 := x = g_{mu: 0}_{nu: 2}
        let g_{mu}_{nu} := [[1, 0], [0, -1]]
        print(Eq1)
        
        if x > 0:
            print("x is positive")
        elif x == 0:
            print("x is zero")
        elif x < 0:
            print("x is negative")
        else:
            print("x is non-positive")
    """
    x = parse_string(code)
    c = CodeIterator(raw_code=code)
    print(x.print_tree())
    print(c.pprint_source_span(x.source_span))

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
# ##############################################################################

import os
from typing import Iterable, List, Optional
from ..ast_nodes import (
    Module, ExprStmt, AstNode, BinaryNode, UnaryNode, ArrayNode,
    IntNode, FloatNode, SymbolNode, NegNode, PosNode, NotNode, 
    PrintNode, Definition, Call, Def, TensorNode, Infinitesimal,
    NodeType, ConstantNode
)
from ..diagnostics import SourceSpan
from tensym.interpreter.lexer import Token, TokenKind, tokenize_string
from ..iterator import Iterator, IterBoundary, CodeIterator


class Parser:
    """Recursive descent parser for the tensor/mathematical language."""
    
    def __init__(
            self,
            tokens: Iterable[Token],
            debug_code_iter: CodeIterator,
            debug: bool = False
    ):
        self.debug_code_iter = debug_code_iter
        self.debug = os.environ.get("TENSYM_PARSER_DEBUG_MODE", "0") == "1" or debug
        self.tokens = Iterator(list(tokens))
        self.current_token: Optional[Token] = None
        self.advance()
    
    def advance(self) -> None:
        """Move to the next token."""
        try:
            next_token = self.tokens.advance()
            if next_token == IterBoundary.EOI:
                self.current_token = None
            else:
                self.current_token = next_token
        except StopIteration:
            self.current_token = None

    def peek(self, n: int = 1) -> Optional[Token]:
        """Look ahead n tokens without consuming them."""
        return self.tokens.peek(n)
    
    def match_kind(self, *kinds: TokenKind) -> bool:
        """Check if current token matches any of the given kinds."""
        if self.current_token is None:
            return False
        return self.current_token.kind in kinds

    def match_lexeme(self, *lexemes: str) -> bool:
        """Check if current token matches any of the given lexemes."""
        if self.current_token is None:
            return False
        return self.current_token.lexeme in lexemes

    def consume(self, kind: TokenKind, error_msg: str = None) -> Token:
        """Consume a token of the given kind or raise an error."""
        code_loc = self.debug_code_iter.pprint_token(self.current_token)
        if not self.match_kind(kind):
            if error_msg is None:
                error_msg = f"Expected {kind}, got {self.current_token.kind if self.current_token else 'EOF'}"
            error_msg += f"\n{code_loc}"
            raise SyntaxError(error_msg)
        token = self.current_token
        self.advance()
        return token
    
    def get_source_span(self, token: 'Token' = None) -> SourceSpan:
        """Get current source span for AST nodes."""
        if token is not None:
            return self.debug_code_iter.source_span_from_token(token)
        return self.debug_code_iter.source_span_from_token(self.current_token)
    
    def skip_newlines(self) -> None:
        """Skip over newline tokens."""
        while self.match_kind(TokenKind.NEWLINE):
            self.advance()
    
    def parse(self) -> Module:
        """Parse tokens into a Module AST."""
        statements = []

        # Skip initial newlines
        self.skip_newlines()
        
        while self.current_token is not None:
            if self.match_kind(TokenKind.NEWLINE, TokenKind.DELIMITER):
                self.advance()
                continue

            stmt = self.statement()
            self.consume(TokenKind.DELIMITER)

            if stmt:
                statements.append(stmt)

            self.skip_newlines()
        
        return Module(source_span=self.get_source_span(), body=statements)
    
    def statement(self) -> Optional[AstNode]:
        """Parse a statement."""
        if self.current_token is None:
            return None

        # Handle print statements
        if self.match_kind(TokenKind.ID) and self.current_token.lexeme == "print":
            return self.print_statement()

        # Otherwise it's an expression statement
        expr = self.expression()
        return ExprStmt(self.get_source_span(), expr) if expr else None

    def print_statement(self) -> AstNode:
        """Parse print statement."""
        self.consume(TokenKind.ID)  # consume 'print'
        expr = self.expression()
        return PrintNode(self.get_source_span(), expr)

    def expression(self) -> Optional[AstNode]:
        """Parse an expression (assignment or boolean expression)."""
        # Check for assignment: ID := expr
        is_atom = self.match_kind(TokenKind.ID)
        is_tensor = self.match_kind(TokenKind.TENSOR_ID)
        if (
                self.match_kind(TokenKind.ID, TokenKind.TENSOR_ID) and
                self.peek() and self.peek().kind == TokenKind.ASSIGNMENT
        ):
            
            var_atom = self.atom()
            self.consume(TokenKind.ASSIGNMENT)
            value = self.boolean_expression()
            
            # Always treat as definition since we matched ASSIGNMENT token
            assert isinstance(var_atom, (SymbolNode, TensorNode)), "Left side of assignment must be a variable or tensor."
            return Definition(self.get_source_span(), var_atom, value)
        
        return self.boolean_expression()
    
    def boolean_expression(self) -> Optional[AstNode]:
        """Parse boolean expressions with and/or."""
        left = self.comparison()
        
        while (self.match_kind(TokenKind.ID) and
               self.current_token.lexeme in ["and", "or"]):
            op_token = self.current_token
            self.advance()
            right = self.comparison()
            
            if op_token.lexeme == "and":
                left = BinaryNode(NodeType.AND, self.get_source_span(), left, right)
            else:  # or
                left = BinaryNode(NodeType.OR, self.get_source_span(), left, right)
        
        return left
    
    def comparison(self) -> Optional[AstNode]:
        """Parse comparison expressions."""
        left = self.arithmetic()
        
        while self.match_kind(
                TokenKind.OP_EQ,
                TokenKind.OP_NE,
                TokenKind.OP_LT,
                TokenKind.OP_LE,
                TokenKind.OP_GT,
                TokenKind.OP_GE
        ):
            op_token = self.current_token
            self.advance()
            right = self.arithmetic()
            
            if op_token.kind == TokenKind.OP_EQ:
                left = BinaryNode(NodeType.EQEQUAL, self.get_source_span(), left, right)
            elif op_token.kind == TokenKind.OP_NE:
                left = BinaryNode(NodeType.NOTEQUAL, self.get_source_span(), left, right)
            elif op_token.kind == TokenKind.OP_LT:
                left = BinaryNode(NodeType.LESS, self.get_source_span(), left, right)
            elif op_token.kind == TokenKind.OP_LE:
                left = BinaryNode(NodeType.LESSEQUAL, self.get_source_span(), left, right)
            elif op_token.kind == TokenKind.OP_GT:
                left = BinaryNode(NodeType.GREATER, self.get_source_span(), left, right)
            elif op_token.kind == TokenKind.OP_GE:
                left = BinaryNode(NodeType.GREATEREQUAL, self.get_source_span(), left, right)
        return left
    
    def arithmetic(self) -> Optional[AstNode]:
        """Parse arithmetic expressions (addition and subtraction)."""
        left = self.term()
        
        while self.match_kind(TokenKind.OP_PLUS, TokenKind.OP_MINUS):
            op_token = self.current_token
            self.advance()
            right = self.term()
            
            if op_token.kind == TokenKind.OP_PLUS:
                left = BinaryNode(NodeType.ADD, self.get_source_span(), left, right)
            else:  # MINUS
                left = BinaryNode(NodeType.SUB, self.get_source_span(), left, right)
        
        return left
    
    def term(self) -> Optional[AstNode]:
        """Parse multiplication and division."""
        left = self.factor()
        
        while self.match_kind(TokenKind.OP_MUL, TokenKind.OP_DIV):
            op_token = self.current_token
            self.advance()
            right = self.factor()
            
            if op_token.kind == TokenKind.OP_MUL:
                left = BinaryNode(NodeType.MUL, self.get_source_span(), left, right)
            else:  # DIV
                left = BinaryNode(NodeType.DIV, self.get_source_span(), left, right)
        
        return left
    
    def factor(self) -> Optional[AstNode]:
        """Parse unary operators and powers."""
        # Handle unary operators
        if self.match_kind(TokenKind.OP_PLUS):
            self.advance()
            return PosNode(self.get_source_span(), self.factor())
        
        if self.match_kind(TokenKind.OP_MINUS):
            self.advance()
            return NegNode(self.get_source_span(), self.factor())
        
        if self.match_kind(TokenKind.OP_NOT):
            self.advance()
            return NotNode(self.get_source_span(), self.factor())
        
        return self.power()
    
    def power(self) -> Optional[AstNode]:
        """Parse exponentiation."""
        left = self.atom()
        
        if self.match_kind(TokenKind.OP_BXOR):  # ^ operator
            self.advance()
            right = self.factor()  # Right associative
            left = BinaryNode(NodeType.POW, self.get_source_span(), left, right)
        
        return left
    
    def atom(self) -> Optional[AstNode]:
        """Parse atomic expressions."""
        if self.current_token is None:
            return None
        
        # Numbers
        if self.match_kind(TokenKind.INTEGER):
            token = self.current_token
            self.advance()
            return IntNode(self.get_source_span(), token.lexeme)
        
        if self.match_kind(TokenKind.FLOAT):
            token = self.current_token
            self.advance()
            return FloatNode(self.get_source_span(), token.lexeme)
        
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
        
        if self.match_kind(TokenKind.TENSOR_ID):
            return self.tensor()
        
        # LaTeX identifiers
        if self.match_kind(TokenKind.LATEX_ID):
            token = self.current_token
            self.advance()
            return SymbolNode(self.get_source_span(), token.lexeme)
        
        # Regular atoms/identifiers
        if self.match_kind(TokenKind.ID):
            token = self.current_token
            self.advance()
            
            # Check for constants
            if token.lexeme in ["pi", "e", "oo", "infty"]:
                return ConstantNode(self.get_source_span(), token.lexeme)
            
            return SymbolNode(self.get_source_span(), token.lexeme)
        
        # If we can't match anything, return None
        return None
    
    def array(self) -> ArrayNode:
        """Parse array literals [1, 2, 3]."""
        self.consume(TokenKind.LBRACKET)
        elements = []
        
        self.skip_newlines()
        
        if not self.match_kind(TokenKind.RBRACKET):
            elements.append(self.expression())
            
            while self.match_kind(TokenKind.DELIMITER) and self.current_token.lexeme == ",":
                self.advance()  # consume comma
                self.skip_newlines()
                elements.append(self.expression())
                self.skip_newlines()
        
        self.consume(TokenKind.RBRACKET, "Expected ']' after array elements")
        return ArrayNode(self.get_source_span(), elements)
    
    def function_call(self) -> Call:
        """Parse function calls like sin(x)."""
        func_token = self.consume(TokenKind.FUNC_ID)
        self.consume(TokenKind.LPAREN)
        
        args = []
        if not self.match_kind(TokenKind.RPAREN):
            args.append(self.expression())
            
            while self.match_kind(TokenKind.DELIMITER) and self.current_token.lexeme == ",":
                self.advance()  # consume comma
                args.append(self.expression())
        
        self.consume(TokenKind.RPAREN, "Expected ')' after function arguments")
        return Call(func_token.lexeme, self.get_source_span(), args)
    
    def tensor(self) -> TensorNode:
        """Parse tensor expressions like T_{mu nu}."""
        tensor_token = self.consume(TokenKind.TENSOR_ID)
        tensor_node = TensorNode(self.get_source_span())
        tensor_node.identifier = tensor_token.lexeme
        
        # Parse indices
        while self.match_kind(TokenKind.UNDERSCORE, TokenKind.OP_BXOR):
            is_covariant = self.match_kind(TokenKind.UNDERSCORE)
            self.advance()  # consume _ or ^
            
            self.consume(TokenKind.LBRACE, "Expected '{' after tensor index marker")
            
            # Parse index identifiers
            while self.match_kind(TokenKind.ID):
                index_token = self.consume(TokenKind.ID)
                value = None
                
                # Check for index assignment like {mu: 0}
                if self.match_kind(TokenKind.SPECIAL_CHAR) and self.current_token.lexeme == ":":
                    self.advance()  # consume :
                    value = self.atom()
                
                tensor_node.add_index(index_token.lexeme, is_covariant, value)
            
            self.consume(TokenKind.RBRACE, "Expected '}' after tensor indices")
        
        return tensor_node


def parse_string(
        raw_code: str = None,
        *,
        filepath: str = None
) -> Module:
    """Parse tokens into a Module AST."""
    tokens = tokenize_string(raw_code=raw_code, filepath=filepath)
    iter = CodeIterator(raw_code=raw_code, filepath=filepath)
    parser = Parser(tokens=tokens, debug_code_iter=iter)
    return parser.parse()

"""Clean AST node definitions for the tensor/mathematical language parser."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

from .diagnostics import SourceSpan


class NodeType(Enum):
    """An enumeration of node types used by a parser."""

    # Binary operators
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    POW = "^"
    AND = "and"
    OR = "or"

    # Comparison operators
    EQEQUAL = "=="
    NOTEQUAL = "!="
    LESS = "<"
    LESSEQUAL = "<="
    GREATER = ">"
    GREATEREQUAL = ">="

    # Unary operators
    POS = "+"
    NEG = "-"
    NOT = "not"

    # Literals
    INT = "int"
    FLOAT = "float"
    CONSTANT = "constant"
    SYMBOL = "symbol"

    # Collections
    ARRAY = "array"

    # Control structures
    ASSIGNMENT = "="
    DEFINITION = ":="
    PRINT = "print"

    # Mathematical constructs
    TENSOR = "tensor"
    FUNCTION_CALL = "call"
    FUNCTION_DEF = "function_def"
    INFINITESIMAL = "infinitesimal"
    FACTORIAL = "factorial"
    ABSOLUTE = "absolute"

    # Statements
    EXPR_STMT = "expr_stmt"
    IF_STMT = "if_stmt"
    MODULE = "module"


######################################################################################################################
###################################################   BASE NODES   ###################################################
######################################################################################################################


class AstNode:
    """Base class for all AST nodes."""

    def __init__(
        self,
        node_type: NodeType,
        source_span: SourceSpan,
        children: List["AstNode"] = None,
    ):
        self.type = node_type
        self.source_span = source_span
        self.children = children or []
        self.parent = None

        # Set parent references
        for child in self.children:
            if isinstance(child, AstNode):
                child.parent = self

    @property
    def is_leaf(self) -> bool:
        """Check if this node has no children."""
        return len(self.children) == 0

    @property
    def is_root(self) -> bool:
        """Check if this node has no parent."""
        return self.parent is None

    def add_child(self, child: "AstNode") -> None:
        """Add a child node."""
        if isinstance(child, AstNode):
            child.parent = self
            self.children.append(child)

    def remove_child(self, child: "AstNode") -> None:
        """Remove a child node."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def get_level(self) -> int:
        """Get the depth level of this node in the tree."""
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def print_tree(self, level: int = -1) -> None:
        """Print a visual representation of the AST tree."""
        spaces = " " * self.get_level() * 3
        prefix = spaces + "|__" if self.parent else ""

        print(f"{prefix}{str(self)}")
        if level != 0:
            for child in self.children:
                if isinstance(child, AstNode):
                    child.print_tree(level - 1)

    def __repr__(self):
        return f"AstNode(type={self.type}, children={len(self.children)})"

    def __str__(self):
        return f"AstNode({self.type})"


class UnaryNode(AstNode):
    """Node with exactly one child."""

    def __init__(self, node_type: NodeType, source_span: SourceSpan, operand: AstNode):
        super().__init__(node_type, source_span, [operand])

    @property
    def operand(self) -> AstNode:
        """Get the operand of this unary operation."""
        return self.children[0]

    def __str__(self):
        return f"UnaryNode({self.type}, operand={self.operand})"

    def __repr__(self):
        return f"UnaryNode(type={self.type}, operand={self.operand})"


class BinaryNode(AstNode):
    """Node with exactly two children."""

    def __init__(
        self,
        node_type: NodeType,
        source_span: SourceSpan,
        left: AstNode,
        right: AstNode,
    ):
        super().__init__(node_type, source_span, [left, right])

    @property
    def left(self) -> AstNode:
        """Get the left operand."""
        return self.children[0]

    @property
    def right(self) -> AstNode:
        """Get the right operand."""
        return self.children[1]

    def __str__(self):
        return f"BinaryNode({self.type}, left={self.left}, right={self.right})"

    def __repr__(self):
        return f"BinaryNode(type={self.type}, left={self.left}, right={self.right})"


######################################################################################################################
##################################################   LITERAL NODES   #################################################
######################################################################################################################


class IntNode(AstNode):
    """Integer literal node."""

    def __init__(self, source_span: SourceSpan, value: str):
        super().__init__(NodeType.INT, source_span, [])
        self.value = int(value)

    @property
    def is_leaf(self) -> bool:
        return True

    def __repr__(self):
        return f"IntNode({self.value})"

    def __str__(self):
        return str(self.value)


class FloatNode(AstNode):
    """Float literal node."""

    def __init__(self, source_span: SourceSpan, value: str):
        super().__init__(NodeType.FLOAT, source_span, [])
        self.value = float(value)

    @property
    def is_leaf(self) -> bool:
        return True

    def __repr__(self):
        return f"FloatNode({self.value})"

    def __str__(self):
        return str(self.value)


class StringNode(AstNode):
    """String literal node."""

    def __init__(self, source_span: SourceSpan, value: str):
        super().__init__(NodeType.SYMBOL, source_span, [])
        self.value = value

    @property
    def is_leaf(self) -> bool:
        return True

    def __repr__(self):
        return f"StringNode({self.value})"

    def __str__(self):
        return self.value


class ConstantNode(AstNode):
    """Mathematical constant node (pi, e, etc.)."""

    def __init__(self, source_span: SourceSpan, name: str):
        super().__init__(NodeType.CONSTANT, source_span, [])
        self.name = name

    @property
    def is_leaf(self) -> bool:
        return True

    def __repr__(self):
        return f"ConstantNode({self.name})"

    def __str__(self):
        return self.name


class SymbolNode(AstNode):
    """Symbol/identifier node."""

    def __init__(self, source_span: SourceSpan, name: str):
        super().__init__(NodeType.SYMBOL, source_span, [])
        self.name = name

    @property
    def is_leaf(self) -> bool:
        return True

    def __repr__(self):
        return f"SymbolNode({self.name})"

    def __str__(self):
        return self.name


######################################################################################################################
##################################################   UNARY NODES   ###################################################
######################################################################################################################


class NegNode(UnaryNode):
    """Unary negation node."""

    def __init__(self, source_span: SourceSpan, operand: AstNode):
        super().__init__(NodeType.NEG, source_span, operand)

    def __str__(self):
        return f"-{self.operand}"

    def __repr__(self):
        return f"NegNode(operand={self.operand})"


class PosNode(UnaryNode):
    """Unary positive node."""

    def __init__(self, source_span: SourceSpan, operand: AstNode):
        super().__init__(NodeType.POS, source_span, operand)

    def __str__(self):
        return f"+{self.operand}"

    def __repr__(self):
        return f"PosNode(operand={self.operand})"


class NotNode(UnaryNode):
    """Logical not node."""

    def __init__(self, source_span: SourceSpan, operand: AstNode):
        super().__init__(NodeType.NOT, source_span, operand)

    def __str__(self):
        return f"not {self.operand}"

    def __repr__(self):
        return f"NotNode(operand={self.operand})"


class PrintNode(UnaryNode):
    """Print statement node."""

    def __init__(self, source_span: SourceSpan, expression: AstNode):
        super().__init__(NodeType.PRINT, source_span, expression)

    def __str__(self):
        return f"print({self.operand})"

    def __repr__(self):
        return f"PrintNode(expression={self.operand})"


######################################################################################################################
##################################################   COLLECTION NODES   ##############################################
######################################################################################################################


class ArrayNode(AstNode):
    """Array literal node."""

    def __init__(self, source_span: SourceSpan, elements: List[AstNode]):
        super().__init__(NodeType.ARRAY, source_span, elements)

    @property
    def elements(self) -> List[AstNode]:
        """Get the array elements."""
        return self.children

    def __repr__(self):
        return f"ArrayNode(elements={self.elements})"

    def __str__(self):
        return f"[{', '.join(str(elem) for elem in self.elements)}]"


######################################################################################################################
##################################################   ASSIGNMENT NODES   ##############################################
######################################################################################################################


class AssignmentNode(BinaryNode):
    """Assignment node (=)."""

    def __init__(self, source_span: SourceSpan, target: AstNode, value: AstNode):
        super().__init__(NodeType.ASSIGNMENT, source_span, target, value)

    @property
    def target(self) -> AstNode:
        """Get the assignment target."""
        return self.left

    @property
    def value(self) -> AstNode:
        """Get the assignment value."""
        return self.right

    def __str__(self):
        return f"{self.target} = {self.value}"

    def __repr__(self):
        return f"AssignmentNode(target={self.target}, value={self.value})"


class Definition(BinaryNode):
    """Definition node (:=)."""

    def __init__(
        self,
        source_span: SourceSpan,
        target: Union["TensorNode", "SymbolNode"],
        value: AstNode,
    ):
        # Create a symbol node for the target
        assert isinstance(target, (TensorNode, SymbolNode)), (
            "Definition target must be a TensorNode or SymbolNode"
        )
        super().__init__(NodeType.DEFINITION, source_span, target, value)

    @property
    def target_key(self) -> str:
        """Get the definition target name."""
        if isinstance(self.left, TensorNode):
            return self.left.identifier
        elif isinstance(self.left, SymbolNode):
            return self.left.name
        else:
            raise TypeError("Definition target must be a TensorNode or SymbolNode")

    @property
    def value(self) -> AstNode:
        """Get the definition value."""
        return self.right

    def __str__(self):
        return f"{self.target_key} := {self.value}"

    def __repr__(self):
        return f"Definition(target_key={self.target_key}, value={self.value})"


class Equation(BinaryNode):
    """Definition node (=) i.e. x = y as an equation."""

    def __init__(
        self,
        source_span: SourceSpan,
        target: Union["TensorNode", "SymbolNode"],
        value: AstNode,
    ):
        # Create a symbol node for the target
        assert isinstance(target, (TensorNode, SymbolNode)), (
            "Definition target must be a TensorNode or SymbolNode"
        )
        super().__init__(NodeType.DEFINITION, source_span, target, value)

    @property
    def target_key(self) -> str:
        """Get the definition target name."""
        if isinstance(self.left, TensorNode):
            return self.left.identifier
        elif isinstance(self.left, SymbolNode):
            return self.left.name
        else:
            raise TypeError("Definition target must be a TensorNode or SymbolNode")

    @property
    def value(self) -> AstNode:
        """Get the definition value."""
        return self.right

    def __str__(self):
        return f"{self.target_key} = {self.value}"


class IfNode(AstNode):
    """
    if <condition>:
        <then_body>
    elif <cond_i>:
        <elif_body_i>
    ...
    else:
        <else_body>
    """

    def __init__(
        self,
        source_span: SourceSpan,
        condition: AstNode,
        then_body: list[AstNode],
        *,
        elifs: list[tuple[AstNode, list[AstNode]]] | None = None,
        else_body: list[AstNode] | None = None,
    ):
        super().__init__(
            node_type=NodeType.IF_STMT,
            source_span=source_span,
        )
        self.condition = condition
        self.then_body = then_body
        self.elifs = elifs or []
        self.else_body = else_body

    # Optional: help generic walkers/pretty-printers
    def children(self) -> list:
        flat = [self.condition, *self.then_body]
        for cond, body in self.elifs:
            flat.append(cond)
            flat.extend(body)
        if self.else_body:
            flat.extend(self.else_body)
        return flat

    def __repr__(self) -> str:
        return (
            f"IfNode(cond={self.condition!r}, "
            f"then={len(self.then_body)} stmts, "
            f"elifs={len(self.elifs)}, "
            f"else={'1' if self.else_body else '0'})"
        )


######################################################################################################################
##################################################   FUNCTION NODES   ################################################
######################################################################################################################


class Call(AstNode):
    """Function call node."""

    def __init__(
        self, identifier: str, source_span: SourceSpan, args: List[AstNode] = None
    ):
        super().__init__(NodeType.FUNCTION_CALL, source_span, args or [])
        self.identifier = identifier

    @property
    def args(self) -> List[AstNode]:
        """Get the function arguments."""
        return self.children

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.identifier}({args_str})"

    def __repr__(self):
        return f"Call(identifier={self.identifier}, args={self.args})"


class Def(AstNode):
    """Function definition node."""

    def __init__(
        self, identifier: str, source_span: SourceSpan, args: List[str], body: AstNode
    ):
        super().__init__(NodeType.FUNCTION_DEF, source_span, [body])
        self.identifier = identifier
        self.arg_names = args
        self.body = body

    @property
    def is_leaf(self) -> bool:
        return False

    def __str__(self):
        args_str = ", ".join(self.arg_names)
        return f"def {self.identifier}({args_str}): {self.body}"

    def __repr__(self):
        return f"Def(identifier={self.identifier}, args={self.arg_names}, body={self.body})"


######################################################################################################################
##################################################   TENSOR NODES   ##################################################
######################################################################################################################


@dataclass
class TensorIndex:
    """Represents a tensor index."""

    identifier: str
    covariant: bool  # True for covariant (lower), False for contravariant (upper)
    value: Optional[AstNode] = None  # For specific index values like T_{mu=0}

    def __str__(self) -> str:
        """String representation of the tensor index."""
        symbol = "_" if self.covariant else "^"
        if self.value:
            return f"{symbol}{{{self.identifier}={self.value}}}"
        else:
            return f"{symbol}{{{self.identifier}}}"


class TensorNode(AstNode):
    """Tensor node with indices."""

    def __init__(self, source_span: SourceSpan, identifier: str = ""):
        super().__init__(NodeType.TENSOR, source_span, [])
        self.identifier = identifier
        self.indices: List[TensorIndex] = []
        self.component_ast: Optional[AstNode] = None  # For tensor definitions

    def add_index(
        self, identifier: str, covariant: bool, value: Optional[AstNode] = None
    ) -> None:
        """Add an index to this tensor."""
        self.indices.append(TensorIndex(identifier, covariant, value))

    def new_index(
        self, identifier: str, covariant: bool, value: Optional[AstNode] = None
    ) -> None:
        """Alias for add_index to match legacy interface."""
        self.add_index(identifier, covariant, value)

    @property
    def is_leaf(self) -> bool:
        return self.component_ast is None and all(
            idx.value is None for idx in self.indices
        )

    def __str__(self) -> str:
        """String representation of the tensor."""
        if not self.indices:
            return self.identifier

        indices_str = ""
        for idx in self.indices:
            symbol = "_" if idx.covariant else "^"
            if idx.value:
                indices_str += f"{symbol}{{{idx.identifier}={idx.value}}}"
            else:
                indices_str += f"{symbol}{{{idx.identifier}}}"

        return f"{self.identifier}{indices_str}"

    def __repr__(self) -> str:
        return f"TensorNode(identifier={self.identifier}, indices={self.indices})"


######################################################################################################################
##################################################   SPECIAL NODES   #################################################
######################################################################################################################


class Infinitesimal(UnaryNode):
    """Infinitesimal/differential node."""

    def __init__(self, source_span: SourceSpan, expression: AstNode):
        super().__init__(NodeType.INFINITESIMAL, source_span, expression)
        self.diff_order: int = 1
        self.is_partial: bool = False

    @property
    def expression(self) -> AstNode:
        """Get the expression being differentiated."""
        return self.operand

    def __str__(self):
        partial_str = "∂" if self.is_partial else "d"
        order_str = f"^{self.diff_order}" if self.diff_order > 1 else ""
        return f"{partial_str}{order_str}({self.expression})"

    def __repr__(self):
        return f"Infinitesimal(expression={self.expression}, diff_order={self.diff_order}, is_partial={self.is_partial})"


######################################################################################################################
##################################################   STATEMENT NODES   ###############################################
######################################################################################################################


class ExprStmt(AstNode):
    """Expression statement node."""

    def __init__(self, source_span: SourceSpan, expression: AstNode):
        super().__init__(NodeType.EXPR_STMT, source_span, [expression])

    @property
    def expr(self) -> AstNode:
        """Get the expression."""
        return self.children[0]

    def __str__(self):
        return str(self.expr)

    def __repr__(self):
        return f"ExprStmt(expression={self.expr})"


class Module(AstNode):
    """Root module node representing a complete program."""

    def __init__(self, source_span: SourceSpan, body: List[AstNode]):
        super().__init__(NodeType.MODULE, source_span, body)

    @property
    def body(self) -> List[AstNode]:
        """Get the module body statements."""
        return self.children

    def __str__(self):
        return "\n".join(str(stmt) for stmt in self.body)

    def __repr__(self):
        return f"Module(body={self.body})"

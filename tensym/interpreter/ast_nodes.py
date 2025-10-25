"""Clean AST node definitions for the tensor/mathematical language parser."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Optional

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
    MODULE = "module"


######################################################################################################################
###################################################   BASE NODES   ###################################################
######################################################################################################################

class AstNode:
    """Base class for all AST nodes."""
    
    def __init__(self, node_type: NodeType, source_span: SourceSpan, children: List["AstNode"] = None):
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
        
        if len(self.children) == 1 and hasattr(self.children[0], 'value'):
            print(f"{prefix}{self.children[0].value}")
        else:
            print(f"{prefix}{self.type.value}")
            
        if level != 0:
            for child in self.children:
                if isinstance(child, AstNode):
                    child.print_tree(level - 1)


class UnaryNode(AstNode):
    """Node with exactly one child."""
    
    def __init__(self, node_type: NodeType, source_span: SourceSpan, operand: AstNode):
        super().__init__(node_type, source_span, [operand])
    
    @property
    def operand(self) -> AstNode:
        """Get the operand of this unary operation."""
        return self.children[0]


class BinaryNode(AstNode):
    """Node with exactly two children."""
    
    def __init__(self, node_type: NodeType, source_span: SourceSpan, left: AstNode, right: AstNode):
        super().__init__(node_type, source_span, [left, right])
    
    @property
    def left(self) -> AstNode:
        """Get the left operand."""
        return self.children[0]
    
    @property
    def right(self) -> AstNode:
        """Get the right operand."""
        return self.children[1]


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


class FloatNode(AstNode):
    """Float literal node."""
    
    def __init__(self, source_span: SourceSpan, value: str):
        super().__init__(NodeType.FLOAT, source_span, [])
        self.value = float(value)
    
    @property
    def is_leaf(self) -> bool:
        return True


class ConstantNode(AstNode):
    """Mathematical constant node (pi, e, etc.)."""
    
    def __init__(self, source_span: SourceSpan, name: str):
        super().__init__(NodeType.CONSTANT, source_span, [])
        self.name = name
    
    @property
    def is_leaf(self) -> bool:
        return True


class SymbolNode(AstNode):
    """Symbol/identifier node."""
    
    def __init__(self, source_span: SourceSpan, name: str):
        super().__init__(NodeType.SYMBOL, source_span, [])
        self.name = name
    
    @property
    def is_leaf(self) -> bool:
        return True


######################################################################################################################
##################################################   UNARY NODES   ###################################################
######################################################################################################################

class NegNode(UnaryNode):
    """Unary negation node."""
    
    def __init__(self, source_span: SourceSpan, operand: AstNode):
        super().__init__(NodeType.NEG, source_span, operand)


class PosNode(UnaryNode):
    """Unary positive node."""
    
    def __init__(self, source_span: SourceSpan, operand: AstNode):
        super().__init__(NodeType.POS, source_span, operand)


class NotNode(UnaryNode):
    """Logical not node."""
    
    def __init__(self, source_span: SourceSpan, operand: AstNode):
        super().__init__(NodeType.NOT, source_span, operand)


class PrintNode(UnaryNode):
    """Print statement node."""
    
    def __init__(self, source_span: SourceSpan, expression: AstNode):
        super().__init__(NodeType.PRINT, source_span, expression)


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


class Definition(BinaryNode):
    """Definition node (:=)."""
    
    def __init__(self, source_span: SourceSpan, target: Union['TensorNode', 'SymbolNode'], value: AstNode):
        # Create a symbol node for the target
        assert isinstance(target, (TensorNode, SymbolNode)), "Definition target must be a TensorNode or SymbolNode"
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


class Equation(BinaryNode):
    """Definition node (=) i.e. x = y as an equation."""

    def __init__(self, source_span: SourceSpan, target: Union['TensorNode', 'SymbolNode'], value: AstNode):
        # Create a symbol node for the target
        assert isinstance(target, (TensorNode, SymbolNode)), "Definition target must be a TensorNode or SymbolNode"
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


######################################################################################################################
##################################################   FUNCTION NODES   ################################################
######################################################################################################################

class Call(AstNode):
    """Function call node."""
    
    def __init__(self, identifier: str, source_span: SourceSpan, args: List[AstNode] = None):
        super().__init__(NodeType.FUNCTION_CALL, source_span, args or [])
        self.identifier = identifier

    @property
    def args(self) -> List[AstNode]:
        """Get the function arguments."""
        return self.children


class Def(AstNode):
    """Function definition node."""
    
    def __init__(self, identifier: str, source_span: SourceSpan, args: List[str], body: AstNode):
        super().__init__(NodeType.FUNCTION_DEF, source_span, [body])
        self.identifier = identifier
        self.arg_names = args
        self.body = body
    
    @property
    def is_leaf(self) -> bool:
        return False


######################################################################################################################
##################################################   TENSOR NODES   ##################################################
######################################################################################################################

@dataclass
class TensorIndex:
    """Represents a tensor index."""
    identifier: str
    covariant: bool  # True for covariant (lower), False for contravariant (upper)
    value: Optional[AstNode] = None  # For specific index values like T_{mu=0}


class TensorNode(AstNode):
    """Tensor node with indices."""
    
    def __init__(self, source_span: SourceSpan, identifier: str = ""):
        super().__init__(NodeType.TENSOR, source_span, [])
        self.identifier = identifier
        self.indices: List[TensorIndex] = []
        self.component_ast: Optional[AstNode] = None  # For tensor definitions
    
    def add_index(self, identifier: str, covariant: bool, value: Optional[AstNode] = None) -> None:
        """Add an index to this tensor."""
        self.indices.append(TensorIndex(identifier, covariant, value))
    
    def new_index(self, identifier: str, covariant: bool, value: Optional[AstNode] = None) -> None:
        """Alias for add_index to match legacy interface."""
        self.add_index(identifier, covariant, value)
    
    @property
    def is_leaf(self) -> bool:
        return self.component_ast is None and all(idx.value is None for idx in self.indices)
    
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


class Module(AstNode):
    """Root module node representing a complete program."""
    
    def __init__(self, source_span: SourceSpan, body: List[AstNode]):
        super().__init__(NodeType.MODULE, source_span, body)
    
    @property
    def body(self) -> List[AstNode]:
        """Get the module body statements."""
        return self.children


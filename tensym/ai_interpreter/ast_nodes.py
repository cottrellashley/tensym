"""Typed AST node classes for tensym (minimal stubs).
"""
from dataclasses import dataclass
from typing import List, Optional, Any


class Node:
    pass


@dataclass
class Module(Node):
    body: List[Node]


@dataclass
class ExprStmt(Node):
    expr: Node


@dataclass
class Name(Node):
    id: str


@dataclass
class Assign(Node):
    target: Name
    value: Node


@dataclass
class TensorLiteral(Node):
    # Placeholder for tensor literals (e.g., matrices, arrays)
    value: Any

"""High-level IR (HIR) nodes for tensym (minimal).

HIR is a small, typed set of nodes representing tensor-aware operations
that are easier to lower to bytecode than raw AST.
"""
from dataclasses import dataclass
from typing import List, Any, Optional, Tuple


class HIRNode:
    pass


@dataclass
class Module(HIRNode):
    body: List[HIRNode]


@dataclass
class Assign(HIRNode):
    target: str
    value: HIRNode


@dataclass
class TensorRef(HIRNode):
    name: str
    indices: List[Tuple[str, int]]  # (label, variance) where variance is -1/1


@dataclass
class TensorLiteral(HIRNode):
    value: Any
    indices: List[Tuple[str, int]]


@dataclass
class TensorProduct(HIRNode):
    factors: List[HIRNode]


@dataclass
class Contract(HIRNode):
    lhs: HIRNode
    rhs: HIRNode
    pairs: List[Tuple[str, str]]  # label pairs to contract


@dataclass
class RaiseIdx(HIRNode):
    tensor: HIRNode
    labels: List[str]
    metric: Optional[str] = None


@dataclass
class LowerIdx(HIRNode):
    tensor: HIRNode
    labels: List[str]
    metric: Optional[str] = None


@dataclass
class Return(HIRNode):
    value: Optional[HIRNode]


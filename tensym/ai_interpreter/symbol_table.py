"""Compile-time symbol table for tensym.

The symbol table handles:
1. Name resolution and scoping during parsing/type checking
2. Slot allocation - mapping names to integer IDs for the VM
3. Index variance tracking and tensor type information
4. Metric/connection registry

The VM gets slot-based instructions, not string names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TensorVariance(Enum):
    COVARIANT = -1  # lower index: T_i
    CONTRAVARIANT = 1  # upper index: T^i


@dataclass
class TensorType:
    rank: int
    indices: List[Tuple[str, TensorVariance]]  # (label, variance)
    shape: Optional[Tuple[int, ...]] = None


@dataclass
class Symbol:
    name: str
    typ: Optional[TensorType] = None
    slot_id: Optional[int] = None  # VM slot allocation
    value: Optional[Any] = None
    is_metric: bool = False
    is_connection: bool = False


class SymbolTable:
    """Compile-time symbol table with VM slot allocation."""

    def __init__(self, parent: Optional["SymbolTable"] = None):
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.next_slot: int = 0 if parent is None else parent.next_slot

        # Index management
        self.dummy_counter = 0
        self.metrics: Dict[str, Symbol] = {}
        self.connections: Dict[str, Symbol] = {}

    def define(
        self,
        name: str,
        typ: Optional[TensorType] = None,
        value: Optional[Any] = None,
        is_metric: bool = False,
        is_connection: bool = False,
    ) -> Symbol:
        """Define a symbol and allocate a VM slot."""
        slot_id = self.next_slot
        self.next_slot += 1

        sym = Symbol(
            name=name,
            typ=typ,
            slot_id=slot_id,
            value=value,
            is_metric=is_metric,
            is_connection=is_connection,
        )
        self.symbols[name] = sym

        if is_metric:
            self.metrics[name] = sym
        if is_connection:
            self.connections[name] = sym

        return sym

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up symbol in current scope chain."""
        cur = self
        while cur is not None:
            if name in cur.symbols:
                return cur.symbols[name]
            cur = cur.parent
        return None

    def get_slot(self, name: str) -> Optional[int]:
        """Get VM slot ID for a name."""
        sym = self.lookup(name)
        return sym.slot_id if sym else None

    def fresh_dummy(self, prefix: str = "i") -> str:
        """Generate a fresh dummy index name."""
        name = f"{prefix}{self.dummy_counter}"
        self.dummy_counter += 1
        return name

    def push_scope(self) -> "SymbolTable":
        """Create a new nested scope."""
        return SymbolTable(parent=self)

    def get_metrics(self) -> Dict[str, Symbol]:
        """Get all metrics in scope chain."""
        metrics = {}
        cur = self
        while cur is not None:
            metrics.update(cur.metrics)
            cur = cur.parent
        return metrics

"""TensorValue wrapper for tensym VM (symbolic-first minimal implementation).

This simple wrapper holds an underlying Python object (could be a SymPy expr later)
and index metadata: a list of (label, variance) where variance is -1/1.
"""

from dataclasses import dataclass
from typing import Any, List, Tuple


@dataclass
class TensorValue:
    value: Any
    indices: List[Tuple[str, int]]  # (label, variance)

    def rank(self) -> int:
        return len(self.indices)

    def with_indices(self, indices: List[Tuple[str, int]]):
        return TensorValue(self.value, indices)

    def __repr__(self) -> str:
        return f"TensorValue(value={self.value!r}, indices={self.indices!r})"

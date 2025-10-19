"""Index system: Index objects, variance, and dummy allocator (minimal).
"""
from dataclasses import dataclass
from enum import Enum
from typing import Iterator


class Variance(Enum):
    COVARIANT = -1
    CONTRAVARIANT = 1


@dataclass(frozen=True)
class Index:
    name: str
    variance: Variance


class DummyAllocator:
    def __init__(self):
        self._counter = 0

    def fresh(self) -> Index:
        name = f"_d{self._counter}"
        self._counter += 1
        return Index(name=name, variance=Variance.COVARIANT)


# simple helper
_allocator = DummyAllocator()

def fresh_dummy() -> Index:
    return _allocator.fresh()


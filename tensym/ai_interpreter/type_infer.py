"""Minimal type inference and index analysis for tensym (placeholder).

This module provides very small helpers to compute free indices for AST/Tensor nodes.
"""
from typing import Set
from .index_system import Index


def free_indices_of_tensor(indexed_labels: list[Index]) -> Set[str]:
    """Return set of label names that are free (naive placeholder)."""
    return {idx.name for idx in indexed_labels}


class TypeError(Exception):
    pass


def ensure_compatible(*types) -> bool:
    # placeholder: always returns True
    return True


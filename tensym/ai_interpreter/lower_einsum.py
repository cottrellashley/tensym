"""Lower Einstein-sum style HIR into explicit HIR ops (Contract / Raise / Lower).

This is a minimal placeholder that currently returns the input HIR unchanged.
A real implementation would detect repeated index labels across factors and
replace implicit sums with explicit Contract/Raise/Lower nodes.
"""

from .hir import HIRNode


def lower(module: HIRNode) -> HIRNode:
    """Return a lowered HIR module. Placeholder: no-op."""
    return module

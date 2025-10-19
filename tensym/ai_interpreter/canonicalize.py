"""Canonicalization utilities: alpha-rename dummy indices and normalize term order.

This is a small placeholder implementing a trivial alpha-renamer for HIR nodes.
"""
from .hir import HIRNode, TensorRef, Contract, TensorProduct
from .ast_walker import Transformer
from .index_system import fresh_dummy


class Canonicalizer(Transformer):
    def __init__(self):
        self._map = {}

    def visit_TensorRef(self, node: TensorRef):
        # rename any dummy labels that begin with '_' using fresh_dummy
        new_indices = []
        for label, var in node.indices:
            if label.startswith("_"):
                idx = fresh_dummy()
                new_indices.append((idx.name, var))
            else:
                new_indices.append((label, var))
        node.indices = new_indices
        return node


def canonicalize(hir: HIRNode) -> HIRNode:
    c = Canonicalizer()
    return c.visit(hir)


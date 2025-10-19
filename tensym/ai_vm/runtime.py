"""Runtime implementations for tensor operations (symbolic-first placeholders).

These implementations are intentionally minimal and operate on the TensorValue
wrapper. They are placeholders to exercise the VM; real implementations should
use SymPy or another symbolic backend.
"""
from typing import Any, Tuple, List
from .values import TensorValue


class RuntimeError(Exception):
    pass


class Runtime:
    def tensor_product(self, *tensors: TensorValue) -> TensorValue:
        # naive product: combine underlying values into a tuple and concatenate indices
        vals = tuple(t.value for t in tensors)
        indices = []
        for t in tensors:
            indices.extend(t.indices)
        return TensorValue(value=vals, indices=indices)

    def contract(self, lhs: TensorValue, rhs: TensorValue, pairs: Tuple[Tuple[str, str], ...]) -> TensorValue:
        # placeholder: remove contracted labels from indices on both sides
        lhs_indices = [lbl for (lbl, v) in lhs.indices]
        rhs_indices = [lbl for (lbl, v) in rhs.indices]
        to_remove_l = set(p[0] for p in pairs)
        to_remove_r = set(p[1] for p in pairs)
        new_indices = [(lbl, v) for (lbl, v) in lhs.indices if lbl not in to_remove_l]
        new_indices += [(lbl, v) for (lbl, v) in rhs.indices if lbl not in to_remove_r]
        # value: just record that a contraction happened
        return TensorValue(value=("contract", lhs.value, rhs.value, pairs), indices=new_indices)

    def raise_idx(self, t: TensorValue, labels: Tuple[str, ...], metric_name: Any = None) -> TensorValue:
        # placeholder: flip variance sign for matching labels
        new_indices = []
        for (lbl, var) in t.indices:
            if lbl in labels:
                new_indices.append((lbl, -var))
            else:
                new_indices.append((lbl, var))
        return TensorValue(value=("raise", t.value, labels, metric_name), indices=new_indices)

    def lower_idx(self, t: TensorValue, labels: Tuple[str, ...], metric_name: Any = None) -> TensorValue:
        # placeholder: flip variance sign for matching labels (same as raise for stub)
        new_indices = []
        for (lbl, var) in t.indices:
            if lbl in labels:
                new_indices.append((lbl, -var))
            else:
                new_indices.append((lbl, var))
        return TensorValue(value=("lower", t.value, labels, metric_name), indices=new_indices)

    def simplify(self, t: TensorValue) -> TensorValue:
        # no-op simplifier
        return t


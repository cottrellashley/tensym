"""Backend abstraction protocol for tensym VM.

This protocol allows swapping between different tensor engines:
- SymPy (symbolic)
- Mathematica (via wolframclient)
- NumPy (numeric)
- Rust/C backends (via FFI)
"""

from dataclasses import dataclass
from typing import Any, Optional, Protocol, Sequence, Tuple, Union

from .values import TensorValue


@dataclass
class BackendContext:
    """Execution context for backend operations."""

    parallel: bool = True
    max_workers: Optional[int] = None
    block_size: Optional[int] = None
    precision: str = "symbolic"  # "symbolic", "float64", "arbitrary"


class Backend(Protocol):
    """Protocol that all tensor backends must implement."""

    # Construction and introspection
    def tensor(
        self,
        data: Any,
        indices: Sequence[Tuple[str, int]],
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        """Create a tensor with given data and index structure."""
        ...

    def metric(self, name: str, signature: Sequence[int]) -> TensorValue:
        """Create or retrieve a metric tensor."""
        ...

    def connection(self, name: str, metric: Optional[TensorValue] = None) -> Any:
        """Create or retrieve a connection (Christoffel symbols)."""
        ...

    # Core tensor operations
    def tensor_product(
        self, *tensors: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        """Compute tensor product of multiple tensors."""
        ...

    def contract(
        self,
        lhs: TensorValue,
        rhs: TensorValue,
        pairs: Sequence[Tuple[str, str]],
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        """Contract tensors over specified index pairs."""
        ...

    def einsum(
        self, spec: str, *tensors: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        """Einstein summation with explicit specification."""
        ...

    # Index operations
    def raise_idx(
        self,
        tensor: TensorValue,
        labels: Sequence[str],
        metric: TensorValue,
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        """Raise indices using metric."""
        ...

    def lower_idx(
        self,
        tensor: TensorValue,
        labels: Sequence[str],
        metric: TensorValue,
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        """Lower indices using metric."""
        ...

    def permute(
        self,
        tensor: TensorValue,
        new_order: Sequence[int],
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        """Permute tensor indices."""
        ...

    # Differential geometry
    def covariant_derivative(
        self,
        tensor: TensorValue,
        idx_label: str,
        connection: Any,
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        """Compute covariant derivative."""
        ...

    # Arithmetic operations
    def add(
        self, lhs: TensorValue, rhs: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        """Add tensors."""
        ...

    def subtract(
        self, lhs: TensorValue, rhs: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        """Subtract tensors."""
        ...

    def multiply(
        self,
        lhs: Union[TensorValue, float, int],
        rhs: TensorValue,
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        """Scalar-tensor or elementwise multiplication."""
        ...

    def negate(
        self, tensor: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        """Negate tensor."""
        ...

    # Simplification and optimization
    def simplify(
        self, tensor: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        """Simplify tensor expression."""
        ...

    def canonicalize(
        self, tensor: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        """Put tensor in canonical form."""
        ...


class SymPyBackend:
    """SymPy-based symbolic backend."""

    def __init__(self):
        try:
            import sympy as sp

            self.sp = sp
        except ImportError:
            raise ImportError("SymPy is required for SymPyBackend")

    def tensor(
        self,
        data: Any,
        indices: Sequence[Tuple[str, int]],
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        # For now, just wrap the data - full SymPy tensor integration later
        return TensorValue(value=data, indices=list(indices))

    def tensor_product(
        self, *tensors: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        # Combine indices and create product representation
        all_indices = []
        values = []
        for t in tensors:
            all_indices.extend(t.indices)
            values.append(t.value)

        # Use multiprocessing for large symbolic products if parallel=True
        if ctx and ctx.parallel and len(tensors) > 2:
            # Placeholder for parallel computation
            result_value = ("parallel_product", tuple(values))
        else:
            result_value = ("product", tuple(values))

        return TensorValue(value=result_value, indices=all_indices)

    def contract(
        self,
        lhs: TensorValue,
        rhs: TensorValue,
        pairs: Sequence[Tuple[str, str]],
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        # Remove contracted indices
        lhs_keep = [idx for idx in lhs.indices if idx[0] not in [p[0] for p in pairs]]
        rhs_keep = [idx for idx in rhs.indices if idx[0] not in [p[1] for p in pairs]]
        result_indices = lhs_keep + rhs_keep

        # Use parallel contraction for large tensors
        if ctx and ctx.parallel:
            result_value = ("parallel_contract", lhs.value, rhs.value, pairs)
        else:
            result_value = ("contract", lhs.value, rhs.value, pairs)

        return TensorValue(value=result_value, indices=result_indices)

    def simplify(
        self, tensor: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        # Delegate to SymPy's simplify
        if hasattr(tensor.value, "simplify"):
            simplified = tensor.value.simplify()
            return TensorValue(value=simplified, indices=tensor.indices)
        return tensor

    # Implement other required methods...
    def metric(self, name: str, signature: Sequence[int]) -> TensorValue:
        return TensorValue(
            value=f"metric_{name}", indices=[(f"{name}_i", -1), (f"{name}_j", -1)]
        )

    def connection(self, name: str, metric: Optional[TensorValue] = None) -> Any:
        return f"connection_{name}"

    def einsum(
        self, spec: str, *tensors: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        # Parse einsum spec and delegate to SymPy
        return TensorValue(
            value=("einsum", spec, [t.value for t in tensors]), indices=[]
        )

    def raise_idx(
        self,
        tensor: TensorValue,
        labels: Sequence[str],
        metric: TensorValue,
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        new_indices = []
        for lbl, var in tensor.indices:
            if lbl in labels:
                new_indices.append((lbl, -var))  # flip variance
            else:
                new_indices.append((lbl, var))
        return TensorValue(
            value=("raise", tensor.value, labels, metric.value), indices=new_indices
        )

    def lower_idx(
        self,
        tensor: TensorValue,
        labels: Sequence[str],
        metric: TensorValue,
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        new_indices = []
        for lbl, var in tensor.indices:
            if lbl in labels:
                new_indices.append((lbl, -var))  # flip variance
            else:
                new_indices.append((lbl, var))
        return TensorValue(
            value=("lower", tensor.value, labels, metric.value), indices=new_indices
        )

    def permute(
        self,
        tensor: TensorValue,
        new_order: Sequence[int],
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        reordered_indices = [tensor.indices[i] for i in new_order]
        return TensorValue(
            value=("permute", tensor.value, new_order), indices=reordered_indices
        )

    def covariant_derivative(
        self,
        tensor: TensorValue,
        idx_label: str,
        connection: Any,
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        # Add the derivative index
        new_indices = tensor.indices + [(idx_label, -1)]  # covariant derivative index
        return TensorValue(
            value=("cov_deriv", tensor.value, idx_label, connection),
            indices=new_indices,
        )

    def add(
        self, lhs: TensorValue, rhs: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        # Indices should match for addition
        return TensorValue(value=("add", lhs.value, rhs.value), indices=lhs.indices)

    def subtract(
        self, lhs: TensorValue, rhs: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        return TensorValue(value=("sub", lhs.value, rhs.value), indices=lhs.indices)

    def multiply(
        self,
        lhs: Union[TensorValue, float, int],
        rhs: TensorValue,
        ctx: Optional[BackendContext] = None,
    ) -> TensorValue:
        if isinstance(lhs, (int, float)):
            return TensorValue(
                value=("scalar_mul", lhs, rhs.value), indices=rhs.indices
            )
        else:
            # Tensor multiplication -> tensor product + contraction
            return self.tensor_product(lhs, rhs, ctx=ctx)

    def negate(
        self, tensor: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        return TensorValue(value=("neg", tensor.value), indices=tensor.indices)

    def canonicalize(
        self, tensor: TensorValue, ctx: Optional[BackendContext] = None
    ) -> TensorValue:
        # Placeholder for canonicalization
        return tensor


# Placeholder for other backends
class MathematicaBackend:
    """Mathematica backend via wolframclient."""

    def __init__(self):
        try:
            from wolframclient.evaluation import WolframLanguageSession

            self.session = WolframLanguageSession()
        except ImportError:
            raise ImportError("wolframclient is required for MathematicaBackend")

    # Implement Backend protocol methods...
    pass


class NumPyBackend:
    """NumPy-based numeric backend."""

    def __init__(self):
        try:
            import numpy as np

            self.np = np
        except ImportError:
            raise ImportError("NumPy is required for NumPyBackend")

    # Implement Backend protocol methods...
    pass

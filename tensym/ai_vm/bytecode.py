"""Bytecode definitions for tensym VM."""
from enum import IntEnum
from dataclasses import dataclass
from typing import Any, Tuple, Optional


class Op(IntEnum):
    # Memory operations (use slots, not names)
    LOAD_CONST = 0        # const_idx
    LOAD_GLOBAL = 1       # slot_id
    STORE_GLOBAL = 2      # slot_id
    LOAD_LOCAL = 3        # slot_id  
    STORE_LOCAL = 4       # slot_id
    
    # Tensor construction
    TENSOR = 5            # shape, indices metadata
    
    # Core tensor operations (backend handles parallelism)
    TENSOR_PRODUCT = 6    # n_args -> pops n tensors, pushes product
    CONTRACT = 7          # pairs: Tuple[Tuple[str,str], ...] 
    EINSUM = 8           # einsum_spec: str (e.g., "ij,jk->ik")
    
    # Index operations  
    RAISE_IDX = 9         # labels: Tuple[str, ...], metric_slot: int
    LOWER_IDX = 10        # labels: Tuple[str, ...], metric_slot: int
    PERMUTE = 11          # new_order: Tuple[int, ...]
    
    # Arithmetic
    ADD = 12
    SUB = 13
    NEG = 14
    MUL = 15              # scalar * tensor or elementwise
    DIV = 16
    
    # Differential geometry
    COV_DERIV = 17        # idx_label: str, connection_slot: Optional[int]
    
    # Control flow and functions
    CALL = 18             # fn_slot: int, nargs: int
    RETURN = 19
    
    # Optional: explicit parallelism (add later if needed)
    SPAWN_CALL = 20       # fn_slot: int, nargs: int -> returns future
    JOIN = 21             # n_futures: int -> waits and collects results


@dataclass
class ExecHint:
    """Optional execution hints for backend optimization."""
    parallel: bool = True
    max_workers: Optional[int] = None
    block_size: Optional[int] = None


@dataclass  
class Instr:
    op: Op
    args: Tuple[Any, ...] = ()
    hint: Optional[ExecHint] = None  # Optional parallelism hints


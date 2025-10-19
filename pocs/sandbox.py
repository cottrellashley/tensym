# spawn-safe, portable demo: rank-4 tensors + ProcessPoolExecutor
import os
from itertools import product
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import sympy as sp

# ---------- build some symbolic tensors ----------
def build_rank4_tensors():
    # 4D spacetime metric (Minkowski) and Kronecker delta
    g = sp.diag(-1, 1, 1, 1)      # 4x4 sympy Matrix
    delta = sp.eye(4)             # 4x4 sympy Matrix (Kronecker delta)

    shape = (4, 4, 4, 4)
    a = np.empty(shape, dtype=object)
    b = np.empty(shape, dtype=object)
    c = np.empty(shape, dtype=object)
    d = np.empty(shape, dtype=object)

    for i, j, k, l in product(range(4), repeat=4):
        # a_ijkl := g_ij * g_kl   (metric ⊗ metric)
        a[i, j, k, l] = g[i, j] * g[k, l]
        # b_ijkl := δ_{i k} * δ_{j l}   (identity-like 4th-order)
        b[i, j, k, l] = delta[i, k] * delta[j, l]
        # c, d: pure symbols to keep things interesting
        c[i, j, k, l] = sp.symbols(f"c_{i}{j}{k}{l}")
        d[i, j, k, l] = sp.symbols(f"d_{i}{j}{k}{l}")

    # Output tensor e: same shape, filled with 0 to start
    e = np.empty(shape, dtype=object)
    e.fill(sp.S.Zero)
    return {"a": a, "b": b, "c": c, "d": d}, e

# ---------- worker plumbing ----------
# We load the buffers once per worker via initializer (faster than sending every task).
_TENSORS = None

def init_worker(buffers):
    global _TENSORS
    _TENSORS = buffers

def compute_path(expr: str, target_idx: tuple[int, int, int, int]):
    """
    Evaluate an expression like:
        "a[0,0,0,0] + b[1,0,0,1] * c[0,0,1,1] - d[0,0,0,0]"
    using the rank-4 arrays in the worker's global _TENSORS.
    Returns (target_idx, sympy_value).
    """
    # VERY restricted eval: only expose tensor names; no builtins.
    env = {name: arr for name, arr in _TENSORS.items()}
    val = eval(expr, {"__builtins__": {}}, env)
    return target_idx, val

if __name__ == "__main__":
    buffers, e = build_rank4_tensors()

    # Define your "paths": (expression_string, target_index_tuple)
    paths: list[tuple[str, tuple[int, int, int, int]]] = [
        ("a[0,0,0,0] + b[1,0,0,1] * c[0,0,1,1] - d[0,0,0,0]", (0, 0, 0, 0)),
        ("a[1,1,1,1] + 2*b[1,1,1,1] + c[1,1,1,1]",             (1, 1, 1, 1)),
        ("b[2,0,2,0] * (c[2,0,2,0] - d[2,0,2,0])",             (2, 0, 2, 0)),
        ("a[3,3,0,0] - a[0,0,3,3] + d[0,3,0,3]",               (3, 3, 0, 0)),
    ]

    # You can generate these systematically from your scheduler/tiler.

    # Use 'spawn' for safety/portability; on Linux you can choose 'fork' if desired.
    ctx = mp.get_context("spawn")

    with ProcessPoolExecutor(
        max_workers=os.cpu_count(),
        mp_context=ctx,
        initializer=init_worker,
        initargs=(buffers,),
        # max_tasks_per_child=500,  # enable if you run long to curb leaks
    ) as ex:
        futures = [ex.submit(compute_path, expr, tgt) for expr, tgt in paths]
        for fut in as_completed(futures):
            tgt, val = fut.result()
            e[tgt] = val

    # Example: show the targets we filled
    for _, tgt in paths:
        print(f"e{tgt} =", e[tgt])

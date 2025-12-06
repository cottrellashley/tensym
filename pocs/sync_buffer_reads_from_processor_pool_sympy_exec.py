#!/usr/bin/env python3
from __future__ import annotations

import os
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import sympy as sp

x = sp.Symbol("x")


# ---------------------------
# Buffer builders
# ---------------------------
def make_specs_buffer(seed: int, count: int, deg: int) -> np.ndarray:
    """
    Each spec: (c, n, coeffs_tuple, y0)
      y' + c*y = q(x)*y^n,   q(x) = sum coeffs[j] * x**j
    """
    rnd = random.Random(seed)
    specs = []
    for _ in range(count):
        c = rnd.choice([-2, -1, 1, 2])
        n = rnd.choice([2, 3])
        cs = [rnd.randint(-2, 2) for _ in range(deg + 1)]
        while all(v == 0 for v in cs):
            cs = [rnd.randint(-2, 2) for _ in range(deg + 1)]
        y0 = rnd.choice([1, 2])
        specs.append((c, n, tuple(cs), y0))
    return np.array(specs, dtype=object)


def specs_to_poly(spec) -> sp.Expr:
    c, n, coeffs, y0 = spec
    return sum(sp.Integer(coeffs[j]) * x**j for j in range(len(coeffs)))


def make_exprs_buffer(specs_buf: np.ndarray) -> np.ndarray:
    exprs = [specs_to_poly(spec) for spec in specs_buf.tolist()]
    return np.array(exprs, dtype=object)


# ---------------------------
# Closed-form Bernoulli solve (no dsolve: stable + fast)
# y' + c*y = q(x)*y^n  -> v = y^(1-n) is linear
# ---------------------------
def solve_bernoulli_fast(c, qpoly, n, y0=1, x0=0):
    m = 1 - n
    mu = sp.exp(m * c * x)
    I = sp.integrate(mu * m * qpoly, x)
    C = (y0**m) * mu.subs(x, x0) - I.subs(x, x0)
    v = (C + I) / mu
    return sp.simplify(v ** sp.Rational(1, m))


# ---------------------------
# Global buffers for workers (set via initializer)
# ---------------------------
_BUF_MODE: str | None = None  # "specs" or "exprs"
_BUF: np.ndarray | None = None
_PER_TASK: int = 0


def _init_worker(buf_mode: str, buf: np.ndarray, per_task: int):
    """Called once per worker; stash buffer as read-only global."""
    global _BUF_MODE, _BUF, _PER_TASK
    _BUF_MODE, _BUF, _PER_TASK = buf_mode, buf, per_task


# Worker tasks (top-level/picklable)
def task_from_specs(k: int) -> int:
    """Read specs -> build SymPy -> compute."""
    global _BUF, _PER_TASK
    out = 0
    count = len(_BUF)
    for i in range(_PER_TASK):
        spec = _BUF[(k + i) % count]  # (c, n, coeffs, y0)
        c, n, coeffs, y0 = spec
        q = sum(sp.Integer(coeffs[j]) * x**j for j in range(len(coeffs)))
        y = solve_bernoulli_fast(c, q, n, y0=y0, x0=0)
        s = sp.series(y, x, 0, 5).removeO()
        val = int(sp.simplify(s.subs({x: sp.Rational(1, 2)})))
        deg_est = int(sp.degree(sp.together(sp.diff(s, x)), x) or 0)
        out ^= (val ^ (deg_est << (i & 15))) & 0x7FFFFFFF
    return out


def task_from_exprs(k: int) -> int:
    """Read pre-built SymPy q(x) -> compute."""
    global _BUF, _PER_TASK
    rnd = random.Random(2000 + k)  # vary c,n,y0 per sub-task
    out = 0
    count = len(_BUF)
    for i in range(_PER_TASK):
        q = _BUF[(k + 2 * i) % count]  # prebuilt polynomial
        c = rnd.choice([-2, -1, 1, 2])
        n = rnd.choice([2, 3])
        y0 = rnd.choice([1, 2])
        y = solve_bernoulli_fast(c, q, n, y0=y0, x0=0)
        s = sp.series(y, x, 0, 5).removeO()
        val = int(sp.simplify(s.subs({x: sp.Rational(1, 2)})))
        deg_est = int(sp.degree(sp.together(sp.diff(s, x)), x) or 0)
        out ^= (val ^ (deg_est << (i & 15))) & 0x7FFFFFFF
    return out


# ---------------------------
# Runners
# ---------------------------
def run_sync(
    tasks: int, buf_mode: str, buf: np.ndarray, per_task: int
) -> tuple[list[int], float]:
    global _BUF_MODE, _BUF, _PER_TASK
    _BUF_MODE, _BUF, _PER_TASK = buf_mode, buf, per_task
    work = task_from_specs if buf_mode == "specs" else task_from_exprs
    t0 = time.perf_counter()
    out = [work(k) for k in range(tasks)]
    t1 = time.perf_counter()
    return out, (t1 - t0)


def run_pool(
    tasks: int, buf_mode: str, buf: np.ndarray, per_task: int, workers: int
) -> tuple[list[int], float]:
    work = task_from_specs if buf_mode == "specs" else task_from_exprs
    t0 = time.perf_counter()
    out = [None] * tasks
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_init_worker,
        initargs=(buf_mode, buf, per_task),
    ) as pool:
        futs = {pool.submit(work, k): k for k in range(tasks)}
        for fut in as_completed(futs):
            out[futs[fut]] = fut.result()
    t1 = time.perf_counter()
    return out, (t1 - t0)


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    CPU = min(os.cpu_count() or 4, 32)
    TASKS = 8 * CPU  # many independent tasks
    COUNT = 64  # buffer length
    DEG = 4  # polynomial degree in q(x)
    PER_TASK = 8  # ODEs per task (heavier -> better amortization)

    # Prefer 'fork' where possible (Linux) for cheap read-only sharing
    try:
        import multiprocessing as mp

        if mp.get_start_method(allow_none=True) != "fork":
            mp.set_start_method("fork")
    except Exception:
        pass

    # Build buffers
    specs_buf = make_specs_buffer(seed=2025, count=COUNT, deg=DEG)
    exprs_buf = make_exprs_buffer(specs_buf)

    # Warm up a little SymPy machinery
    _BUF, _PER_TASK = specs_buf, 2
    _ = task_from_specs(0)
    _BUF = exprs_buf
    _ = task_from_exprs(0)

    # Benchmark both buffer modes
    for mode, buf in [("specs", specs_buf), ("exprs", exprs_buf)]:
        sync_res, t_sync = run_sync(TASKS, mode, buf, PER_TASK)
        pool_res, t_pool = run_pool(TASKS, mode, buf, PER_TASK, workers=CPU)
        assert (
            sync_res == pool_res
        ), f"Mismatch between sync and pool outputs for mode={mode}"
        speedup = t_sync / t_pool if t_pool > 0 else float("inf")
        print(
            f"[{mode}] CPU={CPU} tasks={TASKS} per_task={PER_TASK} deg={DEG} buf_len={COUNT}"
        )
        print(f"   sync : {t_sync:8.3f} s")
        print(f"   pool : {t_pool:8.3f} s   speedup x{speedup:0.2f}")

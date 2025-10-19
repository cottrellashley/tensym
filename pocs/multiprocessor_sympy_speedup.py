# This is a proof-of-concept script to compare synchronous vs. multiprocessing
# execution for solving many independent Bernoulli ODEs using SymPy.
# It demonstrates the use of ProcessPoolExecutor for parallelism.

from __future__ import annotations
import os, time, random
from concurrent.futures import ProcessPoolExecutor, as_completed
import sympy as sp

x = sp.Symbol('x')

def solve_bernoulli(c, qpoly, n, y0=1, x0=0):
    """Solve Bernoulli ODE: y' + c*y = q(x)*y^n via linearizing transform."""
    m  = 1 - n
    mu = sp.exp(m*c*x)
    I  = sp.integrate(mu * m * qpoly, x)
    C  = (y0**m)*mu.subs(x, x0) - I.subs(x, x0)
    v  = (C + I) / mu
    return sp.simplify(v ** sp.Rational(1, m))

def task_bernoulli_batch(k: int, per_task: int = 8, deg: int = 4) -> int:
    """Solve `per_task` Bernoulli ODEs with varying params; return small digest."""
    rnd = random.Random(1000 + k)
    out = 0
    for i in range(per_task):
        c = rnd.choice([-2,-1,1,2])
        n = rnd.choice([2,3])
        coeffs = [rnd.randint(-2,2) for _ in range(deg+1)]
        while all(c0 == 0 for c0 in coeffs):
            coeffs = [rnd.randint(-2,2) for _ in range(deg+1)]
        q = sum(sp.Integer(coeffs[j]) * x**j for j in range(deg+1))
        y  = solve_bernoulli(c, q, n, y0=rnd.choice([1,2]), x0=0)
        s  = sp.series(y, x, 0, 6).removeO()
        val = int(sp.simplify(s.subs({x: sp.Rational(1,2)})))
        deg_est = int(sp.degree(sp.together(sp.diff(s, x)), x) or 0)
        out ^= (val ^ (deg_est << (i % 16))) & 0x7fffffff
    return out

def run_sync(tasks: int, per_task: int, deg: int):
    t0 = time.perf_counter()
    out = [task_bernoulli_batch(k, per_task=per_task, deg=deg) for k in range(tasks)]
    t1 = time.perf_counter()
    return out, t1 - t0

def run_pool(tasks: int, per_task: int, deg: int, workers: int):
    t0 = time.perf_counter()
    out = [None]*tasks
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(task_bernoulli_batch,k,per_task,deg): k for k in range(tasks)}
        for fut in as_completed(futs):
            out[futs[fut]] = fut.result()
    t1 = time.perf_counter()
    return out, t1 - t0

if __name__ == "__main__":
    CPU      = min(os.cpu_count() or 4, 16)  # sensible cap
    TASKS    = 8 * CPU                        # many independent tasks
    PER_TASK = 8                              # ODEs per task
    DEG      = 4                              # polynomial degree in q(x)

    # Prefer 'fork' on Linux for cheap sharing; spawn is fine too here
    try:
        import multiprocessing as mp
        if mp.get_start_method(allow_none=True) != "fork":
            mp.set_start_method("fork")
    except Exception:
        pass

    # Warmup a few symbolic ops so caches are hot
    _ = task_bernoulli_batch(0, per_task=2, deg=3)

    sync_res, sync_t = run_sync(TASKS, PER_TASK, DEG)
    pool_res, pool_t = run_pool(TASKS, PER_TASK, DEG, workers=CPU)

    assert sync_res == pool_res, "Mismatch between sync and pool results!"
    print(f"CPU={CPU}  tasks={TASKS}  per_task={PER_TASK}  deg={DEG}")
    print(f"sync    : {sync_t:.3f} s")
    print(f"pool    : {pool_t:.3f} s   speedup x{sync_t/pool_t:.2f}")

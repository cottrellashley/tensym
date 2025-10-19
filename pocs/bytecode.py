# ======= parser + VM + scheduler (drop-in) =======
from __future__ import annotations
import os, re, multiprocessing as mp
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Tuple
import numpy as np
import sympy as sp

# ---------- IR ----------
@dataclass
class Block:
    bid: int
    target: Tuple[str, Tuple[int,int,int,int]]   # ('e', (i,j,k,l))
    instrs: List[Tuple[str, Tuple[str, ...]]]

@dataclass
class Func:
    name: str
    params: List[str]
    instrs: List[Tuple[str, Tuple[str, ...]]]

@dataclass
class Program:
    buffers: List[str]
    scalars: List[str]
    funcs: Dict[str, Func]
    blocks: List[Block]

# ---------- Parser ----------
_comment = re.compile(r";.*$")
_toksplit = re.compile(r"[,\s]+")

def parse_program(src: str) -> Program:
    # strip comments/whitespace, remove blank lines
    lines = [_comment.sub("", ln).strip() for ln in src.splitlines()]
    lines = [ln for ln in lines if ln]

    i = 0
    buffers, scalars = [], []
    funcs: Dict[str, Func] = {}
    blocks: List[Block] = []

    def parse_instrs(i: int) -> Tuple[List[Tuple[str, Tuple[str, ...]]], int]:
        instrs: List[Tuple[str, Tuple[str, ...]]] = []
        while i < len(lines):
            ln = lines[i]
            if ln.startswith(".END"):
                return instrs, i + 1  # hand back index *after* .END
            parts = _toksplit.split(ln)
            op, args = parts[0].upper(), tuple(parts[1:])
            instrs.append((op, args))
            i += 1
        raise ValueError("Missing .END for block/function")

    while i < len(lines):
        ln = lines[i]
        if ln.startswith(".PROGRAM"):
            i += 1
            continue

        if ln.startswith(".BUFFERS"):
            buffers = _toksplit.split(ln[len(".BUFFERS"):].strip())
            i += 1
            continue

        if ln.startswith(".SCALARS"):
            scalars = _toksplit.split(ln[len(".SCALARS"):].strip())
            i += 1
            continue

        if ln.startswith(".FUNC"):
            m = re.match(r"\.FUNC\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", ln)
            if not m:
                raise ValueError(f"Bad .FUNC header: {ln}")
            name = m.group(1)
            params_str = m.group(2).strip()
            params = [p.strip() for p in params_str.split(",")] if params_str else []
            i += 1  # move to first instruction line
            instrs, i = parse_instrs(i)  # i now points *after* .END
            funcs[name] = Func(name=name, params=params, instrs=instrs)
            continue

        if ln.startswith(".BLOCK"):
            m = re.match(r"\.BLOCK\s+(\d+)\s+TARGET\s+([A-Za-z_]\w*)\[(\d+),(\d+),(\d+),(\d+)\]", ln)
            if not m:
                raise ValueError(f"Bad .BLOCK header: {ln}")
            bid = int(m.group(1))
            tgt_buf = m.group(2)
            idx = tuple(int(m.group(k)) for k in range(3, 7))  # (i,j,k,l)
            i += 1  # move to first instruction
            instrs, i = parse_instrs(i)
            blocks.append(Block(bid=bid, target=(tgt_buf, idx), instrs=instrs))
            continue

        # If none matched, it's truly unexpected at top-level
        raise ValueError(f"Unknown directive: {ln}")

    return Program(buffers=buffers, scalars=scalars, funcs=dict(funcs), blocks=blocks)

# ---------- VM ----------
class VM:
    def __init__(self, tensors: Dict[str, np.ndarray], scalars: Dict[str, sp.Symbol], funcs: Dict[str, Func]):
        self.tensors = tensors
        self.scalars = scalars
        self.funcs = funcs

    def run_block(self, blk: Block) -> Tuple[Tuple[str, Tuple[int,int,int,int]], sp.Expr]:
        regs: Dict[str, sp.Expr] = {}
        def getreg(r): return regs[r]
        def setreg(r, v): regs[r] = v

        def exec_instr(op: str, args: Tuple[str,...]):
            if op == "LDELEM":
                rd, buf, i,j,k,l = args
                setreg(rd, self.tensors[buf][int(i),int(j),int(k),int(l)])
            elif op == "STORE":
                buf, i,j,k,l, rs = args
                # side effects are performed by the caller after return
                self._store = (buf, (int(i),int(j),int(k),int(l)), getreg(rs))
            elif op == "CONST":
                rd, lit = args
                v = self.scalars[lit] if lit in self.scalars else sp.Integer(lit)
                setreg(rd, v)
            elif op == "ADD":
                rd, ra, rb = args; setreg(rd, getreg(ra) + getreg(rb))
            elif op == "SUB":
                rd, ra, rb = args; setreg(rd, getreg(ra) - getreg(rb))
            elif op == "MUL":
                rd, ra, rb = args; setreg(rd, getreg(ra) * getreg(rb))
            elif op == "NEG":
                rd, ra = args; setreg(rd, -getreg(ra))
            elif op == "DERIV":
                rd, ra, sym = args; setreg(rd, sp.diff(getreg(ra), self.scalars[sym]))
            elif op == "CALL":
                rd, fname, *call_args = args
                setreg(rd, self._call_func(fname, [getreg(a) for a in call_args]))
            elif op == "RET":
                raise RuntimeError("RET not allowed at block top-level")
            else:
                raise ValueError(f"Unknown opcode: {op}")

        # run
        self._store = None
        for op, args in blk.instrs:
            exec_instr(op, args)
        if not self._store:
            raise RuntimeError("Block ended without STORE")
        return ((self._store[0], self._store[1]), self._store[2])

    def _call_func(self, name: str, argvals: List[sp.Expr]) -> sp.Expr:
        fn = self.funcs[name]
        if len(argvals) != len(fn.params):
            raise ValueError(f"CALL arity mismatch for {name}")
        regs: Dict[str, sp.Expr] = {p: v for p, v in zip(fn.params, argvals)}
        ret: sp.Expr | None = None

        for op, args in fn.instrs:
            if op == "LDELEM":
                rd, buf, i,j,k,l = args
                regs[rd] = self.tensors[buf][int(i),int(j),int(k),int(l)]
            elif op == "CONST":
                rd, lit = args
                regs[rd] = self.scalars[lit] if lit in self.scalars else sp.Integer(lit)
            elif op == "ADD":
                rd, ra, rb = args; regs[rd] = regs[ra] + regs[rb]
            elif op == "SUB":
                rd, ra, rb = args; regs[rd] = regs[ra] - regs[rb]
            elif op == "MUL":
                rd, ra, rb = args; regs[rd] = regs[ra] * regs[rb]
            elif op == "NEG":
                rd, ra = args; regs[rd] = -regs[ra]
            elif op == "DERIV":
                rd, ra, sym = args; regs[rd] = sp.diff(regs[ra], self.scalars[sym])
            elif op == "RET":
                (rret,) = args
                ret = regs[rret]
                break
            elif op == "STORE":
                raise RuntimeError("STORE not allowed inside pure function")
            elif op == "CALL":
                rd, fname, *call_args = args
                regs[rd] = self._call_func(fname, [regs[a] for a in call_args])
            else:
                raise ValueError(f"Unknown opcode in func {name}: {op}")
        if ret is None:
            raise RuntimeError(f"Function {name} returned without RET")
        return ret

# ---------- pool plumbing ----------
_GLOBAL_VM: VM | None = None
def _init_worker(tensors, scalars, funcs):
    global _GLOBAL_VM
    _GLOBAL_VM = VM(tensors=tensors, scalars=scalars, funcs=funcs)

def _exec_block_task(blk: Block):
    vm = _GLOBAL_VM
    (buf, idx), value = vm.run_block(blk)
    return buf, idx, sp.simplify(value)

# ---------- demo: making tensors/scalars (same as before) ----------
def make_demo_env():
    x = sp.Symbol("x")
    g = sp.diag(-1, 1, 1, 1)
    delta = sp.eye(4)
    shape = (4,4,4,4)
    a = np.empty(shape, dtype=object)
    b = np.empty(shape, dtype=object)
    c = np.empty(shape, dtype=object)
    d = np.empty(shape, dtype=object)
    for i in range(4):
        for j in range(4):
            for k in range(4):
                for l in range(4):
                    a[i,j,k,l] = g[i,j]*g[k,l]
                    b[i,j,k,l] = delta[i,k]*delta[j,l]
                    c[i,j,k,l] = sp.symbols(f"c_{i}{j}{k}{l}")
                    d[i,j,k,l] = sp.Function(f"d_{i}{j}{k}{l}")(x)
    e = np.empty(shape, dtype=object); e.fill(sp.S.Zero)
    return {"a":a,"b":b,"c":c,"d":d,"e":e}, {"x": x}

# ---------- run a program ----------
def run_program(program_text: str):
    prog = parse_program(program_text)
    tensors, scalars = make_demo_env()
    # expose only referenced buffers to workers (optional micro-opt)
    env_tensors = {k: tensors[k] for k in prog.buffers}
    # process pool
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(
        max_workers=os.cpu_count(),
        mp_context=ctx,
        initializer=_init_worker,
        initargs=(env_tensors, scalars, prog.funcs),
    ) as ex:
        futs = [ex.submit(_exec_block_task, blk) for blk in prog.blocks]
        for fut in as_completed(futs):
            buf, idx, val = fut.result()
            tensors[buf][idx] = val
    return tensors

if __name__ == "__main__":
    with open(r"rel.b") as f:
        text = f.read()
    print(run_program(text))


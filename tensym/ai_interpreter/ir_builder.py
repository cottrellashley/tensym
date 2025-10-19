"""IR builder: flatten HIR into bytecode Instr list + constant pool.

This is a minimal, opinionated implementation sufficient to exercise the VM.
It supports Assign, TensorRef, TensorLiteral, TensorProduct, Contract, RaiseIdx,
LowerIdx and Return HIR nodes.
"""
from typing import List, Tuple, Any, Dict
from .hir import Module, Assign, TensorRef, TensorLiteral, TensorProduct, Contract, RaiseIdx, LowerIdx, Return
from ..ai_vm.bytecode import Op, Instr


class IRProgram:
    def __init__(self):
        self.instrs: List[Instr] = []
        self.consts: List[Any] = []
        self.name_pool: Dict[str, int] = {}

    def add_const(self, value: Any) -> int:
        try:
            return self.consts.index(value)
        except ValueError:
            self.consts.append(value)
            return len(self.consts) - 1

    def name_idx(self, name: str) -> int:
        if name in self.name_pool:
            return self.name_pool[name]
        idx = len(self.name_pool)
        self.name_pool[name] = idx
        return idx


class IRBuilder:
    def build(self, module: Module) -> IRProgram:
        prog = IRProgram()
        for stmt in module.body:
            self._emit_stmt(prog, stmt)
        # implicit RETURN
        prog.instrs.append(Instr(Op.RETURN, ()))
        return prog

    def _emit_stmt(self, prog: IRProgram, node):
        if isinstance(node, Assign):
            self._emit_expr(prog, node.value)
            name_idx = prog.name_idx(node.target)
            prog.instrs.append(Instr(Op.STORE_VAR, (name_idx,)))
        else:
            # expression statement
            self._emit_expr(prog, node)

    def _emit_expr(self, prog: IRProgram, node):
        if isinstance(node, TensorLiteral):
            const_idx = prog.add_const(node.value)
            prog.instrs.append(Instr(Op.LOAD_CONST, (const_idx,)))
        elif isinstance(node, TensorRef):
            name_idx = prog.name_idx(node.name)
            prog.instrs.append(Instr(Op.LOAD_VAR, (name_idx,)))
        elif isinstance(node, TensorProduct):
            for f in node.factors:
                self._emit_expr(prog, f)
            prog.instrs.append(Instr(Op.TENSOR_PRODUCT, (len(node.factors),)))
        elif isinstance(node, Contract):
            self._emit_expr(prog, node.lhs)
            self._emit_expr(prog, node.rhs)
            prog.instrs.append(Instr(Op.CONTRACT, (tuple(node.pairs),)))
        elif isinstance(node, RaiseIdx):
            self._emit_expr(prog, node.tensor)
            prog.instrs.append(Instr(Op.RAISE_IDX, (tuple(node.labels), node.metric)))
        elif isinstance(node, LowerIdx):
            self._emit_expr(prog, node.tensor)
            prog.instrs.append(Instr(Op.LOWER_IDX, (tuple(node.labels), node.metric)))
        elif isinstance(node, Return):
            if node.value is not None:
                self._emit_expr(prog, node.value)
            prog.instrs.append(Instr(Op.RETURN, ()))
        else:
            raise NotImplementedError(f"IRBuilder: unhandled node type {type(node)}")


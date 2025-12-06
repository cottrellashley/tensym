"""VM executor for tensym - fetch-decode-execute loop."""

from typing import Any, List

from .backend import Backend, BackendContext
from .bytecode import Instr, Op
from .memory import Memory


class VMError(Exception):
    """VM runtime error."""

    pass


class Executor:
    """Tensym VM executor with pluggable backends."""

    def __init__(self, backend: Backend, constants: List[Any], max_globals: int = 1000):
        self.backend = backend
        self.memory = Memory(constants, max_globals)
        self.stack: List[Any] = []

    def run(self, code: List[Instr]) -> Any:
        """Execute a list of instructions."""
        pc = 0  # program counter

        while pc < len(code):
            instr = code[pc]
            pc += 1

            try:
                pc = self._execute_instr(instr, pc, code)
            except Exception as e:
                raise VMError(f"Error executing {instr.op.name}: {e}") from e

        # Return top of stack if available
        return self.stack.pop() if self.stack else None

    def _execute_instr(self, instr: Instr, pc: int, code: List[Instr]) -> int:
        """Execute a single instruction. Returns next PC."""
        op = instr.op
        args = instr.args
        hint = instr.hint

        # Convert hint to backend context
        ctx = None
        if hint:
            ctx = BackendContext(
                parallel=hint.parallel,
                max_workers=hint.max_workers,
                block_size=hint.block_size,
            )

        # Memory operations
        if op == Op.LOAD_CONST:
            self.stack.append(self.memory.load_const(args[0]))

        elif op == Op.LOAD_GLOBAL:
            self.stack.append(self.memory.load_global(args[0]))

        elif op == Op.STORE_GLOBAL:
            self.memory.store_global(args[0], self.stack.pop())

        elif op == Op.LOAD_LOCAL:
            self.stack.append(self.memory.load_local(args[0]))

        elif op == Op.STORE_LOCAL:
            self.memory.store_local(args[0], self.stack.pop())

        # Tensor construction
        elif op == Op.TENSOR:
            data, indices = args[0], args[1]
            tensor = self.backend.tensor(data, indices, ctx)
            self.stack.append(tensor)

        # Core tensor operations
        elif op == Op.TENSOR_PRODUCT:
            n_args = args[0]
            tensors = [self.stack.pop() for _ in range(n_args)][
                ::-1
            ]  # reverse for correct order
            result = self.backend.tensor_product(*tensors, ctx=ctx)
            self.stack.append(result)

        elif op == Op.CONTRACT:
            pairs = args[0]
            rhs = self.stack.pop()
            lhs = self.stack.pop()
            result = self.backend.contract(lhs, rhs, pairs, ctx=ctx)
            self.stack.append(result)

        elif op == Op.EINSUM:
            spec = args[0]
            n_tensors = args[1] if len(args) > 1 else 2
            tensors = [self.stack.pop() for _ in range(n_tensors)][::-1]
            result = self.backend.einsum(spec, *tensors, ctx=ctx)
            self.stack.append(result)

        # Index operations
        elif op == Op.RAISE_IDX:
            labels, metric_slot = args[0], args[1]
            tensor = self.stack.pop()
            metric = self.memory.load_global(metric_slot)
            result = self.backend.raise_idx(tensor, labels, metric, ctx=ctx)
            self.stack.append(result)

        elif op == Op.LOWER_IDX:
            labels, metric_slot = args[0], args[1]
            tensor = self.stack.pop()
            metric = self.memory.load_global(metric_slot)
            result = self.backend.lower_idx(tensor, labels, metric, ctx=ctx)
            self.stack.append(result)

        elif op == Op.PERMUTE:
            new_order = args[0]
            tensor = self.stack.pop()
            result = self.backend.permute(tensor, new_order, ctx=ctx)
            self.stack.append(result)

        # Arithmetic operations
        elif op == Op.ADD:
            rhs = self.stack.pop()
            lhs = self.stack.pop()
            result = self.backend.add(lhs, rhs, ctx=ctx)
            self.stack.append(result)

        elif op == Op.SUB:
            rhs = self.stack.pop()
            lhs = self.stack.pop()
            result = self.backend.subtract(lhs, rhs, ctx=ctx)
            self.stack.append(result)

        elif op == Op.MUL:
            rhs = self.stack.pop()
            lhs = self.stack.pop()
            result = self.backend.multiply(lhs, rhs, ctx=ctx)
            self.stack.append(result)

        elif op == Op.NEG:
            tensor = self.stack.pop()
            result = self.backend.negate(tensor, ctx=ctx)
            self.stack.append(result)

        # Differential geometry
        elif op == Op.COV_DERIV:
            idx_label, connection_slot = args[0], args[1] if len(args) > 1 else None
            tensor = self.stack.pop()
            connection = (
                self.memory.load_global(connection_slot)
                if connection_slot is not None
                else None
            )
            result = self.backend.covariant_derivative(
                tensor, idx_label, connection, ctx=ctx
            )
            self.stack.append(result)

        # Control flow
        elif op == Op.CALL:
            fn_slot, nargs = args[0], args[1]
            fn = self.memory.load_global(fn_slot)
            args_vals = [self.stack.pop() for _ in range(nargs)][::-1]

            # For built-in functions, call directly
            if callable(fn):
                result = fn(*args_vals)
                self.stack.append(result)
            else:
                raise VMError(f"Cannot call non-function: {fn}")

        elif op == Op.RETURN:
            # Return instruction - execution will end after this
            return len(code)  # Jump to end

        # Optional parallelism (future feature)
        elif op == Op.SPAWN_CALL:
            # TODO: implement async execution
            raise NotImplementedError("SPAWN_CALL not yet implemented")

        elif op == Op.JOIN:
            # TODO: implement future joining
            raise NotImplementedError("JOIN not yet implemented")

        else:
            raise VMError(f"Unknown opcode: {op}")

        return pc

    def push_frame(self, num_locals: int = 0) -> None:
        """Push a new call frame."""
        self.memory.push_frame(num_locals)

    def pop_frame(self) -> None:
        """Pop the current call frame."""
        self.memory.pop_frame()

    def get_stack_top(self) -> Any:
        """Peek at top of stack without popping."""
        return self.stack[-1] if self.stack else None

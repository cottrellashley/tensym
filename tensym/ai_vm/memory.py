"""Runtime memory management for tensym VM.

The VM operates on slot-based addressing, not string names.
All name resolution happens at compile time.
"""

from dataclasses import dataclass
from typing import Any, List


@dataclass
class CallFrame:
    """A single call frame with local slots."""

    locals: List[Any]

    def get(self, slot: int) -> Any:
        if 0 <= slot < len(self.locals):
            return self.locals[slot]
        raise IndexError(f"Invalid local slot: {slot}")

    def set(self, slot: int, value: Any) -> None:
        # Extend locals if needed
        while slot >= len(self.locals):
            self.locals.append(None)
        self.locals[slot] = value


class Memory:
    """VM runtime memory: globals, constants, call stack."""

    def __init__(self, constants: List[Any], max_globals: int = 1000):
        self.constants = constants
        self.globals = [None] * max_globals  # Pre-allocated global slots
        self.call_stack: List[CallFrame] = []

    def load_const(self, idx: int) -> Any:
        """Load from constant pool."""
        if 0 <= idx < len(self.constants):
            return self.constants[idx]
        raise IndexError(f"Invalid constant index: {idx}")

    def load_global(self, slot: int) -> Any:
        """Load from global slot."""
        if 0 <= slot < len(self.globals):
            return self.globals[slot]
        raise IndexError(f"Invalid global slot: {slot}")

    def store_global(self, slot: int, value: Any) -> None:
        """Store to global slot."""
        if 0 <= slot < len(self.globals):
            self.globals[slot] = value
        else:
            raise IndexError(f"Invalid global slot: {slot}")

    def load_local(self, slot: int) -> Any:
        """Load from current frame's local slot."""
        if not self.call_stack:
            raise RuntimeError("No active call frame")
        return self.call_stack[-1].get(slot)

    def store_local(self, slot: int, value: Any) -> None:
        """Store to current frame's local slot."""
        if not self.call_stack:
            raise RuntimeError("No active call frame")
        self.call_stack[-1].set(slot, value)

    def push_frame(self, num_locals: int = 0) -> None:
        """Push a new call frame."""
        frame = CallFrame(locals=[None] * num_locals)
        self.call_stack.append(frame)

    def pop_frame(self) -> None:
        """Pop the current call frame."""
        if not self.call_stack:
            raise RuntimeError("No active call frame to pop")
        self.call_stack.pop()

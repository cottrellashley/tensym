"""Generic visitor / traversal utilities for tensym AST/HIR.

Provides simple visitor base classes that other passes can subclass.
"""

from typing import Any


class Visitor:
    """Recursive visitor with visit_* dispatch."""

    def visit(self, node: Any):
        if node is None:
            return None
        method = getattr(self, f"visit_{type(node).__name__}", None)
        if method is not None:
            return method(node)
        return self.generic_visit(node)

    def generic_visit(self, node: Any):
        # Default: try to iterate attributes that are nodes/lists
        for attr in getattr(node, "__dict__", {}).values():
            if isinstance(attr, list):
                for item in attr:
                    self.visit(item)
            else:
                self.visit(attr)
        return node


class Transformer(Visitor):
    """Transformer that can replace nodes by returning a new node from visit_*.
    This is a simple base; real implementations may need parent/context info.
    """

    def generic_visit(self, node: Any):
        for name, attr in list(getattr(node, "__dict__", {}).items()):
            if isinstance(attr, list):
                new_list = []
                for item in attr:
                    res = self.visit(item)
                    if res is None:
                        continue
                    new_list.append(res)
                setattr(node, name, new_list)
            else:
                res = self.visit(attr)
                if res is None:
                    setattr(node, name, None)
                else:
                    setattr(node, name, res)
        return node

from typing import Protocol, Tuple, Any, Literal
from loguru import logger

try:
    import sympy
except ImportError:
    sympy = None
    logger.warning("SymPy is not installed. Symbolic backend will not be available.")

try:
    import mathematica
except ImportError:
    mathematica = None
    logger.warning("Mathematica is not installed. Mathematica backend will not be available.")

try:
    import scipy
except ImportError:
    scipy = None
    logger.warning("Mathematica is not installed. Mathematica backend will not be available.")

try:
    import numpy
except ImportError:
    numpy = None
    logger.warning("Mathematica is not installed. Mathematica backend will not be available.")


_BACKENDS = {
    'sympy': sympy,
    'mathematica': mathematica,
    'scipy': scipy,
    'numpy': numpy
}

class Backend(Protocol):
    def alloc(self, shape: Tuple[int, ...], kind: Literal["object", "numeric"]) -> Any: ...
    def read(self, buf: Any, idx: Tuple[int, ...]) -> Any: ...
    def write(self, buf: Any, idx: Tuple[int, ...], value: Any) -> None: ...
    def zero(self) -> Any: ...
    def add(self, a: Any, b: Any) -> Any: ...
    def mul(self, a: Any, b: Any) -> Any: ...
    def simplify(self, x: Any) -> Any: ...

_W_BACKEND: str = 'sympy'


"""Select the active Prosidy Darn runtime implementation.

The package imports this module to expose :func:`hello` from either the
optional Rust extension or the pure-Python fallback. Callers normally use the
public package entry point:

```python
import prosidy_darn

message = prosidy_darn.hello()
```

Importing this module probes for the optional Rust extension. Missing extension
modules fall back to Python; import errors raised from inside the extension are
re-raised.
"""

from __future__ import annotations

import importlib
import typing as typ

if typ.TYPE_CHECKING:
    import collections.abc as cabc

PACKAGE_NAME = "prosidy_darn"
RUST_MODULE_NAME = f"{PACKAGE_NAME}._{PACKAGE_NAME}_rs"
_rust_hello: cabc.Callable[[], str] | None = None
_python_hello: cabc.Callable[[], str] | None = None

try:  # pragma: no cover - Rust optional
    rust = importlib.import_module(RUST_MODULE_NAME)
    _rust_hello = typ.cast("cabc.Callable[[], str]", rust.hello)
    _HAS_RUST = True
except ModuleNotFoundError as exc:  # pragma: no cover - Python fallback
    if exc.name != RUST_MODULE_NAME:
        raise

    from .pure import hello as python_hello

    _python_hello = typ.cast("cabc.Callable[[], str]", python_hello)

    _HAS_RUST = False


def hello() -> str:
    """Return the greeting from the active runtime implementation."""
    global _python_hello

    if _HAS_RUST:
        if _rust_hello is None:
            message = "Rust runtime is marked available but no hello function is loaded"
            raise RuntimeError(message)

        return _rust_hello()

    if _python_hello is None:
        from .pure import hello as python_hello

        _python_hello = typ.cast("cabc.Callable[[], str]", python_hello)

    return _python_hello()

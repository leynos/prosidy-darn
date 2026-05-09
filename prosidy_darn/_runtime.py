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

PACKAGE_NAME = "prosidy_darn"
RUST_MODULE_NAME = f"_{PACKAGE_NAME}_rs"
_python_hello = None

try:  # pragma: no cover - Rust optional
    rust = __import__(RUST_MODULE_NAME)
    _rust_hello = rust.hello  # type: ignore[attr-defined]
    _HAS_RUST = True
except ModuleNotFoundError as exc:  # pragma: no cover - Python fallback
    if exc.name != RUST_MODULE_NAME:
        raise

    from .pure import hello as _python_hello

    _HAS_RUST = False


def hello() -> str:
    """Return the greeting from the active runtime implementation."""
    global _python_hello

    if _HAS_RUST:
        return _rust_hello()

    if _python_hello is None:
        from .pure import hello as python_hello

        _python_hello = python_hello

    return _python_hello()

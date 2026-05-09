from __future__ import annotations

PACKAGE_NAME = "prosidy_darn"
RUST_MODULE_NAME = f"_{PACKAGE_NAME}_rs"

try:  # pragma: no cover - Rust optional
    rust = __import__(RUST_MODULE_NAME)
    _rust_hello = rust.hello  # type: ignore[attr-defined]
    _HAS_RUST = True
except ModuleNotFoundError as exc:  # pragma: no cover - Python fallback
    if exc.name != RUST_MODULE_NAME:
        raise

    from .pure import hello as _python_hello

    _HAS_RUST = False
else:  # pragma: no cover - Rust optional
    from .pure import hello as _python_hello


def hello() -> str:
    """Return the greeting from the active runtime implementation."""
    if _HAS_RUST:
        return _rust_hello()

    return _python_hello()

"""Tests for the public package API."""

from __future__ import annotations

import prosidy_darn


def test_hello_uses_python_fallback() -> None:
    """Return the Python greeting when the Rust extension is unavailable."""
    assert prosidy_darn.hello() == "hello from Python"

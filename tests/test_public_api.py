"""Tests for the public package API."""

from __future__ import annotations

import builtins
import importlib
import typing as typ

import pytest

import prosidy_darn
import prosidy_darn._runtime as runtime


def test_hello_uses_python_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return the Python greeting when the Rust extension is unavailable."""
    monkeypatch.setattr(runtime, "_HAS_RUST", False)

    assert prosidy_darn.hello() == "hello from Python"


def test_runtime_import_reraises_nested_module_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preserve import errors raised from inside the optional Rust module."""
    original_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == runtime.RUST_MODULE_NAME:
            message = "No module named 'inner_missing'"
            raise ModuleNotFoundError(
                message,
                name="inner_missing",
            )

        import_function = typ.cast("typ.Any", original_import)
        return import_function(name, *args, **kwargs)

    with monkeypatch.context() as context:
        context.setattr(builtins, "__import__", fake_import)

        with pytest.raises(ModuleNotFoundError, match="inner_missing") as exc_info:
            importlib.reload(runtime)

    assert exc_info.value.name == "inner_missing"
    importlib.reload(runtime)

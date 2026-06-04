"""Tests for the public package API."""

from __future__ import annotations

import importlib

import pytest

import prosidy_darn
import prosidy_darn._runtime as runtime


class TestPublicApi:
    """Tests for the public package API."""

    def test_hello_uses_python_fallback(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Return the Python greeting when the Rust extension is unavailable."""
        monkeypatch.setattr(runtime, "_HAS_RUST", False)

        assert prosidy_darn.hello() == "hello from Python"

    def test_runtime_import_reraises_nested_module_errors(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Preserve import errors raised from inside the optional Rust module."""
        original_import_module = importlib.import_module

        def fake_import_module(name: str, package: str | None = None) -> object:
            if name == runtime.RUST_MODULE_NAME:
                message = "No module named 'inner_missing'"
                raise ModuleNotFoundError(
                    message,
                    name="inner_missing",
                )

            return original_import_module(name, package)

        with monkeypatch.context() as context:
            context.setattr(importlib, "import_module", fake_import_module)

            with pytest.raises(ModuleNotFoundError, match="inner_missing") as exc_info:
                importlib.reload(runtime)

        assert exc_info.value.name == "inner_missing"
        importlib.reload(runtime)

    def test_runtime_import_does_not_load_fallback_when_rust_loads(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Keep a broken Python fallback from breaking a working Rust runtime."""
        original_import_module = importlib.import_module

        class FakeRust:
            @staticmethod
            def hello() -> str:
                return "hello from Rust"

        def fake_import_module(name: str, package: str | None = None) -> object:
            if name == runtime.RUST_MODULE_NAME:
                return FakeRust()
            if name == "prosidy_darn.pure":
                message = "broken fallback"
                raise ModuleNotFoundError(message, name=name)

            return original_import_module(name, package)

        with monkeypatch.context() as context:
            context.setattr(importlib, "import_module", fake_import_module)
            loaded_runtime = importlib.reload(runtime)

            assert loaded_runtime.hello() == "hello from Rust"

        importlib.reload(runtime)


def test_hello_rejects_rust_flag_without_function(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail explicitly if runtime state marks Rust available without a function."""
    monkeypatch.setattr(runtime, "_HAS_RUST", True)
    monkeypatch.setattr(runtime, "_rust_hello", None)

    with pytest.raises(RuntimeError, match="no hello function is loaded"):
        runtime.hello()

"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

import importlib

import pytest

from prosidy_darn import _runtime


@pytest.fixture(autouse=True)
def _reset_runtime_state() -> None:
    """Reset prosidy_darn._runtime module-level state before each test.

    Ensures that monkeypatches or importlib.reload() calls in one test do not
    bleed into the next, which is critical when running with pytest-xdist
    parallel execution (``pytest -n auto``).
    """
    importlib.reload(_runtime)

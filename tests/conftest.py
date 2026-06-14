"""Shared pytest fixtures for the test suite.

This module provides fixtures that apply to every test in the suite. Keep
suite-wide pytest configuration here when the behaviour should be visible
without each test module importing a helper explicitly.

Fixtures
--------
``_reset_runtime_state``
    Reloads ``prosidy_darn._runtime`` before each test. The runtime module owns
    mutable module-level state, and tests that use ``monkeypatch`` or
    ``importlib.reload()`` can otherwise leak that state into later tests. The
    reload is especially important for ``pytest -n auto`` runs, where workers
    execute different test modules in parallel and must not inherit stale
    runtime initialisation.

Future fixtures or pytest configuration additions in this file should be
documented in this module docstring so suite-wide behaviour remains visible to
maintainers.
"""

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

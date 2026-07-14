"""Shared helper package for repository-level tests.

This package contains helpers for tests that validate cross-cutting repository
contracts rather than one Python function. Its current responsibility is the
maturin and PyO3 validation support used by ``tests/test_maturin_build.py``:
version-pin readers, Rust toolchain availability checks, native wheel build
orchestration, and wheel metadata normalization.

Test modules should import these helpers instead of duplicating packaging,
lockfile, or wheel-inspection logic locally. That keeps the native extension
compatibility checks consistent as the Python package and Rust workspace grow.
"""

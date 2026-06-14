"""Shared test helper package.

This package contains reusable fixtures and helper modules for tests that need
to validate repository-level contracts rather than a single Python function.
Keep cross-cutting helpers here when multiple test modules need the same file
parsing, build orchestration, or artifact inspection logic.

Test files should import helpers from this package instead of duplicating
metadata readers or wheel-inspection code locally. That keeps compatibility
checks consistent as the Python package and Rust extension workspace grow.
"""

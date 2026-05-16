# Architectural decision record (ADR) 008: Two-tier linting architecture

## Status

Accepted on 2026-05-15. Prosidy Darn uses Ruff as the primary lint tier and a
focused Pylint pass through the pinned `pylint-pypy-shim` wrapper as the second
tier.

## Date

2026-05-15.

## Context and problem statement

Prosidy Darn needs a linting architecture that is fast enough for routine local
use, strict enough to prevent avoidable code-quality drift, and aligned with
related Leynos Python projects. The `episodic` project already defines a strict
Ruff profile and a focused Pylint second tier executed through
`pylint-pypy-shim` under PyPy.

Ruff covers most linting needs quickly, but selected Pylint diagnostics still
provide useful coverage for logging calls, pattern matching, control-flow
simplification, resource handling, deprecated standard-library usage,
mutable-iteration hazards, and design thresholds. Enabling all of Pylint would
duplicate Ruff and add noisy diagnostics. Running a focused Pylint tier after
Ruff preserves the extra signal without making Pylint the primary policy engine.

## Decision drivers

- Keep local linting fast and predictable.
- Align Prosidy Darn with the lint policy used by `episodic`.
- Make Ruff the broad first-line lint gate.
- Preserve selected Pylint diagnostics that are not fully covered by Ruff.
- Keep Pylint execution reproducible through a pinned shim reference.
- Avoid enabling broad, noisy Pylint categories that would duplicate Ruff.

## Options considered

### Option A: Ruff only

This option keeps linting simple and fast, but loses selected Pylint checks
around logging, pattern matching, control-flow simplification, resource
handling, and mutable iteration.

### Option B: Ruff plus focused PyPy-backed Pylint

This option keeps Ruff as the primary gate and adds a selected Pylint pass
through a pinned `pylint-pypy-shim` wrapper. It matches `episodic` while
allowing Prosidy Darn to adapt targets to its package layout.

### Option C: Ruff plus full Pylint

This option maximizes coverage, but duplicates Ruff, increases noise, and makes
the lint gate harder to maintain.

| Topic             | Option A | Option B | Option C |
| ----------------- | -------- | -------- | -------- |
| Local speed       | High     | Medium   | Low      |
| Diagnostic signal | Medium   | High     | Medium   |
| Noise risk        | Low      | Low      | High     |
| Episodic parity   | Low      | High     | Medium   |
| Maintainability   | High     | High     | Low      |

_Table 1: Linting architecture options._

## Decision outcome / proposed direction

Choose Option B.

`make lint` runs `ruff check` first. If Ruff passes, it runs `pylint-pypy`
through `uv tool run --python pypy` using the pinned `leynos/pylint-pypy-shim`
repository reference.

The Makefile keeps the Pylint invocation configurable through:

- `PYLINT_PYTHON`;
- `PYLINT_PACKAGE_TARGETS`;
- `PYLINT_TEST_TARGETS`;
- `PYLINT_EXTRA_TARGETS`;
- `PYLINT_TARGETS`;
- `PYLINT_PYPY_SHIM_REF`;
- `PYLINT_PYPY_SHIM`;
- `PYLINT`.

The default package and test targets are `prosidy_darn` and `tests`, which
match this repository's current layout. Future Python tooling or script paths
must be added through `PYLINT_EXTRA_TARGETS` or another explicit target group
so the PyPy-backed Pylint tier expands with the repository. The Pylint
configuration in `pyproject.toml` disables all messages by default and enables
only the selected diagnostics imported from `episodic`.

## Goals and non-goals

- Goals:
  - keep `make lint` as the single local lint entrypoint;
  - preserve the `episodic` lint policy where it applies;
  - make lint-policy updates reviewable through `pyproject.toml` and the
    Makefile;
  - document the command, variables, and configuration sections for
    maintainers.
- Non-goals:
  - make Pylint the primary lint engine;
  - enable every Pylint message;
  - require developers to install Pylint into the project virtual environment;
  - copy `episodic` package-specific lint targets.

## Known risks and limitations

- The managed PyPy runtime may lag the repository's Python target. The Pylint
  pass disables `syntax-error` so the shim remains useful on files PyPy can
  parse.
- The Pylint shim pin must be updated deliberately when upstream compatibility
  work changes.
- `episodic` may evolve its lint policy. Prosidy Darn should compare changes
  before importing them rather than applying them mechanically.

## Architectural rationale

The decision separates broad lint policy from focused secondary analysis. Ruff
guards the common style, correctness, and maintainability rules quickly. Pylint
adds a smaller set of complementary checks after Ruff has already filtered the
codebase. Keeping both tiers behind `make lint` preserves one developer command
while making the architecture explicit and reproducible.

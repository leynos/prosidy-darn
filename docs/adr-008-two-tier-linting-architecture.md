# Architectural decision record (ADR) 008: Two-tier linting architecture

## Status

Accepted on 2026-05-15. Prosidy Darn uses Ruff as the primary lint tier and a
focused Pylint pass as the second tier. The Pylint pass originally ran through
the pinned `pylint-pypy-shim` wrapper; see the amendment below for the current
runner.

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

`make lint` runs `ruff check` first. If Ruff passes, it runs Pylint through
`uv tool run --managed-python --python $(PYLINT_PYTHON)` with
`--from 'pylint==$(PYLINT_VERSION)' pylint`, where `PYLINT_PYTHON` defaults to
the managed `pypy@3.12` interpreter. See the amendment below for the reason
this replaced the pinned `leynos/pylint-pypy-shim` repository reference.

The Makefile keeps the Pylint invocation configurable through:

- `PYLINT_PYTHON`;
- `PYLINT_VERSION`;
- `PYLINT_PACKAGE_TARGETS`;
- `PYLINT_TEST_TARGETS`;
- `PYLINT_EXTRA_TARGETS`;
- `PYLINT_TARGETS`;
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

- The managed PyPy runtime may lag the repository's Python target. This was
  the original rationale for disabling `syntax-error`; see the amendment below
  for the current position.
- The Pylint interpreter and version pins must be updated deliberately when
  upstream compatibility work changes.
- `episodic` may evolve its lint policy. Prosidy Darn should compare changes
  before importing them rather than applying them mechanically.

## Architectural rationale

The decision separates broad lint policy from focused secondary analysis. Ruff
guards the common style, correctness, and maintainability rules quickly. Pylint
adds a smaller set of complementary checks after Ruff has already filtered the
codebase. Keeping both tiers behind `make lint` preserves one developer command
while making the architecture explicit and reproducible.

## Amendment (2026-09-25): plain Pylint on PyPy 3.12

PyPy 8 implements Python 3.12, and uv 0.12.19 (2026-09-25) ships it as a
managed interpreter. Pylint now runs on that managed interpreter without the
shim's object-build patch, so the `pylint-pypy-shim` wrapper, and the
`PYLINT_PYPY_SHIM_REF` and `PYLINT_PYPY_SHIM` Makefile variables, are removed.
`PYLINT_PYTHON` now defaults to `pypy@3.12`, pinned to a specific PyPy minor
version rather than bare `pypy`, so a new PyPy release cannot change the parsed
grammar without a commit. A new `PYLINT_VERSION` variable (default `4.0.9`)
pins the Pylint release installed by `uv tool run --from`.

`pyproject.toml` no longer disables `syntax-error`. While disabled, any module
the PyPy runtime could not parse produced no Pylint messages at all and the
lint passed without linting it. No modules were silently skipped on PyPy 3.11
in this repository at the time of this amendment, but the change removes that
failure mode: a parse failure now fails the lint instead of passing silently.

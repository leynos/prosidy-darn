# Architectural decision record (ADR) 009: Skylos dead-code detection

## Status

Accepted on 2026-08-21. Prosidy Darn uses a separately provisioned, blocking
Skylos scan to detect dead production Python code in local and continuous
integration (CI) lint gates.

## Date

2026-08-21.

## Context and problem statement

Ruff and the focused Pylint tier cover many correctness and maintainability
issues, but neither establishes that a declared production symbol is live. The
project needs a deterministic dead-code check that runs locally and in CI
without importing benchmark logic, executing tests, contacting a cloud service,
or expanding the application dependency closure.

## Decision drivers

- Detect unused production symbols before they accumulate.
- Keep `make lint` as the one local Python quality-gate entry point.
- Make CI run the same blocking command as local development.
- Keep all false-positive suppressions small, reviewed, and explained.
- Avoid test-only references influencing production liveness.

## Options considered

### Option A: Depend on Ruff and Pylint alone

This retains the existing fast checks, but does not add a whole-program
dead-code analysis pass.

### Option B: Run Skylos as a separately provisioned production gate

This uses a release-pinned external tool against `prosidy_darn`, keeps tests
out of the liveness graph, and blocks the lint gate on unexplained findings.

### Option C: Import the Episodic benchmark suite

This would bring evaluation corpus, scoring, and retained reports into Prosidy
Darn even though they do not contribute to its production quality gate.

## Decision outcome / proposed direction

Choose Option B.

`make lint` runs Skylos after Ruff and Pylint with `--category dead_code`,
`--gate`, `--no-upload`, `--no-provenance`, and `--no-grep-verify`. CI runs the
same target. The Makefile provisions exactly Skylos 4.33.2 with Python 3.14
through `uv tool run`, so Skylos remains outwith the project development
dependencies. Skylos parses source with its runtime abstract syntax tree (AST),
and the Python 3.14 pin prevents phantom findings on newer syntax.

`make skylos-allow` reserves `SYMBOL` rather than `NAME`, which WSL supplies as
a hostname. It rejects missing and whitespace-only `SYMBOL` and `REASON` values
before invoking Skylos. Its documented allow-list update holds the ignored,
repository-local `.skylos-whitelist.lock` with `flock`, preventing concurrent
writes from losing verified exceptions.

`pyproject.toml` enables strict gate handling and contains the allow-list
configuration. A genuine finding must be removed. Prefer a typed
`[tool.skylos.dead_code.entrypoints]` rule for an implicit runtime caller. A
verified false positive may be added only when that rule cannot model the
boundary, through `make skylos-allow SYMBOL=symbol REASON="reason"`. The
allow-list starts empty.

## Consequences

- Local and CI lint runs can fail for unused production symbols that the
  existing linters do not report.
- Maintainers must investigate an implicit runtime caller before allowing a
  false positive.
- The project does not import Episodic's dead-code benchmark corpus, scorer,
  reports, or benchmark test infrastructure.
- Updating Skylos requires deliberate pin, configuration, and gate review.

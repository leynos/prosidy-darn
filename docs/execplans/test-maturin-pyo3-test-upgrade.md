# Update maturin and PyO3 Validation

This ExecPlan (execution plan) is a living document. The sections
`Constraints`, `Tolerances`, `Risks`, `Progress`, `Surprises & Discoveries`,
`Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work
proceeds.

Status: IN PROGRESS

## Purpose / big picture

Prosidy Darn already has an optional Rust runtime import path, but the
repository does not yet build or test a native extension wheel. This work adds
a minimal PyO3 extension behind that existing runtime hook, updates the package
build configuration to use maturin for native wheels, and imports the maturin
compatibility and build-test approach from `leynos/cuprum` commit
`df25f6c09e388cba1a055d167a5a88d13a8826fd` where it fits this repository.

Success is observable when the standard gates pass:

```plaintext
make check-fmt
make lint
make typecheck
make test
```

The new tests also make future maturin and PyO3 upgrades visible by checking
that maturin version pins stay synchronized and that a built wheel still has
the expected metadata, package entries, and extension layout.

## Constraints

- Keep the public Python API stable: `prosidy_darn.hello()` remains the public
  entry point and continues to fall back to Python when the Rust extension is
  absent.
- Prefer Makefile targets for gates, and capture command output with `tee` in
  `/tmp`.
- Do not run formatters, linters, typecheckers, or tests in parallel.
- Do not use `/tmp` as a build target. Temporary command logs may go there.
- Do not introduce unrelated architecture or product behaviour changes.
- Keep source files under the repository's 400-line ceiling.
- Commit only after the relevant gates have passed.

## Tolerances (exception triggers)

- Scope: stop and escalate if the implementation needs more than 16 changed
  files or more than 700 net added lines.
- Interface: stop and escalate if the public Python API must change.
- Dependencies: stop and escalate if a new dependency other than maturin, PyO3
  or the Rust build metadata required for the native extension is needed.
- Iterations: stop and escalate if the same gate still fails after three
  focused fix attempts.
- Ambiguity: stop and present options if the cuprum approach conflicts with
  Prosidy Darn's documented packaging or runtime constraints.

## Risks

- Risk: maturin may not support the exact interpreter used by local gates.
  Severity: medium.
  Likelihood: medium.
  Mitigation: keep the wheel-build test skippable when the toolchain or
  supported Python version is unavailable, while still testing pin parsing.

- Risk: switching the build backend from hatchling to maturin changes pure
  wheel behaviour.
  Severity: medium.
  Likelihood: low.
  Mitigation: build a minimal extension that uses the existing runtime fallback
  and assert wheel metadata in tests.

- Risk: CI wheel workflows may still assume pure Python packaging.
  Severity: medium.
  Likelihood: medium.
  Mitigation: update the wheel action and release notes where native wheel
  behaviour changes.

## Progress

- [x] 2026-06-05: Load requested `leta`, `python-router`, `rust-router`, and
  `hexagonal-architecture` skills.
- [x] 2026-06-05: Create a leta workspace for the repository.
- [x] 2026-06-05: Inspect the cuprum reference implementation and identify the
  reusable maturin helper and wheel snapshot tests.
- [x] 2026-06-05: Confirm the current branch is
  `test/maturin-pyo3-test-upgrade`, not the main branch.
- [ ] Add the minimal Rust/PyO3 crate and maturin package configuration.
- [ ] Add Prosidy Darn-specific maturin compatibility and build tests.
- [ ] Update documentation for native wheel build responsibilities.
- [ ] Run `make check-fmt`, `make lint`, `make typecheck`, and `make test`.
- [ ] Commit the gated changes.
- [ ] Create a draft pull request.

## Surprises & Discoveries

- The repository has the optional Rust runtime import path already, but no
  checked-in Rust crate or Cargo metadata.
- The release workflow explicitly says the project has no C or Rust
  extensions, so that documentation must change with the native extension.
- The cuprum reference pins maturin in local dev dependencies, the wheel
  workflow, and the reusable wheel action; this repository currently has no
  maturin pin.

## Decision Log

- Decision: use `prosidy_darn._prosidy_darn_rs` as the PyO3 extension module
  name.
  Rationale: `prosidy_darn._runtime.RUST_MODULE_NAME` already resolves to
  `_prosidy_darn_rs`, and maturin can place that extension under the Python
  package through `module-name = "prosidy_darn._prosidy_darn_rs"`.

- Decision: adapt cuprum's maturin helper rather than copying it verbatim.
  Rationale: cuprum's helper normalizes `cuprum`-specific entries, SBOM files,
  and workflow names; Prosidy Darn needs the same compatibility contract with
  package-specific paths and without unrelated stream backend assumptions.

- Decision: keep wheel-build tests skippable when the Rust toolchain, maturin,
  or a supported Python version is unavailable.
  Rationale: pin synchronization should always be checked, but local
  environments may reasonably lack native build support.

## Implementation Plan

First, add Cargo workspace metadata and a minimal Rust crate under `rust/` that
exports one PyO3 function, `hello`, returning the same greeting as the current
Python fallback. The crate compiles to a `cdylib` extension named
`_prosidy_darn_rs`.

Second, update `pyproject.toml` so maturin is the build backend, the dev group
contains the pinned maturin version, and `[tool.maturin]` points at the Rust
crate. Keep the Python package source in the existing repository root layout.

Third, update the build wheel action and release workflow so CI uses the same
pinned maturin version. Add tests under `tests/helpers/` and `tests/` that
read the synchronized pins, compare the installed maturin version when
available, build a native wheel when possible, and normalize wheel metadata
for stable comparison.

Fourth, update repository documentation so maintainers know that native wheel
builds exist and where the compatibility tests live.

Finally, run the required gates with `tee` logs in `/tmp`, fix any failures,
commit the gated changes, and create a draft pull request.

## Outcomes & Retrospective

Implementation is still in progress. This section will record the final gate
results, commits, pull request URL, and any lessons learned once the task is
complete.

# Prosidy Darn developers' guide

This guide is for maintainers implementing Prosidy Darn. The source of truth
for product and architecture decisions remains
[docs/prosidy-darn-technical-design.md](prosidy-darn-technical-design.md), and
the delivery order remains [docs/roadmap.md](roadmap.md).

It is also the developer-facing companion to the users' guide and records how
repository quality gates are expected to run before changes are committed.

## Local environment

Build the development environment with:

```bash
make build
```

The Makefile uses `uv` for virtual environment creation, dependency
installation, and tool execution. The repository targets Python 3.14, and the
quality gates assume the shared `uv` and Cargo caches supplied by the agent
host.

The package builds native wheels with maturin and PyO3. The Rust workspace
lives under `rust/`, and the extension crate is `rust/prosidy-darn-rs`. Keep
the maturin version synchronized across `pyproject.toml`,
`.github/workflows/build-wheels.yml`, `.github/workflows/release.yml`, and
`.github/actions/build-wheels/action.yml`; `tests/test_maturin_build.py` checks
that contract. Keep the PyO3 version in `rust/prosidy-darn-rs/Cargo.toml`
aligned with `rust/Cargo.lock`; the same test module checks that lockfile
contract and builds a native wheel when the local toolchain supports it.
When bumping maturin or PyO3, regenerate the wheel metadata snapshot with:

```bash
uv run pytest tests/test_maturin_build.py::test_maturin_wheel_build_summary \
  --snapshot-update
```

Commit the updated `tests/__snapshots__/test_maturin_build.ambr` file with the
dependency change.

## Development overview

Phase 1 establishes contracts before feature work depends on them. Keep changes
small, gated, and aligned with the roadmap task being implemented. When a task
settles a design decision, update the technical design or the relevant
Architectural Decision Record (ADR) in the same change.

User-facing behaviour belongs in [docs/users-guide.md](users-guide.md).
Maintainer-only conventions belong in this guide or in a component architecture
document once that component exists.

## Hexagonal package layout

Prosidy Darn uses hexagonal architecture: domain code sits at the centre,
application services orchestrate use cases, and adapters connect the system to
the outside world.

The planned package layout is:

- `prosidy_darn.domain.index`: Unicode source indexing and offset conversion.
- `prosidy_darn.domain.ranges`: source range types, merging, and validation.
- `prosidy_darn.domain.detectors`: prose and Markdown range detectors.
- `prosidy_darn.domain.scoring`: boundary and unit punishment rules.
- `prosidy_darn.domain.segmenter`: lattice construction and dynamic
  programming.
- `prosidy_darn.domain.ir`: cue intermediate representation (IR) dataclasses.
- `prosidy_darn.application.segment`: the `SegmentText` use case.
- `prosidy_darn.application.render`: the `RenderUnits` use case.
- `prosidy_darn.application.explain`: the `ExplainSegmentation` use case.
- `prosidy_darn.ports`: protocols for driven ports.
- `prosidy_darn.adapters.inbound.cli`: Cyclopts command definitions and
  `agent-context` generation.
- `prosidy_darn.adapters.outbound.markdown`: Markdown and plain-text parser
  adapters.
- `prosidy_darn.adapters.outbound.renderers`: JSONL, SSML, WebVTT-like, and
  vendor renderers.
- `prosidy_darn.adapters.outbound.delivery`: stdout, file, webhook, and
  feedback adapters.
- `prosidy_darn.config`: composition root and Cyclopts configuration wiring.

All dependencies point inward. `prosidy_darn.domain` and
`prosidy_darn.application` must not import from `prosidy_darn.adapters`,
Cyclopts, parser packages such as `mdast`, PyO3 extension modules, HTTP
clients, filesystem delivery code, or text-to-speech (TTS) vendor libraries.

## Ports, adapters, and composition

Ports are protocols owned by the domain or application layer. Adapters
implement those protocols. Adapters must not call each other directly; an
inbound adapter calls an application use case, and the composition root wires
that use case to the outbound adapters it needs.

`prosidy_darn.config` is the composition root. It may import adapters,
Cyclopts, and concrete port implementations because its job is wiring. Domain
and application modules must stay free of those infrastructure dependencies.

## Quality gates

Run the full default gate with:

```bash
make
```

For code changes, run the relevant gates before committing:

- `make check-fmt`: verify Python and Markdown-adjacent formatting.
- `make lint`: run the two-tier Python lint gate.
- `make typecheck`: run `ty check`.
- `make test`: run the pytest suite.

For Rust extension changes, also run:

- `cargo fmt --manifest-path rust/Cargo.toml --check`: verify Rust formatting.
- `cargo check --manifest-path rust/Cargo.toml`: typecheck the Rust workspace.
- `make lint-rust`: run Clippy and the
  [Whitaker Dylint suite](https://github.com/leynos/whitaker) over the Rust
  workspace with warnings denied. The `whitaker` wrapper must be on `PATH`;
  install it with
  `cargo install --locked whitaker-installer && whitaker-installer`.

For Markdown-only changes, run:

- `make markdownlint`: lint Markdown files and enforce Oxford spelling.
- `make nixie`: validate Mermaid diagrams.
- `git diff --check`: catch trailing whitespace and conflict markers.

### Spelling policy

Run `make spelling` to enforce en-GB-oxendict prose spelling with the pinned
Typos release. The tracked `typos.toml` is generated from the shared estate
dictionary and the narrow repository policy in `typos.local.toml`; never edit
the generated file by hand.

`make spelling-config-write` invokes the exact, commit-pinned
`typos-config-builder` CLI to refresh the untracked shared-dictionary cache
when its authority is newer and write the deterministic configuration. Use
`make spelling-config` to verify cache and generated-config drift. The builder
only parses, refreshes, merges and renders spelling policy. Harvesting, Typos
execution, phrase enforcement and Mermaid validation remain consumer-owned.

The phrase checker rejects punctuation-sensitive shared corrections such as
`hand-written` in tracked UTF-8 text. Repository exceptions belong in the
local overlay as narrow exact or full-line patterns; do not add bare accepted
words for machine interfaces or formal names.

## Two-tier linting

`make lint` uses two tiers:

1. Ruff runs first with the repository's broad lint profile.
2. Pylint runs second through the PyPy-backed
   [`pylint-pypy-shim`](https://github.com/leynos/pylint-pypy-shim) wrapper.

Run the lint gate with:

```bash
make lint
```

Ruff is the fast, comprehensive lint tier. It covers syntax hygiene, import
rules, security checks, complexity limits, docstring checks, naming,
performance warnings, pytest idioms, and Ruff-specific rules.

Pylint is the focused second tier. It is intentionally allow-listed in
`pyproject.toml`, so it catches selected diagnostics that complement Ruff
without duplicating Ruff's broader responsibility. The Pylint tier currently
focuses on logging interpolation, structural pattern matching hazards,
control-flow simplification, resource handling, deprecated standard-library
usage, mutable-iteration hazards, and selected design limits.

The lint architecture is recorded in
[ADR 008: Two-tier linting architecture](adr-008-two-tier-linting-architecture.md).

## Makefile lint variables

The lint target is controlled by these Makefile variables:

- `PYLINT_PYTHON`: the interpreter used by `uv tool run` for Pylint. The
  default is `pypy`.
- `PYLINT_PACKAGE_TARGETS`: package paths passed to Pylint. The default is
  `prosidy_darn`.
- `PYLINT_TEST_TARGETS`: test paths passed to Pylint. The default is `tests`.
- `PYLINT_EXTRA_TARGETS`: additional Python tooling or script paths that
  should enter the PyPy-backed Pylint tier as the repository grows.
- `PYLINT_TARGETS`: the complete path list passed to Pylint. By default, this
  combines package, test, and extra targets.
- `PYLINT_PYPY_SHIM_REF`: the pinned commit of the
  `leynos/pylint-pypy-shim` repository.
- `PYLINT_PYPY_SHIM`: the `git+https` package URL assembled from the pinned
  shim reference.
- `PYLINT`: the complete `uv tool run` command that invokes `pylint-pypy`.

Override `PYLINT_TARGETS` only for local diagnosis. Committed changes should
extend `PYLINT_PACKAGE_TARGETS`, `PYLINT_TEST_TARGETS`, or
`PYLINT_EXTRA_TARGETS` so new Python paths do not silently fall outside the
second lint tier.

## Episodic lint policy

Prosidy Darn imports its lint policy from
[`leynos/episodic`](https://github.com/leynos/episodic). That policy keeps Ruff
as the primary lint gate and uses a pinned PyPy-backed Pylint shim as a second
tier.

The imported policy has these local adaptations:

- `PYLINT_PACKAGE_TARGETS` and `PYLINT_TEST_TARGETS` point at `prosidy_darn`
  and `tests`, matching this repository's package and test layout.
- `PYLINT_EXTRA_TARGETS` is reserved for future Python tooling or script paths.
- Pylint remains allow-listed rather than enabling the full Pylint catalogue.
- Ruff's Python target is set to Python 3.14.
- Test files ignore selected argument-count and self-use checks that are noisy
  for pytest-style test methods.

When `episodic` changes its lint policy, update Prosidy Darn deliberately:

1. Compare the `Makefile` lint target and Pylint shim pin.
2. Compare `[tool.ruff]`, `[tool.ruff.lint]`, and nested Ruff lint sections.
3. Compare `[tool.pylint.*]` sections and message allow-lists.
4. Run the full local quality gates before committing.

## `pyproject.toml` lint configuration

The lint configuration lives in these `pyproject.toml` sections:

- `[tool.ruff]`: global Ruff settings, including line length, preview mode, and
  Python target version.
- `[tool.ruff.lint]`: selected Ruff rule families and project-level ignores.
- `[tool.ruff.lint.per-file-ignores]`: test-specific rule exceptions.
- `[tool.ruff.lint.flake8-import-conventions]`: banned `from` import sources.
- `[tool.ruff.lint.flake8-import-conventions.aliases]`: required import
  aliases for common libraries and standard-library modules.
- `[tool.ruff.lint.flake8-tidy-imports.banned-api]`: deprecated `typing.*`
  names that should be replaced with modern built-in, `collections.abc`,
  `contextlib`, `collections`, or `re` alternatives.
- `[tool.ruff.lint.pydocstyle]`: NumPy-style docstring convention.
- `[tool.ruff.lint.mccabe]`: cyclomatic-complexity threshold.
- `[tool.ruff.lint.pylint]`: Ruff's Pylint-compatible design thresholds.
- `[tool.pylint.main]`: recursive target expansion and maximum module length.
- `[tool.pylint.design]`: Pylint design thresholds for arguments, locals,
  statements, and positional arguments.
- `[tool.pylint."messages control"]`: the focused Pylint allow-list.

Keep comments in the lint sections close to the rule or threshold they explain.
This makes future imports from `episodic` easier to review and keeps policy
changes auditable.

## Testing expectations by phase

ADR-006 scopes the test matrix by phase. Phase 1 uses `pytest` for public
import tests, developer documentation checks, and ADR link validation. Later
phases add the remaining tools when their product surfaces exist:

- `pytest-bdd` owns behavioural scenarios for command-line interface (CLI)
  workflows, renderer contracts, profile precedence, and delivery schemes.
- `syrupy` owns stable snapshots for `agent-context`, explanation output, JSONL
  cue sheets, SSML fragments, and human Rich output.
- Hypothesis or a bounded checker owns invariants over generated inputs,
  states, orderings, or transitions.

When a future adapter crosses an inference-service or model-facing boundary,
use Vidai Mock for behavioural tests. Cover deterministic success, malformed
responses, timeouts, and provider-style failure payloads before relying on a
real service.

## Documentation update rules

Update documentation in the same change that introduces or changes a contract:

- Update [docs/users-guide.md](users-guide.md) for user-visible library,
  command-line, configuration, or output behaviour.
- Update
  [docs/prosidy-darn-technical-design.md](prosidy-darn-technical-design.md)
  when architecture, public contracts, or design rationale changes.
- Add or update an ADR when a decision constrains future implementation.
- Add component architecture documentation when internal interfaces or
  conventions outgrow this guide.

## ADR locations

Phase 1 decisions use these stable ADR locations:

- [docs/adr-001-markdown-parser-boundary.md](adr-001-markdown-parser-boundary.md)
- [docs/adr-002-tokenizer-and-semantic-scoring-policy.md](adr-002-tokenizer-and-semantic-scoring-policy.md)
- [docs/adr-003-profile-rule-expression-policy.md](adr-003-profile-rule-expression-policy.md)
- [docs/adr-004-import-boundary-fitness-check.md](adr-004-import-boundary-fitness-check.md)

Accepted scope constraints already exist:

- [docs/adr-006-test-matrix-phase-scope.md](adr-006-test-matrix-phase-scope.md)
- [docs/adr-007-cli-observability-scope.md](adr-007-cli-observability-scope.md)
- [docs/adr-008-two-tier-linting-architecture.md](adr-008-two-tier-linting-architecture.md)

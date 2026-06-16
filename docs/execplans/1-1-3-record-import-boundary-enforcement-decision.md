# Record the import-boundary enforcement decision

This ExecPlan (execution plan) is a living document. The sections `Constraints`,
`Tolerances`, `Risks`, `Progress`, `Surprises & Discoveries`, `Decision Log`,
and `Outcomes & Retrospective` must be kept up to date as work proceeds. Each
revision must remain self-contained.

Status: DRAFT

## Purpose / big picture

Roadmap task 1.1.3 closes the import-boundary blocking decision for Prosidy
Darn: v1 must name the continuous-integration (CI) fitness function that
prevents `prosidy_darn.domain` and `prosidy_darn.application` from importing
adapters, Cyclopts, parser packages, renderer infrastructure, or delivery code.
The decision matters because the hexagonal dependency rule is cheap to enforce
before adapters exist and expensive to retrofit afterwards. Once the CLI,
parser adapters, and renderers depend on a chosen tool's configuration shape,
swapping it becomes a cross-cutting change.

A "fitness function", in the sense of Ford, Parsons, and Kua's _Building
Evolutionary Architectures_, is an automated check that holds an architectural
characteristic true as the system evolves. For Prosidy Darn the characteristic
is the hexagonal dependency rule (Cockburn's ports and adapters; Martin's
Dependency Rule): all source dependencies point inward, so the pure domain and
the application layer never name an adapter, a framework, or a vendor library.

The repository already contains a stub
`docs/adr-004-import-boundary-fitness-check.md` whose status is "Proposed" and
whose decision outcome is "Pending". This plan therefore finalises and closes
an existing decision rather than creating a new ADR file. The chosen tool is
`leynos/hecate`, a purpose-built df12 hexagonal-architecture checker, with the
mature PyPI package `import-linter` named as the pre-vetted fallback.

Unlike roadmap tasks 1.1.1 and 1.1.2, which were documentation-only, task 1.1.3
carries an executable success criterion: "the chosen check can fail a boundary
violation in a minimal fixture branch". A prose ADR cannot satisfy a criterion
whose verb is "fail". This plan therefore also adds a durable, re-runnable
demonstration: a self-contained architecture fixture plus a pytest test that
runs the selected checker and proves it reports a violation (exit status 1) on
a dirty fixture and passes (exit status 0) on a clean one.
`docs/adr-006-test-matrix-phase-scope.md` already scopes "import-boundary
checks" into Phase 1 tests, so this demonstration is in already-accepted scope.

After this plan is approved and implemented, a maintainer can observe success
by reading the accepted ADR-004, seeing roadmap item 1.1.3 marked done, running
the documentation and Python quality gates without failures, and watching the
new fixture test prove that the selected checker fails a deliberate
domain-to-adapter import while passing a clean fixture.

The implementation carried out from this plan must not create the real
`prosidy_darn.domain`, `prosidy_darn.application`, `prosidy_darn.ports`,
`prosidy_darn.adapters`, or `prosidy_darn.config` packages; must not add
Cyclopts, Rich, or the checker to `pyproject.toml`; and must not wire the
checker into `make lint` or `make all` against real source. Those are the
distinct jobs of roadmap tasks 1.2.1, 1.2.2, and 1.2.3 respectively.

## Context and citations

`docs/roadmap.md` defines roadmap item 1.1.3 under "Ratify the v1 decisions
that block implementation". The item requires
`docs/adr-004-import-boundary-fitness-check.md`, lists 1.0.1 and 1.1.1 as
prerequisites (both already done), and declares success as: "the chosen check
can fail a boundary violation in a minimal fixture branch". The roadmap also
points to `https://github.com/leynos/hecate` for hexagonal-architecture
enforcement tooling, and lists three sibling tasks that this plan must not
encroach upon: 1.2.1 (create the hexagonal package layout), 1.2.2 (add the v1
runtime and development dependencies, including Cyclopts and Rich, so
`make build` installs the toolchain), and 1.2.3 (wire the selected check into a
Makefile target so a deliberate domain-to-adapter import fails with an
actionable diagnostic).

`docs/prosidy-darn-technical-design.md` is the architectural source of truth.
Section 4 states that all dependencies point inward and that domain modules
must not import Cyclopts, `mdast`, PyO3 extension modules, HTTP clients,
filesystem delivery code, or text-to-speech (TTS) vendor libraries. Section 5
enumerates the driving and driven ports. Section 9 names the package boundary,
lists `prosidy_darn.ports` as a distinct package holding driven-port protocols,
and states that `prosidy_darn.config` is the composition root that may import
adapters and Cyclopts while `domain` and `application` may not. Section 16
defines the one architecture fitness function: "`prosidy_darn.domain` and
`prosidy_darn.application` must not import from `prosidy_darn.adapters` or
Cyclopts. The CI gate should include an import-boundary check before the first
non-trivial adapter lands." Section 18 lists the open decision "Which
import-boundary checker should enforce hexagonal dependency rules" and records
the already-accepted ADR-001 and ADR-002 outcomes; this task must record the
ADR-004 outcome there and remove the open-decision bullet.

`docs/adr-001-markdown-parser-boundary.md` and
`docs/adr-002-tokenizer-and-semantic-scoring-policy.md` are the accepted ADRs
to use as structural templates: status acceptance, decision drivers, options
table with a caption, decision outcome, goals and non-goals, migration plan,
known risks and limitations, and architectural rationale.

`docs/adr-006-test-matrix-phase-scope.md` scopes Phase 1 tests to
import-boundary checks, public import tests, developer-documentation checks,
and ADR link validation, and defers `pytest-bdd`, `syrupy`, Hypothesis,
CrossHair, and Verus until the product surfaces they validate exist. The line
that scopes "import-boundary checks" into Phase 1 is the warrant for adding a
fixture test in this task.

`docs/adr-008-two-tier-linting-architecture.md` is the precedent for adopting a
pinned, off-PyPI, git-referenced internal tool (`leynos/pylint-pypy-shim`)
through `uv tool run`, and for keeping such a tool out of the project virtual
environment. ADR-004 composes with ADR-008: the import-boundary check is a
distinct third gate, separate from the two lint tiers, and must not be folded
into `make lint` because the Pylint tier runs under PyPy (per ADR-008), whose
managed interpreter lags the project's Python 3.14 target and cannot run hecate.

`docs/developers-guide.md` documents the hexagonal package layout, the two-tier
lint architecture, the Makefile lint variables (including
`PYLINT_PYPY_SHIM_REF`), and the Phase 1 quality gates. It is the place to
document the new `HECATE_REF` pin, the future `check-imports` seam, and the
pin-update discipline.

`docs/documentation-style-guide.md` defines ADR naming and content conventions,
British English with Oxford spelling, 80-column prose wrapping, 120-column code
wrapping, language identifiers on fenced blocks, and captions on every table.

`tests/test_developer_docs.py` contains the documentation-contract tests for
ADR-001 and ADR-002. New ADR-004 contract tests must mirror that pattern:
status-acceptance assertions, required-phrase assertions over the policy text,
and roadmap closure linked to ADR acceptance. The constants `INITIAL_ADR_PATHS`
and `PHASE_ONE_QUALITY_GATES` already include ADR-004 and the gate commands.

`tests/test_public_api.py` exercises the current scaffold package
(`prosidy_darn/__init__.py`, `_runtime.py`, `pure.py`). The new fixture test
must not collide with it or with the real package namespace.

`Makefile` exposes `check-fmt`, `lint`, `typecheck`, `test`, `markdownlint`, and
`nixie` gates and defines the `PYLINT_PYPY_SHIM_REF` pin and the
`uv tool run --from 'git+https://...@<ref>'` invocation pattern (lines 14-16)
that this task mirrors for hecate.

`pyproject.toml` declares `requires-python = ">=3.14"`, an empty
`dependencies = []`, and a `dev` dependency group. This task must not modify
its dependency tables.

### External prior art gathered with Firecrawl

The following findings, gathered during planning, support and constrain the
decision. They are recorded so the implementer need not re-research them.

- `leynos/hecate` is a standalone Python architecture checker for df12 internal
  hexagonal projects. It scans package roots with the standard-library `ast`
  module, classifies each import into ordered groups declared in
  `[tool.hecate]` (each group has `name`, `prefixes`, and `allowed`), supports
  `include_external_packages` to classify external prefixes such as `cyclopts`,
  supports `ignore_imports` for documented composition-root exceptions, expands
  `__init__.py` re-exports including statically resolvable star exports, emits
  `text` or `json` (`--format`), and uses exit codes 0 (clean), 1 (violations),
  and 2 (configuration or input error). It requires Python >=3.14, uses
  Cyclopts internally, and is configured through `[tool.hecate]` in
  `pyproject.toml` or a `--config PATH` file with the same table shape. Its CLI
  is `hecate check`.
- The PyPI distribution named `hecate` is an unrelated project (David MacIver's
  ncurses CLI tester). `leynos/hecate` is therefore not installable by bare
  name and must be referenced only by a pinned git URL, exactly like
  `pylint-pypy-shim`. The implementer must resolve hecate's current
  default-branch HEAD with
  `git ls-remote https://github.com/leynos/hecate.git HEAD` and pin that full
  40-character commit SHA at implementation time.
- `import-linter` 2.11 (by David Seddon) is a Production/Stable, BSD-2-licensed
  PyPI package supporting current CPython, including the project's Python 3.14
  target. Its `forbidden` contract with `include_external_packages = True`
  expresses the exact requirement
  (`source_modules = [prosidy_darn.domain, prosidy_darn.application, prosidy_darn.ports]`;
  `forbidden_modules` listing adapters plus `cyclopts`, `rich`, and the parser
  and renderer packages), and its `layers` contract maps onto the
  domain/application/adapters layering. Its companion `grimp` builds the import
  graph (Rust core) and catches indirect chains. Its CLI is `lint-imports`; it
  exits non-zero on a broken contract; it has no documented machine-readable
  output format. It is the named fallback for ADR-004.
- `tach` (gauge-sh, Rust-backed, ~2.7k stars, PyPI, supports the project's
  Python 3.14 target) enforces first-party module boundaries via `tach.toml`
  and can check external dependencies, but its model is module-graph-centric
  rather than the hexagonal-group model hecate uses. It is a secondary
  alternative.
- `PyTestArch` and the hand-rolled "walk the package with `ast` and assert"
  approach are both viable but require bespoke maintenance and re-implement
  what hecate already provides for df12 projects.
- Ruff's `flake8-tidy-imports` `banned-api` (TID251) is a global ban table with
  no per-source-module direction, so it cannot express "config may import
  adapters but domain may not" without brittle per-directory `.ruff.toml`
  carve-outs that must re-declare the whole banned-api table. It is
  disqualified for the directional rule and should not be revisited naively.

### Community-of-experts review

A six-member Logisphere expert panel reviewed the proposed decision before this
draft. Their unanimous conclusions are folded into this plan: adopt the tool
plus a durable fixture plus a demonstration test at 1.1.3 (not documentation
only); install the tool out-of-process through a pinned git reference rather
than as a `pyproject.toml` dependency, so Cyclopts is never pulled into the
project virtual environment and task 1.2.2's dependency work is not pre-empted;
model five groups including `ports`, not four; place external prefixes in the
`allowed` lists of `config` and the specific adapter groups, not merely
"forbidden in domain"; assert on JSON output, not brittle text; demonstrate
both the violation-fails and clean-passes directions; and name `import-linter`
as the reversible escape hatch. The Decision Log records each adopted
recommendation.

### Relevant skills

- `leta`, for semantic workspace navigation if code symbols must be inspected.
- `hexagonal-architecture`, for the dependency-rule and ports-and-adapters
  framing the ADR must preserve.
- `execplans`, which defines this document's approval gate before
  implementation.
- `firecrawl`, for any remaining open-source-tooling or prior-art checks.
- `python-testing`, for the subprocess-driven fixture test design.
- `commit-message`, for file-based commit messages when this plan is
  implemented.
- `pr-creation` and `en-gb-oxendict`, for the draft pull request and British
  English with Oxford spelling.

## Constraints

Do not implement the real hexagonal package layout in this task. The approved
implementation must not create `prosidy_darn.domain`,
`prosidy_darn.application`, `prosidy_darn.ports`, `prosidy_darn.adapters`, or
`prosidy_darn.config`. Those packages are roadmap task 1.2.1.

Do not add the checker, Cyclopts, Rich, or any runtime dependency to
`pyproject.toml`. hecate must be referenced only through a pinned git URL
invoked by `uv tool run`, never added to `[project.dependencies]` or
`[dependency-groups]`. Adding it to the dev group would pull its Cyclopts
dependency into the project virtual environment, contradicting the very
boundary this decision enforces, and would do task 1.2.2's dependency-spine
work. If satisfying 1.1.3 appears to require a `pyproject.toml` dependency
change, stop and escalate.

Do not wire the checker into `make lint`, `make all`, or any aggregate gate
that scans real source. The demonstration runs only against the self-contained
fixture through the new pytest test. Wiring the gate against the real
`prosidy_darn` tree is roadmap task 1.2.3.

Do not run hecate in-process. hecate is not a project dependency; it is an
isolated CLI tool whose own Cyclopts dependency must stay out of the project
virtual environment and test process. The demonstration test must shell out to
hecate as a subprocess through this shape:

```bash
uv tool run --python 3.14 --from 'git+https://github.com/leynos/hecate.git@<sha>' hecate ...
```

It must never execute `import hecate`. Invoking `uv tool run --python 3.14`
also pins the tool to the project's Python 3.14 target regardless of the
interpreter that runs `pytest`.

Pin hecate by a full 40-character commit SHA, never a branch or tag, so the pin
is immutable and reproducible, mirroring `PYLINT_PYPY_SHIM_REF`.

Never reference hecate by bare name. The PyPI `hecate` is an unrelated package.
The ADR, the Makefile comment, and the developers' guide must warn that a bare
`uv add hecate`, `pip install hecate`, or requirements entry installs the wrong
project.

Preserve the hexagonal dependency rule in the documented production
configuration. The ADR must model `domain` and `application` (and `ports`) so
they cannot import adapters, Cyclopts, Rich, the parser package, renderer
infrastructure, delivery code, or TTS vendor libraries, while `config` (the
composition root) and the relevant adapter groups may.

Keep the public API and user-facing behaviour unchanged. This task changes
documentation, a Makefile tool reference, and tests only. `docs/users-guide.md`
changes only if a user-visible statement must be corrected, which this task
should not require.

Use British English with Oxford spelling. Follow the documentation style guide:
wrap Markdown prose and bullets at 80 columns, wrap code at 120 columns, use
dash bullets, give every fenced code block a language identifier, and caption
every table.

The plan must be approved before implementation begins. Silence is not approval.

Do not mark roadmap item 1.1.3 done until the approved implementation has added
the fixture demonstration and contract tests, passed the required gates,
cleared CodeRabbit concerns, been committed, and been pushed.

## Tolerances

Stop and ask for direction if implementation of the approved plan requires
changes outside these paths:

- `docs/adr-004-import-boundary-fitness-check.md`
- `docs/roadmap.md`
- `docs/prosidy-darn-technical-design.md`
- `docs/developers-guide.md`
- `docs/contents.md`
- `docs/users-guide.md` (only if a user-visible statement must be corrected)
- `docs/execplans/1-1-3-record-import-boundary-enforcement-decision.md`
- `Makefile` (add the `HECATE_REF`, `HECATE_SPEC`, and `HECATE` variables and
  export them to the `test` target; do not add a gate to `lint`/`all`)
- `tests/test_developer_docs.py`
- `tests/test_import_boundary_fitness.py` (new)
- `tests/fixtures/import_boundary/**` (new fixture trees and config)
- `.github/workflows/ci.yml` and `.github/workflows/release.yml` (verify the
  `python-version: '3.14'` pins remain aligned with the project target)

Stop and ask for direction if more than 400 net lines of documentation, or more
than 200 net lines of test, fixture, and Makefile code combined, are needed.
This task records a decision and proves the tool on a fixture; it must not
become an adapter or package-layout implementation slice.

Stop and ask for direction if any of these scope expansions become necessary:

- creating any real `prosidy_darn` domain, application, ports, adapters, or
  config package;
- adding a runtime or development dependency to `pyproject.toml`, including the
  checker itself, Cyclopts, or Rich;
- wiring the checker into `make lint`, `make all`, or any gate over real source;
- selecting a checker other than hecate as the v1 primary.

Stop and ask for direction if hecate cannot be fetched or run at all during
implementation (network restriction, removed SHA, interpreter unavailable), so
the demonstration evidence cannot be captured even once. Record the blocker in
the Decision Log rather than weakening the success criterion.

Stop and ask for direction if any quality gate still fails after three focused
fix attempts.

Stop and ask for direction if `make fmt` rewrites unrelated Markdown or source
files. Restore unrelated formatting churn before continuing, unless the user
explicitly accepts the broader change.

Stop and ask for direction if CodeRabbit reports concerns that would require
adapter implementation, package-layout creation, or dependency changes to
resolve. For documentation, test, or Makefile-scoped concerns, revise and rerun
the relevant checks.

## Risks

Risk: Single-maintainer, off-PyPI supply chain. hecate is a df12-internal tool
with an effective bus factor of one, pinned by git SHA, and is the sole v1
architecture gate. Severity: medium. Likelihood: medium. Mitigation: pin a full
SHA; record `import-linter` 2.11 as the named, capability-equivalent fallback
with a config-only migration path behind a stable `check-imports` seam; note
that the tool is small stdlib-`ast` code and cheap to fork or vendor.

Risk: PyPI name collision. A future `uv add hecate` or requirements entry would
install an unrelated package. Severity: medium. Likelihood: medium. Mitigation:
warn prominently in the ADR, the Makefile comment, and the developers' guide
that hecate is git-ref-only and must never be referenced by bare name.

Risk: CI Python pin drift. The project targets Python >=3.14, so the CI and
release workflows must exercise Python 3.14. Severity: medium. Likelihood:
medium. Mitigation: verify both workflows pin `python-version: '3.14'` as part
of this task. Independently, hecate runs only as an isolated
`uv tool run --python 3.14` subprocess (never imported), so it is unaffected by
the interpreter that runs `pytest`, and the Pylint tier's managed PyPy
(ADR-008) remains a deliberate, separate exception.

Risk: False green (silent no-op). A mistyped prefix, an omitted external
package, a barrel re-export, or an unknown-key-ignored config could make the
dirty fixture pass with exit 0. Severity: high. Likelihood: medium. Mitigation:
the demonstration asserts both directions on the same config path — clean
passes (exit 0, no violations) and dirty fails (exit 1, the specific offending
edge named) — and treats exit 2 as a harness failure distinct from exit 1.

Risk: Mis-modelled `ports` group. The technical design lists
`prosidy_darn.ports` as a distinct package that `domain` and `application`
legitimately import. A four-group model (domain, application, adapters, config)
would either flag every `domain -> ports` import or leave `ports` unclassified.
Severity: high. Likelihood: high if ignored. Mitigation: the ADR models five
groups with explicit `allowed` lists, granting `domain` and `application` an
inward edge to `ports`, and granting adapters an edge to `domain.ir` and
`ports`.

Risk: External import-name versus distribution-name skew.
`include_external_packages` keys on the top-level import name, which can differ
from the PyPI distribution name (for example the Markdown parser). A wrong name
silently never fires. Severity: medium. Likelihood: medium. Mitigation: the ADR
records the requirement to verify each banned and allowed external's actual
import top-level name; the fixture uses a stand-in external prefix so the
demonstration is self-contained and needs no real dependency installed.

Risk: Brittle text assertions. Asserting on hecate's human-readable text
couples the test to unstable wording, ordering, and path rendering. Severity:
medium. Likelihood: medium. Mitigation: the test asserts on `--format json`
structured fields and module-dotted identifiers, never absolute filesystem
paths.

Risk: Static-analysis blind spot. hecate (like every static checker) cannot see
dynamic imports (`importlib.import_module`, `__import__`). The existing
`_runtime.py` already uses `__import__`. Severity: low for this task.
Likelihood: low. Mitigation: record it as an accepted limitation shared by all
static checkers, mitigated by code review and the convention that dynamic
imports live in `config` or `_runtime`.

Risk: Fixture pollutes the real run later. A fixture placed inside the real
package namespace would be swept into the production hecate run after 1.2.1.
Severity: medium. Likelihood: low. Mitigation: keep the fixture under
`tests/fixtures/import_boundary/` with its own `--config` file, outside the
`prosidy_darn` import surface.

Risk: Demonstration proves tool capability, not production-config correctness.
Because the real packages do not exist until 1.2.1, a green fixture says
nothing about whether the production `[tool.hecate]` groups are right.
Severity: medium. Likelihood: high if unstated. Mitigation: the ADR states this
limitation explicitly and assigns the real-tree proof to task 1.2.3's success
criterion.

## Progress

- [x] (2026-06-09) Loaded the `leta`, `python-router`, and
  `hexagonal-architecture` skills and the `execplans` skill, and created a leta
  workspace for this repository.
- [x] (2026-06-09) Read the roadmap, the technical design (sections 4, 5, 9, 16,
  and 18), ADR-001, ADR-002, ADR-006, ADR-008, the ADR-004 stub, the
  developers' guide, the documentation style guide, the documentation-contract
  tests, the Makefile, and `pyproject.toml`.
- [x] (2026-06-09) Inspected `leynos/hecate` (README, configuration schema, and
  `pyproject.toml`) and confirmed the PyPI name collision, the Python >=3.14
  requirement, the `[tool.hecate]` schema, and the exit-code taxonomy.
- [x] (2026-06-09) Ran a Firecrawl-backed research agent team over
      `import-linter`,
  `tach`, `PyTestArch`, the custom-`ast` approach, Ruff `flake8-tidy-imports`,
  and the architecture-fitness-function prior art.
- [x] (2026-06-09) Ran a six-member Logisphere community-of-experts panel to
  stress-test and revise the decision before drafting.
- [x] (2026-06-15) Received explicit user approval to implement the plan.
- [x] (2026-06-16) Renamed the branch to
  `1-1-3-record-import-boundary-enforcement-decision` and track the matching
  remote.
- [x] (2026-06-15) Resolved the current hecate HEAD pin as
  `46f8c8798e7a80a3a1ab5a13c2a000a4423ffc12`.
- [x] (2026-06-15) Added the documentation-contract tests for ADR-004
  acceptance.
- [x] (2026-06-15) Added the fixture demonstration test
  (`tests/test_import_boundary_fitness.py`) and the clean and dirty fixture
  trees.
- [x] (2026-06-15) Added the `HECATE_REF`, `HECATE_SPEC`, and `HECATE` Makefile
  variables, exported `HECATE_REF` to the `test` target, and pinned the full
  hecate commit SHA.
- [x] (2026-06-15) Ran the focused hecate fixture test with `HECATE_REF`
  set to `46f8c8798e7a80a3a1ab5a13c2a000a4423ffc12`; the clean and dirty
  fixture tests both passed.
- [x] (2026-06-15) Captured one-shot dirty-fixture evidence: hecate reported
  the forbidden `fixture_domain.adapter_breach -> fixture_adapters.runtime` and
  `fixture_domain.external_breach -> pretend_framework` edges and exited 1.
- [x] (2026-06-15) Finalised ADR-004 (status, options table, decision,
  production config, limitations, fallback).
- [x] (2026-06-15) Aligned `docs/prosidy-darn-technical-design.md` section 18,
  the developers' guide, and `docs/contents.md`.
- [x] (2026-06-15) Confirmed `.github/workflows/ci.yml` and
  `.github/workflows/release.yml` already pin `python-version: '3.14'`, so no
  Python-pin correction was required.
- [x] (2026-06-15) Marked roadmap item 1.1.3 done.
- [x] (2026-06-15) Ran the local gates sequentially with `/tmp` logs:
  `make fmt`, `make check-fmt`, `make markdownlint`, `make nixie`,
  `make typecheck`, `make lint`, and `make test` all passed.
- [x] (2026-06-15) Ran `coderabbit review --agent` after focused tests; the
  second attempt exited 0 and emitted no findings.
- [x] (2026-06-15) Ran final `coderabbit review --agent`; it completed with
  `findings: 0`.
- [x] (2026-06-16) Committed with file-based messages, pushed
  `1-1-3-record-import-boundary-enforcement-decision`, and opened draft pull
  request #21.
- [x] (2026-06-16) Expanded `docs/roadmap.md` so item 1.1.3 records the
  accepted hecate decision, import-linter fallback, fixture evidence, execplan
  reference, draft PR #21, and the remaining 1.2.3 real-tree gate boundary.
- [x] (2026-06-16) Revalidated the roadmap update with `make check-fmt`,
  `make markdownlint`, and `make nixie`; committed and pushed
  `afed99e Update roadmap for import-boundary decision`.
- [x] (2026-06-16) Fixed the hecate fixture test so direct pytest and CI
  slipcover runs derive the repository `HECATE_REF` pin from the Makefile when
  the Makefile-only environment export is absent.
- [x] (2026-06-16) Verified the CI-equivalent command
  `uv run python -m slipcover ... -m pytest --forked -v` with `HECATE_REF`
  unset; both hecate fixture tests executed and the full suite passed.
- [x] (2026-06-16) Ran `coderabbit review --agent` for the CI hecate fixture
  fix; it completed with `findings: 0`.
- [x] (2026-06-16) Verified current inline review findings and fixed only the
  still-valid issues: ADR-004 core-versus-auxiliary group wording, developer
  guide fallback wording, execplan link/spelling/milestone consistency, roadmap
  PR-number stability, and `HECATE_REF` environment override validation.
- [x] (2026-06-16) Revalidated the inline-finding fixes with focused hecate
  tests, the CI-equivalent slipcover pytest command, `make check-fmt`,
  `make markdownlint`, `make nixie`, `make lint`, `make typecheck`, and
  `make test`.
- [x] (2026-06-16) Ran `coderabbit review --agent` after the inline-finding
  fixes; it completed with `findings: 0`.

## Surprises & discoveries

- Observation: ADR-004 already exists as a "Proposed" stub with a pending
  outcome. Evidence: `docs/adr-004-import-boundary-fitness-check.md` lines 3-9.
  Impact: the implementation finalises the existing file in place rather than
  creating a new one, preserving the stable review path the stub promises.
- Observation: the PyPI distribution `hecate` is unrelated to `leynos/hecate`.
  Evidence: `https://pypi.org/pypi/hecate/json` returns David MacIver's ncurses
  CLI tester. Impact: hecate must be referenced only by pinned git URL;
  bare-name installs are a foot-gun the ADR must warn against.
- Observation: by implementation time both `.github/workflows/ci.yml` and
  `.github/workflows/release.yml` pinned `python-version: '3.14'`. Evidence:
  the two workflow files. Impact: Milestone 6a became a verification step
  rather than a workflow-editing step. (The `pyproject.toml` comment about
  managed PyPy is the deliberate ADR-008 Pylint-tier exception, not an error.)
- Observation: hecate requires Python >=3.14 and imports Cyclopts. Evidence:
  hecate's `pyproject.toml`. Impact: hecate must run out-of-process as an
  isolated `uv tool run --python 3.14` subprocess and must not be folded into
  `make lint` (whose Pylint tier runs under PyPy per ADR-008).
- Observation: the technical design treats `prosidy_darn.ports` as a distinct
  package (section 9) that domain and application import, even though section 4
  says ports "belong to the domain or application layer". Evidence: design
  sections 4 and 9; developers' guide line 53. Impact: the production config
  must model a `ports` group and grant inward edges to it, or the gate becomes
  un-greenable.
- Observation: hecate classifies every module's direct imports (with `__init__`
  barrel expansion) rather than building a transitive reachability graph.
  Evidence: hecate README "Core concepts". Impact: a forbidden import in a
  domain helper is still caught (the helper is itself scanned), so per-module
  direct classification is sufficient for the strict layered rule; the ADR
  records this rather than overclaiming grimp-style transitive analysis.
- Observation: by implementation time both `.github/workflows/ci.yml` and
  `.github/workflows/release.yml` already pinned `python-version: '3.14'`.
  Evidence: the two workflow files. Impact: Milestone 6a's pin correction was
  already done upstream, so this task touched no workflow file.
- Observation: the repository's own Ruff and `ty` gates scan `tests/fixtures`.
  Evidence: `make lint` and `make typecheck` over the fixture trees. Impact:
  the fixture modules bind each deliberate import to a module-level name so
  Ruff does not report it as unused, and the never-installed stand-in external
  import carries a single `# ty: ignore[unresolved-import]` comment; hecate
  still sees every import because it parses the source with `ast`. This keeps
  the fixtures self-contained without editing `pyproject.toml`.
- Observation: hecate's JSON violation objects expose `importer`, `imported`,
  `importer_group`, `imported_group`, `line`, `rule_id`, and `source_path`.
  Evidence: a one-shot run against the dirty fixture. Impact: the test asserts
  on the module-dotted `importer` and `imported` fields and never on
  `source_path`, keeping assertions stable across machines.
- Observation: the local branch
  `1-1-3-record-import-boundary-enforcement-decision` already existed at
  `89b2d896d7028d54f55bc72bef2199a0e762c676` and tracks a gone remote branch.
  Evidence: `git branch -m` failed with "a branch named … already exists" and
  `git branch -vv` showed the stale branch. Impact: the stale branch was
  preserved as
  `stale/1-1-3-record-import-boundary-enforcement-decision-20260615` so the
  current branch could be renamed safely.
- Observation: a prior `issue-16-import-boundary-fitness-tests` branch contains
  an older implementation of this task, but it is based before the current
  Maturin/PyO3 work. Evidence:
  `git diff --stat HEAD..issue-16-import-boundary-fitness-tests` showed
  unrelated deletions and rewrites in Rust, workflow, README, runtime, and
  test-helper files. Impact: only scoped commits and ideas are reused; the old
  branch is not merged wholesale.
- Observation: the first CodeRabbit milestone attempt connected and reached
  "preparing_sandbox" but produced no findings, rate-limit response, or further
  progress for over four minutes. Evidence: `/tmp/coderabbit-fixture-...out`
  contains only setup status lines. Impact: the stalled local process was
  terminated and CodeRabbit will be retried after the next complete milestone
  and during final validation.
- Observation: the GitHub CI workflow runs pytest directly through slipcover
  rather than `make test`, so `HECATE_REF` was not exported by Makefile in that
  path. Evidence: `.github/workflows/ci.yml` invokes
  `uv run python -m slipcover ... -m pytest --forked -v`. Impact:
  `tests/test_import_boundary_fitness.py` now falls back to the Makefile
  `HECATE_REF` pin, and a CI-equivalent slipcover run with `HECATE_REF` unset
  exercised both hecate fixture tests instead of skipping them.

## Decision log

- Decision: Treat 1.1.3 as a decision-finalization task that also adds a durable
  demonstration, not documentation only. Rationale: the roadmap success
  criterion ("can fail a boundary violation in a minimal fixture") is
  executable, and ADR-006 already scopes import-boundary checks into Phase 1
  tests. Documentation only would push the sole proof of tool selection to
  1.2.3. Date/Author: 2026-06-09 / Claude (planning).
- Decision: Select `leynos/hecate` as the v1 primary import-boundary fitness
  function, with `import-linter` 2.11 named as the vetted fallback. Rationale:
  the roadmap points to hecate; it is the df12 house tool purpose-built for the
  hexagonal-group model, models the composition-root exception through
  `ignore_imports`, expands barrels, emits JSON, runs natively on Python 3.14,
  and aligns with the existing pinned-git-ref tooling pattern. The supply-chain
  and bus-factor risks are accepted and made reversible by naming a capability-
  equivalent PyPI fallback behind a stable seam. Date/Author: 2026-06-09 /
  Claude (planning).
- Decision: Install hecate out-of-process via a pinned git reference invoked by
  `uv tool run`, not as a `pyproject.toml` dependency. Rationale: adding it to
  the dev group would pull Cyclopts into the project virtual environment
  (contradicting the boundary) and would do task 1.2.2's dependency work; the
  established `pylint-pypy-shim` pattern keeps such tools isolated.
  Date/Author: 2026-06-09 / Claude (planning).
- Decision: Run hecate only as an isolated `uv tool run --python 3.14`
  subprocess, and verify the CI workflows pin Python 3.14. Rationale: the
  project targets Python >=3.14; hecate is not a project dependency and imports
  Cyclopts, so it must run isolated to keep Cyclopts out of the project
  environment. The Pylint tier's managed PyPy (ADR-008) is a separate,
  deliberate exception. Date/Author: 2026-06-09 / Claude (planning; updated
  2026-06-16 during implementation).
- Decision: Model five groups (`domain`, `ports`, `application`, `adapters`,
  `config`) with explicit `allowed` lists, and place external prefixes in the
  `allowed` lists of `config` and the relevant adapter groups, absent from
  `domain`, `application`, and `ports`. Rationale: ports is a real package that
  domain and application import, and externals such as Cyclopts are
  legitimately imported by config and the CLI adapter; a four-group or
  "forbid-in-domain-only" model produces false positives or false negatives.
  Date/Author: 2026-06-09 / Claude (planning).
- Decision: Demonstrate with a self-contained, multi-case fixture and a
  subprocess pytest test asserting JSON structured fields, proving exit 0 on a
  clean tree and exit 1 on a dirty tree, and treating exit 2 as a harness
  failure. Use a stand-in external prefix so the external-ban path needs no
  real dependency. Rationale: a fail-only or text-grep test cannot catch the
  false-green and false-positive failure modes; JSON and module-dotted
  identifiers are determinism-safe. Date/Author: 2026-06-09 / Claude (planning).
- Decision: Ratify a stable `check-imports` seam name and the
  `HECATE_REF`/`HECATE_SPEC`/`HECATE` Makefile variable surface in the ADR and
  the developers' guide now, but leave the real gate wiring to 1.2.3.
  Rationale: declaring the seam makes the tool swappable by construction
  without doing 1.2.3's work. Date/Author: 2026-06-09 / Claude (planning).
- Decision: Use `pytest` documentation-contract tests plus one subprocess
  fixture test, not `pytest-bdd`, `syrupy`, Hypothesis, CrossHair, or Verus.
  Rationale: ADR-006 scopes Phase 1 to documentation, link, and import-boundary
  checks; no user behaviour, output snapshot, input invariant, or proof-worthy
  logic is introduced. Date/Author: 2026-06-09 / Claude (planning).

## Outcomes & retrospective

Implemented on 2026-06-15. ADR-004 is accepted, names hecate as the primary v1
import-boundary fitness function, and names import-linter as the fallback
behind the stable `check-imports` seam. The fixture demonstration proves hecate
exits 0 on the clean tree and 1 on the dirty tree, the documentation-contract
tests lock the policy, and roadmap item 1.1.3 is marked done. Local gates
passed sequentially, and final CodeRabbit review completed with `findings: 0`.
The branch was renamed to `1-1-3-record-import-boundary-enforcement-decision`,
pushed, and draft pull request #21 was opened. The roadmap was then expanded to
carry the implementation decision, evidence, observations, and remaining
follow-on boundary for task 1.2.3. The hecate fixture test now exercises the
pinned checker under direct pytest, `make test`, and the CI slipcover
invocation.

## Context and orientation

Prosidy Darn is a Python package built on hexagonal architecture. "Hexagonal
architecture" means the domain owns business concepts and the port protocols it
needs, the application layer orchestrates use cases, and adapters connect the
outside world to those ports. The "dependency rule" requires that all source
dependencies point inward: the domain and application layers never name an
adapter, a framework such as Cyclopts, a parser package, a renderer, a delivery
sink, or a TTS vendor library. The composition root (`prosidy_darn.config`) is
the one place that wires concrete adapters to ports and may therefore import
them.

An "import-boundary fitness function" is the automated CI check that holds the
dependency rule true. This task selects that check.

The current repository is at scaffold stage. `prosidy_darn/` holds only
`__init__.py`, `_runtime.py`, and `pure.py`. The real `domain`, `application`,
`ports`, `adapters`, and `config` packages do not exist yet; roadmap task 1.2.1
creates them. Consequently this task cannot run the checker against the real
tree. It records the decision, documents the production configuration shape for
1.2.3 to commit, and proves the checker works against a throwaway fixture.

The key files for this task are:

- `docs/roadmap.md`: item 1.1.3 and the sibling tasks 1.2.1, 1.2.2, and 1.2.3.
- `docs/adr-004-import-boundary-fitness-check.md`: the stub to finalize.
- `docs/adr-001-markdown-parser-boundary.md` and
  `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`: accepted-ADR
  templates.
- `docs/adr-006-test-matrix-phase-scope.md`: the warrant for a Phase 1
  import-boundary fixture test.
- `docs/adr-008-two-tier-linting-architecture.md`: the pinned-git-ref tool
  precedent and the reason the check is a distinct third gate.
- `docs/prosidy-darn-technical-design.md`: sections 4, 5, 9, and 16 (the rule)
  and 18 (the open decision to close).
- `docs/developers-guide.md`: where the `HECATE_REF` pin, the `check-imports`
  seam, and the pin-update discipline are documented.
- `docs/contents.md`: the documentation index; add the 1.1.3 execplan entry.
- `tests/test_developer_docs.py`: the documentation-contract test pattern.
- `Makefile`: the `PYLINT_PYPY_SHIM_REF` pin pattern to mirror.

Important terms:

- "Group" (hecate): a named set of dotted module prefixes plus the list of group
  names it is `allowed` to import. The first group whose prefix matches a
  module wins, so specific prefixes precede general ones.
- "Composition root": `prosidy_darn.config`, the only group allowed to import
  adapters and frameworks.
- "Stand-in external prefix": a fake top-level import name used only in the
  fixture (for example `pretend_framework`) so the external-ban demonstration
  needs no real dependency installed; hecate parses the import statement with
  `ast` and never executes it.
- "Seam": the stable `make check-imports` target name and `HECATE_*` variable
  surface that lets the underlying tool be swapped without a documentation
  rewrite.

## Plan of work

Milestone 1 prepares the branch and confirms the baseline. Confirm the current
branch and, if it is not already
`1-1-3-record-import-boundary-enforcement-decision`, rename it with
`git branch -m`. Re-resolve hecate's HEAD commit SHA with
`git ls-remote https://github.com/leynos/hecate.git HEAD` and record the full
SHA to pin. Read the roadmap, the ADR-004 stub, ADR-001, ADR-002, ADR-006,
ADR-008, the technical design sections named above, the developers' guide, the
documentation-contract tests, and the Makefile.

Milestone 2 adds failing documentation-contract tests first. Extend
`tests/test_developer_docs.py` with tests that prove roadmap item 1.1.3 cannot
be closed unless ADR-004 is accepted and states the chosen policy. The tests
should check for these observable facts:

- ADR-004 exists and is accepted (status section contains "## Status" and
  "Accepted on ").
- ADR-004 names hecate as the v1 import-boundary fitness function, installed via
  a pinned git reference and run out-of-process through `uv tool run`.
- ADR-004 names `import-linter` as the vetted fallback behind a stable
  `check-imports` seam.
- ADR-004 states that the checker is never added to `pyproject.toml` and is
  never referenced by bare name because the PyPI `hecate` is an unrelated
  package.
- ADR-004 states the five-group production model and that `domain`,
  `application`, and `ports` may not import adapters, Cyclopts, Rich, the
  parser package, renderers, or delivery code, while `config` may.
- ADR-004 records hecate's exit-code contract (0 clean, 1 violations, 2
  configuration or input error), distinct from the application CLI taxonomy.
- The roadmap item for 1.1.3 is marked done only when ADR-004 is accepted.

Run the focused test and confirm it fails for the expected reason before
editing the ADR.

Milestone 3 adds the failing fixture demonstration test. Create
`tests/fixtures/import_boundary/` containing a clean tree and a dirty tree,
plus a fixture-local hecate configuration file, and
`tests/test_import_boundary_fitness.py` that shells out to hecate over each
tree. The fixture trees model the real five-group shape with throwaway package
names so the config exercises the same rule classes the production config will:

- the clean tree contains a `domain` module importing a `ports` module, and an
  `adapters` module importing a `domain` IR-style module; both edges are
  allowed, so hecate must exit 0 with no violations;
- the dirty tree contains a `domain` module importing an `adapters` module (a
  forbidden first-party edge) and a `domain` module importing a stand-in
  external prefix classified into an infrastructure group (a forbidden external
  edge); so hecate must exit 1 and name both offending edges in its JSON output.

The test invokes hecate as a subprocess via this command shape:

```bash
uv tool run --python 3.14 --from '<HECATE_SPEC>' hecate check --config <fixture config> --format json
```

It reads the pinned reference from the `HECATE_REF` environment variable
exported by `make test`. It asserts exit 0 and an empty violation list on the
clean tree, and exit 1 with the specific offending module-dotted edges on the
dirty tree. It treats exit 2 (configuration or input error) as a harness
failure, not a pass. If `uv tool run` cannot fetch or resolve the tool (a
confirmed network or ref-availability error, distinct from a contract result),
the test skips with a clear reason; otherwise it asserts. Confirm the test
fails (or skips with an explanatory message) before the Makefile pin exists.

Milestone 4 adds the Makefile tool reference. Add `HECATE_REF` (the full pinned
SHA), `HECATE_SPEC` (`git+https://github.com/leynos/hecate.git@$(HECATE_REF)`),
and `HECATE`
(`$(UV_ENV) uv tool run --python 3.14 --from '$(HECATE_SPEC)' hecate`) near the
`PYLINT_PYPY_SHIM_REF` block, with a comment warning that hecate is
git-ref-only and must never be referenced by bare name. Export `HECATE_REF` to
the `test` target so the fixture test can read it. Do not add a `check-imports`
target to `lint` or `all`; the real gate is task 1.2.3. Run the fixture test
through `make test` and confirm it now passes (or skips only on confirmed
unavailability).

Milestone 5 finalises ADR-004. Replace the "Pending" outcome with "Accepted on
`YYYY-MM-DD`". Keep the existing context and decision-driver material and add
the sections the style guide requires: a decided options table comparing
hecate, import-linter, tach, PyTestArch or custom `ast`, and Ruff `banned-api`
across the project's concrete requirements (first-party ban, external ban,
composition-root exception, JSON output, Python 3.14, barrel handling,
supply-chain cost); the decision outcome; the documented production
`[tool.hecate]` five-group config block; goals and non-goals; a migration plan;
known risks and limitations (supply chain and bus factor, PyPI name collision,
interpreter isolation, static-`ast` blind spot, the `TYPE_CHECKING`-import
policy determined against a fixture during implementation, and the
fixture-proves-capability-not-production- correctness caveat); and the
architectural rationale. State that the seam is `make check-imports` and that
wiring against the real tree is task 1.2.3, and that import-linter is the
reversible escape hatch. Capture the one-shot demonstration command and its
exit-1 output in the Artefacts section of this plan.

Milestone 6 aligns surrounding documentation. Update
`docs/prosidy-darn-technical-design.md` section 18 to remove the
import-boundary open-decision bullet and record the ADR-004 outcome alongside
ADR-001 and ADR-002. Update `docs/developers-guide.md` to document the
`HECATE_REF` pin and its update discipline (a reviewed change like
`PYLINT_PYPY_SHIM_REF`), the future `check-imports` seam, the bare-name
prohibition, and that the architecture-fitness check is a distinct third gate
that must not be folded into `make lint`. Add the 1.1.3 execplan entry to
`docs/contents.md`. Touch `docs/users-guide.md` only if a user-visible
statement needs correcting.

Milestone 6a verifies the CI Python pins. The project targets Python >=3.14,
and by implementation time `.github/workflows/ci.yml` and
`.github/workflows/release.yml` already pinned `python-version: '3.14'`.
Confirm both workflows still exercise the supported interpreter and do not
otherwise alter the workflows.

Milestone 7 updates task tracking. Mark item 1.1.3 in `docs/roadmap.md` done
only after ADR-004 is accepted, the fixture demonstration passes, and the
contract tests pass. Do not mark 1.2.1, 1.2.2, or 1.2.3 done.

Milestone 8 validates the change. Run formatting checks, Markdown linting,
Mermaid validation, type checking, linting, and tests sequentially with `tee`
logs under `/tmp`. Do not run gates in parallel. If a gate fails, inspect the
full log and make focused fixes.

Milestone 9 runs CodeRabbit review. Run `coderabbit review --agent` after the
local gates pass. Address every actionable in-scope concern. If CodeRabbit asks
for adapter code, package-layout creation, or dependency additions, record the
concern in the Decision Log and escalate instead of expanding scope.

Milestone 10 commits and opens the draft pull request. Use the `commit-message`
skill's file-based workflow. Push the branch with upstream tracking. Open a
draft pull request whose title includes `(1.1.3)`, whose summary mentions this
ExecPlan, and whose `## References` section includes the Lody session URL
derived from `echo ${LODY_SESSION_ID}`.

## Concrete steps

Run all commands from the repository root.

Confirm and, if needed, rename the branch:

```bash
pwd
git branch --show-current
git branch -m 1-1-3-record-import-boundary-enforcement-decision
```

Re-resolve the hecate pin:

```bash
git ls-remote https://github.com/leynos/hecate.git HEAD
```

Read the local context:

```bash
sed -n '94,136p' docs/roadmap.md
sed -n '1,46p' docs/adr-004-import-boundary-fitness-check.md
sed -n '1,140p' docs/adr-001-markdown-parser-boundary.md
sed -n '109,226p' docs/prosidy-darn-technical-design.md
sed -n '1117,1190p' docs/prosidy-darn-technical-design.md
sed -n '1226,1243p' docs/prosidy-darn-technical-design.md
sed -n '1,30p' tests/test_developer_docs.py
sed -n '1,17p' Makefile
```

After adding the contract and fixture tests, run the focused checks:

```bash
UV_CACHE_DIR=.uv-cache UV_TOOL_DIR=.uv-tools uv run pytest \
  tests/test_developer_docs.py tests/test_import_boundary_fitness.py -v \
  | tee /tmp/pytest-1-1-3-$(basename "$(pwd)")-$(git branch --show-current).out
```

Capture the one-shot demonstration evidence (replace `<REF>` with the pinned
SHA and the config path with the fixture's dirty-tree config):

```bash
HECATE_REF=<REF> uv tool run --python 3.14 \
  --from "git+https://github.com/leynos/hecate.git@<REF>" \
  hecate check --config tests/fixtures/import_boundary/dirty/hecate.toml \
  --format json ; echo "exit=$?"
```

After ADR and Markdown edits, format if needed and run the gates sequentially:

```bash
make fmt | tee /tmp/fmt-$(basename "$(pwd)")-$(git branch --show-current).out
make check-fmt | tee /tmp/check-fmt-$(basename "$(pwd)")-$(git branch --show-current).out
make markdownlint | tee /tmp/markdownlint-$(basename "$(pwd)")-$(git branch --show-current).out
make nixie | tee /tmp/nixie-$(basename "$(pwd)")-$(git branch --show-current).out
make typecheck | tee /tmp/typecheck-$(basename "$(pwd)")-$(git branch --show-current).out
make lint | tee /tmp/lint-$(basename "$(pwd)")-$(git branch --show-current).out
make test | tee /tmp/test-$(basename "$(pwd)")-$(git branch --show-current).out
```

Run CodeRabbit after the local gates pass:

```bash
coderabbit review --agent \
  | tee /tmp/coderabbit-$(basename "$(pwd)")-$(git branch --show-current).out
```

Inspect, commit with a file-based message, and push:

```bash
git diff -- docs tests Makefile .github/workflows/ci.yml .github/workflows/release.yml
git add docs tests Makefile .github/workflows/ci.yml .github/workflows/release.yml
COMMIT_MSG_DIR=$(mktemp -d)
cat > "$COMMIT_MSG_DIR/COMMIT_MSG.md" << 'ENDOFMSG'
Record import-boundary fitness check decision (ADR-004)

Accept ADR-004 selecting leynos/hecate as the v1 import-boundary fitness
function, installed out-of-process via a pinned git reference and run on
Python 3.14, with import-linter named as the vetted fallback behind a
stable check-imports seam.

Prove the criterion with a self-contained architecture fixture and a
subprocess pytest test that asserts hecate fails a domain-to-adapter and
domain-to-external import (exit 1) and passes a clean fixture (exit 0).

Add documentation-contract tests, document the production five-group
config, record the HECATE_REF pin discipline, and close roadmap item
1.1.3.
ENDOFMSG
git commit -F "$COMMIT_MSG_DIR/COMMIT_MSG.md"
rm -rf "$COMMIT_MSG_DIR"
git push -u origin 1-1-3-record-import-boundary-enforcement-decision
```

Capture the Lody session and open the draft pull request:

```bash
echo ${LODY_SESSION_ID}
```

The pull-request title must contain `(1.1.3)`, the body must mention this
ExecPlan, and the final `## References` section must include
`https://lody.ai/leynos/sessions/${LODY_SESSION_ID}`.

## Validation and acceptance

The approved implementation is accepted when all of these are true:

- `tests/test_developer_docs.py` verifies that ADR-004 is accepted and states
  the hecate-primary and import-linter-fallback decision, the pinned-git-ref
  out-of-process install, the bare-name prohibition, the five-group production
  model, and the exit-code contract.
- `tests/test_import_boundary_fitness.py` runs the selected checker as a
  subprocess and asserts exit 0 with no violations on the clean fixture and
  exit 1 naming the offending edges on the dirty fixture, treating exit 2 as a
  harness failure. The test is collected by `make test` and skips only on
  confirmed tool unavailability with a clear reason.
- `docs/adr-004-import-boundary-fitness-check.md` is accepted and carries
  Status, Date, Context and problem statement, Decision drivers, Options
  considered (with a captioned comparison table), Decision outcome, the
  documented production `[tool.hecate]` config, Goals and non-goals, Migration
  plan, Known risks and limitations, and Architectural rationale.
- `docs/roadmap.md` marks item 1.1.3 done only after ADR-004 is accepted and the
  tests pass.
- `docs/prosidy-darn-technical-design.md` section 18,
  `docs/developers-guide.md`, and `docs/contents.md` are aligned with the
  accepted decision, and no document contradicts ADR-004.
- No real `prosidy_darn` domain, application, ports, adapters, or config package
  is created; no `pyproject.toml` dependency is added; no gate over real source
  is wired.
- `.github/workflows/ci.yml` and `.github/workflows/release.yml` pin
  `python-version: '3.14'`, with no remaining reference to an earlier
  interpreter outside the deliberate ADR-008 PyPy Pylint tier.
- `make check-fmt`, `make markdownlint`, `make nixie`, `make typecheck`,
  `make lint`, and `make test` all pass.
- `coderabbit review --agent` reports no unresolved in-scope concerns.
- The branch is pushed and has a draft pull request whose title includes
  `(1.1.3)` and whose body links this ExecPlan and the Lody session.

Record the Red-Green evidence for the test-first work. Red: the contract tests
and the fixture test fail (or the fixture test skips with an explanatory
message) before the ADR, Makefile pin, and fixture config exist. Green: after
the ADR is accepted, the pin is added, and the fixture and config exist, the
focused test command reports all tests passing and the one-shot demonstration
command prints the dirty-tree violations with `exit=1`.

No `pytest-bdd` scenario is required because the task adds no user interaction
behaviour. No `syrupy` snapshot is required because no output format is
introduced. No Hypothesis or CrossHair property test is required because no
adapter invariant over arbitrary inputs is implemented. No Verus proof is
required because the task introduces no Rust extension and no new contractual
business logic.

## Idempotence and recovery

All read and validation commands are safe to rerun. Re-running the tests and
quality gates does not change the worktree apart from repository-ignored caches.

If `make fmt` changes unrelated files, inspect `git diff` immediately and
restore unrelated churn unless the user approves keeping it.

If a validation command fails, inspect its `/tmp` log, make the smallest
related fix, and rerun only the failed gate before rerunning the full sequence.

If `uv tool run` cannot fetch hecate (network restriction, removed SHA, or
interpreter unavailability), the fixture test must skip with a clear reason
rather than hang or emit an inscrutable traceback; record the unavailability in
the Decision Log and, if the demonstration evidence cannot be captured even
once, stop and escalate per the Tolerances.

If the branch push fails because the remote branch already exists, inspect the
remote with `git fetch origin`, `git status --short --branch`, and
`git branch -vv`. Do not force-push unless explicitly approved. If the draft
pull request already exists, update its title and body rather than opening a
duplicate. If the branch must be renamed after the pull request exists, use
GitHub's branch-rename flow so the pull request follows the rename rather than
renaming locally and pushing.

## Artefacts and notes

The production `[tool.hecate]` configuration that ADR-004 documents (for task
1.2.3 to commit against the real tree; the exact external import names are
verified during implementation) is:

```toml
[tool.hecate]
root_packages = ["prosidy_darn"]
include_external_packages = true

# Order matters: specific prefixes before general ones.
[[tool.hecate.groups]]
name = "domain"
prefixes = ["prosidy_darn.domain"]
allowed = ["domain", "ports"]

[[tool.hecate.groups]]
name = "ports"
prefixes = ["prosidy_darn.ports"]
allowed = ["ports", "domain"]

[[tool.hecate.groups]]
name = "application"
prefixes = ["prosidy_darn.application"]
allowed = ["application", "domain", "ports"]

[[tool.hecate.groups]]
name = "adapters"
prefixes = ["prosidy_darn.adapters"]
allowed = ["adapters", "application", "ports", "domain", "cyclopts", "rich", "markdown_parser", "delivery"]

[[tool.hecate.groups]]
name = "config"
prefixes = ["prosidy_darn.config"]
allowed = ["config", "adapters", "application", "ports", "domain", "cyclopts", "rich", "markdown_parser", "delivery"]

# External frameworks and infrastructure, banned from domain/application/ports
# by their absence from those groups' allowed lists. Each external group's
# prefix is the top-level IMPORT name, verified against the installed package
# during implementation. Every group named in an "allowed" list above is defined
# below, so the policy is self-consistent.
[[tool.hecate.groups]]
name = "cyclopts"
prefixes = ["cyclopts"]
allowed = ["cyclopts"]

[[tool.hecate.groups]]
name = "rich"
prefixes = ["rich"]
allowed = ["rich"]

[[tool.hecate.groups]]
name = "markdown_parser"
prefixes = ["mdast"]
allowed = ["markdown_parser"]

# Illustrative HTTP/webhook client for delivery sinks; confirm the actual import
# name when task 4.3.3 selects the delivery library.
[[tool.hecate.groups]]
name = "delivery"
prefixes = ["httpx"]
allowed = ["delivery"]
```

The Makefile tool reference to add (pin the full SHA resolved at implementation
time):

```make
# Resolved with:
#   git ls-remote https://github.com/leynos/hecate.git HEAD
HECATE_REF ?= 46f8c8798e7a80a3a1ab5a13c2a000a4423ffc12
# hecate is git-ref-only: the PyPI name "hecate" is an unrelated project.
HECATE_SPEC = git+https://github.com/leynos/hecate.git@$(HECATE_REF)
HECATE = $(UV_ENV) uv tool run --python 3.14 --from '$(HECATE_SPEC)' hecate
```

Implementation resolved `HECATE_REF` to
`46f8c8798e7a80a3a1ab5a13c2a000a4423ffc12`.

One-shot dirty-fixture evidence captured on 2026-06-15:

```plaintext
fixture_pkg.fixture_domain.adapter_breach -> fixture_pkg.fixture_adapters.runtime
fixture_pkg.fixture_domain.external_breach -> pretend_framework
exit=1
```

Firecrawl research evidence:

- `https://github.com/leynos/hecate` and its `docs/configuration.md`: the
  `[tool.hecate]` schema, `include_external_packages`, `ignore_imports`, barrel
  expansion, `--format json`, and exit codes 0/1/2.
- `https://pypi.org/pypi/hecate/json`: the PyPI `hecate` name belongs to an
  unrelated ncurses CLI tester.
- `https://import-linter.readthedocs.io/` and
  `https://pypi.org/project/import-linter/`: import-linter 2.11, BSD-2,
  supports the project's Python 3.14 target, `forbidden` and `layers` contracts,
  `include_external_packages`, `lint-imports`.
- `https://docs.gauge.sh/` and `https://github.com/gauge-sh/tach`: tach module
  and external-dependency enforcement via `tach.toml`.
- `https://docs.astral.sh/ruff/rules/#flake8-tidy-imports-tid`: TID251
  `banned-api` is a global table without per-source-module direction.
- Ford, Parsons, and Kua, _Building Evolutionary Architectures_: the
  architecture-fitness-function concept underpinning the ADR rationale.

## Interfaces and dependencies

This task introduces no runtime interface and no Python dependency. It adds a
pinned tool reference (consumed only by the demonstration test and, later, by
task 1.2.3's gate) and documents the future port and package boundary the
technical design already describes.

The checker contract that later tasks rely on is:

- the command `hecate check --config <path> --format json`;
- exit code 0 (no violations), 1 (violations found), 2 (configuration or input
  error);
- JSON output identifying each violating module, its group, and the forbidden
  target, asserted on by module-dotted identifiers rather than filesystem paths;
- configuration through `[tool.hecate]` groups with `name`, `prefixes`, and
  `allowed`, plus `include_external_packages` and `ignore_imports`.

The fallback contract, if hecate must be replaced, is import-linter 2.11 behind
the same `make check-imports` seam: a `forbidden` contract with
`source_modules = ["prosidy_darn.domain", "prosidy_darn.application", "prosidy_darn.ports"]`,
`forbidden_modules` listing the adapter packages plus `cyclopts`, `rich`, and
the parser and renderer packages, and `include_external_packages = True`.

## Revision note

Initial draft created on 2026-06-09. It captures the repository findings, the
Firecrawl-backed tooling research, the six-member Logisphere
community-of-experts review, the approval gate, the test-first milestones
(documentation-contract tests and a subprocess fixture demonstration), the
validation commands, and the pull-request requirements for roadmap item 1.1.3.
Implementation must not start until the user explicitly approves the plan.

Revised on 2026-06-09 after review feedback that the project targets Python
>=3.14 and any reference to an earlier interpreter is an error. Reframed the
out-of-process hecate rationale around tool isolation and the ADR-008 PyPy tier
rather than the CI interpreter version. Later implementation verified that
`.github/workflows/ci.yml` and `.github/workflows/release.yml` already pin
Python 3.14, so Milestone 6a is a verification step rather than a workflow
edit. This does not change the import-boundary decision or the demonstration
design.

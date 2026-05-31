# Create baseline developer docs and ADR locations

This ExecPlan (execution plan) is a living document. The sections `Constraints`,
`Tolerances`, `Risks`, `Progress`, `Surprises & Discoveries`, `Decision Log`,
and `Outcomes & Retrospective` must be kept up to date as work proceeds.

Status: Closed

## Purpose / big picture

Roadmap task 1.0.1 prepares Prosidy Darn contributors to implement the rest of
Phase 1 without guessing where architectural decisions live or how local checks
should be run. After this work is approved and implemented, a maintainer can
open `docs/developers-guide.md` and see the hexagonal package layout, quality
gates, testing expectations, documentation update rules, and links to the ADR
locations that block Phase 1 work.

This plan was approved and implemented. The developer guide and ADR placeholder
files now exist, and the roadmap entry has been marked complete.

The observable result is documentation, not runtime behaviour. Success is
visible when:

- `docs/developers-guide.md` exists and points maintainers at the package
  boundaries from `docs/prosidy-darn-technical-design.md`.
- `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`,
  `docs/adr-003-profile-rule-expression-policy.md`, and
  `docs/adr-004-import-boundary-fitness-check.md` exist as proposed decision
  locations.
- The roadmap and developers' guide make those ADR paths discoverable.
- Documentation and existing Python quality gates pass.

## Context and citations

The roadmap defines task 1.0.1 as the gate for maintainer-facing guidance. It
requires `docs/developers-guide.md`, stable initial ADR locations under
`docs/`, and discoverable ADR paths from the roadmap and developers' guide.

The technical design is the source of truth for this task:

- Section 4 defines the hexagonal architecture and the dependency rule.
- Section 5 names the driving and driven ports.
- Section 9 gives the proposed package layout.
- Section 16 defines the verification strategy and import-boundary fitness
  function.
- Section 18 lists the open decisions that need ADR locations.

The documentation style guide defines Markdown style, ADR names, and ADR
sections. ADR-006 scopes the Phase 1 test matrix to import-boundary checks,
public import tests, developer documentation checks, and ADR link validation.

## Constraints

This task is documentation-first. It must not implement domain segmentation,
CLI commands, parser adapters, renderers, profile storage, delivery sinks, or
semantic-scoring behaviour.

Do not add new runtime or development dependencies in this task. Roadmap task
1.2.2 owns adding `pytest-bdd`, `syrupy`, and Hypothesis to the development
dependency group. Until that task lands, this task uses the existing `pytest`
dependency for documentation and link validation tests.

Keep the architecture hexagonal in the developer guide. The guide must state
that `prosidy_darn.domain` and `prosidy_darn.application` must not import
adapters, Cyclopts, parser packages, HTTP clients, filesystem delivery code, or
vendor libraries.

Do not mark ADR-002, ADR-003, or ADR-004 as accepted unless their decisions are
actually resolved. In this task they are proposed placeholders that create
stable review locations for later Phase 1 tasks.

Do not change user-facing library or command-line behaviour. If
`docs/users-guide.md` changes, the change must be limited to consistency or
cross-reference updates, not new behaviour.

Use British English with Oxford spelling, follow
`docs/documentation-style-guide.md`, wrap Markdown paragraphs at 80 columns,
and provide a language identifier for every fenced code block.

Do not mark roadmap item 1.0.1 done until the implementation, validation,
commit, push, and draft pull request for the approved plan are complete.

## Tolerances

Stop and ask for direction if implementing the approved plan requires changes
outside these paths:

- `docs/developers-guide.md`
- `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`
- `docs/adr-003-profile-rule-expression-policy.md`
- `docs/adr-004-import-boundary-fitness-check.md`
- `docs/roadmap.md`
- `docs/users-guide.md`
- `docs/prosidy-darn-technical-design.md`
- `tests/test_developer_docs.py`

Stop and ask for direction if more than 350 net lines of documentation or more
than 120 net lines of test code are needed. This task should establish
locations and contributor guidance, not settle every Phase 1 decision.

Stop and ask for direction if any existing accepted ADR must be rewritten
beyond adding a discoverability link.

Stop and ask for direction if satisfying validation requires adding
`pytest-bdd`, `syrupy`, Hypothesis, CrossHair, Verus, or Vidai Mock as a
dependency in this task. Those tools remain documented expectations for later
surfaces unless the user explicitly expands 1.0.1.

Stop and ask for direction if any quality gate still fails after three focused
fix attempts.

Stop and ask for direction if Markdown formatting rewrites unrelated files.
Either restore unrelated churn or document why it is unavoidable before
continuing.

## Risks

Risk: The new developer guide could drift from the technical design's package
layout. Severity: medium. Likelihood: medium. Mitigation: Mirror the package
table from section 9, link back to the design, and add a test that checks key
ADR paths are discoverable from the developer guide.

Risk: Proposed ADR placeholders could look like accepted decisions. Severity:
high. Likelihood: medium. Mitigation: Give ADR-002, ADR-003, and ADR-004
`Proposed` status, include a clear "decision pending" outcome, and state which
roadmap task owns acceptance.

Risk: The user's broad test-tool requirements could be interpreted as adding
all future test dependencies in this documentation task. Severity: medium.
Likelihood: medium. Mitigation: Follow ADR-006. Use existing `pytest` checks
for this task, and write the developer guide so future tasks know when to use
`pytest-bdd`, `syrupy`, Hypothesis, CrossHair, Verus, and Vidai Mock.

Risk: Developers may not know when Vidai Mock applies. Severity: low.
Likelihood: medium. Mitigation: Add a developer-guide note that behavioural
tests for future inference or model-facing adapters must use Vidai Mock, but
state that 1.0.1 does not introduce an inference service boundary.

Risk: Roadmap item 1.0.1 could be marked done before implementation approval.
Severity: medium. Likelihood: low. Mitigation: Keep this ExecPlan in `DRAFT`
status until approved. Mark the roadmap checkbox only during the approved
implementation close-out.

## Milestone 1: Prepare branch and baseline evidence

Confirm the branch name:

```bash
git branch --show-current
```

If the branch is not `1-0-1-baseline-developer-docs-and-initial-adr-files`,
rename it before implementation work:

```bash
git branch -m 1-0-1-baseline-developer-docs-and-initial-adr-files
```

Inspect the current worktree:

```bash
git status --short --branch
```

Read these files before editing:

- `docs/roadmap.md`
- `docs/prosidy-darn-technical-design.md`
- `docs/documentation-style-guide.md`
- `docs/adr-001-markdown-parser-boundary.md`
- `docs/adr-006-test-matrix-phase-scope.md`
- `docs/adr-007-cli-observability-scope.md`
- `docs/users-guide.md`
- `Makefile`

Acceptance: the implementer can state which existing ADRs already exist, which
ADR paths are missing, and which Makefile targets validate this change.

## Milestone 2: Add failing documentation checks first

Create `tests/test_developer_docs.py` before creating the new documentation.
The tests should use only the Python standard library and `pytest`.

Add tests that initially fail because the developer guide and placeholder ADRs
do not yet exist. The tests should verify:

- `docs/developers-guide.md` exists.
- The developer guide links to every initial Phase 1 ADR location:
  `docs/adr-001-markdown-parser-boundary.md`,
  `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`,
  `docs/adr-003-profile-rule-expression-policy.md`, and
  `docs/adr-004-import-boundary-fitness-check.md`.
- Each linked ADR file exists.
- `docs/roadmap.md` mentions the same ADR paths.
- The developer guide mentions the Phase 1 quality gates:
  `make check-fmt`, `make typecheck`, `make lint`, `make test`,
  `make markdownlint`, and `make nixie`.

Run the focused test and confirm it fails for the expected missing files:

```bash
UV_CACHE_DIR=.uv-cache UV_TOOL_DIR=.uv-tools uv run pytest \
  tests/test_developer_docs.py -v
```

Acceptance: the new test fails because the planned documentation is missing,
not because of syntax errors, import errors, or environmental failures.

## Milestone 3: Write the developer guide

Create `docs/developers-guide.md` using the documentation style guide. It
should be maintainer-facing and should avoid duplicating the entire technical
design.

Include these sections:

- Development overview: state that the technical design is authoritative and
  that the roadmap sequences implementation.
- Hexagonal package layout: list the planned packages from section 9 of the
  technical design and explain the inward dependency rule in plain language.
- Ports, adapters, and composition root: identify `prosidy_darn.config` as the
  composition root and explain that adapters implement ports instead of calling
  each other directly.
- Local quality gates: name the Makefile targets and explain when to run each
  one.
- Testing expectations by phase: summarize ADR-006, including `pytest` for
  current documentation checks, `pytest-bdd` for later behavioural scenarios,
  `syrupy` for stable output snapshots, and Hypothesis or a bounded checker for
  future invariants over generated inputs or state transitions.
- Inference-service testing: state that future model-facing or inference
  adapters must use Vidai Mock for behavioural tests, including deterministic
  success and failure cases.
- Documentation update rules: state when to update `docs/users-guide.md`, the
  technical design, component architecture docs, and ADRs.
- ADR locations: link to ADR-001 through ADR-004, plus ADR-006 and ADR-007 as
  already accepted scope constraints.

Acceptance: a contributor can read the developer guide and know where to place
domain, application, adapter, and composition-root code in later tasks.

## Milestone 4: Add proposed ADR locations

Create these files under `docs/`:

- `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`
- `docs/adr-003-profile-rule-expression-policy.md`
- `docs/adr-004-import-boundary-fitness-check.md`

Each file must follow the ADR structure in `docs/documentation-style-guide.md`.
Because task 1.0.1 creates locations but does not resolve the decisions, use
`Proposed` status and state the owning roadmap task:

- ADR-002 is resolved by roadmap task 1.1.2.
- ADR-003 is resolved by roadmap task 1.1.4.
- ADR-004 is resolved by roadmap task 1.1.3.

Each placeholder ADR should include:

- Status.
- Date.
- Context and problem statement.
- Decision drivers.
- Options to be considered later.
- Decision outcome / proposed direction, explicitly saying the decision is
  pending.
- Consequences of leaving the decision unresolved until the owning task.

Acceptance: the files are useful review locations without pretending that
future design decisions have already been made.

## Milestone 5: Update discoverability links

Update `docs/roadmap.md` only if needed to keep task 1.0.1 discoverability
clear. The roadmap already lists ADR-001 through ADR-004, ADR-006, and ADR-007,
so the expected implementation change is to mark item 1.0.1 done only after all
gates pass.

Review `docs/users-guide.md`. Do not add maintainer-only package layout detail
unless the file already needs a consistency correction. If it changes, keep the
change user-facing and avoid documenting internal architecture as public API.

Review `docs/prosidy-darn-technical-design.md`. If the developer guide
introduces a new maintainer convention not already captured in the design,
either add a small cross-reference or record why no design update is needed in
this ExecPlan's `Decision Log`.

Acceptance: ADR paths are discoverable from both `docs/roadmap.md` and
`docs/developers-guide.md`, and user-facing docs do not advertise new behaviour.

## Milestone 6: Validate sequentially

Run formatting first because documentation changes may need wrapping:

```bash
make fmt 2>&1 | tee \
  /tmp/fmt-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
```

Then run all requested and documentation-specific gates sequentially:

```bash
make check-fmt 2>&1 | tee \
  /tmp/check-fmt-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
make markdownlint 2>&1 | tee \
  /tmp/markdownlint-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
make nixie 2>&1 | tee \
  /tmp/nixie-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
make lint 2>&1 | tee \
  /tmp/lint-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
make typecheck 2>&1 | tee \
  /tmp/typecheck-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
make test 2>&1 | tee \
  /tmp/test-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
```

Do not run these gates in parallel. If a gate fails because of missing external
tools or sandbox access, rerun the same command with elevated permissions
rather than changing the repository to work around the environment.

Acceptance: every listed command exits successfully, and the focused
documentation test passes as part of `make test`.

## Milestone 7: Close out, commit, push, and open draft PR

After validation passes, update this ExecPlan's living sections:

- Mark implementation milestones complete in `Progress`.
- Record unexpected findings in `Surprises & Discoveries`.
- Record validation outcomes in `Outcomes & Retrospective`.

Mark roadmap item 1.0.1 done in `docs/roadmap.md`. Re-run any gates affected by
that edit, at least:

```bash
make fmt 2>&1 | tee \
  /tmp/fmt-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
make markdownlint 2>&1 | tee \
  /tmp/markdownlint-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
make nixie 2>&1 | tee \
  /tmp/nixie-prosidy-darn-1-0-1-baseline-developer-docs-and-initial-adr-files.out
```

Commit with a file-based commit message. Do not use `git commit -m`.

Push the branch and set upstream tracking:

```bash
git push -u origin 1-0-1-baseline-developer-docs-and-initial-adr-files
```

Create a draft pull request. The title must include the roadmap item number:

```plaintext
Create baseline developer docs and ADR locations (1.0.1)
```

The PR summary must mention this ExecPlan:
`docs/execplans/1-0-1-baseline-developer-docs-and-initial-adr-files.md`.

Acceptance: the pushed branch tracks
`origin/1-0-1-baseline-developer-docs-and-initial-adr-files`, the draft PR
exists, and the PR description identifies the implementation as approved
ExecPlan work.

## Progress

- [x] 2026-05-10: Read `AGENTS.md`, the roadmap, technical design,
  documentation style guide, existing ADRs, Makefile gates, users' guide, and
  package/test layout.
- [x] 2026-05-10: Created context pack `pk_qlc7scyu` for the Wyvern planning
  review team with roadmap, design, style, ADR, and gate evidence.
- [x] 2026-05-10: Received Wyvern architecture/doc-scope review and folded the
  deliverable recommendations into this draft.
- [x] 2026-05-10: Renamed the local planning branch to
  `1-0-1-baseline-developer-docs-and-initial-adr-files`.
- [x] 2026-05-10: Drafted the pre-implementation ExecPlan.
- [x] 2026-05-10: Received explicit user approval to implement the plan.
- [x] 2026-05-10: Added `tests/test_developer_docs.py` and confirmed the
  focused test fails for the expected missing developer guide and ADR
  placeholder files.
- [x] 2026-05-10: Ran `coderabbit review --agent` after the Milestone 2 test
  commit. The service failed before producing review findings because the
  account is out of usage credits, so there were no concerns to clear.
- [x] 2026-05-10: Created `docs/developers-guide.md` and proposed ADR
  placeholders for ADR-002, ADR-003, and ADR-004.
- [x] 2026-05-10: Re-ran `uv run pytest tests/test_developer_docs.py -v`;
  all 5 documentation contract tests passed.
- [x] 2026-05-10: Ran `coderabbit review --agent` after the developer guide
  and ADR placeholder commit. The service again failed before producing review
  findings because the account is out of usage credits, so there were no
  concerns to clear.
- [x] 2026-05-10: Reviewed roadmap, users' guide, and technical design
  discoverability. The roadmap already names ADR-001 through ADR-004, the
  users' guide needs no change because no user-facing behaviour changed, and
  the technical design already covers the conventions summarized in the
  developer guide.
- [x] 2026-05-10: Ran final gates. `make check-fmt`, `make markdownlint`,
  `make nixie`, `make lint`, `make typecheck`, and `make test` passed.
- [x] 2026-05-10: Observed `make fmt` still fails because `mdformat-all`
  rewrites existing design-stage review tables into a form that
  `markdownlint --fix` reports as MD060. The final checking gates pass after
  restoring unrelated formatter churn.
- [x] 2026-05-10: Marked roadmap item 1.0.1 done.
- [x] 2026-05-10: Ran a final `coderabbit review --agent` attempt after
  close-out. It failed before producing review findings because the account is
  still out of usage credits.
- [x] 2026-05-10: Committed the implementation, pushed the branch, and updated
  the draft PR description with the implementation summary and validation
  evidence.

## Surprises & Discoveries

- ADR-001, ADR-006, and ADR-007 already exist. Task 1.0.1 therefore needs to
  create ADR-002 through ADR-004 as proposed locations, not all initial ADRs
  from scratch.
- The current project has only the package smoke-test surface. There is no CLI,
  renderer, inference service, parser adapter, or output format for
  `pytest-bdd`, `syrupy`, Hypothesis, CrossHair, Verus, or Vidai Mock to
  exercise in this task.
- The Makefile has separate Markdown gates, `make markdownlint` and
  `make nixie`, in addition to the user's requested Python gates.
- `coderabbit review --agent` is installed, but the service currently cannot
  return reviews because the account is out of usage credits.
- `make fmt` is not currently idempotent for the whole repository because it
  rewrites existing wide tables in
  `docs/prosidy-darn-logisphere-design-stage-review.md` into a form that
  `markdownlint --fix` still rejects with MD060 table-column-style errors.

## Decision Log

- 2026-05-10: Keep this plan pre-implementation and `DRAFT` because the user
  explicitly stated that the plan must be approved before it is implemented.
  Consequence: only the ExecPlan itself is created in the planning pass.
- 2026-05-10: Scope validation for the implementation to existing `pytest`
  documentation checks plus Makefile gates. Rationale: ADR-006 limits Phase 1
  to developer-doc checks and ADR link validation, while roadmap task 1.2.2
  owns adding `pytest-bdd`, `syrupy`, and Hypothesis.
- 2026-05-10: Treat ADR-002, ADR-003, and ADR-004 as proposed placeholders.
  Rationale: roadmap tasks 1.1.2, 1.1.4, and 1.1.3 own the substantive
  decisions.
- 2026-05-10: Document Vidai Mock as a future inference-adapter behavioural
  testing requirement rather than adding it to this task. Rationale: task 1.0.1
  introduces no inference service boundary.
- 2026-05-10: Begin implementation after explicit user approval. Rationale:
  the approval gate has been satisfied, so the plan status moves from `DRAFT` to
  `IN PROGRESS`.
- 2026-05-10: Continue after the Milestone 2 CodeRabbit invocation failed for
  billing credits. Rationale: the requested review command was run, the failure
  happened before any review findings were produced, and therefore there were
  no concerns to clear before the next milestone.
- 2026-05-10: Continue after the second CodeRabbit invocation failed for the
  same usage-credit limit. Rationale: no CodeRabbit review findings were
  returned, so no concerns can be cleared in this environment.

## Outcomes & Retrospective

Implementation is complete. The branch now adds:

- `docs/developers-guide.md`;
- proposed ADR locations for ADR-002, ADR-003, and ADR-004;
- `tests/test_developer_docs.py` for developer-guide and ADR discoverability;
- roadmap completion for item 1.0.1.

Validation passed for `make check-fmt`, `make markdownlint`, `make nixie`,
`make lint`, `make typecheck`, and `make test`. The test suite reports 9 tests
passing. `make fmt` was attempted and remains blocked by pre-existing
repository formatter churn described in `Surprises & Discoveries`. CodeRabbit
was invoked after the major milestones and at close-out, but the service
returned no review findings because the account is out of usage credits.

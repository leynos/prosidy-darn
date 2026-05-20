# Ratify the Markdown parser boundary Architecture Decision Record (ADR)

This ExecPlan (execution plan) is a living document. The sections `Constraints`,
 `Tolerances`, `Risks`, `Progress`, `Surprises & Discoveries`, `Decision Log`,
and `Outcomes & Retrospective` must be kept up to date as work proceeds.

Status: COMPLETE

## Purpose / big picture

Roadmap task 1.1.1 closes the first blocking parser decision for Prosidy Darn:
v1 must either ship one Markdown-aware parser plus a plain-text fallback, or
ship both `mdast` and a PyO3 `markdown-rs` range extractor immediately. This
task matters because parser choice sits behind a hexagonal outbound adapter
boundary. Once the CLI, domain segmenter, parser adapter and renderers depend
on parser ranges, changing the contract becomes expensive.

The repository already contains `docs/adr-001-markdown-parser-boundary.md`, and
that Architecture Decision Record (ADR) is marked accepted. This plan therefore
treats 1.1.1 as a validation and closure task, not as a fresh decision from a
blank page. After this plan is approved and implemented, a maintainer can
observe success by reading the accepted ADR, seeing roadmap item 1.1.1 marked
done, and running the documentation and Python quality gates without failures.

The implementation carried out from this plan must not build the parser
adapter. It records, validates and closes the decision that later parser work
must follow.

## Context and citations

`docs/roadmap.md` defines roadmap item 1.1.1 under "Ratify the v1 decisions
that block implementation". The item requires
`docs/adr-001-markdown-parser-boundary.md`, and its success condition is one
accepted ADR defining parser adapter order and fallback behaviour.

`docs/prosidy-darn-technical-design.md` is the architectural source of truth.
Section 4 defines the hexagonal architecture: domain and application code may
not import parser packages, PyO3 extension modules, Cyclopts, renderers, HTTP
clients or other adapters. Section 9 names the planned package boundary
`prosidy_darn.adapters.outbound.markdown`. Section 10 already states the parser
strategy: use `mdast` when version and compatibility probes pass, use plain
text only for non-Markdown or explicit degraded mode, and keep a PyO3
`markdown-rs` extractor as a contingency rather than a concurrent v1 adapter.
Section 18 records ADR-001 as the accepted decision for that open parser
question.

`docs/documentation-style-guide.md` defines ADR naming and content conventions.
ADRs live under `docs/`, use names such as
`adr-001-markdown-parser-boundary.md`, and should make status, context,
decision drivers, options, outcome, risks and rationale easy to review.

`docs/developers-guide.md` requires architecture and product decision changes
to update the relevant design or ADR document in the same change. It also
defines Phase 1 quality gates and points contributors at the roadmap as the
work sequence.

`docs/adr-006-test-matrix-phase-scope.md` scopes Phase 1 tests to
import-boundary checks, public import tests, developer documentation checks and
ADR link validation. It deliberately defers `pytest-bdd`, `syrupy`, Hypothesis
and parser compatibility tests until the product surfaces they validate exist.

External prior art gathered with Firecrawl confirms that `mdast` is a Markdown
abstract syntax tree format built on `unist`; the PyPI `mdast` package is
Python bindings for the `mdast` functionality of `markdown-rs`; and
`markdown-rs` is a Rust CommonMark parser exposing mdast output with positional
information. These findings support the existing ADR's shape: `mdast` is a
reasonable first Python-facing adapter candidate, while `markdown-rs` remains
the stronger fallback when source-position proof fails.

Relevant skills for this work are:

- `leta`, for semantic workspace navigation if code symbols must be inspected.
- `hexagonal-architecture` preserves the ADR's port-and-adapter
  boundary around parsing.
- `execplans` defines this document's approval gate before implementation.
- `firecrawl-mcp`, for checking current open-source parser prior art.
- `commit-message`, for file-based commit messages when this plan is
  implemented.
- `pr-creation` and `en-gb-oxendict-style`, for the draft pull request.

## Constraints

Do not implement parser runtime code in this task. The approved implementation
may change documentation and documentation-contract tests, but it must not
create `prosidy_darn.adapters.outbound.markdown`, add a `StructureParser`
implementation, add `mdast`, add PyO3, add Rust crates, or alter CLI behaviour.

Preserve the hexagonal dependency rule. The decision must keep parser packages
behind an outbound adapter and must not allow domain or application modules to
import `mdast`, PyO3 extension modules, `markdown-rs`, Cyclopts, renderers or
other infrastructure.

Do not add runtime or development dependencies for this roadmap item. The
project currently has no parser dependency in `pyproject.toml`, and roadmap
task 1.2.2 owns the dependency spine. If satisfying 1.1.1 appears to require
adding `mdast`, `pytest-bdd`, `syrupy`, Hypothesis, CrossHair, Verus or Rust
tooling, stop and escalate.

Keep the existing accepted ADR decision unless new evidence proves it is wrong.
Minor clarifications are allowed, but switching from "one Markdown-aware
adapter plus plain text" to "ship both `mdast` and PyO3 in v1" requires human
approval and a substantive ADR change.

Do not mark roadmap item 1.1.1 done until the approved implementation has added
validation evidence, passed the required gates, cleared CodeRabbit concerns,
been committed and been pushed.

Use British English with Oxford spelling. Follow
`docs/documentation-style-guide.md`: wrap Markdown paragraphs and bullets at 80
columns, wrap code blocks at 120 columns, use dash bullets, use footnote style
for references where needed, and give every fenced code block a language.

The plan must be approved before implementation begins. Silence is not approval.

## Tolerances

Stop and ask for direction if implementation of the approved plan requires
changes outside these paths:

- `docs/adr-001-markdown-parser-boundary.md`
- `docs/developers-guide.md`
- `docs/prosidy-darn-technical-design.md`
- `docs/roadmap.md`
- `docs/users-guide.md`
- `tests/test_developer_docs.py`

Stop and ask for direction if more than 180 net lines of documentation or more
than 80 net lines of test code are needed. This item closes an ADR decision; it
should not become a parser implementation slice.

Stop and ask for direction if the accepted decision in ADR-001 must change
materially, if a public API signature must be introduced, or if a new
dependency is required.

Stop and ask for direction if any quality gate still fails after three focused
fix attempts.

Stop and ask for direction if `make fmt` rewrites unrelated Markdown files or
source files. Restore unrelated churn before continuing, unless the user
explicitly accepts the broader formatting change.

Stop and ask for direction if CodeRabbit reports concerns that would require
parser implementation or dependency changes to resolve. For documentation-only
concerns, revise the plan or docs and rerun the relevant checks.

## Risks

Risk: The task already has an accepted ADR, so the implementer could duplicate
or churn a settled decision instead of validating it. Severity: medium.
Likelihood: medium. Mitigation: Treat the first milestone as evidence
gathering; only edit ADR-001 if the documentation and tests reveal a real gap.

Risk: The broad test-tool requirement could be over-applied to this Phase 1
documentation task. Severity: medium. Likelihood: medium. Mitigation: Follow
ADR-006. Use `pytest` documentation-contract tests for this item, and record
that `pytest-bdd`, `syrupy`, Hypothesis, CrossHair and Verus become relevant
only when corresponding behaviours, snapshots, input invariants or proof
surfaces exist.

Risk: Plain-text fallback might be documented too casually, weakening
Markdown-aware structural protection. Severity: high. Likelihood: medium.
Mitigation: Ensure ADR-001 and any docs state that plain text is for
non-Markdown or explicit degraded mode, and that Markdown input using it must
emit a degradation diagnostic.

Risk: The ADR could leak adapter choices into the domain contract. Severity:
high. Likelihood: low. Mitigation: Keep parser packages named only as adapter
implementations. The domain consumes source ranges and structural attributes,
not `mdast` nodes or Rust-specific types.

Risk: Roadmap closure could happen without automated evidence. Severity:
medium. Likelihood: medium. Mitigation: Add or extend
`tests/test_developer_docs.py` before marking the roadmap item done.

## Progress

- [x] (2026-05-18T22:32:17Z) Loaded the `leta`, `hexagonal-architecture`,
  `execplans`, `firecrawl-mcp`, `commit-message`, `pr-creation`, and
  `en-gb-oxendict-style` skills needed for planning, validation, commit, and
  pull request work.
- [x] (2026-05-18T22:32:17Z) Created a leta workspace for this repository.
- [x] (2026-05-18T22:32:17Z) Renamed the branch to
  `1-1-1-markdown-parser-boundary-adr`.
- [x] (2026-05-18T22:32:17Z) Used Wyvern read-only planning agents to inspect
  documentation scope, existing ADR state, Makefile gates, likely tests and
  implementation risks.
- [x] (2026-05-18T22:32:17Z) Used Firecrawl to check current `mdast`,
  `markdown-rs`, and PyPI `mdast` prior art.
- [x] (2026-05-18T22:32:17Z) Drafted this pre-implementation ExecPlan.
- [x] (2026-05-20T11:37:04+02:00) Received explicit user approval to
  implement the plan.
- [x] (2026-05-20T11:37:04+02:00) Added documentation-contract tests for
  ADR-001 acceptance, parser adapter order, fallback behaviour and roadmap
  closure.
- [x] (2026-05-20T11:37:04+02:00) Ran the focused documentation test and
  observed the expected failure: ADR-001 passed the new contract checks, while
  roadmap item 1.1.1 remained unchecked.
- [x] (2026-05-20T11:37:04+02:00) Marked roadmap item 1.1.1 done after
  validation evidence showed ADR-001 already satisfies the parser-boundary
  contract.
- [x] (2026-05-20T11:37:04+02:00) Reran the focused documentation test and
  confirmed all eight documentation-contract tests passed.
- [x] (2026-05-20T11:37:04+02:00) Ran `make fmt`; it surfaced unrelated
  pre-existing Markdown line-length findings and rewrote unrelated docs, so
  the unrelated formatter churn was restored.
- [x] (2026-05-20T11:37:04+02:00) Ran the final local gates successfully:
  `make check-fmt`, `make markdownlint`, `make nixie`, `make typecheck`,
  `make lint`, and `make test`.
- [x] (2026-05-20T11:37:04+02:00) Ran `coderabbit review --agent`;
  CodeRabbit completed with zero findings.
- [x] (2026-05-20T11:37:04+02:00) Committed the implementation as
  `ca2f8ef` and pushed it to
  `origin/1-1-1-markdown-parser-boundary-adr`.
- [x] (2026-05-20T11:37:04+02:00) Updated draft pull request
  `https://github.com/leynos/prosidy-darn/pull/11` with the implemented
  scope, validation evidence, ExecPlan reference and Lody session reference.

## Surprises & discoveries

- Observation: `docs/adr-001-markdown-parser-boundary.md` already exists and
  is marked accepted. Evidence: The file status says, "Accepted on 2026-05-09"
  and chooses Option B. Impact: Implementation should validate and close the
  existing decision rather than create a new ADR from scratch.
- Observation: The Python package layout is still scaffold-level.
  Evidence: Repository inspection found `prosidy_darn/__init__.py`,
  `prosidy_darn/_runtime.py`, and `prosidy_darn/pure.py`, but no domain,
  application, ports, or adapter packages yet. Impact: This roadmap item must
  not introduce parser adapters ahead of the package-boundary work.
- Observation: `pyproject.toml` does not yet declare `mdast`, `markdown-rs`,
  Cyclopts, Rich, `pytest-bdd`, `syrupy` or Hypothesis. Evidence: Repository
  inspection found an empty runtime dependency list and a small development
  stack centred on `pytest`, Ruff and type checking. Impact: Tests for this
  item should stay at documentation-contract level.
- Observation: Firecrawl found that PyPI `mdast` 0.2.1 was released on
  2025-03-28 and provides Python bindings to `markdown-rs`, while the
  `markdown-rs` repository describes byte-accounted parsing with positional
  information. Evidence: Firecrawl scraped `https://pypi.org/project/mdast/` and
   `https://github.com/wooorm/markdown-rs`. Impact: The existing ADR's
  version/probe gate remains important; the package exists, but source-range
  correctness must still be proven locally.
- Observation: The new focused documentation-contract test did not require an
  ADR edit. Evidence: `tests/test_developer_docs.py` passed the ADR acceptance,
  adapter order, probe-gate, PyO3 contingency and degraded-fallback assertions
  before any ADR changes; only roadmap closure failed. Impact: Implementation
  can avoid ADR churn and close the roadmap item after validation evidence is
  present.
- Observation: `make fmt` can fail after rewriting unrelated Markdown files
  because it invokes `markdownlint --fix` across the whole repository and then
  reports existing line-length issues in docs outside this task's scope.
  Evidence: the formatter reported MD013 findings in the technical design,
  scripting standards and design-stage review docs. Impact: Restore unrelated
  churn and rely on `make check-fmt` plus the scoped diff to verify this
  change.

## Decision log

- Decision: Treat 1.1.1 as a documentation validation and closure task.
  Rationale: ADR-001 already exists and is accepted, while the roadmap checkbox
  remains open. The missing work is evidence, alignment, and task closure.
  Date/Author: 2026-05-18T22:32:17Z / Codex.
- Decision: Do not add `mdast`, PyO3, Rust crates or parser packages in this
  task. Rationale: The roadmap separates v1 decision ratification from
  dependency and parser implementation work, and the hexagonal boundary should
  be established before adapters exist. Date/Author: 2026-05-18T22:32:17Z /
  Codex.
- Decision: Use `pytest` documentation-contract tests, not `pytest-bdd`,
  `syrupy`, Hypothesis, CrossHair or Verus, for this item. Rationale: ADR-006
  scopes Phase 1 tests to documentation and link contracts until parser
  behaviour, output snapshots, input invariants or proof-worthy logic exist.
  Date/Author: 2026-05-18T22:32:17Z / Codex.

## Outcomes & retrospective

ADR-001 did not need clarification. The implementation added
documentation-contract tests that assert ADR-001 is accepted, records the v1
parser adapter order, keeps PyO3 as a contingency, requires degradation
reporting for Markdown plain-text fallback and closes roadmap item 1.1.1. The
roadmap item is now marked done. Local validation passed through
`make check-fmt`, `make markdownlint`, `make nixie`, `make typecheck`,
`make lint` and `make test`. CodeRabbit reported zero findings.

Final outcome: commit `ca2f8ef` implements the documentation closure and draft
pull request 11 now describes the implemented scope and validation evidence.
This task intentionally introduced no parser code or new dependency.

## Context and orientation

Prosidy Darn is planned as a Python package using hexagonal architecture.
"Hexagonal architecture" means the domain owns business concepts and ports,
while adapters connect the outside world to those ports. For this task, the
important boundary is the Markdown parser port: parser packages are outbound
adapter details, not domain dependencies.

The key files are:

- `docs/roadmap.md`: the ordered implementation roadmap. Item 1.1.1 is
  currently the Markdown parser boundary ADR task.
- `docs/adr-001-markdown-parser-boundary.md`: the accepted ADR that chooses
  one Markdown-aware parser adapter plus plain text for v1.
- `docs/prosidy-darn-technical-design.md`: the authoritative technical design.
  Sections 4, 9, 10 and 18 are directly relevant.
- `docs/developers-guide.md`: maintainer-facing implementation guidance,
  quality gates and documentation update rules.
- `docs/users-guide.md`: user-facing behaviour. It changes only if the
  approved implementation changes user-visible behaviour, which this task
  should not.
- `tests/test_developer_docs.py`: current documentation-contract tests.
- `Makefile`: local quality gates. Prefer its targets over direct tool
  invocation.

Important terms:

- "Markdown-aware parser" means a parser that returns structural source ranges
  for headings, paragraphs, lists, code blocks, emphasis and similar Markdown
  constructs.
- "Plain-text fallback" means segmentation without Markdown-aware structural
  protection. It is allowed for non-Markdown input or explicit degraded mode,
  and must report degradation when used for Markdown input.
- "Source range" means a half-open range over the original input text: the
  start offset is included, and the end offset is excluded.
- "`mdast`" means the Markdown abstract syntax tree format and, in this
  repository's ADR, the Python package selected only when version and runtime
  compatibility probes pass.
- "PyO3 `markdown-rs` range extractor" means a possible Rust-backed
  contingency that returns compact source ranges to Python if `mdast` cannot
  prove byte-accurate positions.

## Plan of work

Milestone 1 prepares the branch and confirms the baseline. Confirm the current
branch is `1-1-1-markdown-parser-boundary-adr`, inspect the worktree, and read
the roadmap, ADR-001, technical design, developer guide, documentation style
guide, ADR-006, tests and Makefile. If the branch is not named correctly,
rename it before editing. If the worktree contains unrelated changes, leave
them alone and avoid touching those files.

Milestone 2 adds failing documentation-contract tests first. Extend
`tests/test_developer_docs.py` with tests that prove roadmap item 1.1.1 cannot
be closed unless ADR-001 is accepted and states the selected parser order and
fallback behaviour. The tests should check for these observable facts:

- ADR-001 exists and is accepted.
- ADR-001 states that v1 ships one Markdown-aware parser adapter plus
  plain-text fallback.
- ADR-001 states that `mdast` is selected only when a version check and runtime
  compatibility probe pass.
- ADR-001 states that PyO3 `markdown-rs` is a contingency, not a concurrent v1
  adapter.
- ADR-001 states that plain-text fallback must report degraded Markdown
  structural protection when used for Markdown input.
- The roadmap item for 1.1.1 is marked done only when the ADR is accepted.

Run the focused test after adding it and confirm it fails for the expected
reason before changing docs. If the test already passes because the existing
ADR fully satisfies it, document that in `Surprises & Discoveries` and proceed
to Milestone 3 without forcing an artificial failure.

Milestone 3 aligns documentation. Review
`docs/adr-001-markdown-parser-boundary.md` against the new test and the
technical design. Make the smallest possible edit if the ADR lacks a required
closure detail. Review `docs/prosidy-darn-technical-design.md` and
`docs/developers-guide.md` for stale or conflicting wording. Update them only
if needed to keep the accepted decision discoverable and consistent. Avoid
duplicating the full ADR in other documents.

Milestone 4 updates task tracking. Mark item 1.1.1 in `docs/roadmap.md` done
only after the ADR and tests agree. Do not mark later parser, dependency, or
adapter tasks done. Do not update `docs/users-guide.md` unless Milestone 3
identifies a user-facing behaviour statement that must be corrected; this task
should normally have no user-facing behaviour change.

Milestone 5 validates the change. Run formatting checks, Markdown linting,
Mermaid validation, type checking, linting, and tests sequentially with `tee`
logs under `/tmp`. If a command fails, inspect the full log and make focused
fixes. Do not run quality gates in parallel.

Milestone 6 runs CodeRabbit review. Run `coderabbit review --agent` after the
documentation/test milestone has passed local gates. Address every actionable
concern within the scope of this plan. If CodeRabbit asks for parser code,
dependency additions or broader architecture changes, record the concern in
`Decision Log` and escalate instead of expanding scope silently.

Milestone 7 commits and opens the draft pull request. Use the `commit-message`
skill's file-based commit workflow. Push `1-1-1-markdown-parser-boundary-adr` to
 `origin/1-1-1-markdown-parser-boundary-adr` and set upstream tracking. Create
a draft pull request whose title includes `(1.1.1)`, whose summary links this
ExecPlan, and whose `## References` section includes the Lody session URL
derived from `echo ${LODY_SESSION_ID}`.

## Concrete steps

Run all commands from the repository root:

```bash
pwd
git branch --show-current
git status --short --branch
```

Expected branch output:

```plaintext
1-1-1-markdown-parser-boundary-adr
```

If the branch has not already been renamed, run:

```bash
git branch -m 1-1-1-markdown-parser-boundary-adr
```

Read the local context:

```bash
sed -n '70,90p' docs/roadmap.md
sed -n '1,140p' docs/adr-001-markdown-parser-boundary.md
sed -n '680,765p' docs/prosidy-darn-technical-design.md
sed -n '1,140p' tests/test_developer_docs.py
```

After adding tests, run the focused check:

```bash
UV_CACHE_DIR=.uv-cache UV_TOOL_DIR=.uv-tools uv run pytest \
  tests/test_developer_docs.py -v \
  | tee /tmp/pytest-developer-docs-$(basename "$(pwd)")-$(git branch --show-current).out
```

After documentation edits, run Markdown formatting if needed:

```bash
make fmt | tee /tmp/fmt-$(basename "$(pwd)")-$(git branch --show-current).out
```

Then run required gates sequentially:

```bash
make check-fmt | tee /tmp/check-fmt-$(basename "$(pwd)")-$(git branch --show-current).out
make markdownlint | tee /tmp/markdownlint-$(basename "$(pwd)")-$(git branch --show-current).out
make nixie | tee /tmp/nixie-$(basename "$(pwd)")-$(git branch --show-current).out
make typecheck | tee /tmp/typecheck-$(basename "$(pwd)")-$(git branch --show-current).out
make lint | tee /tmp/lint-$(basename "$(pwd)")-$(git branch --show-current).out
make test | tee /tmp/test-$(basename "$(pwd)")-$(git branch --show-current).out
```

Run CodeRabbit after local gates pass:

```bash
coderabbit review --agent \
  | tee /tmp/coderabbit-$(basename "$(pwd)")-$(git branch --show-current).out
```

Inspect changes:

```bash
git diff -- docs tests
git status --short --branch
```

Commit with a file-based message:

```bash
git add docs tests
COMMIT_MSG_DIR=$(mktemp -d)
cat > "$COMMIT_MSG_DIR/COMMIT_MSG.md" << 'ENDOFMSG'
Ratify Markdown parser boundary plan

Add the approved execution plan for closing roadmap item 1.1.1.
The plan keeps parser implementation out of scope until the
Markdown parser boundary ADR is validated and approved for closure.
ENDOFMSG
git commit -F "$COMMIT_MSG_DIR/COMMIT_MSG.md"
rm -rf "$COMMIT_MSG_DIR"
```

Push and set upstream tracking:

```bash
git push -u origin 1-1-1-markdown-parser-boundary-adr
```

Capture the Lody session:

```bash
echo ${LODY_SESSION_ID}
```

Create the draft pull request using a body file. The body must mention this
ExecPlan and include a final `## References` section with:

```plaintext
https://lody.ai/leynos/sessions/${LODY_SESSION_ID}
```

## Validation and acceptance

The approved implementation is accepted when all of these are true:

- `tests/test_developer_docs.py` verifies that ADR-001 is accepted and defines
  the parser adapter order, `mdast` probe gate, PyO3 contingency and degraded
  plain-text fallback behaviour.
- `docs/roadmap.md` marks item 1.1.1 done only after validation passes.
- `docs/adr-001-markdown-parser-boundary.md` remains accepted and continues to
  choose one Markdown-aware parser adapter plus one plain-text fallback for v1.
- The technical design and developer guide do not contradict ADR-001.
- No parser implementation, parser dependency, CLI behaviour or user-facing API
  is added by this task.
- `make check-fmt`, `make markdownlint`, `make nixie`, `make typecheck`,
  `make lint`, and `make test` all pass.
- `coderabbit review --agent` reports no unresolved in-scope concerns.
- The branch is pushed to
  `origin/1-1-1-markdown-parser-boundary-adr` and has a draft pull request
  whose title includes `(1.1.1)` and whose body links this ExecPlan.

No `pytest-bdd` behavioural scenario is required for this item because the
approved implementation does not add user interaction behaviour. No `syrupy`
snapshot is required because no output format is introduced or changed. No
Hypothesis or CrossHair property test is required because no parser invariant
over arbitrary inputs is implemented in this task. No Verus proof is required
because this task introduces no Rust extension and no new contractual business
logic.

## Idempotence and recovery

All read and validation commands are safe to rerun. Re-running tests and
quality gates should not change the worktree, except for caches ignored by the
repository.

If `make fmt` changes unrelated files, inspect `git diff` immediately. Restore
unrelated formatting churn unless the user approves keeping it.

If a validation command fails, inspect its `/tmp` log, make the smallest
related fix, and rerun only the failed gate before rerunning the full gate
sequence.

If the branch push fails because the remote branch already exists, inspect the
remote state with:

```bash
git fetch origin
git status --short --branch
git branch -vv
```

Do not force-push unless explicitly approved.

If the draft pull request already exists, update its title and body rather than
opening a duplicate.

## Artifacts and notes

Firecrawl evidence gathered during planning:

- `https://github.com/syntax-tree/mdast`: `mdast` represents Markdown as a
  syntax tree, implements `unist`, and covers CommonMark and GitHub Flavored
  Markdown.
- `https://github.com/wooorm/markdown-rs`: `markdown-rs` is a Rust CommonMark
  parser that exposes mdast output and positional information; the repository
  advertises complete CommonMark/GFM coverage and fuzz testing.
- `https://pypi.org/project/mdast/`: PyPI `mdast` 0.2.1 provides Python
  bindings for the `mdast` functionality of `markdown-rs` and ships wheels for
  common Linux x86-64 and aarch64 targets.

Wyvern planning evidence:

- ADR-001 already exists and is accepted, so roadmap closure should validate
  the existing ADR rather than rewrite it wholesale.
- The repository has not yet introduced the final hexagonal package layout or
  parser dependencies.
- The Makefile exposes `check-fmt`, `markdownlint`, `nixie`, `typecheck`,
  `lint`, and `test` gates that should be run sequentially.

## Interfaces and dependencies

This task introduces no runtime interface and no dependency. It preserves the
future parser boundary described by the technical design:

```python
class StructureParser(Protocol):
    def parse(self, source_text: str) -> ParsedStructure: ...
```

The exact names and dataclasses for that future port are out of scope for this
task. Later implementation must keep the port in the domain or application
contract layer and place concrete parser implementations under an outbound
adapter package such as `prosidy_darn.adapters.outbound.markdown`.

The final accepted decision that later work must honour is:

- v1 has one Markdown-aware parser adapter plus one plain-text fallback;
- `mdast` is the first Markdown-aware adapter only when its supported version
  range and runtime compatibility probe pass;
- PyO3 `markdown-rs` is a contingency if `mdast` cannot provide stable source
  ranges;
- plain-text fallback is explicit degraded behaviour for Markdown input;
- the parser layer returns source ranges and structural attributes only, and
  never renders Markdown back to text.

## Revision note

Initial draft created on 2026-05-18. It captures repository findings, Wyvern
planning feedback, Firecrawl prior-art checks, approval gating, implementation
milestones, validation commands and pull-request requirements for roadmap item
1.1.1. Implementation must not start until the user explicitly approves the
plan.

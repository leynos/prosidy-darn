# Record the token-limit and semantic-scoring dependency policy

This ExecPlan (execution plan) is a living document. The sections `Constraints`,
`Tolerances`, `Risks`, `Progress`, `Surprises & Discoveries`, `Decision Log`,
and `Outcomes & Retrospective` must be kept up to date as work proceeds.

Status: COMPLETED

## Purpose / big picture

Roadmap task 1.1.2 closes the second blocking dependency decision for Prosidy
Darn: v1 must decide which token counter the project names as the first
`TokenCounter` adapter and how embedding adapters stay out of the core import
path. This task matters because both ports sit behind a hexagonal outbound
adapter boundary. Once `TokenCounter` and `SemanticScorer` adapters land,
changing the optional-dependency policy becomes expensive — every later runtime
or development dependency choice in task 1.2.2 and Phase 5 semantic scoring
inherits the policy chosen here.

The repository already contains a stub
`docs/adr-002-tokenizer-and-semantic- scoring-policy.md` whose status is
"Proposed" and whose decision outcome is "Pending". This plan therefore treats
1.1.2 as a decision-finalization and closure task. After this plan is approved
and implemented, a maintainer can observe success by reading the accepted
ADR-002, seeing roadmap item 1.1.2 marked done, running the documentation and
Python quality gates without failures, and confirming that no optional
tokenizer, embedding, or model package has been added to `pyproject.toml` yet.

The implementation carried out from this plan must not build a `TokenCounter`
adapter, a `SemanticScorer` adapter, or any package skeleton. It records,
validates, and closes the policy that later optional-dependency and adapter
work must follow.

## Context and citations

`docs/roadmap.md` defines roadmap item 1.1.2 under "Ratify the v1 decisions
that block implementation". The item requires
`docs/adr-002-tokenizer-and-semantic-scoring-policy.md`, lists 1.0.1 and 1.1.1
as prerequisites, and declares success as: "optional dependencies can be
installed or omitted without changing the public segmentation API".

`docs/prosidy-darn-technical-design.md` is the architectural source of truth.
Section 4 keeps domain and application code free of adapter imports. Section
5.2 names `TokenCounter` and `SemanticScorer` as driven ports with disabled
default adapters and optional tokenizer or embedding adapters. Section 7.3
states that semantic-break rewards must never override hard structural
illegality. Section 9 names the planned package boundary as
`prosidy_darn.adapters.outbound` and warns that the core library must not
import optional heavy dependencies at module import time. Section 10 sets the
parser-policy precedent that ADR-002 follows for tokenizer and embedding
adapters. Section 17.3 schedules embedding-backed semantic scoring for the
"semantic scoring release" phase, not the MVP. Section 18 records the open
decision: "Which tokenizer should provide optional token limits".

`docs/adr-001-markdown-parser-boundary.md` already provides the precedent
template for an accepted parser-boundary ADR: status acceptance, decision
drivers, options table, decision outcome, goals and non-goals, migration plan,
risks, and architectural rationale.

`docs/adr-006-test-matrix-phase-scope.md` scopes Phase 1 tests to
import-boundary checks, public import tests, developer-doc checks, and ADR link
validation. It deliberately defers `pytest-bdd`, `syrupy`, Hypothesis,
CrossHair, and Verus until the product surfaces they validate exist. Semantic
scoring regression cases are scoped to Phase 5+ in that same ADR.

`docs/adr-007-cli-observability-scope.md` defines the v1 observability scope
that any later optional-dependency diagnostic surface must respect; missing
optional dependency warnings should appear through the same diagnostic channel
that CLI failures already use.

`docs/developers-guide.md` lists ADR-002 as a blocking Phase 1 decision and
requires architecture and product decision changes to update the relevant
design or ADR document in the same change. It defines Phase 1 quality gates and
points contributors at the roadmap as the work sequence.

`docs/documentation-style-guide.md` defines ADR naming and content conventions.
ADRs live under `docs/`, use names such as
`adr-002-tokenizer-and-semantic-scoring-policy.md`, and must include Status,
Date, Context and problem statement, Decision drivers, Options considered,
Decision outcome, Goals and non-goals, and Architectural rationale.

`tests/test_developer_docs.py` contains the documentation-contract tests for
ADR-001 (lines 90-132). The new ADR-002 contract tests must mirror that
pattern: status acceptance, required-phrase assertions over the policy text,
and roadmap closure linked to ADR acceptance.

External prior art gathered with Firecrawl supports the decision direction:

- `tiktoken` (OpenAI, MIT) ships a small native wheel (<1 MB), supports Python
  3.9+, exposes `tiktoken.get_encoding(name)` and
  `tiktoken.encoding_for_model(model)`, and bundles `cl100k_base` (GPT-4 /
  GPT-3.5-turbo) and `o200k_base` (GPT-4o / GPT-4o-mini). It is the
  conventional first-candidate token counter for small Python CLIs.
- `transformers` `AutoTokenizer` (Hugging Face, Apache 2.0) cannot be installed
  without the full `transformers` library; Hugging Face issue
  `huggingface/transformers#31043` documents this constraint. The full
  framework footprint disqualifies it as the first v1 candidate.
- `tokenizers` (Hugging Face, Apache 2.0) is a lighter Rust-backed BPE
  implementation via PyO3 but requires vocab and merges files at runtime,
  adding model-distribution surface that `tiktoken` does not.
- `sentence-transformers` (Apache 2.0) with the canonical
  `sentence-transformers/all-MiniLM-L6-v2` model is the conventional small
  local embedding adapter; the library wheel is light (~589 kB) but the
  recommended runtime stack pulls PyTorch ≥1.11, adding a multi-hundred-MB
  footprint. It must live behind an extra and behind the `SemanticScorer` port.
- PEP 621 `[project.optional-dependencies]` is the right surface for
  user-facing runtime extras like `tokenizer` and `semantic`. PEP 735
  `[dependency-groups]` is the right surface for development-only groups; it
  does not install the package or its runtime dependencies and is therefore not
  appropriate for optional adapter dependencies.
- `darn-it` 1.2.0 on PyPI ships `requires_dist: None` and bundles its
  tokenizer inside the Rust wheel, demonstrating that downstream consumers need
  not inherit a Python tokenizer dependency from chunking back-ends.
- Lazy-import patterns for optional dependencies in Python libraries
  consistently recommend importing inside the adapter only and raising a
  hint-bearing `ImportError` when missing. PEP 810 (explicit lazy imports) is
  not yet usable.

Relevant skills for this work are:

- `leta`, for semantic workspace navigation if code symbols must be inspected.
- `hexagonal-architecture`, to preserve the ADR's port-and-adapter boundary
  around tokenization and semantic scoring.
- `execplans`, which defines this document's approval gate before
  implementation.
- `firecrawl`, for checking current open-source tokenizer and embedding prior
  art.
- `commit-message`, for file-based commit messages when this plan is
  implemented.
- `pr-creation` and `en-gb-oxendict`, for the draft pull request and British
  English with Oxford spelling.

## Constraints

Do not implement adapter runtime code in this task. The approved implementation
may change documentation and documentation-contract tests, but it must not
create `prosidy_darn.adapters.outbound.tokenizer`,
`prosidy_darn.adapters.outbound.semantic`, the `TokenCounter` protocol, the
`SemanticScorer` protocol, the `prosidy_darn.ports` module, or any adapter
implementation. It must not add `tiktoken`, `tokenizers`, `transformers`,
`sentence-transformers`, `torch`, or any other optional model or embedding
dependency to `pyproject.toml`.

Preserve the hexagonal dependency rule. The decision must keep optional
tokenizer and embedding packages behind outbound adapters and must not allow
domain or application modules to import `tiktoken`, `sentence_transformers`,
`torch`, `tokenizers`, `transformers`, or any model-provider client library at
module import time.

Do not add runtime or development dependencies for this roadmap item. Task
1.2.2 owns the v1 dependency spine for Cyclopts and Rich, and Phase 5 owns the
embedding-backed semantic scorer. If satisfying 1.1.2 appears to require adding
any tokenizer, embedding, model, or HTTP client dependency, stop and escalate.

Keep the public segmentation API unchanged. The policy must specify that
omitting optional extras must not change the public Python API or CLI surface;
only the diagnostic-bearing failure mode for missing optional dependencies may
differ.

Use PEP 621 `[project.optional-dependencies]` as the documented mechanism for
optional adapter extras. Do not document PEP 735 `[dependency-groups]` for
optional runtime extras; that mechanism is for development-only groups.

Default optional adapters must be disabled. Missing optional dependencies must
produce explicit, actionable diagnostics that name the extra to install, not
silent fall-through.

Use British English with Oxford spelling. Follow the documentation style guide:
wrap Markdown paragraphs and bullets at 80 columns, wrap code blocks at 120
columns, use dash bullets, give every fenced code block a language, and caption
every table.

The plan must be approved before implementation begins. Silence is not approval.

Do not mark roadmap item 1.1.2 done until the approved implementation has added
validation evidence, passed the required gates, cleared CodeRabbit concerns,
been committed, and been pushed.

## Tolerances

Stop and ask for direction if implementation of the approved plan requires
changes outside these paths:

- `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`
- `docs/developers-guide.md`
- `docs/prosidy-darn-technical-design.md`
- `docs/roadmap.md`
- `docs/users-guide.md`
- `tests/test_developer_docs.py`

Stop and ask for direction if more than 240 net lines of documentation or more
than 80 net lines of test code are needed. This item closes an ADR decision; it
should not become an adapter implementation slice.

Stop and ask for direction if any of these scope expansions become necessary:

- introducing a new public API signature, port protocol, or adapter module;
- adding a runtime, optional, or development dependency to `pyproject.toml`;
- defining `[project.optional-dependencies]` in `pyproject.toml` rather than
  documenting the future shape in ADR-002;
- adopting a tokenizer other than `tiktoken` as the first v1 candidate.

Stop and ask for direction if any quality gate still fails after three focused
fix attempts.

Stop and ask for direction if `make fmt` rewrites unrelated Markdown or source
files. Restore unrelated formatting churn before continuing, unless the user
explicitly accepts the broader formatting change.

Stop and ask for direction if CodeRabbit reports concerns that would require
adapter implementation or dependency changes to resolve. For documentation-only
concerns, revise the plan or docs and rerun the relevant checks.

## Risks

Risk: The ADR could leak adapter choices into the domain contract. Severity:
high. Likelihood: low. Mitigation: Keep `tiktoken`, `tokenizers`,
`transformers`, `sentence-transformers`, and `torch` named only as candidate
adapter implementations or optional extras. The domain consumes a
`TokenCounter` port and a `SemanticScorer` port, never a vendor or framework
type.

Risk: The optional-dependency mechanism could be specified incorrectly,
documenting PEP 735 `[dependency-groups]` where PEP 621
`[project.optional-dependencies]` is needed. Severity: high. Likelihood:
medium. Mitigation: Cite both PEPs in the ADR, justify the choice of PEP 621
for user-facing extras, and verify the test contract asserts the PEP 621
phrasing.

Risk: The "disabled by default" policy might be documented too casually,
allowing silent fall-through when an optional extra is requested but missing.
Severity: high. Likelihood: medium. Mitigation: Ensure ADR-002 requires an
explicit, actionable diagnostic naming the missing extra, and that the
documentation-contract test asserts the diagnostic requirement.

Risk: Picking `tiktoken` as the first candidate could be rejected because it is
OpenAI-specific. Severity: medium. Likelihood: low. Mitigation: ADR-002 must
frame `tiktoken` as the first v1 candidate, not the only or permanent
candidate, and must keep `tokenizers` and `transformers` named as future
alternatives behind the same port.

Risk: The broad test-tool requirement could be over-applied to this Phase 1
documentation task. Severity: medium. Likelihood: medium. Mitigation: Follow
ADR-006. Use `pytest` documentation-contract tests for this item, and record
that `pytest-bdd`, `syrupy`, Hypothesis, CrossHair, and Verus become relevant
only when corresponding behaviours, snapshots, input invariants, or proof
surfaces exist.

Risk: Roadmap closure could happen without automated evidence. Severity:
medium. Likelihood: medium. Mitigation: Add documentation-contract tests in
`tests/test_developer_docs.py` before marking roadmap item 1.1.2 done.

Risk: The accepted ADR-002 text could drift from `docs/developers-guide.md`,
`docs/prosidy-darn-technical-design.md`, or `docs/users-guide.md`. Severity:
medium. Likelihood: medium. Mitigation: Cross-check those documents during
Milestone 3 and update them only if their current wording contradicts the
accepted policy.

## Progress

- [x] (2026-05-23T00:00:00Z) Loaded the `leta`, `hexagonal-architecture`,
  `execplans`, and `firecrawl` skills needed for planning, validation, commit,
  and pull request work.
- [x] (2026-05-23T00:00:00Z) Created a leta workspace for this repository.
- [x] (2026-05-23T00:00:00Z) Used Wyvern read-only planning agents to inspect
  the existing ADR-002 stub, the roadmap and technical design references, the
  documentation-contract test patterns, ADR-006 scope, and dependent roadmap
  items.
- [x] (2026-05-23T00:00:00Z) Used Firecrawl-class research to survey
  `tiktoken`, `transformers`, `tokenizers`, `sentence-transformers`, `darn-it`,
  PEP 621, PEP 735, and lazy-import idioms for optional Python dependencies.
- [x] (2026-05-23T00:00:00Z) Drafted this pre-implementation ExecPlan.
- [x] (2026-05-26) Received explicit user approval to implement the plan.
- [x] (2026-05-26) Branch
  `1-1-2-record-token-limit-and-semantic-scoring-dependency-policy` already
  tracks the matching remote.
- [x] (2026-05-26) Added documentation-contract tests in
  `tests/test_developer_docs.py` for ADR-002 acceptance, optional-dependency
  policy, default-disabled adapters, diagnostic requirement, PEP 621 extras
  mechanism, and roadmap closure.
- [x] (2026-05-26) Ran the focused documentation test and confirmed the
  three new tests failed for the expected reasons before changing the ADR.
- [x] (2026-05-26) Edited
  `docs/adr-002-tokenizer-and-semantic-scoring-policy.md` from "Proposed" to
  "Accepted on 2026-05-26" with options A-D, decision outcome bulleting the
  policy commitments, goals and non-goals, migration plan, risks, and
  architectural rationale.
- [x] (2026-05-26) Cross-checked surrounding docs and updated only
  `docs/prosidy-darn-technical-design.md` §18 to remove the closed tokenizer
  open decision and record ADR-002's outcome alongside ADR-001's.
- [x] (2026-05-26) Marked roadmap item 1.1.2 done in `docs/roadmap.md` once
  ADR-002 was accepted and the contract tests passed.
- [x] (2026-05-28) Ran the final local gates sequentially:
  `make check-fmt` (33 files already formatted), `make markdownlint` (29 files,
  0 errors), `make nixie` (all diagrams validated), `make typecheck` (all
  checks passed), `make lint` (ruff + pylint-pypy: 10.00/10), `make test` (15
  passed).
- [x] (2026-05-28) Ran `coderabbit review --agent` — 0 findings, no concerns.
- [x] (2026-05-26) Committed the change using a file-based commit message
  (`f9eaa82`).
- [x] (2026-05-26) Pushed the branch to the existing upstream and opened
  draft PR #12.

## Surprises & discoveries

- Observation: ADR-002 already exists but is marked Proposed with a pending
  outcome. Evidence: `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`
  lines 3-9 carry status "Proposed" and decision outcome "Pending. Roadmap task
  1.1.2 must decide …". Impact: Implementation should fill the ADR's decision
  outcome and supporting sections rather than create a new file from scratch.
- Observation: The Python package layout is still scaffold-level. Evidence:
  `prosidy_darn/__init__.py`, `prosidy_darn/_runtime.py`, and
  `prosidy_darn/pure.py` are the only modules under `prosidy_darn/`; no domain,
  application, ports, or adapter packages exist yet. Impact: ADR-002 must
  reason about the future port location without implying that the port already
  exists.
- Observation: `pyproject.toml` currently declares no runtime dependencies
  and no `[project.optional-dependencies]` section. Evidence: line 8 reads
  `dependencies = []` and there is no `[project.optional-dependencies]` table.
  Impact: ADR-002 documents the future extras shape but the implementation must
  not add the table or any extra in this task.
- Observation: `transformers` `AutoTokenizer` cannot be installed without the
  full `transformers` library. Evidence: Hugging Face issue
  `huggingface/transformers#31043` and the project metadata for `transformers`
  5.x. Impact: ADR-002 must rule it out as the first v1 candidate while keeping
  it eligible as a future adapter behind the same port.

## Decision log

- Decision: Treat 1.1.2 as a documentation finalization and closure task.
  Rationale: ADR-002 already exists in Proposed status, the roadmap checkbox
  remains open, and the missing work is policy specification, contract tests,
  and task closure rather than adapter implementation. Date/Author: 2026-05-23
  / Claude (planning).
- Decision: Name `tiktoken` as the first v1 `TokenCounter` candidate behind
  the port. Rationale: It is a small native MIT-licensed wheel, supports Python
  3.9+, ships the `cl100k_base` and `o200k_base` encodings, and is the
  conventional first choice for small Python CLIs. `transformers`
  `AutoTokenizer` cannot install standalone (HF issue #31043), and `tokenizers`
  adds runtime model-file distribution surface. Date/Author: 2026-05-23 /
  Claude (planning).
- Decision: Use PEP 621 `[project.optional-dependencies]` to document the
  future extras shape. Rationale: PEP 621 is the standardized mechanism for
  user-facing published extras; PEP 735 `[dependency-groups]` does not install
  the package or its runtime dependencies and is therefore unsuited to optional
  adapter dependencies. Date/Author: 2026-05-23 / Claude (planning).
- Decision: Do not add `tiktoken`, `tokenizers`, `transformers`,
  `sentence-transformers`, `torch`, or any HTTP client in this task. Rationale:
  The roadmap separates v1 decision ratification from dependency and adapter
  implementation work; tasks 1.2.2 and 5.1.2 own those additions. Date/Author:
  2026-05-23 / Claude (planning).
- Decision: Use `pytest` documentation-contract tests, not `pytest-bdd`,
  `syrupy`, Hypothesis, CrossHair, or Verus, for this item. Rationale: ADR-006
  scopes Phase 1 tests to documentation and link contracts until adapter
  behaviour, output snapshots, input invariants, or proof-worthy logic exist.
  Date/Author: 2026-05-23 / Claude (planning).

## Outcomes & retrospective

Implementation completed on 2026-05-28. All expected outcomes achieved:

- ADR-002 is accepted on 2026-05-26, naming `tiktoken` as the first v1
  `TokenCounter` candidate behind the port.
- PEP 621 `[project.optional-dependencies]` is the documented mechanism for
  future optional adapter extras (`tokenizer` and `semantic`).
- Default-disabled adapters are required to return neutral results and raise
  an explicit `ImportError` when their optional extra is missing.
- The public segmentation API must remain stable when extras are omitted.
- Roadmap item 1.1.2 is marked done in `docs/roadmap.md`.
- Three documentation-contract tests in `tests/test_developer_docs.py`
  (`test_tokenizer_policy_adr_is_accepted`,
  `test_tokenizer_policy_adr_defines_v1_adapter_policy`,
  `test_tokenizer_policy_roadmap_item_is_closed`) lock the accepted policy.
- All local gates pass: `make check-fmt`, `make markdownlint`, `make nixie`,
  `make typecheck`, `make lint`, `make test` (15/15 passed).
- CodeRabbit review reports 0 findings.
- Draft PR #12 is open at
  <https://github.com/leynos/prosidy-darn/pull/12>.
- No tokenizer, embedding, model, or HTTP client dependency was added in this
  task, preserving scope separation from tasks 1.2.2 and 5.1.2.

No surprises during final validation. The earlier implementation work
(2026-05-26) held up cleanly against the full gate sequence two days later.

## Context and orientation

Prosidy Darn is planned as a Python package using hexagonal architecture.
"Hexagonal architecture" means the domain owns business concepts and ports,
while adapters connect the outside world to those ports. For this task, the
important boundaries are the `TokenCounter` and `SemanticScorer` ports.
Optional tokenizer and embedding packages are outbound adapter details, never
domain dependencies.

The key files are:

- `docs/roadmap.md`: the ordered implementation roadmap. Item 1.1.2 is the
  token-limit and semantic-scoring dependency policy task.
- `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`: the ADR whose
  status this task must move from "Proposed" to "Accepted".
- `docs/adr-001-markdown-parser-boundary.md`: the accepted parser-boundary
  ADR. Use it as a structural template for ADR-002.
- `docs/prosidy-darn-technical-design.md`: the authoritative technical design.
  Sections 4, 5.2, 7.3, 9, 10, 17.3, and 18 are directly relevant.
- `docs/developers-guide.md`: maintainer-facing implementation guidance,
  Phase 1 ADR list, and quality gates.
- `docs/users-guide.md`: user-facing behaviour. It changes only if the
  approved implementation introduces user-visible behaviour, which this task
  should not.
- `tests/test_developer_docs.py`: current documentation-contract tests. The
  ADR-001 assertions on lines 90-132 are the template for new ADR-002
  assertions.
- `pyproject.toml`: lists current runtime and development dependencies and is
  where future extras will live. This task must not modify it.
- `Makefile`: local quality gates. Prefer its targets over direct tool
  invocation.

Important terms:

- "Token counter" means a component that reports a token count for a string,
  used to enforce optional renderer-side token limits. In v1 the port is
  `TokenCounter` and the first candidate adapter is `tiktoken`.
- "Semantic scorer" means a component that returns optional cohesion-drop
  scores at candidate boundaries to act as boundary rewards, never as hard
  split rules. In v1 the port is `SemanticScorer` with a disabled default
  adapter.
- "Optional extra" means a PEP 621 `[project.optional-dependencies]` entry,
  installable via `pip install prosidy-darn[<extra>]`. Optional extras are
  published as part of the package metadata and form part of the package's
  public installation interface.
- "Default disabled adapter" means an adapter that returns a neutral or empty
  result when called and does not import the optional dependency at module load
  time. It satisfies the port without imposing the dependency.
- "Lazy import" means importing the optional dependency inside the adapter
  method or function body, not at module top level. A missing dependency is
  surfaced as an explicit `ImportError` whose message names the extra to
  install.

## Plan of work

Milestone 1 prepares the branch and confirms the baseline. Confirm the current
branch is `1-1-2-record-token-limit-and-semantic-scoring-dependency-policy`. If
it is not, rename it before editing using `git branch -m`. Inspect the
worktree. Read the roadmap, ADR-001, ADR-002 stub, ADR-006, the technical
design, the developer guide, the users' guide, the documentation style guide,
the existing documentation-contract tests, the Makefile, and `pyproject.toml`.

Milestone 2 adds failing documentation-contract tests first. Extend
`tests/test_developer_docs.py` with tests that prove roadmap item 1.1.2 cannot
be closed unless ADR-002 is accepted and states the chosen policy. The tests
should check for these observable facts:

- ADR-002 exists and is accepted (status section contains "## Status" and
  "Accepted on ").
- ADR-002 names `tiktoken` as the first v1 `TokenCounter` candidate behind
  the port.
- ADR-002 states that `transformers` `AutoTokenizer`, `tokenizers`, and
  `sentence-transformers` remain eligible future adapters behind the same port
  but are not adopted in v1.
- ADR-002 states that optional dependencies are declared via PEP 621
  `[project.optional-dependencies]` and installed via
  `pip install prosidy-darn[<extra>]` (no dependency entries are added in this
  task).
- ADR-002 states that the default `TokenCounter` and `SemanticScorer`
  adapters are disabled by default and that missing optional dependencies
  produce an explicit diagnostic naming the extra to install.
- ADR-002 states that domain and application modules must not import any
  optional tokenizer or embedding package at module import time, and that
  optional adapters use lazy imports inside the adapter implementation.
- The roadmap item for 1.1.2 is marked done only when ADR-002 is accepted.

Run the focused test after adding it and confirm it fails for the expected
reason before changing the ADR. If a subset already passes because the ADR stub
satisfies it, document that in `Surprises & Discoveries` and continue.

Milestone 3 finalizes ADR-002. Replace the "Pending" decision outcome with
"Accepted on `YYYY-MM-DD`" plus the chosen policy. Add the sections required by
the documentation style guide and absent from the stub: options considered,
decision outcome, goals and non-goals, migration plan, known risks and
limitations, and architectural rationale. The ADR must follow the shape of
ADR-001 and must clearly state:

- `tiktoken` is the first v1 `TokenCounter` candidate behind the port;
- `tokenizers`, `transformers`, and `sentence-transformers` are future
  adapters behind the same ports and are not adopted in v1;
- optional dependencies are declared via PEP 621
  `[project.optional-dependencies]`, with extra names suggested as `tokenizer`
  (e.g. `tiktoken`) and `semantic` (e.g. `sentence-transformers`);
- default `TokenCounter` and `SemanticScorer` adapters are disabled and
  return a neutral or empty result;
- optional adapters use lazy imports inside the adapter implementation and
  raise an `ImportError` whose message names the extra to install when the
  dependency is missing;
- domain and application modules must not import any optional tokenizer or
  embedding package at module import time;
- the public segmentation API does not change with extras installed or
  omitted;
- task 1.2.2 owns the actual `pyproject.toml` extras declaration once the
  package skeleton lands, and task 5.1.2 owns the first embedding-backed
  semantic scorer adapter.

Milestone 4 aligns surrounding documentation. Check
`docs/prosidy-darn-technical-design.md` §§7, 10, 17.3, and 18 and
`docs/developers-guide.md` for any conflicting wording about tokenization or
semantic scoring. Update them only if the existing wording contradicts the
accepted policy; avoid duplicating the full ADR text in other documents.
`docs/users-guide.md` should change only if a user-visible behaviour statement
must be corrected.

Milestone 5 updates task tracking. Mark item 1.1.2 in `docs/roadmap.md` done
only after the ADR and tests agree. Do not mark later dependency or adapter
tasks done.

Milestone 6 validates the change. Run formatting checks, Markdown linting,
Mermaid validation, type checking, linting, and tests sequentially with `tee`
logs under `/tmp`. If a command fails, inspect the full log and make focused
fixes. Do not run quality gates in parallel.

Milestone 7 runs CodeRabbit review. Run `coderabbit review --agent` after the
documentation and test milestones have passed local gates. Address every
actionable concern within the scope of this plan. If CodeRabbit asks for
adapter code, dependency additions, or broader architecture changes, record the
concern in `Decision Log` and escalate instead of expanding scope.

Milestone 8 commits and opens the draft pull request. Use the `commit-message`
skill's file-based commit workflow. Push
`1-1-2-record-token-limit-and-semantic-scoring-dependency-policy` to its
upstream and set tracking. Create a draft pull request whose title includes
`(1.1.2)`, whose summary links to this ExecPlan, and whose `## References`
section includes the Lody session URL derived from `echo ${LODY_SESSION_ID}`.

## Concrete steps

Run all commands from the repository root:

```bash
pwd
git branch --show-current
git status --short --branch
```

Expected branch output after rename:

```plaintext
1-1-2-record-token-limit-and-semantic-scoring-dependency-policy
```

If the branch has not already been renamed, run:

```bash
git branch -m 1-1-2-record-token-limit-and-semantic-scoring-dependency-policy
```

Read the local context:

```bash
sed -n '85,110p' docs/roadmap.md
sed -n '1,50p' docs/adr-002-tokenizer-and-semantic-scoring-policy.md
sed -n '1,140p' docs/adr-001-markdown-parser-boundary.md
sed -n '200,225p' docs/prosidy-darn-technical-design.md
sed -n '690,750p' docs/prosidy-darn-technical-design.md
sed -n '1220,1240p' docs/prosidy-darn-technical-design.md
sed -n '85,140p' tests/test_developer_docs.py
```

After adding tests, run the focused check:

```bash
UV_CACHE_DIR=.uv-cache UV_TOOL_DIR=.uv-tools uv run pytest \
  tests/test_developer_docs.py -v \
  | tee /tmp/pytest-developer-docs-$(basename "$(pwd)")-$(git branch --show-current).out
```

After ADR edits, run Markdown formatting if needed:

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
Ratify token-limit and semantic-scoring dependency policy

Accept ADR-002 with tiktoken as the first v1 TokenCounter candidate,
sentence-transformers and friends behind PEP 621 optional extras, and
lazy-imported adapters that keep the core import path free of
optional tokenizer or embedding packages.

Add documentation-contract tests that lock the accepted policy in
place and close roadmap item 1.1.2.
ENDOFMSG
git commit -F "$COMMIT_MSG_DIR/COMMIT_MSG.md"
rm -rf "$COMMIT_MSG_DIR"
```

Push and set upstream tracking:

```bash
git push -u origin 1-1-2-record-token-limit-and-semantic-scoring-dependency-policy
```

Capture the Lody session:

```bash
echo ${LODY_SESSION_ID}
```

Create the draft pull request using a body file. The title must contain
`(1.1.2)`. The body must mention this ExecPlan and include a final
`## References` section with:

```plaintext
https://lody.ai/leynos/sessions/${LODY_SESSION_ID}
```

## Validation and acceptance

The approved implementation is accepted when all of these are true:

- `tests/test_developer_docs.py` verifies that ADR-002 is accepted and
  defines the first v1 `TokenCounter` candidate, the future-adapter set, the
  PEP 621 optional-dependency mechanism, the default-disabled adapter policy,
  the missing-extra diagnostic requirement, and the import-path constraint.
- `docs/roadmap.md` marks item 1.1.2 done only after ADR-002 is accepted
  and the contract tests pass.
- `docs/adr-002-tokenizer-and-semantic-scoring-policy.md` is accepted and
  carries Status, Date, Context and problem statement, Decision drivers,
  Options considered, Decision outcome, Goals and non-goals, Migration plan,
  Known risks and limitations, and Architectural rationale sections.
- The technical design and developer guide do not contradict ADR-002.
- No adapter implementation, optional dependency, port protocol, CLI
  behaviour, or user-facing API is added by this task.
- `make check-fmt`, `make markdownlint`, `make nixie`, `make typecheck`,
  `make lint`, and `make test` all pass.
- `coderabbit review --agent` reports no unresolved in-scope concerns.
- The branch is pushed to its remote and has a draft pull request whose
  title includes `(1.1.2)` and whose body links this ExecPlan and the Lody
  session.

No `pytest-bdd` behavioural scenario is required for this item because the
approved implementation does not add user interaction behaviour. No `syrupy`
snapshot is required because no output format is introduced or changed. No
Hypothesis or CrossHair property test is required because no adapter invariant
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

## Artefacts and notes

Firecrawl-class research evidence gathered during planning:

- `https://pypi.org/project/tiktoken/` and `https://github.com/openai/tiktoken`:
  `tiktoken` is a small native MIT-licensed BPE tokenizer, Python 3.9+, with
  `cl100k_base` and `o200k_base` encodings bundled.
- `https://pypi.org/project/transformers/` and
  `https://github.com/huggingface/transformers/issues/31043`: `transformers`
  5.x targets Python 3.10+ and cannot ship `AutoTokenizer` without the full
  library.
- `https://pypi.org/project/tokenizers/`: Rust-backed BPE via PyO3, Python
  3.10+, requires runtime vocab/merges files.
- `https://pypi.org/project/sentence-transformers/` and
  `https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2`: small SBERT
  embedding model (384-dim, ~22.7 M parameters); recommended runtime pulls
  PyTorch.
- `https://pypi.org/project/darn-it/`: `darn-it` 1.2.0 ships
  `requires_dist: None`; the tokenizer is bundled inside the Rust wheel.
- `https://peps.python.org/pep-0621/` and `https://peps.python.org/pep-0735/`:
  PEP 621 is the standard mechanism for `[project.optional-dependencies]`; PEP
  735 `[dependency-groups]` is for development-only sets and does not install
  the package or its runtime dependencies.
- `https://discuss.python.org/t/optional-imports-for-optional-dependencies/104760`
  and `https://peps.python.org/pep-0810/`: the conventional pattern is
  function-scoped lazy imports with hint-bearing `ImportError`; explicit lazy
  imports (PEP 810) are not yet usable.

Wyvern planning evidence:

- ADR-002 already exists in Proposed status, so roadmap closure should
  finalize the existing ADR rather than create one from scratch.
- The repository has not yet introduced the final hexagonal package layout,
  the `TokenCounter` and `SemanticScorer` ports, or any tokenizer or embedding
  dependency.
- The Makefile exposes `check-fmt`, `markdownlint`, `nixie`, `typecheck`,
  `lint`, and `test` gates that must be run sequentially per repository policy.

## Interfaces and dependencies

This task introduces no runtime interface and no dependency. It preserves the
future port boundary described by the technical design:

```python
class TokenCounter(typ.Protocol):
    def count_tokens(self, text: str, *, model: str | None) -> int: ...


class SemanticScorer(typ.Protocol):
    def score_boundary(self, left: str, right: str) -> float: ...
```

The exact names and signatures are illustrative only. Later implementation must
keep both ports inside `prosidy_darn.ports` (domain-adjacent contract layer)
and place concrete adapter implementations under
`prosidy_darn.adapters.outbound.tokenizer` and
`prosidy_darn.adapters.outbound.semantic`.

The final accepted policy that later work must honour is:

- v1 names `tiktoken` as the first `TokenCounter` candidate adapter;
- `tokenizers`, `transformers` `AutoTokenizer`, and `sentence-transformers`
  remain eligible future adapters behind the same ports and are not adopted in
  v1;
- optional dependencies are declared via PEP 621
  `[project.optional-dependencies]` once task 1.2.2 lands the package skeleton;
- default `TokenCounter` and `SemanticScorer` adapters are disabled and
  return a neutral or empty result;
- optional adapters use lazy imports inside the adapter implementation and
  raise an `ImportError` naming the extra to install when the dependency is
  missing;
- domain and application modules must not import any optional tokenizer or
  embedding package at module import time;
- the public segmentation API does not change with extras installed or
  omitted.

## Revision note

Initial draft created on 2026-05-23. It captures repository findings, Wyvern
planning feedback, Firecrawl-class prior-art checks, approval gating,
implementation milestones, validation commands, and pull-request requirements
for roadmap item 1.1.2. Implementation must not start until the user explicitly
approves the plan.

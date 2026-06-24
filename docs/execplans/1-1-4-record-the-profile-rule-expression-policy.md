# Record the profile rule-expression policy

This ExecPlan (execution plan) is a living document. The sections `Constraints`,
`Tolerances`, `Risks`, `Progress`, `Surprises & Discoveries`, `Decision Log`,
and `Outcomes & Retrospective` must be kept up to date as work proceeds.

Status: IN PROGRESS

## Purpose / big picture

Roadmap task 1.1.4 closes the last v1-blocking configuration decision for
Prosidy Darn before Phase 2 begins: must profile files be allowed to define
arbitrary custom rule expressions, or only named rule weights? This matters
because profiles tune the segmenter's boundary and unit punishment scoring, and
once profile parsing exists, retrofitting an expression-language contract — or
removing one — is expensive and risky. The roadmap states the success criterion
plainly: "profile configuration can be implemented without adding a new
expression-language decision in the segmenter".

The repository already contains a stub
`docs/adr-003-profile-rule-expression-policy.md` whose status is "Proposed" and
whose decision outcome is "Pending". This plan therefore treats 1.1.4 as a
decision-finalisation and closure task. After this plan is approved and
implemented, a maintainer can observe success by reading the accepted ADR-003,
seeing roadmap item 1.1.4 marked done, running the documentation and Python
quality gates without failures, and confirming that no profile parser,
`ProfileVocabulary`, `TTSProfile`, or scoring code has been added yet.

The implementation carried out from this plan must not build a profile loader, a
profile vocabulary registry, a `TTSProfile` value object, or any segmenter
scoring code. It records, validates, and closes the policy that later
configuration and adapter work (tasks 1.2.x, 2.3.1, and 3.2.x) must follow.

This is the decision the plan finalises: v1 profiles carry only named rule
weights drawn from a closed, documented vocabulary; the segmenter's shaped
scoring rules stay domain-owned and fixed; and the profile loader never
interprets configuration strings as code. A future expression need, if it ever
arises, must come back through a new ADR adopting a purpose-built, sandboxed,
non-Turing-complete evaluator — never Python `eval`.

## Context and citations

`docs/roadmap.md` defines roadmap item 1.1.4 under "Ratify the v1 decisions that
block implementation" (lines 102-109). The item requires
`docs/adr-003-profile-rule-expression-policy.md`, lists 1.0.1 and 1.1.2 as
prerequisites, and declares success as: "profile configuration can be
implemented without adding a new expression-language decision in the segmenter".
Both prerequisites are complete: item 1.0.1 (baseline developer docs and ADR
locations) and item 1.1.2 (token-limit and semantic-scoring dependency policy)
are both marked done.

`docs/prosidy-darn-technical-design.md` is the architectural source of truth.
The directly relevant sections are:

- Section 4 keeps domain and application code free of adapter and framework
  imports; `prosidy_darn.config` is the only composition-root code permitted to
  import adapters and Cyclopts.
- Section 7.3 (boundary punishment, lines 451-489) defines the default
  punishment table and, crucially, the **shaped rules**: inverse-triangular
  paragraph-internal punishment, decaying heading-adjacent punishment,
  profile-specific quote-attribution separation, and semantic-break rewards that
  scale with local cohesion drop but never override hard structural illegality.
- Section 7.4 (unit punishment, lines 491-543) shows the duration model dividing
  by `words_per_second`, which a profile value must never be allowed to set to
  zero.
- Section 8 (profiles and configuration, lines 590-656) already publishes three
  built-in profiles using named, enum-valued, boolean, and numeric knobs (for
  example `quote_attribution_separation = "high"`,
  `dialogue_turn_reward = "very_high"`, `semantic_breaks = "disabled"`,
  `allow_nested_voice_spans = false`, `hard_max_seconds = 28.0`,
  `words_per_second = 2.6`, `ideal_seconds = [4.0, 12.0]`). It also defines the
  five-tier Cyclopts configuration precedence and the on-disk profile store at
  `${XDG_CONFIG_HOME:-~/.config}/prosidy-darn/profiles.toml`.
- Section 9 (library API, lines 658-704) fixes the planned package boundary,
  including `prosidy_darn.domain.scoring` (punishment rules),
  `prosidy_darn.config` (composition root and Cyclopts wiring), and the rule
  that the core library must not import optional heavy dependencies at module
  import time.
- Section 13 (CLI contract) and Section 15 (failure modes) fix the stable exit
  code taxonomy. Table 6 (lines 952-966) assigns **exit code 7** to
  "Configuration or profile error", and the failure-modes table (line 1113)
  requires an invalid profile to "Reject before processing input and enumerate
  valid profile keys or enum values with exit code 7".
- Section 18 (open decisions, lines 1226-1242) records the open question this
  task resolves: "Whether profile files should allow arbitrary custom rule
  expressions or only named rule weights." It already records the accepted
  ADR-001 and ADR-002 outcomes, which this task extends with ADR-003.

`docs/adr-001-markdown-parser-boundary.md` and
`docs/adr-002-tokenizer-and-semantic-scoring-policy.md` are the two accepted
ADRs. ADR-002 is the closest structural and procedural precedent: it moved from
"Proposed" to "Accepted on", added Options considered, Decision outcome, Goals
and non-goals, Migration plan, Known risks and limitations, and Architectural
rationale, and was locked by documentation-contract tests. Mirror its shape.

`docs/adr-004-import-boundary-fitness-check.md` is the sibling Phase 1 decision
(roadmap 1.1.3); it remains "Proposed" and is owned by a separate task. This
task must not change it.

`docs/adr-006-test-matrix-phase-scope.md` scopes Phase 1 tests to import-boundary
checks, public import tests, developer-doc checks, and ADR link validation. It
deliberately defers `pytest-bdd`, `syrupy`, Hypothesis, CrossHair, and Verus
until the product surfaces they validate exist. This task therefore uses
`pytest` documentation-contract tests only; see "Validation and acceptance" for
the explicit justification.

`docs/developers-guide.md` lists ADR-003 as a blocking Phase 1 decision location
(around line 263) and requires architecture and product decision changes to
update the relevant design or ADR document in the same change. It defines the
Phase 1 quality gates.

`docs/documentation-style-guide.md` defines ADR naming and required-section
conventions (lines 355-465): Status, Date, Context and problem statement,
Decision drivers, then conditional sections including Options considered,
Decision outcome, Goals and non-goals, Migration plan, Known risks and
limitations, and Architectural rationale.

`docs/users-guide.md` documents the planned `--profile` flag and the three
built-in profile names (lines 56-98, 203-215). It changes only if this task
introduces a user-visible behaviour statement, which it should not; the profile
file format is not yet a shipped user surface.

`tests/test_developer_docs.py` contains the documentation-contract tests. It
already lists `docs/adr-003-profile-rule-expression-policy.md` in
`INITIAL_ADR_PATHS` (line 18) and verifies it exists and is discoverable from
the developers' guide and roadmap. The ADR-001 acceptance assertions (lines
91-133) and ADR-002 acceptance assertions (lines 136-198) are the template for
new ADR-003 assertions.

### External prior art (Firecrawl research, accessed 2026-06-18)

The decision direction is supported by primary-source prior art gathered with
Firecrawl during planning:

- Python's built-in `eval()` executes whatever it is given; stripping
  `__builtins__` and globals does not make it safe, and crafted expressions can
  still escape or crash the interpreter
  (<https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html>).
- The `simpleeval` project README explicitly disclaims being a security
  boundary, warns that sandboxing CPython is widely believed impossible, and
  notes denial-of-service via expensive expressions
  (<https://github.com/danthedeckie/simpleeval>); it has a documented
  sandbox-bypass advisory history
  (<https://ubuntu.com/security/notices/USN-8301-1>).
- The `asteval` documentation states it "cannot guarantee that asteval is
  completely safe from malicious code", claims only to be "safer than the
  builtin `eval()`", and cannot prevent resource-exhaustion denial of service
  (<https://lmfit.github.io/asteval/motivation.html>).
- When expressions are genuinely required, the established alternative is a
  purpose-built, non-Turing-complete, sandboxed language: Google CEL describes
  itself as "Safe: Non-Turing complete, and only accesses data provided by the
  host application" and "ideal for extending declarative configurations"
  (<https://cel.dev/>, <https://github.com/google/cel-go>); JsonLogic is "a
  small, safe way to delegate one decision", "We never `eval()`", with read-only
  access to host-provided data (<https://jsonlogic.com/>).
- Comparable tuning systems expose a fixed, named knob surface rather than an
  embedded DSL: ESLint sets each rule to a named severity (`off`/`warn`/`error`)
  plus rule-specific options (<https://eslint.org/docs/latest/use/configure/rules>),
  and CodeScene tunes code-health scanning via a declarative
  `code-health-rules.json` of named rule weights and thresholds
  (<https://codescene.io/docs/guides/technical/code-health.html>).
- Configuration guidance holds that config should store declarative values, not
  developer-only logic; logic hidden in config has crossed into code
  (<https://blog.urth.org/2011/01/06/config-versus-code/>).

### Relevant skills

- `leta`, for semantic workspace navigation when symbols must be inspected.
- `hexagonal-architecture`, to preserve the ADR's port-and-adapter boundary so
  the named-weight vocabulary stays domain-owned and the profile loader stays an
  outbound config adapter.
- `python-router` and its testing branch, for the documentation-contract test
  shape if the assertions grow.
- `execplans`, which defines this document's approval gate before
  implementation.
- `firecrawl`, for checking current open-source expression-safety prior art.
- `commit-message`, for file-based commit messages when this plan is
  implemented.
- `pr-creation` and `en-gb-oxendict`, for the draft pull request and British
  English with Oxford spelling.

## Constraints

Do not implement profile or configuration runtime code in this task. The
approved implementation may change documentation and documentation-contract
tests, but it must not create `prosidy_darn.config`, a profile loader, a
`ProfileVocabulary` registry, a `TTSProfile` value object, `prosidy_darn.domain.
scoring`, or any Cyclopts configuration wiring. It must not add a `[profile.*]`
parsing path or any TOML profile-reading code.

Preserve the hexagonal dependency rule. The decision must keep the named-weight
vocabulary domain-owned and the profile loader an outbound config adapter.
Domain and application modules, and the vocabulary registry itself, must never
import the adapter, Cyclopts, or any framework type. The composition root
(`prosidy_darn.config`) remains the only place permitted to import adapters and
Cyclopts.

Do not contradict the technical design. The accepted policy must remain
consistent with the three published built-in profiles in §8, the shaped rules in
§7.3, the five-tier configuration precedence in §8, and the exit-code taxonomy
in §13 and §15 (profile errors are exit code 7).

Do not add runtime or development dependencies for this roadmap item. If
satisfying 1.1.4 appears to require adding a TOML library, an expression engine,
or any other dependency, stop and escalate. The standard library `tomllib` is
already available for any later parsing work and is not added here.

Never adopt arbitrary expression evaluation. The accepted policy must forbid
Python `eval`, `exec`, `simpleeval`, and `asteval` as profile interpreters
permanently. Any future expression capability requires a new ADR adopting a
sandboxed, non-Turing-complete evaluator; this ADR must not pre-select a
specific engine.

Use British English with Oxford spelling. Follow the documentation style guide:
wrap Markdown paragraphs and bullets at 80 columns, wrap code blocks at 120
columns, use dash bullets, give every fenced code block a language, and caption
every table.

The plan must be approved before implementation begins. Silence is not approval.

Do not mark roadmap item 1.1.4 done until the approved implementation has added
validation evidence, passed the required gates, cleared CodeRabbit concerns,
been committed, and been pushed.

## Tolerances

Stop and ask for direction if implementation of the approved plan requires
changes outside these paths:

- `docs/adr-003-profile-rule-expression-policy.md`
- `docs/developers-guide.md`
- `docs/prosidy-darn-technical-design.md`
- `docs/roadmap.md`
- `docs/users-guide.md`
- `tests/test_developer_docs.py`

Stop and ask for direction if more than 320 net lines of documentation or more
than 90 net lines of test code are needed. This item closes an ADR decision; it
should not become a configuration-adapter implementation slice.

Stop and ask for direction if any of these scope expansions become necessary:

- introducing a new public API signature, port protocol, value object, or
  adapter module;
- adding a runtime, optional, or development dependency to `pyproject.toml`;
- changing the technical design's five-tier configuration precedence, the
  published built-in profile names, or the exit-code taxonomy;
- selecting a specific future expression engine rather than deferring that
  choice to a new ADR.

Stop and ask for direction if any quality gate still fails after three focused
fix attempts.

Stop and ask for direction if `make fmt` rewrites unrelated Markdown or source
files. Restore unrelated formatting churn before continuing, unless the user
explicitly accepts the broader formatting change.

Stop and ask for direction if CodeRabbit reports concerns that would require
adapter implementation or dependency changes to resolve. For documentation-only
concerns, revise the plan or docs and rerun the relevant checks.

## Risks

Risk: The ADR resolves only the narrow "expression vs weight" wording and leaves
the design's §7.3 shaped-rule requirement dangling, so Phase 2 reopens the
question. Severity: high. Likelihood: medium. Mitigation: The ADR must state
explicitly that the shaped rules (inverse-triangular, decaying, cohesion-scaled)
are domain-owned and fixed in v1, and that profiles select and scale them but
never define them. This is the sentence that actually closes §18.

Risk: The named-weight vocabulary ownership is asserted but not located, so the
adapter hard-codes a key list that drifts from the domain's. Severity: high.
Likelihood: medium. Mitigation: The ADR must place the vocabulary (legal keys,
per-key value shape, and enum-to-number mapping) in the domain scoring layer as
a pure registry, require the config adapter to import and enforce it, and source
the "valid set" diagnostic from it. Confirm the dependency arrow permits an
adapter-to-domain-vocabulary import while still forbidding domain-to-adapter
imports.

Risk: Numeric scalar validation is omitted, leaving the larger untrusted
surface unspecified (`hard_max_seconds = -5`, `words_per_second = 0` causing a
§7.4 division by zero, `ideal_seconds = [12.0, 4.0]` with min greater than max,
or wrong arity). Severity: high. Likelihood: medium. Mitigation: The ADR must
specify per-key numeric ranges and arity plus the cross-field invariant
`ideal_min <= ideal_max <= hard_max_seconds`, and require these to reject with
exit code 7.

Risk: "Reject unknown keys" with no versioning makes every future vocabulary
addition a forward-compatibility break for user-authored and tool-written
profile files. Severity: high. Likelihood: medium. Mitigation: The ADR must add
a vocabulary-evolution rule: profiles carry a `schema_version`; adding a key or
widening an enum is backward-compatible, while removing, renaming, or narrowing
is breaking and requires a new ADR. Fail closed on malformed input within a
schema version; evolve gracefully across versions.

Risk: The dual value-shape (numeric, boolean, enum) invites a single key
accepting more than one shape, creating ambiguity. Severity: medium.
Likelihood: medium. Mitigation: The ADR must require exactly one declared value
shape per key and prohibit mixed-shape keys.

Risk: The policy claims to govern only scoring weights but the §8 profiles also
carry renderer (`allow_nested_voice_spans`) and Phase-5 semantic
(`semantic_breaks`) keys, so the first such feature bypasses the policy.
Severity: medium. Likelihood: medium. Mitigation: The ADR must extend the
named-weight discipline to all profile knob families — scoring, renderer, and
semantic — so no future feature smuggles in an expression.

Risk: The broad test-tool requirement (pytest-bdd, syrupy, Hypothesis,
CrossHair, Verus) is over-applied to this Phase 1 documentation task. Severity:
medium. Likelihood: medium. Mitigation: Follow ADR-006. Use `pytest`
documentation-contract tests for this item, and record why behavioural,
snapshot, property, and proof tools become relevant only when the corresponding
parser, output, invariant, or proof surfaces exist.

Risk: Roadmap closure happens without automated evidence. Severity: medium.
Likelihood: medium. Mitigation: Add documentation-contract tests in
`tests/test_developer_docs.py` before marking roadmap item 1.1.4 done.

Risk: The accepted ADR-003 text drifts from `docs/developers-guide.md`,
`docs/prosidy-darn-technical-design.md`, or `docs/users-guide.md`. Severity:
medium. Likelihood: medium. Mitigation: Cross-check those documents during
Milestone 4 and update them only where their current wording would contradict
the accepted policy.

## Progress

- [x] (2026-06-18) Loaded the `leta`, `python-router`, `rust-router`,
  `hexagonal-architecture`, and `execplans` skills for planning, navigation,
  and the approval gate.
- [x] (2026-06-18) Created a leta workspace for this repository.
- [x] (2026-06-18) Inspected the ADR-003 stub, the roadmap and technical design
  references (§§4, 7.3, 7.4, 8, 9, 13, 15, 18), the documentation-contract test
  patterns, ADR-006 scope, ADR-002 as the format precedent, and the Makefile
  gate targets.
- [x] (2026-06-18) Used Firecrawl research to survey expression-safety prior art
  (`eval`, `simpleeval`, `asteval`, CEL, JsonLogic) and named-weight precedents
  (ESLint, CodeScene).
- [x] (2026-06-18) Ran a community-of-experts design review of the proposed
  decision and folded its P0-P2 revisions into this plan.
- [x] (2026-06-18) Renamed the working branch to
  `1-1-4-record-the-profile-rule-expression-policy`.
- [x] (2026-06-18) Drafted this pre-implementation ExecPlan.
- [x] (2026-06-24) Received explicit user approval to implement the plan in
  this Lody session.
- [x] (2026-06-24) Confirmed the branch name
  `1-1-4-record-the-profile-rule-expression-policy`, set it to track
  `origin/1-1-4-record-the-profile-rule-expression-policy`, updated the PR
  title to remove the `Plan:` prefix, renamed the Lody session, and refreshed
  the PR `## References` session link.
- [x] (2026-06-24) Ran `make markdownlint nixie`; both documentation gates
  passed after fixing a Markdown lint issue in this execplan.
- [x] (2026-06-24) Committed and pushed the implementation-start execplan
  update as `995d0ef`.
- [x] (2026-06-24) Updated `docs/roadmap.md` to record that roadmap item 1.1.4
  is in progress, without marking it complete.
- [ ] Add failing documentation-contract tests for ADR-003 acceptance and the
  locked policy commitments.
- [ ] Confirm the new tests fail for the expected reason before editing the ADR.
- [ ] Finalise ADR-003 from "Proposed" to "Accepted on", adding the required
  style-guide sections and the policy commitments.
- [ ] Align surrounding documentation (design §18, and §8 or the developers'
  guide only where wording would otherwise contradict the policy).
- [ ] Mark roadmap item 1.1.4 done.
- [ ] Run the local quality gates sequentially and capture logs.
- [ ] Run `coderabbit review --agent` and clear in-scope concerns.
- [ ] Commit, push, and open the draft pull request for the execplan.

## Surprises & discoveries

- Observation: ADR-003 already exists but is "Proposed" with a "Pending"
  outcome. Evidence: `docs/adr-003-profile-rule-expression-policy.md` lines 3-5
  and 33-36. Impact: Implementation finalises the existing ADR rather than
  creating a new file.
- Observation: The technical design already commits to named, enum-and-numeric
  profile knobs in §8, so "named weights only" is the consistent reading; the
  unresolved part is the §7.3 shaped-rule expressiveness, not the key/value
  surface. Evidence: design lines 626-651 (named knobs) versus lines 479-489
  (shaped rules). Impact: The ADR must explicitly separate "scaling a fixed
  domain-owned shape" from "defining a shape", or it does not close §18.
- Observation: The §8 profiles set different subsets of keys, so profiles are
  sparse overlays on defaults, not complete objects. Evidence: design lines
  626-651. Impact: The ADR must define partial-profile semantics and where
  cross-field invariants are checked relative to Cyclopts' tiered merge.
- Observation: The project-wide `make fmt` target currently fails on two
  pre-existing line-length issues in
  `docs/execplans/1-1-3-record-import-boundary-enforcement-decision.md`, which
  is outside this plan's approved path list. Evidence: the 2026-06-24
  `/tmp/fmt-*-1-1-4-record-the-profile-rule-expression-policy.out` log reports
  MD013 failures on lines 242 and 650 of that 1.1.3 execplan. Impact:
  implementation must not carry unrelated formatter churn; use the deterministic
  Markdown gates for changed files and escalate before editing the 1.1.3 plan
  unless explicitly authorized.

## Decision log

- Decision: Treat 1.1.4 as a documentation finalisation and closure task, not an
  adapter implementation slice. Rationale: ADR-003 already exists in "Proposed"
  status, the roadmap checkbox remains open, and the missing work is policy
  specification, contract tests, and task closure. Date/Author: 2026-06-18 /
  Claude (planning).
- Decision: Accept "named rule weights only" for v1 profiles and forbid
  arbitrary custom rule expressions. Rationale: The design already models
  profiles as named knobs; "safe eval" libraries disclaim being a security
  boundary; comparable tuning systems use named knob surfaces; and a closed
  vocabulary satisfies the roadmap success criterion without adding an
  expression-language decision to the segmenter. Date/Author: 2026-06-18 /
  Claude (planning).
- Decision: State that the §7.3 shaped rules are domain-owned and fixed in v1,
  and that profiles select and scale them but never define them. Rationale: This
  is the precise sentence that closes §18; without it the policy answers a
  narrower question than the open decision poses. Date/Author: 2026-06-18 /
  Claude (planning, from community-of-experts review).
- Decision: Locate the named-weight vocabulary in the domain scoring layer as a
  pure registry and require the config adapter to import and enforce it.
  Rationale: Keeps a single source of truth for legal keys and the
  enum-to-number mapping while preserving the hexagonal dependency rule.
  Date/Author: 2026-06-18 / Claude (planning, from community-of-experts review).
- Decision: Specify numeric-scalar validation and a `schema_version` evolution
  rule in the ADR. Rationale: Scalars are the larger untrusted surface than
  enums, and hard-rejecting unknown keys without versioning would make every
  future vocabulary addition a forward-compatibility break. Date/Author:
  2026-06-18 / Claude (planning, from community-of-experts review).
- Decision: Do not pre-select CEL or JsonLogic; require a future ADR to assess
  engines. Rationale: Naming an engine in an ADR that defers the decision invites
  premature adoption; the firm commitment is only the prohibition on
  `eval`-class evaluation. Date/Author: 2026-06-18 / Claude (planning, from
  community-of-experts review).
- Decision: Use `pytest` documentation-contract tests, not `pytest-bdd`,
  `syrupy`, Hypothesis, CrossHair, or Verus, for this item. Rationale: ADR-006
  scopes Phase 1 tests to documentation and link contracts until parser
  behaviour, output snapshots, input invariants, or proof-worthy logic exist.
  Date/Author: 2026-06-18 / Claude (planning).
- Decision: Keep roadmap item 1.1.4 open while recording it as in progress.
  Rationale: branch and pull-request housekeeping are complete, but the roadmap
  success criterion still depends on ADR-003 acceptance, documentation-contract
  tests, CodeRabbit review, and final quality gates. Date/Author: 2026-06-24 /
  Codex (implementation).

## Outcomes & retrospective

To be completed when the approved implementation finishes. It must compare the
result against this purpose: ADR-003 accepted with the named-weight-only policy
and the shaped-rule clarification, contract tests locking the policy, roadmap
item 1.1.4 marked done, all local gates passing, CodeRabbit clear, and no
profile parser, vocabulary registry, value object, or scoring code added.

## Context and orientation

Prosidy Darn is planned as a Python package using hexagonal architecture.
"Hexagonal architecture" means the domain owns business concepts and ports,
while adapters connect the outside world to those ports. For this task the
important boundary is between the domain scoring layer, which owns the
punishment rules and the named-weight vocabulary, and the configuration adapter,
which reads profile files and maps named weights onto a domain profile value.

The key files are:

- `docs/roadmap.md`: the ordered implementation roadmap. Item 1.1.4 is the
  profile rule-expression policy task.
- `docs/adr-003-profile-rule-expression-policy.md`: the ADR whose status this
  task moves from "Proposed" to "Accepted".
- `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`: the accepted ADR to
  use as a structural and procedural template.
- `docs/prosidy-darn-technical-design.md`: the authoritative technical design.
  Sections 4, 7.3, 7.4, 8, 9, 13, 15, and 18 are directly relevant.
- `docs/developers-guide.md`: maintainer-facing guidance, the Phase 1 ADR list,
  and the quality gates.
- `docs/users-guide.md`: user-facing behaviour. It changes only if a
  user-visible statement must be corrected, which this task should not require.
- `docs/documentation-style-guide.md`: ADR naming and required-section rules.
- `tests/test_developer_docs.py`: the documentation-contract tests. The ADR-002
  assertions on lines 136-198 are the template for the new ADR-003 assertions.
- `pyproject.toml`: current dependencies. This task must not modify it.
- `Makefile`: local quality gates (`check-fmt`, `markdownlint`, `nixie`,
  `typecheck`, `lint`, `test`). Prefer its targets over direct tool invocation.

Important terms:

- "Named rule weight" means a configuration key drawn from a closed, documented
  vocabulary whose value tunes a fixed scoring rule. Each key has exactly one
  declared value shape.
- "Value shape" means one of: a numeric scalar (for example `hard_max_seconds`),
  a numeric pair (`ideal_seconds = [min, max]`), a boolean flag (for example
  `prefer_short_units`), or a closed-set categorical level enum (for example
  `quote_attribution_separation`, drawn from a fixed set such as `disabled`,
  `very_low`, `low`, `medium`, `high`, `very_high`).
- "Shaped rule" means a scoring rule whose punishment varies across a span
  rather than being a single constant — for example the inverse-triangular
  paragraph-internal punishment or the decaying heading-adjacent punishment in
  design §7.3. Shapes are domain-owned and fixed in v1.
- "Custom rule expression" means any user-authored formula, predicate, or
  embedded mini-language in a profile file. v1 forbids these; the loader never
  interprets strings as code.
- "Named-weight vocabulary" means the domain-owned registry of legal keys, their
  value shapes, their valid ranges or enum members, and the mapping from
  categorical levels to concrete numbers used by the scoring layer.
- "Sparse overlay" means a profile that sets a subset of keys; unspecified keys
  inherit the default profile's value.

## Plan of work

Milestone 1 prepares the branch and confirms the baseline. Confirm the current
branch is `1-1-4-record-the-profile-rule-expression-policy`. Read the roadmap,
ADR-002 and ADR-003, ADR-006, the technical design sections listed above, the
developers' guide, the users' guide, the documentation style guide, the existing
documentation-contract tests, the Makefile, and `pyproject.toml`.

Milestone 2 adds failing documentation-contract tests first. Extend
`tests/test_developer_docs.py` with tests that prove roadmap item 1.1.4 cannot be
closed unless ADR-003 is accepted and states the chosen policy. Mirror the
ADR-002 assertions. The tests should check for these observable facts:

- ADR-003 exists and is accepted (status section contains "## Status" and
  "Accepted on").
- ADR-003 states that v1 profiles allow only named rule weights from a closed,
  documented vocabulary and that arbitrary custom rule expressions are not
  permitted.
- ADR-003 states that the profile loader never evaluates configuration strings
  as code and never uses `eval`, `exec`, `simpleeval`, or `asteval`.
- ADR-003 states that the segmenter's shaped scoring rules are domain-owned and
  fixed in v1, and that profiles select and scale them but never define them.
- ADR-003 states that the named-weight vocabulary is owned by the domain scoring
  layer and enforced by the configuration adapter.
- ADR-003 states that each named-weight key has exactly one declared value shape
  and that mixed-shape keys are prohibited.
- ADR-003 states the rejection contract: unknown keys, out-of-vocabulary enum
  values, and out-of-range or malformed numeric scalars are rejected before
  processing input with exit code 7, enumerating the valid set.
- ADR-003 states the numeric invariants, including `words_per_second` greater
  than zero and `ideal_min <= ideal_max <= hard_max_seconds`.
- ADR-003 states that profiles are sparse overlays carrying a `schema_version`,
  that additive vocabulary changes are backward-compatible, and that removing,
  renaming, or narrowing requires a new ADR.
- ADR-003 states that any future expression capability requires a new ADR
  adopting a sandboxed, non-Turing-complete evaluator, without pre-selecting an
  engine.
- The roadmap item for 1.1.4 is marked done.

Run the focused test after adding it and confirm it fails for the expected
reason before changing the ADR. If a subset already passes because the ADR stub
satisfies it, document that in `Surprises & Discoveries` and continue.

Milestone 3 finalises ADR-003. Replace the "Pending" decision outcome with
"Accepted on `YYYY-MM-DD`" plus the chosen policy. Add the sections required by
the documentation style guide and absent from the stub: options considered (with
a captioned comparison table), decision outcome, goals and non-goals, migration
plan, known risks and limitations, and architectural rationale. The ADR must
follow the shape of ADR-002 and must clearly state every commitment that the
Milestone 2 tests assert, including:

- v1 profiles allow only named rule weights from a closed, documented
  vocabulary; arbitrary custom rule expressions are not permitted;
- the loader never interprets configuration strings as code and never uses
  `eval`, `exec`, `simpleeval`, or `asteval`;
- the shaped scoring rules are domain-owned and fixed in v1; profiles select and
  scale them, never define them;
- the named-weight vocabulary lives in the domain scoring layer as a pure
  registry; the configuration adapter imports and enforces it and sources its
  diagnostics from it; domain, application, and the vocabulary never import the
  adapter or Cyclopts;
- each key has exactly one declared value shape (numeric scalar, numeric pair,
  boolean flag, or closed-set categorical level enum); mixed-shape keys are
  prohibited;
- the rejection contract uses exit code 7, rejects before processing input,
  enumerates the valid set, names the offending profile source, and collects all
  errors rather than failing on the first;
- numeric invariants hold, including `hard_max_seconds` greater than zero,
  `words_per_second` greater than zero, `ideal_seconds` a two-element ascending
  pair, and `ideal_min <= ideal_max <= hard_max_seconds`;
- profiles are sparse overlays on defaults, carry a `schema_version`, and cross-
  field invariants are validated on the merged configuration after Cyclopts'
  five-tier precedence combines sources;
- additive vocabulary changes (new key, widened enum) are backward-compatible;
  removing, renaming, or narrowing is breaking and requires a new ADR;
- the named-weight discipline binds all profile knob families — scoring,
  renderer (for example `allow_nested_voice_spans`), and Phase-5 semantic (for
  example `semantic_breaks`);
- any future expression capability requires a new ADR adopting a sandboxed,
  non-Turing-complete evaluator, assessed then, with no engine pre-selected;
- the three built-in profiles (`audiobook_single_narrator`,
  `dramatized_multivoice`, `low_latency_streaming`) are the canonical
  conformance fixtures and every key they use is in the locked vocabulary;
- this task adds no profile parser, vocabulary registry, value object, or
  scoring code; tasks 1.2.x, 2.3.1, and 3.2.x own that implementation.

Milestone 4 aligns surrounding documentation. Check
`docs/prosidy-darn-technical-design.md` §18 and add the accepted ADR-003 outcome
alongside ADR-001 and ADR-002. Review §8 and the developers' guide for wording
that would contradict the accepted policy and adjust only where necessary; avoid
duplicating the full ADR text elsewhere. `docs/users-guide.md` changes only if a
user-visible statement must be corrected.

Milestone 5 updates task tracking. Mark item 1.1.4 in `docs/roadmap.md` done
only after the ADR and tests agree. Do not mark later configuration or adapter
tasks done.

Milestone 6 validates the change. Run formatting checks, Markdown linting,
Mermaid validation, type checking, linting, and tests sequentially with `tee`
logs under `/tmp`. If a command fails, inspect the full log and make focused
fixes. Do not run quality gates in parallel.

Milestone 7 runs CodeRabbit review with `coderabbit review --agent` after the
local gates pass. Address every actionable concern within the scope of this
plan. If CodeRabbit asks for adapter code, dependency additions, or broader
architecture changes, record the concern in `Decision Log` and escalate instead
of expanding scope.

Milestone 8 commits and opens the draft pull request. Use the `commit-message`
skill's file-based workflow. Push the branch to its upstream and set tracking.
Create a draft pull request whose title includes `(1.1.4)`, whose summary links
to this ExecPlan, and whose `## References` section includes the Lody session
URL derived from `echo ${LODY_SESSION_ID}`.

## Concrete steps

Run all commands from the repository root.

Confirm the branch and baseline:

```bash
pwd
git branch --show-current
git status --short --branch
```

Expected branch output:

```plaintext
1-1-4-record-the-profile-rule-expression-policy
```

Read the local context:

```bash
sed -n '102,109p' docs/roadmap.md
sed -n '1,60p' docs/adr-003-profile-rule-expression-policy.md
sed -n '1,80p' docs/adr-002-tokenizer-and-semantic-scoring-policy.md
sed -n '451,489p' docs/prosidy-darn-technical-design.md
sed -n '590,656p' docs/prosidy-darn-technical-design.md
sed -n '950,966p' docs/prosidy-darn-technical-design.md
sed -n '1226,1242p' docs/prosidy-darn-technical-design.md
sed -n '136,198p' tests/test_developer_docs.py
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

Then run the required gates sequentially:

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

Inspect changes and commit with a file-based message:

```bash
git diff -- docs tests
git add docs tests
COMMIT_MSG_DIR=$(mktemp -d)
cat > "$COMMIT_MSG_DIR/COMMIT_MSG.md" << 'ENDOFMSG'
Ratify profile rule-expression policy

Accept ADR-003 with named rule weights only: a closed, domain-owned
vocabulary of numeric, boolean, and enum knobs, no arbitrary expressions,
no eval-class evaluation, and shaped scoring rules kept domain-owned and
fixed so profiles select and scale them rather than define them.

Add documentation-contract tests that lock the accepted policy in place and
close roadmap item 1.1.4.
ENDOFMSG
git commit -F "$COMMIT_MSG_DIR/COMMIT_MSG.md"
rm -rf "$COMMIT_MSG_DIR"
```

Push and set upstream tracking, then capture the Lody session and open the
draft pull request:

```bash
git push -u origin 1-1-4-record-the-profile-rule-expression-policy
echo ${LODY_SESSION_ID}
```

The pull request title must contain `(1.1.4)`. The body must mention this
ExecPlan and include a final `## References` section with:

```plaintext
https://lody.ai/leynos/sessions/${LODY_SESSION_ID}
```

## Validation and acceptance

The approved implementation is accepted when all of these are true:

- `tests/test_developer_docs.py` verifies that ADR-003 is accepted and states
  the named-weight-only policy, the no-`eval` prohibition, the domain-owned
  shaped-rule clarification, the vocabulary ownership, the single-shape-per-key
  rule, the exit-code-7 rejection contract, the numeric invariants, the
  sparse-overlay and `schema_version` evolution rule, and the deferral of any
  future expression engine to a new ADR.
- `docs/roadmap.md` marks item 1.1.4 done only after ADR-003 is accepted and the
  contract tests pass.
- `docs/adr-003-profile-rule-expression-policy.md` is accepted and carries
  Status, Date, Context and problem statement, Decision drivers, Options
  considered, Decision outcome, Goals and non-goals, Migration plan, Known risks
  and limitations, and Architectural rationale sections.
- The technical design §18 records the ADR-003 outcome, and no other document
  contradicts the accepted policy.
- No profile parser, vocabulary registry, value object, configuration adapter,
  CLI behaviour, or user-facing API is added by this task.
- `make check-fmt`, `make markdownlint`, `make nixie`, `make typecheck`,
  `make lint`, and `make test` all pass.
- `coderabbit review --agent` reports no unresolved in-scope concerns.
- The branch is pushed to its remote and has a draft pull request whose title
  includes `(1.1.4)` and whose body links this ExecPlan and the Lody session.

No `pytest-bdd` behavioural scenario is required for this item because the
approved implementation adds no user interaction behaviour. No `syrupy` snapshot
is required because no output format is introduced or changed. No Hypothesis or
CrossHair property test is required because no parser or scoring invariant over
arbitrary inputs is implemented in this task. No Verus proof is required because
this task introduces no Rust extension and no new contractual business logic.
These tools become relevant in Phase 2 and Phase 3 when the profile loader, the
vocabulary registry, and the scoring rules are implemented; this ADR specifies
the contract they will then verify.

## Idempotence and recovery

All read and validation commands are safe to rerun. Re-running tests and quality
gates should not change the worktree, except for caches ignored by the
repository.

If `make fmt` changes unrelated files, inspect `git diff` immediately. Restore
unrelated formatting churn unless the user approves keeping it.

If a validation command fails, inspect its `/tmp` log, make the smallest related
fix, and rerun only the failed gate before rerunning the full gate sequence.

If the branch push fails because the remote branch already exists, inspect the
remote state with `git fetch origin`, `git status --short --branch`, and
`git branch -vv`. Do not force-push unless explicitly approved.

If the draft pull request already exists, update its title and body rather than
opening a duplicate.

## Artifacts and notes

Community-of-experts review evidence gathered during planning (folded into the
ADR commitments above): the proposed "named weights only" direction is sound,
but the decision text must additionally (P0) specify numeric-scalar validation
and cross-field invariants, locate the named-weight vocabulary in the domain
with adapter enforcement, separate "scaling a fixed domain-owned shape" from
"defining a shape", and add a `schema_version` vocabulary-evolution rule; (P1)
pin the rejection contract to exit code 7 with source reporting and
collect-all-errors, require one value shape per key, define profiles as sparse
overlays validated on the merged Cyclopts result, and bind the three built-in
profiles as conformance fixtures; (P2) extend the discipline to renderer and
semantic knob families, relabel the task as "documentation plus contract tests
plus binding design constraints" rather than documentation-only, and avoid
pre-selecting a future expression engine.

Firecrawl prior-art evidence is captured under "External prior art" above with
source URLs and the 2026-06-18 access date.

Implementation resumed on 2026-06-24 after explicit user approval. The branch
already had the required task name; the local branch now tracks the matching
remote branch, the pull request title is `Profile rule-expression policy
(1.1.4)`, and the Lody session title and pull request session reference match
the active implementation session.

The first implementation-status update was committed and pushed as `995d0ef`
after `make markdownlint nixie` passed. The roadmap now records item 1.1.4 as
in progress but not complete, matching the remaining ADR, test, CodeRabbit, and
final-gate work.

## Interfaces and dependencies

This task introduces no runtime interface and no dependency. It records the
policy that later configuration and scoring work must honour. The illustrative
boundary the policy preserves is:

```python
# Domain-owned (prosidy_darn.domain.scoring): the named-weight vocabulary.
# Names and signatures are illustrative only; this task does not implement them.
class ProfileVocabulary(typ.Protocol):
    def is_known_key(self, key: str) -> bool: ...

    def value_shape(self, key: str) -> ValueShape: ...

    def level_to_number(self, key: str, level: str) -> float: ...
```

```python
# Adapter-owned (prosidy_darn.config): the profile loader imports and enforces
# the domain vocabulary and maps named weights onto a domain TTSProfile value.
# It never evaluates configuration strings as code.
def load_profile(raw: Mapping[str, object], vocab: ProfileVocabulary) -> TTSProfile: ...
```

The final accepted policy that later work must honour is the named-weight-only
policy described in Milestone 3: a closed, domain-owned vocabulary with a single
value shape per key; fixed, domain-owned shaped rules that profiles scale but do
not define; an exit-code-7 rejection contract with numeric invariants; sparse
overlays validated on the merged Cyclopts result; a `schema_version` evolution
rule; the named-weight discipline applied to scoring, renderer, and semantic
knobs alike; and a hard prohibition on `eval`-class evaluation, with any future
expression capability deferred to a new ADR.

## Revision note

Initial draft created on 2026-06-18. It captures repository findings,
Firecrawl prior-art research, a community-of-experts design review and its
P0-P2 revisions, the approval gate, implementation milestones, validation
commands, and pull-request requirements for roadmap item 1.1.4. Implementation
must not start until the user explicitly approves the plan.

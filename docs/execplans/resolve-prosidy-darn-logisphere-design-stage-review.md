# Resolve Prosidy Darn design-stage review concerns

This ExecPlan (execution plan) is a living document. Its mandatory living
sections must be kept up to date as work proceeds.

Status: COMPLETE

## Purpose / big picture

The Logisphere design-stage review found several contract problems that are
cheap to fix while Prosidy Darn is still a documentation-first scaffold, but
expensive to repair after public APIs, renderers, parser adapters, and CLI
automation exist. The immediate outcome of this plan is a revised technical
design and roadmap that remove the highest-risk ambiguity before implementation
starts.

After this plan is implemented, a maintainer can read
`docs/prosidy-darn-technical-design.md` and see stable contracts for renderer
outputs, exit codes, source indexing, range and span kinds, JSONL cue sheets,
delivery destinations, and `mdast` compatibility detection. The behaviour is
observable through documentation diffs and validation gates: `make fmt`,
`make check-fmt`, `make markdownlint`, `make nixie`, and `git diff --check`
must pass.

## Context and citations

The source review is `docs/prosidy-darn-logisphere-design-stage-review.md`. The
prioritized findings are:

- P5: `Renderer.render(...) -> str` cannot support binary, multi-file, or
  streaming renderers. The review recommends a `RenderResult` type that can
  carry `str | bytes` plus metadata before adapters exist. See
  `docs/prosidy-darn-logisphere-design-stage-review.md:72`.
- T2: the exit code taxonomy omits timeout, webhook delivery failure, and
  feedback submission failure. See
  `docs/prosidy-darn-logisphere-design-stage-review.md:162`.
- P2 and Z3: `SourceIndex.byte_to_char: dict[int, int]` is memory-expensive for
  large documents and should be abstracted behind a swappable contract. See
  `docs/prosidy-darn-logisphere-design-stage-review.md:50` and
  `docs/prosidy-darn-logisphere-design-stage-review.md:143`.
- P6: `SourceRange.kind` and `SpokenSpan.kind` are strings while `TTSUnit.kind`
  is a `UnitKind` enum, creating a stringly-typed domain seam. See
  `docs/prosidy-darn-logisphere-design-stage-review.md:82`.
- T3: the JSONL serialization contract is implied but not specified. See
  `docs/prosidy-darn-logisphere-design-stage-review.md:170`.
- T5: `--deliver` mixes bare keywords and colon schemes, making future parsing
  fragile. See `docs/prosidy-darn-logisphere-design-stage-review.md:182`.
- D2: the `mdast` fallback chain has no version pinning or compatibility probe.
  See `docs/prosidy-darn-logisphere-design-stage-review.md:198`.

The current design locations that will change are:

- Domain model definitions for `SourceRange`, `SpokenSpan`, `TTSUnit`, and
  `SourceIndex` in `docs/prosidy-darn-technical-design.md:252`.
- Markdown parser fallback strategy in
  `docs/prosidy-darn-technical-design.md:626`.
- Renderer protocol in `docs/prosidy-darn-technical-design.md:648`.
- CLI command and exit-code contract in
  `docs/prosidy-darn-technical-design.md:733`.
- Delivery and feedback behaviour in
  `docs/prosidy-darn-technical-design.md:823`.
- Failure mode table in `docs/prosidy-darn-technical-design.md:882`.
- Roadmap tasks for JSONL serialization and renderer delivery in
  `docs/roadmap.md:206` and `docs/roadmap.md:327`.

## Constraints

This plan changes design documentation and roadmap sequencing only. It must not
implement Python code, change package dependencies, or add tests until the plan
is approved for execution.

Keep the architecture hexagonal. Domain contracts may define protocols and
value types, but infrastructure details such as HTTP clients, filesystem
delivery, and `mdast` package imports must remain in adapters or the
composition root.

Preserve literal source-slice semantics. Any change to `SourceIndex`,
`SourceRange`, JSONL output, or renderer contracts must keep
`TTSUnit.source_text == original_text[source_start:source_end]` as a core
invariant.

Do not weaken the agent-native CLI requirements. JSON output remains parseable,
diagnostics remain on stderr, commands stay non-interactive by default, and
invalid enum or delivery values must enumerate supported values.

Use British English with Oxford spelling in documentation, following
`docs/documentation-style-guide.md`.

## Tolerances

Stop and ask for direction if any design update would require changing the
package's v1 scope beyond the prioritized findings listed in this plan.

Stop and ask for direction if resolving `--deliver` requires deleting webhook
delivery, file delivery, or stdout delivery from v1 rather than clarifying
their grammar.

Stop and ask for direction if the JSONL contract cannot be specified without
choosing an incompatible serialization library or adding a dependency that is
not already planned.

Stop and ask for direction if `make fmt` rewrites unrelated Markdown files.
Restore unrelated churn before continuing, or document why the churn is
unavoidable.

## Risks

The renderer protocol may be over-generalized if it tries to solve every future
binary and streaming target now. Mitigation: specify a small `RenderResult`
value with a payload union, metadata, and optional manifest fields, while
deferring true streaming APIs until a renderer needs them.

The source-index memory design may become too abstract for v1. Mitigation:
define a `SourceIndex` protocol and one default implementation now, then place
compact or Rust-backed indexes behind the same protocol later.

The `kind` enum decision can block extensibility. Mitigation: define closed
core enums for built-in range and span kinds, plus an explicit extension field
or namespaced custom-kind policy if third-party adapters need it.

The delivery grammar may become less agent-friendly if it is too clever.
Mitigation: keep the public syntax simple and canonical, and make parsing rules
machine-discoverable through `agent-context`.

The `mdast` compatibility check could become brittle if it only checks package
version. Mitigation: require both a supported version range and a runtime probe
parse that verifies byte offsets against known source slices.

## Milestone 1: Renderer and JSONL contracts

Revise `docs/prosidy-darn-technical-design.md` so the renderer protocol no
longer returns `str` directly. Introduce a small `RenderResult` design with at
least these fields:

```python
@dc.dataclass(frozen=True, slots=True)
class RenderResult:
    payload: str | bytes
    media_type: str
    encoding: str | None
    extension: str
    is_fragment: bool = False
    manifest: tuple[RenderedPart, ...] = ()
```

The exact field names may change during implementation, but the document must
state that renderers return a value object rather than raw text. JSONL and SSML
renderers use `str` payloads. Future vendor renderers may use `bytes` or a
manifest for multi-file output. Streaming remains deferred unless an adapter
needs it; the design should say that streaming renderers can be added as a
separate port without breaking `CueRenderer`.

In the same milestone, add an explicit JSONL cue-sheet contract. State that
JSONL is UTF-8 text, one JSON object per line, one `TTSUnit` per object, no
wrapping array, and a final newline. Specify stable field names for `TTSUnit`,
`SpokenSpan`, `PerformanceDirection`, and diagnostics. Specify that tuple
fields serialize as arrays, `None` serializes as JSON `null` for stable
optional fields, unknown fields are rejected by default in v1, and numeric
offsets are integers in source coordinate space. Link this contract to the
`segment` command and JSONL renderer so snapshots do not define it accidentally.

Acceptance: a reviewer can point to one section that defines renderer return
shape and one section that defines JSONL wire format, and both sections cite
the same cue IR fields.

## Milestone 2: Exit codes, delivery grammar, and feedback failures

Extend the CLI exit-code table in `docs/prosidy-darn-technical-design.md`.
Reserve distinct codes for delivery failure, feedback persistence or submission
failure, and operation timeout. Do not reuse rendering failure for webhook or
feedback problems.

Revise the failure mode table so webhook delivery failures, file delivery
failures, feedback local persistence failures, feedback upstream submission
failures, and timeouts map to those codes. Preserve the requirement that HTTP
status is reported only for successful TLS-validated HTTPS POST attempts.

Replace the ad-hoc delivery grammar with a canonical grammar. The preferred
design is:

```plaintext
--deliver stdout
--deliver file --deliver-to ./out.ssml
--deliver webhook --deliver-to https://example.test/hook
```

If implementation chooses to retain `file:<path>` and `webhook:<url>` for
compatibility, the design must define them as aliases and make one canonical
form visible in `agent-context`. The grammar must avoid ambiguity around
Windows drive letters and URI colons. Error messages must enumerate accepted
schemes and required companion flags.

Acceptance: the CLI contract contains a delivery grammar, error examples, exit
codes for each delivery and feedback failure class, and `agent-context`
requirements for exposing the grammar.

## Milestone 3: Source index memory and typed kinds

Replace the current concrete `SourceIndex` dataclass design with a domain
protocol and a default implementation. The protocol should expose the
operations the segmenter needs, such as converting byte offsets to character
offsets, character offsets to byte offsets, validating boundaries, and slicing
original source text. The default Python implementation may keep simple arrays
or maps, but the design must state memory expectations and permit compact
implementations.

Add an input-size and memory-budget note. A reasonable initial target is to
support Markdown documents up to at least several hundred kilobytes in normal
CLI use without dict-per-byte memory blowup. If the exact target is uncertain,
the design should name the uncertainty and require a benchmark or memory smoke
test before the implementation task closes.

Define closed enums for built-in `SourceRange.kind` and `SpokenSpan.kind`, or
explicitly define an open extension policy. The preferred v1 contract is:
`SourceRangeKind` for structural ranges, `SpokenSpanKind` for spoken output
spans, and `UnitKind` for cue units. Each enum should include an `UNKNOWN` or
`CUSTOM` escape only if the design also specifies how custom names are
serialized and validated.

Acceptance: no domain-model example in the design uses bare `kind: str` for
built-in source ranges or spoken spans unless an open-set extension policy is
documented next to it.

## Milestone 4: `mdast` compatibility detection

Revise the Markdown parser strategy so `mdast` use is gated by an explicit
compatibility contract. The adapter should check a supported package version
range and run a probe parse at startup or first use. The probe input must
include Markdown structures whose expected byte offsets are known. The adapter
must reject `mdast` if it omits offsets, reports only line and column data,
reports byte offsets in an unexpected shape, or returns ranges that do not
slice back to the expected source text.

Document the fallback sequence:

1. Use `mdast` only when version and probe checks pass.
2. Use the PyO3 `markdown-rs` range extractor when `mdast` is unavailable or
   incompatible.
3. Use plain-text parsing only when Markdown-aware protection is not required,
   and report a diagnostic when Markdown structure is being degraded.

Acceptance: the technical design states how `mdast` compatibility is detected,
what failure mode it maps to, and which roadmap task owns the probe test.

## Milestone 5: Roadmap and user-facing documentation alignment

Update `docs/roadmap.md` so the design fixes are sequenced before the tasks
that would freeze affected contracts. The likely updates are:

- Make JSONL serialization task 2.3.2 depend on the explicit JSONL contract.
- Make renderer task 4.2.1 depend on the `RenderResult` decision.
- Make delivery tasks 4.3.1 through 4.3.3 depend on the revised delivery grammar
  and exit-code taxonomy.
- Make Markdown parser task 2.1.3 include the `mdast` compatibility probe.
- Make source range tasks 2.1.2 and TTS range detector task 2.2.1 refer to the
  typed range and span kind policy.
- Add success criteria for source-index memory bounds or a memory benchmark.

Update `docs/users-guide.md` only if the public CLI examples change from the
existing `--deliver file:<path>` form to the canonical
`--deliver file --deliver-to <path>` form. Keep README changes out of scope
unless links or feature summaries become inaccurate.

Acceptance: roadmap dependencies prevent implementation of affected adapters
before the contracts are resolved, and user-facing examples match the chosen
CLI grammar.

## Validation

Run these commands sequentially from the repository root:

```bash
make fmt 2>&1 | tee /tmp/fmt-prosidy-darn-resolve-logisphere-review.out
make check-fmt 2>&1 | tee /tmp/check-fmt-prosidy-darn-resolve-logisphere-review.out
make markdownlint 2>&1 | tee /tmp/markdownlint-prosidy-darn-resolve-logisphere-review.out
make nixie 2>&1 | tee /tmp/nixie-prosidy-darn-resolve-logisphere-review.out
git diff --check
```

Expected results:

```plaintext
make fmt exits 0
make check-fmt exits 0
make markdownlint exits 0
make nixie exits 0
git diff --check exits 0
```

If `make fmt` rewrites unrelated Markdown, inspect `git diff` and restore
unrelated churn before committing.

## Progress

- [x] 2026-05-09: Drafted plan from
  `docs/prosidy-darn-logisphere-design-stage-review.md` and the current
  technical design.
- [x] 2026-05-09: Approved for implementation and moved to in-progress state.
- [x] 2026-05-09: Milestone 1 complete. The technical design now specifies
  `RenderResult` and a JSONL cue-sheet wire contract.
- [x] 2026-05-09: Milestone 2 complete. The CLI contract now has delivery,
  feedback, and timeout exit codes plus canonical `--deliver` / `--deliver-to`
  grammar.
- [x] 2026-05-09: Milestone 3 complete. The domain model now uses typed range
  and spoken-span kinds and treats `SourceIndex` as a swappable protocol.
- [x] 2026-05-09: Milestone 4 complete. The Markdown adapter strategy now
  requires `mdast` version checks and a runtime compatibility probe.
- [x] 2026-05-09: Milestone 5 complete. Roadmap tasks and user-facing CLI
  examples now align with the revised contracts.
- [x] 2026-05-09: Validation commands passed and evidence logs were recorded.

## Surprises & Discoveries

- 2026-05-09: The technical design already mentions JSONL in several places,
  but the actual JSONL wire contract is not centralized. This confirms T3 is a
  design gap rather than a wording issue.
- 2026-05-09: The roadmap already has tasks for JSONL serialization, renderers,
  and delivery, so the follow-up can mostly add dependencies and success
  criteria instead of inventing new phases.
- 2026-05-09: Implementation is documentation-only at this stage, matching the
  plan constraint. No Python source files or dependency manifests need changes.
- 2026-05-09: The user guide still used the older colon-packed delivery
  examples, so the public-facing examples needed to move with the technical
  design to avoid teaching a deprecated grammar before implementation exists.
- 2026-05-09: `make fmt` rewrote `docs/scripting-standards.md`, which is not
  part of this plan. The unrelated formatter churn was restored before the
  remaining gates ran.

## Decision Log

- 2026-05-09: Treat `RenderResult` as the preferred renderer contract because it
  resolves P5 without committing v1 to a streaming interface before any
  streaming renderer exists.
- 2026-05-09: Treat delivery and feedback failures as separate exit-code
  domains because the review identifies agent branching as the key consumer of
  the taxonomy.
- 2026-05-09: Prefer typed built-in kinds with a documented extension policy
  over unrestricted `str` fields, because the current design already uses
  `UnitKind` and should not mix typing styles in the domain model.
- 2026-05-09: Keep implementation blocked until this ExecPlan is approved. The
  current request is to plan the review resolution, not to execute the design
  edits.
- 2026-05-09: User approved implementation of this ExecPlan. Proceed with
  design and roadmap edits while keeping implementation code out of scope.
- 2026-05-09: Use only the split `--deliver <scheme>` plus `--deliver-to`
  grammar as canonical in documentation. Colon-packed `file:<path>` and
  `webhook:<url>` forms remain a future compatibility option only if
  `agent-context` still advertises the split grammar.
- 2026-05-09: Keep source-index memory validation in the roadmap rather than
  inventing a benchmark now, because this change set is documentation-only and
  no `SourceIndex` implementation exists yet.

## Outcomes & Retrospective

The design-stage review concerns are resolved in documentation. The technical
design now defines `RenderResult`, a JSONL cue-sheet contract, delivery and
feedback exit codes, canonical delivery grammar, typed range and span kinds, a
swappable `SourceIndex` protocol, memory-validation expectations, and `mdast`
version/probe requirements. The roadmap now sequences those decisions before
affected implementation tasks, and the user guide examples use the canonical
delivery grammar.

Validation passed with these logs:

- `/tmp/fmt-prosidy-darn-resolve-logisphere-review-final.out`;
- `/tmp/check-fmt-prosidy-darn-resolve-logisphere-review-final.out`;
- `/tmp/markdownlint-prosidy-darn-resolve-logisphere-review-final.out`;
- `/tmp/nixie-prosidy-darn-resolve-logisphere-review-final.out`;
- `/tmp/diff-check-prosidy-darn-resolve-logisphere-review-final.out`.

No Python implementation or dependency changes were made. Streaming renderers
remain intentionally deferred to a future port; the v1 renderer contract now
has enough return metadata for binary or multi-part renderers without claiming
to support streaming.

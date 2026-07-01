# Prosidy Darn roadmap

This roadmap translates
[docs/prosidy-darn-technical-design.md](prosidy-darn-technical-design.md) into
an outcome-oriented delivery sequence. It does not promise dates. Each phase
carries one testable idea at the GIST level; each step answers a sequencing
question; each task is a review-sized execution unit.

The roadmap treats the technical design as the source of truth. Architectural
decision records (ADRs) should be added under `docs/` as the open decisions in
the design are resolved.

Assumed team: one primary engineer with part-time review capacity. The v1 scope
is Phases 1-3; that scope is negotiable if capacity is constrained. The full
six-phase roadmap is intentionally broader than v1 and should be triaged
separately.

Open design decisions from SS18 map to these resolution deadlines and tasks:

- Markdown parser strategy: resolve before Phase 1 exit in task 1.2.1. Record
  `docs/adr-001-markdown-parser-boundary.md`.
- Tokenizer and semantic-scoring dependency policy: resolve before Phase 1 exit
  in task 1.2.2. Record `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`.
- Profile custom rule-expression policy: resolve before Phase 2 start in task
  1.2.4. Record `docs/adr-003-profile-rule-expression-policy.md`.
- Import-boundary checker: resolve before Phase 1 exit in task 1.2.3. Record
  `docs/adr-004-import-boundary-fitness-check.md`.
- First non-SSML vendor renderer: defer until Phase 5+ and resolve in task
  6.2.1. Record `docs/adr-005-first-vendor-renderer.md` only when that task
  starts.

Additional accepted ADRs constrain implementation scope:

- Test-matrix phase scope is recorded in
  `docs/adr-006-test-matrix-phase-scope.md`.
- Observability scope is recorded in
  `docs/adr-007-cli-observability-scope.md`.

## 1. Foundational contracts and build spine

Idea: if Prosidy Darn settles its package boundary, hexagonal architecture,
configuration model, and verification contracts before feature work starts,
later slices can converge on one coherent v1 architecture instead of reworking
interfaces after adapters exist.

This phase establishes the contracts that would be expensive to change once the
CLI, parser adapters, and renderers depend on them.

Phase 1 acceptance checklist:

- developer documentation checks pass;
- initial ADRs exist under `docs/` for the v1 blocking decisions;
- local formatting, Markdown linting, and diagram validation pass.

### 1.1. Establish baseline developer documentation and ADR locations

This step answers whether contributors have enough maintainer-facing guidance
to implement Phase 1 consistently. Its outcome gates the ADR and package
boundary work that follows. See prosidy-darn-technical-design.md §§4, 9, 16,
and 18.

- [x] 1.1.1. Create baseline developer docs and initial ADR files.
  - Add `docs/developers-guide.md` with the hexagonal package layout, local
    quality gates, testing expectations, and documentation update rules.
  - Place the initial ADR files under `docs/` so Phase 1 decisions have stable
    review locations before implementation begins.
  - See prosidy-darn-technical-design.md §§4, 9, 16, and 18.
  - Success: developer documentation checks pass, and ADR paths are discoverable
    from the roadmap and developers' guide.

### 1.2. Ratify the v1 decisions that block implementation

This step answers which design choices are fixed for v1 and which remain
swappable behind ports. Its outcome informs dependency selection, package
layout, and the first implementation slice. See
prosidy-darn-technical-design.md §§8, 10, and 18.

- [x] 1.2.1. Record the Markdown parser boundary as an ADR.
  - Requires 1.1.1.
  - Decide whether v1 ships one Markdown-aware parser plus plain text or ships
    both `mdast` and a PyO3 `markdown-rs` range extractor immediately.
  - Write `docs/adr-001-markdown-parser-boundary.md`.
  - See prosidy-darn-technical-design.md §§1 and 10.
  - Success: one accepted ADR defines the parser adapter order and fallback
    behaviour.
- [x] 1.2.2. Record the token-limit and semantic-scoring dependency policy.
  - Requires 1.1.1 and 1.2.1.
  - Decide which token counter is optional in v1 and how embedding adapters stay
    out of the core import path.
  - Write `docs/adr-002-tokenizer-and-semantic-scoring-policy.md`.
  - See prosidy-darn-technical-design.md §§7, 10, and 18.
  - Success: optional dependencies can be installed or omitted without changing
    the public segmentation API.
- [ ] 1.2.3. Record the import-boundary enforcement decision.
  - Requires 1.1.1 and 1.2.1.
  - Select the CI fitness function that prevents `domain` and `application`
    modules from importing adapters, Cyclopts, or renderer infrastructure.
  - Write `docs/adr-004-import-boundary-fitness-check.md`.
  - See prosidy-darn-technical-design.md §§4, 5, 9, and 16.
  - Success: the chosen check can fail a boundary violation in a minimal
    fixture branch.
- [ ] 1.2.4. Record the profile rule-expression policy.
  - Requires 1.1.1 and 1.2.2.
  - Decide whether profile files allow arbitrary custom rule expressions or only
    named rule weights before Phase 2 starts.
  - Write `docs/adr-003-profile-rule-expression-policy.md`.
  - See prosidy-darn-technical-design.md §§7, 8, and 18.
  - Success: profile configuration can be implemented without adding a new
    expression-language decision in the segmenter.

### 1.3. Establish the package skeleton and dependency spine

This step answers whether the repository can express the design's ports and
adapters without leaking framework concerns into the domain. See
prosidy-darn-technical-design.md §§4-6 and 9.

- [ ] 1.3.1. Create the hexagonal package layout.
  - Requires 1.2.3.
  - Add `domain`, `application`, `ports`, `adapters`, and `config` packages.
  - Preserve the existing public import surface while introducing the new
    structure.
  - Success: the package imports without optional adapter dependencies.
- [ ] 1.3.2. Add the v1 runtime and development dependencies.
  - Requires 1.2.1 and 1.3.1.
  - Add Cyclopts and Rich as runtime dependencies.
  - Add `pytest-bdd`, `syrupy`, and Hypothesis to the development dependency
    group alongside `pytest`.
  - See prosidy-darn-technical-design.md §§8, 13, and 16.
  - Success: `make build` installs the declared v1 toolchain without manual
    package installation.
- [ ] 1.3.3. Wire the architecture fitness check into the local gate.
  - Requires 1.2.3 and 1.3.1.
  - Add the selected import-boundary check to the appropriate Makefile target.
  - See prosidy-darn-technical-design.md §§4, 9, and 16.
  - Success: a deliberate domain-to-adapter import fails the check with an
    actionable diagnostic.
- [ ] 1.3.4. Add maturin and PyO3 validation for native wheels.
  - Requires 1.3.1 and 1.3.2.
  - Add a minimal PyO3 extension, maturin build configuration, and compatibility
    tests for maturin pin synchronization, PyO3 lockfile alignment, native wheel
    metadata, and extension import execution.
  - See
    [Update maturin and PyO3 validation](execplans/test-maturin-pyo3-test-upgrade.md).
  - Success: native wheel creation and installed extension import execution are
    verified, and `make check-fmt`, `make lint`, `make typecheck`, `make test`,
    `cargo fmt --manifest-path rust/Cargo.toml --check`, and
    `cargo check --manifest-path rust/Cargo.toml` pass.

### 1.4. Build the shared fixture and contract corpus

This step answers whether the project can verify source fidelity, Unicode
offsets, and output contracts before the segmenter grows complex. The fixture
corpus informs every subsequent vertical slice. See
prosidy-darn-technical-design.md §§6, 7, and 16.

- [ ] 1.4.1. Add canonical Markdown and prose fixtures.
  - Requires 1.3.1.
  - Cover headings, paragraphs, lists, blockquotes, tables, inline code, code
    blocks, dialogue, quote attribution, and scene breaks.
  - Include ASCII and non-ASCII examples with smart quotes, combining marks,
    emoji, accented names, and non-Latin scripts.
  - Success: fixtures exercise every range kind required by the design.
- [ ] 1.4.2. Add deterministic snapshot fixtures for output contracts.
  - Requires 1.4.1 and 1.3.2.
  - Use `syrupy` for `agent-context`, explanation output, JSONL cue sheets,
    SSML fragments, and Rich terminal output.
  - See prosidy-darn-technical-design.md §16.
  - Success: snapshot identifiers, timestamps, and generated unit IDs are
    stable across repeated runs.

## 2. Literal cue segmentation from Markdown and prose

Idea: if the first vertical slice can turn Markdown or prose into literal,
Unicode-safe, non-overlapping cue units, Prosidy Darn already solves the core
TTS preparation problem before renderers, embeddings, or vendor integrations
land.

This phase delivers the first useful library surface: source text in, cue units
out, with explainable boundaries and hard source-slice invariants.

### 2.1. Prove source indexing and structural ranges are trustworthy

This step answers whether Prosidy Darn can preserve source provenance across
Python and Rust offset models. Its outcome unlocks all later segmentation work.
See prosidy-darn-technical-design.md §§6, 7.1, and 10.

- [ ] 2.1.1. Implement the Unicode source index.
  - Requires steps 1.2-1.4.
  - Provide character-to-byte and byte-to-character conversion for every valid
    source boundary through the `SourceIndex` protocol.
  - Include a memory smoke test or benchmark for ASCII-dominant and
    multibyte-heavy Markdown documents.
  - Success: Hypothesis-generated Unicode inputs round-trip offsets without
    slicing inside a UTF-8 code point, and the default index avoids
    dict-per-byte memory growth.
- [ ] 2.1.2. Implement source range types and range merging.
  - Requires 2.1.1.
  - Use the `SourceRangeKind` enum for built-in structural ranges and document
    custom adapter kinds through the v1 extension policy.
  - Merge overlapping or adjacent same-kind ranges so one structural violation
    receives one punishment.
  - See prosidy-darn-technical-design.md §§6 and 7.1.
  - Success: representative fixtures produce deterministic merged range sets
    and reject misspelled built-in range kinds.
- [ ] 2.1.3. Implement Markdown and plain-text structure parsers.
  - Requires 2.1.2 and 1.2.1.
  - Add the selected Markdown parser adapter, its version and compatibility
    probes, and a plain-text fallback adapter.
  - Keep the PyO3 range extractor as a contingency only if ADR-001 selects it
    before implementation.
  - See prosidy-darn-technical-design.md §10.
  - Success: parser adapters return source ranges without rendering Markdown
    back to text, and incompatible parser versions fail with a parser
    capability diagnostic or use the ADR-approved contingency adapter.

### 2.2. Deliver the deterministic cue splitter

This step answers whether the `darn-it`-style punishment model adapts cleanly
to TTS cue boundaries. Its outcome proves the core library can produce usable
directable units without optional semantic models. See
prosidy-darn-technical-design.md §§7.2-7.5.

- [ ] 2.2.1. Implement TTS range detectors for words, sentences, clauses, and
  dialogue.
  - Requires 2.1.3.
  - Include dialogue quotes, quote attribution, dialogue turns, parentheticals,
    abbreviations, initialisms, and pronunciation-sensitive tokens.
  - Use the `SourceRangeKind` and `SpokenSpanKind` policies for emitted range
    and spoken-span categories.
  - Success: fixture ranges cover every detector category without crashing on
    malformed or unusual prose, and built-in categories are not serialized as
    arbitrary strings.
- [ ] 2.2.2. Implement the boundary lattice and default punishment rules.
  - Requires 2.2.1.
  - Include priority tiers, shaped paragraph and heading penalties, dialogue
    attribution penalties, and emergency boundaries.
  - Create the approved regression corpus for single-narrator, dialogue-heavy,
    Markdown-heavy, pathological long-paragraph, and Unicode-heavy inputs.
  - See prosidy-darn-technical-design.md §§7.2-7.3.
  - Success: `explain` data can identify the rule contributions for accepted
    and rejected boundaries, and corpus snapshots catch punishment-value drift.
- [ ] 2.2.3. Implement edge-cost dynamic programming.
  - Requires 2.2.2.
  - Combine boundary punishment with unit duration, directability, speaker
    consistency, internal-break, renderer-limit, and orphan costs.
  - See prosidy-darn-technical-design.md §§7.4-7.5.
  - Success: generated units satisfy source-slice integrity, coverage and
    ordering, and boundary legality properties.
- [ ] 2.2.4. Implement the diagnostic fallback ladder.
  - Requires 2.2.3.
  - Allow progressively lower-priority boundaries only when hard limits make
    the preferred lattice impossible.
  - See prosidy-darn-technical-design.md §§7.2 and 7.5.
  - Success: impossible spans fail with a source-backed diagnostic instead of a
    silent word split.

### 2.3. Expose the library segmentation API

This step answers whether callers can use segmentation without knowing about
CLI configuration or adapter wiring. See prosidy-darn-technical-design.md §9.

- [ ] 2.3.1. Implement `SegmentOptions`, `TTSProfile`, and `segment_markdown`.
  - Requires 2.2.4.
  - Keep Cyclopts and adapter implementation types out of the public library
    API.
  - See prosidy-darn-technical-design.md §§8-9.
  - Success: a Python caller can segment Markdown with built-in profiles and
    receive `TTSUnit` records.
- [ ] 2.3.2. Implement JSONL cue serialization.
  - Requires 2.3.1.
  - Preserve source offsets, spoken-text placeholders, unit kind, speaker,
    direction, subspans, and diagnostics.
  - Implement the explicit JSONL cue-sheet contract: UTF-8 text, one cue object
    per line, tuple fields as arrays, stable optional fields as JSON null, and
    unknown top-level fields rejected by default in v1.
  - See prosidy-darn-technical-design.md §§6, 11, and 11.1.
  - Success: JSONL output round-trips through the library without losing source
    span information and matches the documented wire contract.

## 3. Agent-native CLI cue loop

Idea: if the CLI can segment, explain, configure, and report failures through
consistent Cyclopts commands, agents and humans can use the same deterministic
cue loop before renderer integrations exist.

This phase turns the library into the primary workflow surface. It validates
the agent-native command vocabulary, tiered configuration, Rich human output,
and machine-readable contracts.

### 3.1. Deliver the day-one `segment` and `explain` commands

This step answers whether the CLI can drive the core segmentation loop without
interactive prompts or hidden formatting. See prosidy-darn-technical-design.md
§§13 and 16.

- [ ] 3.1.1. Implement the Cyclopts composition root and `segment` command.
  - Requires 2.3.2.
  - Read Markdown from `--input <path>` or stdin.
  - Emit JSONL to stdout by default and honour `--json`.
  - Success: stdin and file-input behaviour scenarios pass without prompts.
- [ ] 3.1.2. Implement the `explain` command with bounded output.
  - Requires 3.1.1.
  - Report accepted boundaries and nearby rejected candidates with rule
    contributions.
  - See prosidy-darn-technical-design.md §§7.3, 7.5, and 13.
  - Success: `--limit` bounds output and `syrupy` snapshots lock the JSON
    contract.
- [ ] 3.1.3. Implement Rich human output behind output-mode checks.
  - Requires 3.1.1 and 3.1.2.
  - Use Rich only when stdout is a terminal and machine output is not requested.
  - See prosidy-darn-technical-design.md §13.
  - Success: JSON, JSONL, and `agent-context` outputs contain no Rich markup or
    terminal control sequences.

### 3.2. Prove tiered configuration and profiles

This step answers whether Cyclopts can own configuration precedence without
leaking CLI framework concerns into the domain. See
prosidy-darn-technical-design.md §8.

- [ ] 3.2.1. Implement built-in and XDG-backed profile loading.
  - Requires 2.3.1.
  - Provide `profile list`, `profile get`, `profile save`, and
    `profile delete`.
  - See prosidy-darn-technical-design.md §§8 and 13.
  - Success: profile names appear in `agent-context`.
- [ ] 3.2.2. Implement Cyclopts configuration precedence.
  - Requires 3.2.1.
  - Apply explicit flags, `PROSIDY_DARN_` environment variables, project TOML,
    named profiles, and Python defaults in the design order.
  - See prosidy-darn-technical-design.md §8.
  - Success: `pytest-bdd` scenarios demonstrate every override level.
- [ ] 3.2.3. Validate profile and enum errors before side effects.
  - Requires 3.2.2.
  - Enumerate valid values in CLI diagnostics.
  - See prosidy-darn-technical-design.md §§13 and 15.
  - Success: invalid values return stable exit codes and actionable messages.

### 3.3. Publish machine-readable CLI introspection

This step answers whether agents can discover the command surface without
parsing prose help. See prosidy-darn-technical-design.md §§13 and 16.

- [ ] 3.3.1. Implement `agent-context`.
  - Requires steps 3.1-3.2.
  - Derive command names, flags, enum values, exit codes, output modes, and
    available profiles from the Cyclopts command specification.
  - Success: `agent-context` snapshots change only when the command contract
    changes.
- [ ] 3.3.2. Add the end-to-end CLI combination suite.
  - Requires 3.3.1.
  - Cover profile precedence, stdin and file inputs, JSON and Rich output,
    invalid enums, and delivery modes that exist by this phase.
  - See prosidy-darn-technical-design.md §16.
  - Success: the suite fails if human formatting leaks into machine output or a
    flag combination bypasses validation.
- [ ] 3.3.3. Implement local feedback capture.
  - Requires 3.3.1.
  - Store feedback in the XDG state JSONL file and expose endpoint availability
    through `agent-context`.
  - See prosidy-darn-technical-design.md §§13-14.
  - Success: feedback can be recorded without network access.

## 4. Renderable speech artefacts

Idea: if Prosidy Darn can turn cue units into standards-based speech artefacts
without making SSML the source of truth, it can support real TTS pipelines
while preserving editable cue metadata.

This phase adds spoken-text extraction, renderers, and delivery sinks. It keeps
segmentation and rendering separate so renderer limitations do not corrupt the
cue IR.

### 4.1. Produce spoken text from literal source slices

This step answers whether Markdown syntax can be removed for speech while
source provenance remains exact. See prosidy-darn-technical-design.md §§6, 10,
and 11.

- [ ] 4.1.1. Implement spoken-text extraction for Markdown source ranges.
  - Requires 2.3.2.
  - Preserve source text literally while producing TTS-friendly spoken text.
  - Success: emphasis, inline code, headings, links, and punctuation retain
    source span mappings.
- [ ] 4.1.2. Implement spoken subspans for dialogue and attribution.
  - Requires 4.1.1 and 2.2.1.
  - Represent dialogue, attribution, and narrator spans without forcing the
    segmenter to split the source unit.
  - See prosidy-darn-technical-design.md §§6 and 11.
  - Success: single-narrator and dramatized profiles can render the same unit
    through different span policies.

### 4.2. Render cue units to SSML and JSONL contracts

This step answers whether renderers can compile cue metadata without becoming
canonical storage. See prosidy-darn-technical-design.md §§11 and 13.

- [ ] 4.2.1. Implement the `CueRenderer` port and JSONL renderer adapter.
  - Requires 4.1.1.
  - Return `RenderResult` values from renderers rather than raw strings.
  - Keep renderer selection in the application layer, not the CLI adapter.
  - Success: JSONL rendering matches the library serialization contract and
    returns UTF-8 text metadata through `RenderResult`.
- [ ] 4.2.2. Implement the SSML 1.1 renderer.
  - Requires 4.2.1 and 4.1.2.
  - Map unit identifiers, paragraph and sentence structure, breaks, emphasis,
    prosody, pronunciation, substitution, and supported voice spans.
  - See prosidy-darn-technical-design.md §11.
  - Success: SSML snapshots include `<mark>` boundaries and preserve cue IDs.
- [ ] 4.2.3. Implement renderer capability checks.
  - Requires 4.2.2.
  - Flatten or reject nested voice spans according to profile and renderer
    capabilities.
  - See prosidy-darn-technical-design.md §§11 and 15.
  - Success: unsupported renderer combinations fail before writing partial
    artefacts.

### 4.3. Deliver rendered artefacts through safe sinks

This step answers whether generated artefacts can land where agents and humans
need them without ad-hoc shell redirection. See
prosidy-darn-technical-design.md §14.

- [ ] 4.3.1. Implement the `render` CLI command.
  - Requires 4.2.3.
  - Read cue JSONL and render JSONL, SSML, or WebVTT-like placeholders as
    supported targets.
  - Expose the canonical delivery grammar through Cyclopts and
    `agent-context`.
  - See prosidy-darn-technical-design.md §§11 and 13.
  - Success: render failures use the stable exit code taxonomy.
- [ ] 4.3.2. Implement `--deliver stdout` and atomic file delivery.
  - Requires 4.3.1.
  - Use `--deliver file --deliver-to <path>` for file destinations.
  - Write files atomically in the destination directory.
  - See prosidy-darn-technical-design.md §14.
  - Success: failed file writes do not leave corrupt target artefacts and use
    the delivery-failure exit code.
- [ ] 4.3.3. Implement webhook delivery.
  - Requires 4.3.2.
  - Use `--deliver webhook --deliver-to <url>` for webhook destinations.
  - Preserve a local artefact before posting, report HTTP status only after a
    successful TLS-validated HTTPS POST attempt, and map delivery failures to
    the delivery-failure exit code.
  - See prosidy-darn-technical-design.md §§14-15.
  - Success: unknown delivery schemes enumerate the supported set, and missing
    `--deliver-to` values fail before rendering.

## 5. Semantic breaks and synthesis context

Idea: if semantic scoring and synthesis windows improve cue quality without
changing the literal unit contract, Prosidy Darn can become more useful for
long-form TTS while keeping the deterministic core trustworthy.

This phase adds optional intelligence after the deterministic loop is already
usable. Each feature must degrade cleanly when optional dependencies are absent.

### 5.1. Add optional semantic-break scoring

This step answers whether local semantic cohesion can improve boundary choice
without overriding hard structural rules. See prosidy-darn-technical-design.md
§§7.3, 7.4, and 17.3.

- [ ] 5.1.1. Implement the `SemanticScorer` port and disabled adapter.
  - Requires phase 4.
  - Keep the disabled adapter as the default path.
  - Success: semantic scoring can be absent without changing deterministic
    segmentation output.
- [ ] 5.1.2. Add the first embedding-backed semantic scorer.
  - Requires 5.1.1 and 1.2.2.
  - Use scores as rewards and internal-break costs, not hard split rules.
  - See prosidy-darn-technical-design.md §§7.3-7.4.
  - Success: explanations show semantic contributions separately from
    structural punishment.
- [ ] 5.1.3. Add semantic-scoring degradation scenarios.
  - Requires 5.1.2.
  - Cover missing models, unavailable optional dependencies, and disabled
    scoring.
  - See prosidy-darn-technical-design.md §15.
  - Success: missing semantic dependencies produce diagnostics only when
    requested.

### 5.2. Plan synthesis windows without duplicating cue units

This step answers whether Prosidy Darn can provide TTS context while retaining
non-overlapping cue audio. See prosidy-darn-technical-design.md §12.

- [ ] 5.2.1. Implement synthesis-window planning.
  - Requires 4.3.1.
  - Generate context windows that retain audio only for the corresponding
    non-overlapping cue ranges.
  - Success: cue units remain a complete source partition while windows may
    overlap.
- [ ] 5.2.2. Add renderer hooks for synthesis-window metadata.
  - Requires 5.2.1.
  - Expose keep ranges, context ranges, and cue IDs to provider-specific
    renderers.
  - See prosidy-darn-technical-design.md §§11-12.
  - Success: synthesis-window metadata can be serialized without changing
    `TTSUnit.source_text`.

## 6. Deferred extensions after the v1 cue promise

Idea: if the core v1 promise is already trustworthy and boring to operate, the
project can evaluate broader extensions on product value instead of letting
them destabilize the main release.

This phase collects design scope that should wait until the deterministic
segmentation, CLI, and renderer loop is stable.

### 6.1. Evaluate richer discourse and performance inference

This step decides whether more advanced inference belongs in Prosidy Darn or in
an adjacent editing tool. See prosidy-darn-technical-design.md §§2, 7.1, and 16.

- [ ] 6.1.1. Decide whether elementary discourse unit detection graduates from
  deferred scope.
  - Requires phase 5.
  - Success: one ADR either adds discourse parsing to a future release or keeps
    it outwith the package boundary.
- [ ] 6.1.2. Decide whether performance inference needs a separate editing
  surface.
  - Requires phase 5.
  - See prosidy-darn-technical-design.md §§2 and 16.
  - Success: inferred direction metadata remains editable and is not presented
    as ground truth.

### 6.2. Evaluate vendor-specific TTS integrations

This step decides which provider-specific renderers justify first-class support
after the SSML and JSONL contracts are stable. See
prosidy-darn-technical-design.md §§11, 12, and 18.

- [ ] 6.2.1. Select the first non-SSML vendor renderer.
  - Requires phase 4.
  - Compare provider payload shape, mark support, voice-span support, and
    synthesis-window compatibility.
  - Write `docs/adr-005-first-vendor-renderer.md`.
  - Success: one ADR names the first vendor target and the renderer capability
    constraints it introduces.
- [ ] 6.2.2. Decide whether WebVTT-like timing export belongs in core.
  - Requires 5.2.2.
  - See prosidy-darn-technical-design.md §§11-12.
  - Success: timing export is either added to a future renderer slice or kept
    as downstream application scope.

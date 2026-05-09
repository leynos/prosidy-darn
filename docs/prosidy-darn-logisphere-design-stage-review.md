# Prosidy Darn -- Logisphere design-stage review

**Panel:** Full Logisphere crew **Documents under review:**

- `docs/prosidy-darn-technical-design.md` (rev 5144043)
- `docs/roadmap.md` (rev 5144043)

**Review date:** 2026-05-09

______________________________________________________________________

## 1. Proposal summary

Prosidy Darn is a Python package that splits Markdown and narrative prose into
directable text-to-speech cue units. It adapts the `darn-it` chunking model
from document retrieval to speech direction, replacing Markdown-preservation
punishment with performance-beat-preservation punishment. The design uses
hexagonal architecture, a dynamic-programming segmenter, an engine-neutral cue
intermediate representation, and an agent-native Cyclopts CLI.

The design document is thorough. It makes a large number of decisions and
defers a smaller, explicit set. The roadmap translates the design into six
phased delivery stages.

## 2. Core bets

The design is wagering on the following assumptions. The review examines each.

| #   | Bet                                                                                                                                                                              | Confidence                                                                                                                                                                            |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1  | The `mdast` Python package exposes stable, byte-accurate source positions sufficient for segmentation.                                                                           | Medium. The design acknowledges this may not hold and provides a PyO3 fallback, but leaves the decision open.                                                                         |
| B2  | Python dynamic programming is fast enough for the bounded shortest-path solve over realistic document lengths.                                                                   | High for typical prose. Low confidence for adversarial inputs (very long single-paragraph documents, machine-generated Markdown with thousands of list items).                        |
| B3  | A single punishment-cost model can serve audiobook narration, dramatised multivoice, and low-latency streaming through profile parameterisation alone.                           | Medium. The punishment table and profile values are initial guesses. The design acknowledges tuning is needed but does not describe how profile values will be validated empirically. |
| B4  | Cyclopts' tiered configuration model is expressive enough to own all CLI configuration without custom precedence logic.                                                          | High. The Cyclopts documentation supports this, and the design keeps library callers outside the Cyclopts path.                                                                       |
| B5  | SSML 1.1 is a sufficient first renderer target despite processor-specific behaviour.                                                                                             | High for v1 scope. The design correctly treats SSML as a lossy delivery artefact and keeps the cue IR authoritative.                                                                  |
| B6  | The team can build and maintain a hexagonal Python architecture with Rust parser bindings, four renderer targets, webhook delivery, XDG profile storage, and a full test matrix. | Unknown. The design document says nothing about team size or capacity. The roadmap is six phases deep with over 40 individual tasks.                                                  |

______________________________________________________________________

## 3. Panel findings

### 3.1. Pandalump 🐼 -- Structural integrity

**P1. 🟢 Hexagonal decomposition is well-drawn.** The dependency direction is
consistent: domain inward, adapters outward, ports at the seam. The Mermaid
diagram, module table (Table 5), and port tables (Tables 2-3) reinforce each
other. The naming vocabulary is coherent. A new contributor could build the
right mental model from the document alone.

**P2. 🟡 `SourceIndex` lives in the domain but serves the adapter boundary.**
The design correctly identifies the byte/char offset bridge as a correctness
property (SS6). However, `SourceIndex` holds `byte_to_char: dict[int, int]` and
`char_to_byte: tuple[int, ...]`. For a 500 KB document, `byte_to_char` is a
dict with up to 500,000 entries. This is a structural decision with performance
implications that the design treats as a pure domain concern. Consider whether
the index should be a domain protocol with a default implementation rather than
a single frozen dataclass -- this would let a Rust-backed adapter supply a more
compact index without violating the boundary.

**P3. 🟡 The `config` module sits outside the hexagonal taxonomy.** Table 5
lists `prosidy_darn.config` as the composition root. A composition root is
infrastructure, not domain. The document should clarify that `config` is an
infrastructure module that wires ports to adapters and is permitted to import
from `adapters`. Otherwise the import-boundary fitness check will need a
special-case exemption that weakens the rule.

**P4. 🟢 `TTSUnit` as the stable contract is a good load-bearing choice.** The
cue IR sits between segmentation and rendering, and both code paths speak it.
Freezing it early is the right call. The roadmap correctly builds JSONL
serialisation immediately after domain types.

**P5. 🔴 The `Renderer` protocol is under-specified for extensibility.** The
protocol has a single `render(units, options) -> str` method that returns a
string. This works for SSML and JSONL but will not work for WebVTT-like output
with timing data, vendor payloads that are binary or multi-file, or any
renderer that needs streaming output. The return type should be reconsidered
before adapters are built against it. At minimum, a `RenderResult` type that
can carry `str | bytes` plus metadata (content type, encoding, fragment vs
document) would prevent a breaking protocol change when the second renderer
lands.

**P6. 🟡 `SpokenSpan.kind` and `SourceRange.kind` are `str`, not enums.** The
design defines `UnitKind` as a `StrEnum` but leaves `SpokenSpan.kind` and
`SourceRange.kind` as bare `str`. This creates a stringly-typed seam at the
centre of the domain model. If these are extensible (open set), the design
should say so explicitly. If they are closed, they should be enums. Mixing
patterns in the same layer invites bugs.

### 3.2. Wafflecat 🐈🧇 -- Alternative futures

**W1. 💡 No alternatives are documented.** The design is well-reasoned, but it
does not record which alternatives were considered or why they were rejected.
For a document this thorough, the absence is conspicuous. At minimum, the
design should record why greedy segmentation was rejected in favour of global
DP, and why a simpler sentence-boundary splitter was insufficient. These are
the questions a future maintainer will ask.

**W2. 🟡 The 80% version is much simpler than the proposed architecture.** A
sentence splitter (using `pysbd` or similar) that respects paragraph
boundaries, emits literal slices, and writes JSONL would solve the core "split
prose into TTS-sized chunks" problem without dynamic programming, punishment
tuning, profiles, synthesis windows, or hexagonal architecture. The design is
building for the 100% case -- dramatised multivoice with semantic scoring --
from the start. The roadmap partially addresses this by phasing semantic
scoring into Phase 5, but the architecture carries the weight of all phases
from Phase 1.

The design should explicitly state why the simpler approach is insufficient. If
the answer is "greedy splitting produces bad cuts at paragraph, dialogue, and
heading boundaries," that is a strong justification -- but it should be written
down.

**W3. 🟢 The `darn-it` prior art is a genuine structural advantage.** Adapting
a proven chunking model to a new domain is lower-risk than inventing a new one.
The design correctly identifies which properties transfer (literal slicing,
global optimisation) and which do not (the objective function). This is a
well-chosen bet.

**W4. 🟡 Deferred decisions are accumulating.** SS18 lists five open decisions.
The roadmap adds several more implicit ones (which import-boundary checker,
which tokeniser, which vendor renderer). The design would benefit from a
decision deadline for each: which must be resolved before Phase 1 code, which
can wait until Phase 2, and which are genuinely deferrable to Phase 5+. The
roadmap partially addresses this with dependency annotations, but the mapping
from open decisions to roadmap tasks is not explicit.

### 3.3. Buzzy Bee 🐝 -- Scaling and cost

**Z1. 🟡 No input size bounds or performance targets are stated.** The design
does not specify expected document sizes, processing time targets, or memory
budgets. For a CLI tool processing prose, "a novel chapter" (5,000-15,000
words) is a reasonable implicit target, but the design should state it. The
dynamic-programming segmenter's complexity is `O(N * W)` where `N` is the
number of lattice positions and `W` is the successor window width. For a
100,000-word document with word-level boundaries, `N` could reach 100,000. The
bounded successor search keeps `W` manageable, but the design should state the
expected `N` range and confirm that the DP table fits comfortably in memory.

**Z2. 🟢 The bounded successor search is the right cost control.** Limiting the
DP search by duration, character count, and renderer limits prevents quadratic
blowup. This is a direct carry-over from `darn-it` and is well-understood.

**Z3. 🟡 The `SourceIndex` dict representation is expensive for large
documents.** As noted in P2, `byte_to_char: dict[int, int]` for a 500 KB
document creates significant memory pressure. A sorted array with binary
search, or a simple formula for ASCII-dominated text with fallback for
multi-byte sequences, would be more efficient. This matters if Prosidy Darn is
used as a library processing many documents in a batch pipeline.

**Z4. 💡 Webhook delivery timeout is capped at 30 seconds but there is no
overall CLI timeout.** A hung Markdown parser or a pathological DP solve could
block the CLI indefinitely. Consider whether the CLI should have a configurable
overall wall-clock timeout.

### 3.4. Telefono ☎️ -- Contracts and interfaces

**T1. 🟢 The `agent-context` command is a strong contract choice.** Deriving
machine-readable command metadata from the Cyclopts specification rather than
maintaining a separate schema eliminates a class of drift bugs. The versioned
`schema_version` field allows additive evolution.

**T2. 🔴 The exit code taxonomy has a gap.** Table 6 defines codes 0-7 but does
not reserve a code for timeout, webhook delivery failure, or feedback
submission failure. The webhook delivery section (SS14) says to "report HTTP
status" but does not specify which exit code a delivery failure produces. If
delivery failure is exit code 6 ("Rendering failed"), that conflates two
different failure domains. If it is a new code, the taxonomy needs extending
before the CLI ships.

**T3. 🟡 JSONL serialisation contract is implied but not specified.** The
design says the JSONL renderer outputs `TTSUnit` records and that JSONL
round-trips through the library. But the document does not specify the JSON
field names, the serialisation of `tuple` fields, the handling of `None` vs
absent keys, or the treatment of `PerformanceDirection` defaults. These are the
details that break interoperability. The first JSONL snapshot test will define
the contract by accident if it is not specified deliberately.

**T4. 🟢 The stable exit code contract is valuable for agent consumers.**
Agents can branch on exit codes without parsing stderr. The design correctly
separates data (stdout) from diagnostics (stderr).

**T5. 🟡 The `--deliver` scheme grammar is ad-hoc.** `stdout`, `file:<path>`,
and `webhook:<url>` use three different syntactic patterns. `stdout` is a bare
keyword; `file` and `webhook` use colon-separated schemes. If a fourth delivery
method is added (e.g. `s3:<bucket>/<key>`), the scheme parser will need to
handle colons in paths on Windows and colons in URIs. Consider whether
`--deliver-to` with a more structured argument (or separate `--deliver-file`,
`--deliver-webhook` flags) would be less fragile.

### 3.5. Doggylump 🐶 -- Failure modes and operations

**D1. 🟢 The fallback ladder (SS7.5) is well-designed.** Progressive
degradation from preferred boundaries through clause, word, and grapheme-safe
emergency boundaries, terminating in an explicit error rather than a silent
word split, is exactly right. This is the design's strongest operational
feature.

**D2. 🟡 The `mdast` fallback chain has no timeout or version pinning.** The
design says "use `mdast` if it exposes stable source positions; use PyO3 if it
does not." But there is no specification for how the adapter detects "stable
enough" positions at runtime. Does it check a version number? Run a probe
parse? Catch an exception? If `mdast` changes its position format in a patch
release, the adapter needs a detection mechanism that does not silently produce
wrong offsets.

**D3. 🟡 Webhook delivery failure preserves the local artefact "when
possible."** The "when possible" qualifier is concerning. Under what
circumstances is local preservation not possible? If the artefact is only in
memory and the process exits after a webhook failure, it is lost. The design
should specify that the artefact is always written locally before attempting
webhook delivery, making local persistence unconditional.

**D4. 🟢 Failure mode table (Table 7) covers the right scenarios.** The seven
failure modes and their responses are specific and actionable. The emphasis on
diagnostic output before silent degradation is good operational design.

**D5. 💡 No guidance on observability.** For a CLI tool this may be acceptable,
but the design mentions webhook delivery, optional network-dependent semantic
scoring, and upstream feedback posting. These are operations that benefit from
structured logging. The design should state whether structured logging is in
scope or explicitly out of scope.

### 3.6. Dinolump 🦕 -- Long-term viability and team impact

**L1. 🔴 Team capacity is unaddressed.** The design describes a system with: a
hexagonal Python package, a Rust/PyO3 parser binding, four renderer targets,
webhook delivery with TLS enforcement, XDG profile storage, five-level
configuration precedence, an agent-context introspection layer, a feedback
system, and a test matrix spanning `pytest`, `pytest-bdd`, `syrupy`, and
Hypothesis across multiple profiles, renderers, input modes, and delivery
schemes. The roadmap contains 40+ tasks across six phases. Neither document
mentions team size, contributor experience, or capacity.

If this is a solo project, the scope is ambitious. The hexagonal architecture
and comprehensive test strategy are justified if the project will be maintained
long-term, but the initial build cost is significant. The design should
acknowledge the team context and identify which parts of the architecture are
negotiable if capacity is constrained.

**L2. 🟡 The Rust/Python bridge adds cognitive load.** The design requires
contributors to understand Python packaging, Rust's `markdown` crate, PyO3
bindings, UTF-8 byte offsets vs Python code-point offsets, and the interaction
between them. This is a non-trivial knowledge requirement. The design mitigates
this by keeping the Rust layer as a "parser or range oracle," which is the
right constraint. But the fallback chain (`mdast` -> PyO3 -> plain text) means
three parser implementations to maintain. Consider whether two (the selected
primary + plain text) is sufficient for v1.

**L3. 🟢 Technology choices are mainstream.** Python, Cyclopts, Rich, pytest,
Hypothesis, TOML, JSONL, SSML -- these are well-understood technologies with
active communities. The Rust dependency is narrowly scoped. Hiring and
onboarding risk is low.

**L4. 🟡 The testing strategy is comprehensive but expensive.** Four test tools
(`pytest`, `pytest-bdd`, `syrupy`, Hypothesis) across a combinatorial matrix of
profiles, renderers, inputs, and delivery schemes will generate a large test
suite. This is good for confidence but expensive to maintain. The roadmap
should identify which test dimensions are mandatory for each phase and which
are deferred. Snapshot churn from `syrupy` is a known maintenance cost; the
design's guidance on deterministic fixtures is helpful but may not be
sufficient.

**L5. 🟢 The document is self-documenting.** The naming is consistent, the
terminology table is useful, the module layout is clear, and the Mermaid
diagram matches the textual description. A new contributor can understand the
architecture from the document alone. This is rare and valuable.

______________________________________________________________________

## 4. Pre-mortem (Doggylump leads)

> _It is six months from now. Prosidy Darn has caused a significant incident.
> Working backwards._

### Scenario A: Silent offset corruption

**What happened:** The `mdast` package released a minor version that changed
source position representation from byte offsets to line/column pairs. The
adapter did not detect the change because it duck-typed the position fields.
Segmentation produced units with wrong `source_start`/`source_end` values. A
downstream TTS pipeline synthesised garbled audio from corrupted source slices.
The error was not caught because the Hypothesis property tests only ran against
the plain-text adapter in CI.

**Blast radius:** Every document processed after the `mdast` upgrade produced
corrupt output. No data was lost (source text is immutable), but trust in the
tool was damaged.

**Signal missed:** No integration test verified that the `mdast` adapter
produced correct offsets for a known fixture after dependency updates.

**Mitigation:** Add a pinned `mdast` version with an explicit compatibility
test. Add a source-slice integrity assertion that runs on every segmentation
call, not just in property tests. Make `SourceIndex` validation a runtime
invariant, not just a test-time property.

### Scenario B: Punishment tuning death spiral

**What happened:** A user reported that the `audiobook_single_narrator` profile
split a short dialogue exchange into five tiny units. A contributor adjusted the
 `dialogue_turn_reward` upward to fix the report. This caused a different
document to produce a single 25-second unit that exceeded the TTS engine's
practical limit. Another adjustment was made. After three rounds of tuning, the
punishment values had drifted from their design rationale and no one could
explain why `dialogue_turn_reward` was -750 instead of -450.

**Blast radius:** Profile instability. Users could not trust that an upgrade
would preserve their existing segmentation.

**Signal missed:** No regression corpus of "known good" segmentations existed
to catch punishment-value regressions.

**Mitigation:** Establish a regression corpus of representative documents with
approved segmentation outputs. Run the corpus on every punishment-value change.
Document the rationale for each initial value in the code, not just in the
design document. Consider making punishment values part of the snapshot
contract.

### Scenario C: Webhook credential leak in feedback payload

**What happened:** Despite the design's explicit security requirements (SS14),
a contributor added a `context` field to the feedback payload that included the
full `SegmentOptions` object for debugging. The options object contained the
profile name, which was benign, but also the `PROSIDY_DARN_FEEDBACK_ENDPOINT`
value, which contained an authentication token in the URL query string. The
sanitiser allowlist was not updated to block the new field, because the
allowlist operated on the feedback entry, not on nested objects.

**Blast radius:** Authentication tokens for the feedback endpoint were posted
back to the feedback endpoint itself (circular but not externally exploitable)
and persisted in the local JSONL file (readable by any local process).

**Signal missed:** The allowlist was a flat field list, not a recursive
sanitiser. No test verified that arbitrary additions to the payload were
stripped.

**Mitigation:** Implement the sanitiser as a builder that constructs the
payload from allowed fields rather than stripping disallowed fields from an
existing object. Use a "construct, don't filter" pattern. Add a test that
attempts to smuggle a known-bad field and asserts it is absent.

______________________________________________________________________

## 5. Alternatives checkpoint (Wafflecat leads)

### Strongest alternative: Greedy sentence splitter with post-hoc merging

Instead of dynamic programming over a boundary lattice, segment greedily at
sentence boundaries, then merge adjacent units that fall below the minimum
duration and split units that exceed the maximum. Use a simple priority queue
for merge candidates (prefer merging within the same paragraph, then within the
same dialogue turn, then across paragraphs).

**What it trades away:**

- Global optimality. A greedy splitter cannot choose an awkward local cut to
  preserve a better later structure. The DP solver can.
- Shaped punishment. Inverse-triangular paragraph-internal costs and
  heading-adjacent decay are not expressible in a greedy model.
- Extensibility to semantic scoring. The DP lattice is a natural place to
  inject semantic-break rewards; a greedy merger is not.

**What it gains:**

- Dramatically simpler implementation. No lattice construction, no punishment
  engine, no DP solver. The core algorithm fits in 100 lines.
- Easier tuning. Merge/split thresholds are intuitive; punishment values are
  not.
- Faster time to a working tool. The greedy version could ship in Phase 1
  alone.

**Assessment:** The greedy alternative is genuinely viable for single-narrator
audiobook use cases where sentence boundaries are usually the right split
points. It falls down for dramatised multivoice, where speaker-turn boundaries
and dialogue attribution matter more than sentence boundaries. The design's
choice of DP is justified _if_ the dramatised use case is a first-class goal.
If the initial audience is single-narrator audiobook producers, the greedy
approach would deliver value sooner and the DP solver could be introduced later
as a "quality upgrade." The design should state which audience is primary.

______________________________________________________________________

## 6. Verdict

### ⚠️ Proceed with conditions

The design is structurally sound, well-documented, and makes defensible
architectural choices. The hexagonal decomposition is clean, the cue IR is a
good stable contract, the fallback ladder is well-designed, and the
agent-native CLI contract is strong. The `darn-it` lineage gives the DP
segmenter a solid foundation.

However, three issues should be addressed before implementation begins:

### Findings by severity

| #   | Severity | Expert | Finding                                                                                  |
| --- | -------- | ------ | ---------------------------------------------------------------------------------------- |
| P5  | 🔴       | 🐼     | `Renderer` protocol returns `str`; will break for binary/multi-file/streaming renderers. |
| T2  | 🔴       | ☎️     | Exit code taxonomy has no code for delivery failure, timeout, or feedback errors.        |
| L1  | 🔴       | 🦕     | Team capacity is unaddressed; scope is ambitious for an unknown team size.               |
| P2  | 🟡       | 🐼     | `SourceIndex` dict is expensive; consider a protocol with swappable implementations.     |
| P3  | 🟡       | 🐼     | `config` module's hexagonal status is ambiguous.                                         |
| P6  | 🟡       | 🐼     | `SpokenSpan.kind` and `SourceRange.kind` are `str`, not enums.                           |
| W2  | 🟡       | 🐈🧇   | The 80% simpler alternative is not discussed or rejected in the document.                |
| W4  | 🟡       | 🐈🧇   | Open decisions lack resolution deadlines.                                                |
| Z1  | 🟡       | 🐝     | No input size bounds or performance targets.                                             |
| Z3  | 🟡       | 🐝     | `SourceIndex` dict is memory-expensive for large documents.                              |
| D2  | 🟡       | 🐶     | `mdast` adapter has no version detection or compatibility probe.                         |
| D3  | 🟡       | 🐶     | Webhook failure should always preserve the local artefact unconditionally.               |
| L2  | 🟡       | 🦕     | Three parser implementations add cognitive load; consider two for v1.                    |
| L4  | 🟡       | 🦕     | Four-tool test strategy is comprehensive but maintenance-expensive.                      |
| T3  | 🟡       | ☎️     | JSONL serialisation contract is implied, not specified.                                  |
| T5  | 🟡       | ☎️     | `--deliver` scheme grammar mixes syntactic patterns.                                     |
| P1  | 🟢       | 🐼     | Hexagonal decomposition is well-drawn.                                                   |
| P4  | 🟢       | 🐼     | `TTSUnit` as stable contract is a good choice.                                           |
| W3  | 🟢       | 🐈🧇   | `darn-it` lineage is a genuine structural advantage.                                     |
| Z2  | 🟢       | 🐝     | Bounded successor search is the right cost control.                                      |
| T1  | 🟢       | ☎️     | `agent-context` command is a strong contract choice.                                     |
| T4  | 🟢       | ☎️     | Stable exit codes are valuable for agents.                                               |
| D1  | 🟢       | 🐶     | Fallback ladder is well-designed.                                                        |
| D4  | 🟢       | 🐶     | Failure mode table covers the right scenarios.                                           |
| L3  | 🟢       | 🦕     | Technology choices are mainstream.                                                       |
| L5  | 🟢       | 🦕     | Document is self-documenting.                                                            |
| W1  | 💡       | 🐈🧇   | No alternatives are documented.                                                          |
| Z4  | 💡       | 🐝     | No overall CLI wall-clock timeout.                                                       |
| D5  | 💡       | 🐶     | No guidance on observability or structured logging.                                      |

### Conditions for proceeding

1. **Address P5 (Renderer protocol).** Widen the return type to support
   `str | bytes` plus metadata before any adapter implements the protocol. This
   is cheaper to fix now than after two renderers exist.

2. **Address T2 (exit code taxonomy).** Add exit codes for delivery failure and
   feedback submission failure, or explicitly assign them to existing codes
   with documentation. Agents will branch on these codes; ambiguity here
   becomes a production bug.

3. **Address L1 (team capacity).** Add a brief statement of team context to the
   design or roadmap. If this is a solo project, consider cutting the v1 scope
   to Phases 1-3 (segmentation + CLI) and deferring renderers and semantic
   scoring. If it is a team project, the current scope is reasonable.

### Recommended next steps

1. Resolve the three 🔴 findings above. These are the conditions.
2. Add a "rejected alternatives" section to the design (W1, W2). Even two
   paragraphs explaining why greedy splitting was rejected strengthens the
   document.
3. Specify the JSONL serialisation contract explicitly (T3) before the first
   snapshot test locks it by accident.
4. Decide `SourceRange.kind` and `SpokenSpan.kind` typing (P6) before domain
   types are frozen.
5. Map open decisions (SS18) to roadmap tasks with resolution deadlines (W4).
6. Add input size expectations and memory budget guidance (Z1, Z3).
7. Clarify `config` module's architectural status (P3).

______________________________________________________________________

_Review conducted by the Logisphere crew. Findings are recommendations, not
mandates. The design authors know their domain better than we do; we know where
things tend to break._

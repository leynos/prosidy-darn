# Architectural decision record (ADR) 006: Test matrix phase scope

## Status

Accepted on 2026-05-09. The project keeps `pytest`, `pytest-bdd`, `syrupy`, and
Hypothesis in the planned test stack, but each phase must implement only the
dimensions that exist in that phase.

## Date

2026-05-09.

## Context and problem statement

The design review warned that the proposed test matrix is comprehensive but
maintenance-expensive. The technical design assigns clear roles to the four
test tools, but implementation needs a phase boundary so early work is not
blocked by renderer, delivery, or semantic-scoring dimensions that do not exist
yet.

## Decision drivers

- Preserve high confidence in source-slice integrity and CLI behaviour.
- Avoid combinatorial test growth before corresponding features exist.
- Keep snapshots deliberate and deterministic.
- Make regression coverage strong enough to protect punishment-profile tuning.

## Options considered

### Option A: Require the full matrix from Phase 1

This option maximizes confidence but forces renderer, delivery, profile, and
semantic-scoring scenarios before those features exist.

### Option B: Scope required dimensions by phase

This option keeps the four-tool strategy but expands the matrix only as the
corresponding product surface lands.

### Option C: Use `pytest` only until v1 is complete

This option minimizes early maintenance cost but delays behaviour, snapshot,
and property-test feedback until contracts may already be hard to change.

| Topic               | Option A | Option B | Option C |
| ------------------- | -------- | -------- | -------- |
| Early confidence    | High     | Medium   | Low      |
| Early maintenance   | High     | Medium   | Low      |
| Contract protection | Strong   | Strong   | Weak     |
| Implementation fit  | Poor     | Strong   | Medium   |

_Table 1: Test-matrix scope options._

## Decision outcome / proposed direction

Choose Option B.

The mandatory dimensions are:

- Phase 1: import-boundary checks, public import tests, developer-doc checks,
  and ADR link validation.
- Phase 2: domain unit tests, Hypothesis source-slice properties, parser
  compatibility tests, and JSONL serialization snapshots.
- Phase 3: `pytest-bdd` scenarios for `segment`, `explain`, profile
  precedence, JSON output, Rich output, and agent-context.
- Phase 4: renderer snapshots, renderer capability failures, delivery
  behaviours, and feedback persistence/submission paths.
- Phase 5+: semantic-scoring regression cases and synthesis-window behaviour.

Punishment-profile changes require a small approved regression corpus once the
default punishment rules exist. The corpus must cover single-narrator prose,
dialogue-heavy prose, Markdown-heavy prose, one pathological long paragraph,
and Unicode-heavy input.

## Goals and non-goals

- Goals:
  - keep the test stack aligned to delivered features;
  - prevent snapshot and BDD work from defining contracts accidentally;
  - make punishment tuning reviewable.
- Non-goals:
  - reduce the required test tools;
  - require renderer or delivery scenarios before those adapters exist;
  - prove subjective prosody or emotional inference quality.

## Known risks and limitations

- A phase-scoped matrix can still grow quickly if every profile is combined
  with every renderer and input mode.
- Snapshot fixtures need curation; otherwise syrupy churn will obscure real
  contract changes.
- The regression corpus protects known examples, not all prose styles.

## Architectural rationale

Phase-scoped testing matches the hexagonal architecture. Domain invariants are
tested before adapters exist, CLI behaviours are tested through inbound
adapters, and renderer/delivery contracts are added only when outbound adapters
are implemented.

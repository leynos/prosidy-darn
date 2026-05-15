# Prosidy Darn developers' guide

This guide is for maintainers implementing Prosidy Darn. The source of truth
for product and architecture decisions remains
[docs/prosidy-darn-technical-design.md](prosidy-darn-technical-design.md), and
the delivery order remains [docs/roadmap.md](roadmap.md).

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

## Local quality gates

Use Makefile targets rather than invoking tools directly:

- `make check-fmt`: check Python and Markdown-adjacent formatting.
- `make typecheck`: run the project type checker.
- `make lint`: run Python lint checks.
- `make test`: run `pytest` tests.
- `make markdownlint`: lint Markdown files.
- `make nixie`: validate Mermaid diagrams.

Run all relevant gates before committing. For code changes, run
`make check-fmt`, `make typecheck`, `make lint`, and `make test`. For Markdown
changes, also run `make markdownlint` and `make nixie`.

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

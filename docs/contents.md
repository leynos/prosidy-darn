# Documentation contents

- [Documentation contents](contents.md) - Start here to find the repository's
  documentation set and understand which document answers which question.

## Guides

- [Users' guide](users-guide.md) - Check implementation status and find the
  design documentation for planned workflows.
- [Developers' guide](developers-guide.md) - Work on the codebase, run quality
  gates, and understand maintainer-facing practices.
- [Repository layout](repository-layout.md) - Locate source code, tests,
  documentation, plans, configuration, and support files.
- [Documentation style guide](documentation-style-guide.md) - Apply the
  repository's writing, Markdown, diagram, and document-structure conventions.
- [Scripting standards](scripting-standards.md) - Follow the conventions for
  helper scripts, command execution, and script testing.

## Design and architecture

- [Prosidy Darn technical design](prosidy-darn-technical-design.md) - Understand
  the system architecture, parser boundary, scoring model, and extension points.
- [Prosidy Darn Logisphere design-stage review](prosidy-darn-logisphere-design-stage-review.md)
  - Review the
  pre-implementation architecture critique and risk analysis.
- [Complexity antipatterns and refactoring strategies](complexity-antipatterns-and-refactoring-strategies.md)
  - Identify
  code-health risks and apply the documented refactoring responses.

## Decision records

- [ADR 0001: Markdown parser boundary](adrs/adr-0001-markdown-parser-boundary.md)
  - Preserve the accepted parser boundary decision.
- [ADR 0002: Tokenizer and semantic scoring policy](adrs/adr-0002-tokenizer-and-semantic-scoring-policy.md)
  - Preserve the
  accepted tokenization and scoring decision.
- [ADR 0003: Profile rule expression policy](adrs/adr-0003-profile-rule-expression-policy.md)
  - Preserve the accepted profile
  rule expression decision.
- [ADR 0004: Import boundary fitness check](adrs/adr-0004-import-boundary-fitness-check.md)
  - Preserve the accepted import
  boundary enforcement decision.
- [ADR 0006: Test matrix phase scope](adrs/adr-0006-test-matrix-phase-scope.md)
  - Preserve the accepted phased test matrix decision.
- [ADR 0007: CLI observability scope](adrs/adr-0007-cli-observability-scope.md)
  - Preserve the accepted command-line observability decision.
- [ADR 0008: Linting architecture](adrs/adr-0008-two-tier-linting-architecture.md)
  - Preserve the accepted two-tier decision and its fourth Python quality-tier
  addendum.
- [ADR 0009: Skylos dead-code detection](adrs/adr-0009-skylos-dead-code-detection.md)
  - Preserve the accepted dead-code detection decision.

## Planning

- [Roadmap](roadmap.md) - Track phased delivery work, dependencies, and
  completion criteria.
- [Execution plans](execplans/) - Follow task-specific implementation plans:
  - [1.0.1 baseline developer docs and initial ADR files](execplans/1-0-1-baseline-developer-docs-and-initial-adr-files.md)
  - [1.1.1 Markdown parser boundary ADR](execplans/1-1-1-markdown-parser-boundary-adr.md)
  - [Resolve Prosidy Darn Logisphere design-stage review](execplans/resolve-prosidy-darn-logisphere-design-stage-review.md)
  - [1.2.4 Update maturin and PyO3 validation](execplans/test-maturin-pyo3-test-upgrade.md)

# Architectural decision record (ADR) 004: Import-boundary fitness check

## Status

Proposed. The decision is pending and is owned by roadmap task 1.2.3.

## Date

2026-05-10.

## Context and problem statement

The technical design requires `prosidy_darn.domain` and
`prosidy_darn.application` to stay independent of adapters, Cyclopts, parser
packages, filesystem delivery, HTTP clients, and vendor integrations. The
repository needs a local and continuous-integration (CI) fitness check before
non-trivial adapters land.

This ADR location exists before implementation so the enforcement decision has
a stable review path.

## Decision drivers

- Enforce the hexagonal dependency rule automatically.
- Produce actionable diagnostics for boundary violations.
- Keep the check lightweight enough for local gates.
- Avoid importing optional adapter dependencies merely to inspect imports.

## Options to be considered

- Use an import-linter style tool with configured contracts.
- Add a custom `pytest` test that parses imports from relevant packages.
- Use a static analysis rule from an existing linter if it can express the
  boundary clearly.

## Decision outcome / proposed direction

Pending. Roadmap task 1.2.3 must choose the import-boundary fitness check
before task 1.3.3 wires enforcement into the local gate.

## Consequences while pending

Developers must follow the dependency rule manually. Package skeleton work may
proceed only if it keeps domain and application modules free of adapter and
framework imports.

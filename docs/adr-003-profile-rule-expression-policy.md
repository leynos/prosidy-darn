# Architectural decision record (ADR) 003: Profile rule-expression policy

## Status

Proposed. The decision is pending and is owned by roadmap task 1.2.4.

## Date

2026-05-10.

## Context and problem statement

Profiles configure segmentation, duration, rendering, and command-line
defaults. The technical design needs a v1 policy for whether profile files can
define arbitrary custom rule expressions or only named rule weights.

This ADR location exists before implementation so profile parsing does not
accidentally create an expression-language contract.

## Decision drivers

- Keep profile files understandable for users and agents.
- Avoid executing arbitrary expressions from configuration.
- Keep default punishment tuning reviewable.
- Preserve a path for advanced rule customization if v1 needs it.

## Options to be considered

- Allow only named rule weights in v1 profiles.
- Allow a constrained expression language for custom rules.
- Defer custom rule expressions and expose only built-in profiles in v1.

## Decision outcome / proposed direction

Pending. Roadmap task 1.2.4 must decide the profile rule-expression policy
before Phase 2 starts.

## Consequences while pending

Implementation tasks may document planned profile names and defaults, but they
must not add arbitrary profile expression parsing until this ADR is accepted.

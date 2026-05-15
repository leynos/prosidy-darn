# Architectural decision record (ADR) 002: Tokenizer and semantic-scoring policy

## Status

Proposed. The decision is pending and is owned by roadmap task 1.1.2.

## Date

2026-05-10.

## Context and problem statement

Prosidy Darn needs deterministic core segmentation that works without optional
model dependencies. Later tasks also need a token-limit policy and an optional
semantic-scoring policy that can improve boundary choices without making the
core import path depend on tokenizer or embedding packages.

This ADR location exists before implementation so reviewers have a stable place
to resolve the policy before package and dependency work begins.

## Decision drivers

- Keep core segmentation usable offline.
- Keep optional tokenizer and embedding dependencies out of the domain import
  path.
- Preserve source-slice integrity when optional scores or token limits are
  enabled.
- Make missing optional dependencies produce explicit diagnostics.

## Options to be considered

- Choose one optional tokenizer adapter for v1 and keep semantic scoring
  disabled by default.
- Support multiple tokenizer adapters behind one `TokenCounter` port.
- Defer semantic scoring until after deterministic segmentation is complete.

## Decision outcome / proposed direction

Pending. Roadmap task 1.1.2 must decide the tokenizer and semantic-scoring
dependency policy before task 1.2.2 adds the v1 runtime and development
dependencies.

## Consequences while pending

Implementation tasks may refer to the `TokenCounter` and `SemanticScorer`
ports, but they must not add concrete tokenizer, embedding, or model-provider
dependencies until this ADR is accepted.

# Architectural decision record (ADR) 002: Tokenizer and semantic-scoring policy

## Status

Accepted on 2026-05-26. V1 names `tiktoken` as the first `TokenCounter`
candidate adapter behind the port, keeps `tokenizers`, `transformers`
`AutoTokenizer`, and `sentence-transformers` as eligible future adapters behind
the same ports, declares optional dependencies via PEP 621
`[project.optional-dependencies]`, and requires default-disabled adapters that
raise an explicit `ImportError` when their optional extra is missing.

## Date

2026-05-26.

## Context and problem statement

Prosidy Darn needs deterministic core segmentation that works without optional
model dependencies. Later tasks also need a token-limit policy and an optional
semantic-scoring policy that can improve boundary choices without making the
core import path depend on tokenizer or embedding packages.

The technical design names `TokenCounter` and `SemanticScorer` as driven ports
under `prosidy_darn.ports`, with concrete adapter implementations under
`prosidy_darn.adapters.outbound`. Section 18 records the open question of which
tokenizer should supply optional token limits, and section 9 already requires
that the core library not import optional heavy dependencies at module import
time.

This ADR fixes the policy that later optional-dependency and adapter work must
follow. It does not introduce adapter code, ports, or dependency entries in
`pyproject.toml`; those land in task 1.2.2 (runtime and development dependency
spine) and task 5.1.2 (first embedding-backed semantic scorer).

## Decision drivers

- Keep core segmentation usable offline.
- Keep optional tokenizer and embedding dependencies out of the domain import
  path.
- Preserve source-slice integrity when optional scores or token limits are
  enabled.
- Make missing optional dependencies produce explicit diagnostics that name
  the extra to install.
- Prefer a small, MIT-licensed, native tokenizer wheel that does not require
  runtime model-file distribution for the first v1 adapter.
- Keep semantic scoring strictly optional and deferred to Phase 5 so the v1
  deterministic loop does not depend on embedding stacks.

## Options considered

### Option A: Adopt `tiktoken` as the first `TokenCounter` candidate

`tiktoken` is OpenAI's MIT-licensed BPE tokenizer. It ships a small native
wheel for Python 3.9 and later, exposes `tiktoken.get_encoding(name)` and
`tiktoken.encoding_for_model(model)`, and bundles `cl100k_base` (GPT-4 and
GPT-3.5-turbo) and `o200k_base` (GPT-4o and GPT-4o-mini). It is the
conventional first choice for small Python command-line tools that need a
deterministic token count without distributing model files at runtime.

### Option B: Adopt Hugging Face `transformers` `AutoTokenizer`

`AutoTokenizer` cannot be installed without the full `transformers` library, as
documented by Hugging Face issue `huggingface/transformers#31043`. The
framework footprint is several hundred megabytes and pulls a deep dependency
tree. The breadth is unjustified for a token-count adapter and disqualifies
`transformers` as the first v1 candidate. It remains eligible as a future
adapter behind the same port.

### Option C: Adopt `tokenizers` (Hugging Face, Rust-backed)

`tokenizers` is a lighter Rust-backed BPE implementation via PyO3, but it
requires vocab and merges files at runtime, adding model-file distribution
surface that `tiktoken` does not have. It is a strong future option but is not
the first v1 candidate.

### Option D: Defer the token-counter decision and supply only a disabled adapter

Deferring leaves the open question in section 18 unresolved through Phase 1,
delays dependency selection in task 1.2.2, and blocks the renderer-side
token-limit work scheduled for Phase 4. A disabled-only stance also weakens the
dependency policy because there is no concrete adapter to validate it against.

| Topic                          | Option A (`tiktoken`) | Option B (`AutoTokenizer`) | Option C (`tokenizers`) | Option D (defer) |
| ------------------------------ | --------------------- | -------------------------- | ----------------------- | ---------------- |
| Wheel footprint                | Small native          | Multi-hundred MB framework | Small Rust extension    | None             |
| Runtime model-file requirement | None (bundled)        | Model files                | Vocab/merges files      | None             |
| Standalone installable         | Yes                   | No (HF #31043)             | Yes                     | N/A              |
| Licence                        | MIT                   | Apache 2.0                 | Apache 2.0              | N/A              |
| First v1 candidate             | Yes                   | No                         | No                      | No               |
| Future adapter behind the port | Yes                   | Yes                        | Yes                     | N/A              |

_Table 1: Token-counter adapter options for v1._

## Decision outcome / proposed direction

Choose Option A. The accepted policy is:

- `tiktoken` is the first v1 `TokenCounter` candidate behind the port;
- `tokenizers`, `transformers` `AutoTokenizer`, and `sentence-transformers`
  remain eligible future adapters behind the same ports and are not adopted in
  v1;
- optional dependencies are declared via PEP 621
  `[project.optional-dependencies]`, with suggested extra names `tokenizer`
  (for example, `tiktoken`) and `semantic` (for example,
  `sentence-transformers`); end users opt in with
  `pip install prosidy-darn[<extra>]`;
- default `TokenCounter` and `SemanticScorer` adapters are disabled and
  return a neutral or empty result;
- optional adapters use lazy imports inside the adapter implementation
  and raise an `ImportError` naming the extra to install when the dependency is
  missing;
- domain and application modules must not import any optional tokenizer
  or embedding package at module import time;
- the public segmentation API does not change with extras installed or
  omitted; only the diagnostic-bearing failure mode for missing optional
  dependencies differs.

PEP 735 `[dependency-groups]` is not used for these extras because it does not
install the package or its runtime dependencies and is therefore unsuited to
user-facing optional adapter dependencies; it remains available for
development-only groups.

Concrete dependency entries do not land in `pyproject.toml` as part of this
ADR. Task 1.2.2 owns the actual extras declaration once the package skeleton
lands, and task 5.1.2 owns the first embedding-backed `SemanticScorer` adapter.

## Goals and non-goals

- Goals:
  - settle the open tokenizer question from technical design section 18;
  - fix a single optional-extras mechanism (PEP 621) before
    `pyproject.toml` grows extras entries;
  - keep `TokenCounter` and `SemanticScorer` adapters disabled by default
    and behind explicit options;
  - guarantee that missing optional dependencies produce an actionable
    diagnostic naming the extra to install.
- Non-goals:
  - implement the `TokenCounter` or `SemanticScorer` ports;
  - add `tiktoken`, `tokenizers`, `transformers`, `sentence-transformers`,
    `torch`, or any HTTP client to `pyproject.toml`;
  - prescribe the exact `ImportError` message text;
  - select a permanent or only tokenizer for the lifetime of the project.

## Migration plan

1. Land this ADR with documentation-contract tests that lock the accepted
   policy in place.
2. In task 1.2.2, add `[project.optional-dependencies]` to `pyproject.toml`
   with `tokenizer` (containing `tiktoken`) and reserve a `semantic` extra for
   the Phase 5 embedding adapter. Keep both extras out of the default install
   set.
3. In a later Phase 1 or Phase 2 adapter task, implement the disabled
   default `TokenCounter` adapter and the lazy-importing `tiktoken` adapter
   under `prosidy_darn.adapters.outbound.tokenizer`.
4. In task 5.1.1, implement the disabled default `SemanticScorer` adapter
   under `prosidy_darn.adapters.outbound.semantic`.
5. In task 5.1.2, implement the first embedding-backed semantic scorer
   adapter (for example, `sentence-transformers`) behind the `semantic` extra.
   Future tokenizer adapters (such as `tokenizers` or `transformers`
   `AutoTokenizer`) may be added behind the same port without a new ADR,
   provided they preserve the diagnostic and import contract recorded here.

## Known risks and limitations

- `tiktoken` is OpenAI-specific in heritage. The policy treats it as the
  first v1 candidate, not a permanent or sole candidate; alternative adapters
  can be added behind the same port without a new ADR.
- Lazy imports inside adapter methods can hide import-time errors from
  static analysis. Mitigation: each optional adapter must raise an
  `ImportError` whose message names the extra to install, and the diagnostic
  must surface through the same channel used for CLI failures.
- PEP 621 extras are public package metadata. Removing or renaming an
  extra is a breaking change for users; later ADRs must record any such change.
- PEP 810 (explicit lazy imports) is not yet usable; the implementation
  must rely on conventional function-scoped imports until that PEP is available.

## Architectural rationale

The decision keeps the domain dependent on the `TokenCounter` and
`SemanticScorer` ports, never on a vendor or framework type. Optional tokenizer
and embedding packages are outbound adapter details that load only when their
adapter is selected. PEP 621 extras give end users a standard installation
surface for those optional adapters, and the default-disabled adapters
guarantee that omitting any extra leaves the public segmentation API unchanged.
The policy mirrors the parser-boundary precedent set by ADR-001: pick one
concrete first candidate, keep the port open for future alternatives, and fail
closed with an explicit diagnostic when an optional capability is requested but
unavailable.

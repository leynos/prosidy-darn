# Architectural decision record (ADR) 001: Markdown parser boundary

## Status

Accepted on 2026-05-09. V1 ships one Markdown-aware parser adapter plus a
plain-text fallback. The initial Markdown-aware adapter is `mdast` when its
version and compatibility probe pass. A local PyO3 `markdown-rs` range
extractor is a contingency, not a concurrent v1 adapter.

## Date

2026-05-09.

## Context and problem statement

Prosidy Darn needs byte-accurate Markdown source ranges so segmentation can
preserve headings, paragraphs, lists, code blocks, inline emphasis, and other
source structures without rewriting the input. The technical design originally
allowed three parser implementations in v1: `mdast`, a PyO3 wrapper around
`markdown-rs`, and a plain-text fallback.

That breadth protects correctness, but it also increases contributor load
before the first segmentation implementation exists. Contributors would need to
understand Python packaging, Rust bindings, source-position compatibility,
plain-text degradation, and parser selection all at once.

## Decision drivers

- Keep source-slice integrity as a non-negotiable correctness property.
- Reduce v1 parser implementation count where doing so does not weaken the
  public contract.
- Preserve a clear path to PyO3 if `mdast` cannot expose stable source ranges.
- Keep parser selection outside the domain layer.
- Make parser capability failures explicit rather than silently degrading
  Markdown-aware protection.

## Options considered

### Option A: Ship `mdast`, PyO3, and plain text in v1

This option gives the broadest fallback chain from the start. It also requires
two Markdown-aware adapters, two source-position compatibility surfaces, and
more packaging work before the first useful segmentation path exists.

### Option B: Ship one Markdown-aware parser plus plain text in v1

This option selects `mdast` as the initial Markdown-aware parser only when a
version check and runtime probe prove that its source ranges are byte-accurate.
Plain text remains available for non-Markdown input or explicit degraded mode.
PyO3 remains available as a contingency if the Phase 1 spike rejects `mdast`.

### Option C: Ship plain text only in v1

This option minimizes implementation work but gives up Markdown-aware
protection for headings, lists, code blocks, and inline structures. That would
undercut the `darn-it` lineage and make v1 less representative of the intended
product.

| Topic               | Option A         | Option B                   | Option C |
| ------------------- | ---------------- | -------------------------- | -------- |
| Source protection   | Strongest        | Strong if probe passes     | Weak     |
| Contributor load    | Highest          | Moderate                   | Lowest   |
| Packaging risk      | Highest          | Moderate                   | Lowest   |
| V1 product fidelity | Strong           | Strong                     | Weak     |
| Contingency path    | Already included | Explicit PyO3 substitution | Deferred |

_Table 1: Parser-boundary options._

## Decision outcome / proposed direction

Choose Option B.

V1 implements exactly one Markdown-aware parser adapter plus one plain-text
fallback. The initial parser is `mdast` when it satisfies both checks:

- supported package-version range;
- runtime compatibility probe over known Markdown fixtures with byte offsets
  that slice back to expected source substrings.

If `mdast` fails those checks during the Phase 1 parser spike, the project may
activate the PyO3 contingency and use a compact `markdown-rs` range extractor
instead. The project should not ship both `mdast` and PyO3 Markdown adapters in
v1 unless a later ADR accepts the maintenance cost.

## Goals and non-goals

- Goals:
  - keep Markdown-aware segmentation in v1;
  - keep parser failure behaviour explicit and testable;
  - reduce v1 parser implementation count.
- Non-goals:
  - support every Markdown extension through multiple parser backends;
  - optimize parser throughput before source-position correctness is proven;
  - build a general Rust extension layer before the parser spike requires it.

## Migration plan

1. Add the `mdast` compatibility probe and version check in the parser adapter
   task.
2. Implement the plain-text fallback for non-Markdown or explicitly degraded
   input.
3. If the probe fails, replace the selected Markdown-aware parser with the PyO3
   contingency before Phase 2 parser work proceeds.
4. Record any later decision to ship both Markdown-aware adapters in a new ADR.

## Known risks and limitations

- If `mdast` passes the initial probe but later changes its position format, the
  runtime probe must fail closed before segmentation.
- If PyO3 becomes necessary, the Rust packaging work moves back into v1.
- Plain-text fallback cannot provide Markdown-aware structural protection and
  must report degradation when used for Markdown input.

## Architectural rationale

The decision keeps the domain dependent on a `StructureParser` port rather than
any parser package. Parser choice remains an outbound adapter concern, while
the domain continues to consume source ranges and `SourceIndex` operations.

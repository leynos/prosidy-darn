# Architectural decision record (ADR) 007: CLI observability scope

## Status

Accepted on 2026-05-09. V1 does not add a separate structured logging
subsystem. It relies on stable exit codes, JSON error bodies, `explain`
diagnostics, and feedback capture. A logging port is deferred until networked
or long-running adapters create a concrete need.

## Date

2026-05-09.

## Context and problem statement

The design review noted that webhook delivery, optional semantic scoring, and
feedback posting may benefit from structured logging. Prosidy Darn is currently
a local CLI and Python library design. Adding logging before implementation
would introduce another cross-cutting contract before the first parser,
segmenter, or renderer exists.

## Decision drivers

- Keep v1 implementation focused on cue segmentation and agent-native CLI
  contracts.
- Preserve machine-readable diagnostics for agents.
- Avoid logging sensitive source text, rendered speech payloads, webhook URLs,
  or feedback secrets.
- Leave room for a future observability port if adapters need it.

## Options considered

### Option A: Add structured logging in v1

This option gives operators richer diagnostics immediately, but it adds
configuration, redaction, test, and documentation surfaces before the CLI has
network-heavy workflows.

### Option B: Use CLI contracts and `explain` diagnostics in v1

This option relies on stable exit codes, JSON error output, bounded diagnostic
data, and the `explain` command. It keeps a logging port out of v1.

### Option C: No observability contract

This option leaves failures to human stderr text and ad-hoc debugging, which is
not sufficient for agent-native CLI use.

| Topic                | Option A | Option B | Option C |
| -------------------- | -------- | -------- | -------- |
| Agent usability      | Strong   | Strong   | Weak     |
| Implementation cost  | High     | Low      | Low      |
| Sensitive-data risk  | Medium   | Low      | Medium   |
| Future extensibility | Strong   | Medium   | Weak     |

_Table 1: Observability scope options._

## Decision outcome / proposed direction

Choose Option B.

V1 observability consists of:

- stable exit codes;
- JSON error bodies for `--json` workflows;
- human-readable stderr diagnostics;
- bounded `explain` output for segmentation decisions;
- local feedback JSONL after minimization and redaction;
- `agent-context` reporting whether upstream feedback is configured.

Do not add a logging subsystem or logging port in v1. Reconsider this decision
when any of these conditions becomes true:

- semantic scoring performs network calls;
- webhook or feedback delivery needs retry history beyond the immediate error;
- batch processing needs per-document progress or audit records;
- users need machine-readable trace events that are not covered by `explain`.

## Goals and non-goals

- Goals:
  - keep diagnostics parseable for agents;
  - avoid leaking source text or credentials through logs;
  - defer infrastructure until it has a concrete consumer.
- Non-goals:
  - provide centralized logging, metrics, or tracing in v1;
  - expose OpenTelemetry or similar integrations;
  - log raw source text, rendered payloads, environment dumps, or webhook URLs.

## Known risks and limitations

- Debugging delivery failures may require rerunning commands with `--json` or
  using feedback entries rather than inspecting logs.
- Batch users may need structured progress later.
- A future logging port must reuse the feedback sanitizer rules and should
  default to source-text minimization.

## Architectural rationale

The decision keeps observability at the CLI/application boundary for v1. It
does not leak logging infrastructure into the domain and preserves a clean path
to add an outbound observability port later if real adapter behaviour demands
it.

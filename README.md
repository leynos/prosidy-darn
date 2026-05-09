# Prosidy Darn

*Prepare Markdown and narrative prose for directable text-to-speech cues.*

Prosidy Darn is a design-first Python package for splitting source text into
literal, source-stable TTS units. The project is currently a scaffold with its
technical design and roadmap in place; the segmentation engine and CLI are
planned in the roadmap.

______________________________________________________________________

## Why prosidy-darn?

- **Literal source slices**: cue units keep exact source offsets, so downstream
  tools can trace every spoken span back to the original text.
- **Performance-aware chunking**: the design adapts `darn-it` style punishment
  optimization for TTS direction, dialogue, duration, and renderer limits.
- **Python library and CLI**: the same segmentation engine is intended to serve
  Python callers and an agent-native Cyclopts CLI.
- **Renderer-neutral cue sheets**: JSONL cue units remain the source of truth,
  while SSML and vendor payloads become render targets.

______________________________________________________________________

## Quick start

### Installation

```bash
uv sync --group dev
```

### Basic usage

The current package scaffold exposes a small import smoke test:

```bash
uv run python - <<'PY'
from prosidy_darn import hello

print(hello())
PY
```

Expected output:

```plaintext
hello from Python
```

______________________________________________________________________

## Features

Planned v1 capabilities include:

- Unicode-safe source indexing with both character and byte offsets.
- Markdown structural ranges from `mdast` or a small `markdown-rs` adapter.
- TTS-specific ranges for sentences, clauses, dialogue turns, attribution, and
  performance beats.
- Global dynamic-programming segmentation over boundary and unit punishment.
- Cyclopts CLI commands for `segment`, `explain`, `render`, profiles,
  `agent-context`, and feedback.
- Rich human output with clean ASCII machine output for agents and pipelines.
- JSONL cue sheets and SSML rendering.

______________________________________________________________________

## Learn more

- [Prosidy Darn users' guide](docs/users-guide.md) — installation, current
  smoke test, and planned library and CLI usage
- [Technical design](docs/prosidy-darn-technical-design.md) — architecture,
  algorithm, CLI, and verification design
- [Roadmap](docs/roadmap.md) — planned delivery phases and task breakdown
- [Agent instructions](AGENTS.md) — contribution and repository workflow
  guidance

______________________________________________________________________

## Licence

ISC — see [LICENSE](LICENSE) for details.

______________________________________________________________________

## Contributing

Contributions are welcome. Please read [AGENTS.md](AGENTS.md) before making
changes; it defines the local workflow, quality gates, and documentation
standards for this repository.

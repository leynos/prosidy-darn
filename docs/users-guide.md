# Prosidy Darn users' guide

Prosidy Darn prepares Markdown and narrative prose for directable
text-to-speech (TTS) workflows. Its v1 design keeps the original source text
immutable, emits literal source spans for each cue unit, and attaches metadata
that can drive SSML, vendor payloads, cue review tools, or manual direction.

The current repository is still in the design and scaffold stage. The only
implemented import is the package smoke-test function, but the examples below
show the intended v1 library and CLI contract so early users and implementers
can align on the same shape.

## Install for local development

```bash
uv sync --group dev
```

Run the current package smoke test:

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

## Library usage

The planned public library API centres on `segment_markdown` and
`segment_text`. Both functions accept source text and a named TTS profile, then
return non-overlapping cue units whose `source_text` is always equal to
`original_text[source_start:source_end]`.

```python
from prosidy_darn import segment_markdown

source = """# Chapter one

"Don't open it," Mara said.
"""

units = segment_markdown(
    source,
    profile="audiobook_single_narrator",
    target_seconds=(4.0, 12.0),
    hard_max_seconds=28.0,
)

for unit in units:
    print(unit.id, unit.source_start, unit.source_end, unit.kind)
    assert unit.source_text == source[unit.source_start : unit.source_end]
```

Expected output shape:

```plaintext
u-0001 0 14 heading
u-0002 16 45 dialogue_with_attribution
```

The exact boundaries depend on the final segmentation profile and Markdown
parser adapter, but the source-slice invariant is mandatory.

### Common inputs

- `text`: the original Unicode source string. The library MUST NOT require ASCII
  input.
- `profile`: one of `audiobook_single_narrator`, `dramatized_multivoice`, or
  `low_latency_streaming`.
- `target_seconds`: the preferred spoken-duration range for one cue unit.
- `hard_max_seconds`: the maximum estimated duration for a cue unit.
- `max_engine_chars`: an optional renderer limit used to reject overlarge units.

### Common outputs

Each returned cue unit is expected to expose:

- `id`: a stable cue identifier for the segmentation run.
- `source_start` and `source_end`: source offsets for provenance.
- `source_text`: the exact original substring.
- `spoken_text`: renderer-facing text with Markdown syntax removed where
  appropriate.
- `kind`: a classifier such as `narration`, `dialogue`, `attribution`,
  `heading`, or `dialogue_with_attribution`.
- `speaker`: the inferred or configured speaker, when known.
- `direction`: performance metadata such as pace, energy, pause hints, and
  renderer constraints.
- `diagnostics`: warnings about fallback boundaries, parser limitations, or
  renderer compromises.

## CLI usage

The planned CLI is non-interactive by default and uses Cyclopts for command
specification and tiered configuration. Human output may use Rich when stdout
is a terminal. Machine output, including JSON, JSONL, and `agent-context`,
remains plain ASCII except for source text supplied by the user.

### Segment a Markdown file

```bash
prosidy-darn segment \
  --input story.md \
  --profile audiobook_single_narrator \
  --json
```

Sample JSON output:

```json
{
  "units": [
    {
      "id": "u-0001",
      "source_start": 0,
      "source_end": 45,
      "kind": "dialogue_with_attribution",
      "speaker": "Mara"
    }
  ],
  "truncated": false
}
```

### Explain boundary choices

```bash
prosidy-darn explain \
  --input story.md \
  --profile audiobook_single_narrator \
  --json \
  --limit 20
```

Sample output:

```json
{
  "boundaries": [
    {
      "offset": 45,
      "accepted": true,
      "total_cost": -520,
      "reasons": ["dialogue_turn_boundary", "after_sentence_end"]
    }
  ],
  "truncated": false
}
```

### Render cue units

```bash
prosidy-darn render \
  --input cues.jsonl \
  --format ssml \
  --deliver file \
  --deliver-to ./out.ssml \
  --json
```

Sample output:

```json
{
  "delivered_to": "file:./out.ssml",
  "format": "ssml"
}
```

### Discover the command contract

```bash
prosidy-darn agent-context
```

The command returns versioned JSON describing commands, flags, profiles, exit
codes, delivery schemes, and whether an upstream feedback endpoint is
configured.

### Useful flags

- `--profile <name>`: selects a segmentation and rendering profile.
- `--json`: emits structured output to stdout.
- `--limit <n>`: bounds list and explanation output.
- `--dry-run`: previews consequential operations where supported.
- `--deliver stdout|file|webhook`: selects the render artefact destination.
- `--deliver-to <path-or-url>`: supplies the file path or webhook URL when
  `--deliver` is `file` or `webhook`.
- `--force`: bypasses a destructive confirmation only where a command is
  explicitly destructive.

## End-to-end example

Given `story.md`:

```markdown
# The Door

"Don't open it," Mara said.
```

Create newline-delimited JSON cue units, inspect the boundary explanation, and
render SSML:

```bash
prosidy-darn segment \
  --input story.md \
  --profile audiobook_single_narrator \
  --json > cues.jsonl

prosidy-darn explain \
  --input story.md \
  --profile audiobook_single_narrator \
  --json \
  --limit 20

prosidy-darn render \
  --input cues.jsonl \
  --format ssml \
  --deliver file \
  --deliver-to ./story.ssml \
  --json
```

Expected result:

- `cues.jsonl` contains newline-delimited cue records that preserve source
  offsets into `story.md`;
- the explanation shows why the dialogue and attribution stay together for the
  single-narrator profile;
- `story.ssml` contains renderer-ready speech markup without replacing the cue
  JSON as the source of truth.

## Troubleshooting and FAQ

### Why does the current package only print `hello from Python`?

The repository is still at the documentation and scaffold stage. The technical
design and roadmap define the intended v1 behaviour before implementation
begins.

### Which profile should examples use?

Use `audiobook_single_narrator` for ordinary audiobook-style narration,
`dramatized_multivoice` for multi-voice rendering experiments, and
`low_latency_streaming` for short synthesis windows.

### Why did the CLI reject `--deliver webhook --deliver-to http://...`?

Webhook delivery targets are HTTPS-only by design. Plain HTTP URLs supplied to
`--deliver-to` must be rejected before any POST is attempted.

### Why are source offsets present in every cue?

Offsets are the provenance contract. They let review tools, renderers, and
manual direction UIs trace every cue back to the original source without
relying on rewritten text.

### Why not edit SSML directly?

SSML is a render target, not the source of truth. Prosidy Darn keeps a
renderer-neutral cue representation, so different engines can be supported
without losing source provenance or direction metadata.

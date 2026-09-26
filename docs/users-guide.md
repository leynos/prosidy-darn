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

Run the current package smoke test. The Rust extension is preferred when it is
available; otherwise the package falls back to the pure-Python implementation:

```bash
uv run python - <<'PY'
from prosidy_darn import hello

print(hello())
PY
```

Expected output when the Rust extension is available:

```plaintext
hello from Rust
```

Expected output when the Rust extension is unavailable:

```plaintext
hello from Python
```

Run the local lint gate with:

```bash
make lint
```

The lint gate runs Ruff first, then runs a focused Pylint pass through the
[`pylint-pypy-shim`](https://github.com/leynos/pylint-pypy-shim) wrapper under
PyPy. The Pylint tier is intentionally allow-listed so it complements Ruff
without replacing Ruff's broader rule set.

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

### JSONL cue output format

The `segment` command and the JSONL renderer both emit newline-delimited JSON
cue sheets. Each line is one complete JSON object describing a single
`TTSUnit`, and the file carries no wrapping array. The example below is
pretty-printed for readability; on disk each record occupies exactly one line.

```json
{
  "id": "u-0002",
  "source_start": 16,
  "source_end": 45,
  "source_text": "\"Don't open it,\" Mara said.",
  "spoken_text": "Don't open it, Mara said.",
  "spoken_spans": [
    {
      "source_start": 16,
      "source_end": 32,
      "spoken_start": 0,
      "spoken_end": 14,
      "kind": "spoken_dialogue",
      "voice": "Mara",
      "attributes": {}
    },
    {
      "source_start": 33,
      "source_end": 45,
      "spoken_start": 15,
      "spoken_end": 25,
      "kind": "attribution",
      "voice": null,
      "attributes": {}
    }
  ],
  "kind": "dialogue_with_attribution",
  "speaker": "Mara",
  "direction": {
    "intent": "warn",
    "pace": "measured",
    "energy": "low",
    "pitch": null,
    "volume": null,
    "tension": 0.4,
    "pause_before_ms": 0,
    "pause_after_ms": 250,
    "emphasis": ["open"]
  },
  "diagnostics": []
}
```

The cue-sheet contract guarantees a stable shape:

- **UTF-8 encoding**: cue sheets are always UTF-8 text.
- **No wrapping array**: each line is one JSON object, with no surrounding
  array, no blank lines, and a trailing newline at the end of the file.
- **Stable optional fields serialize as `null`**: optional fields such as
  `speaker`, `direction.pitch`, and a span's `voice` are emitted as `null`
  rather than omitted, so downstream tools always see the same keys.
- **`source_text` invariant**: `source_text` always equals the original
  `source_text[source_start:source_end]` slice, so every cue traces back to a
  literal source span.

Numeric offsets are source-coordinate character integers unless a field name
ends in `_byte`.

### Consuming JSONL programmatically

A cue sheet can be read line by line with the standard library `json` module:

```python
import json

with open("cues.jsonl", encoding="utf-8") as handle:
    for line in handle:
        cue = json.loads(line)
        print(cue["id"], cue["kind"], cue["spoken_text"])
```

Shell pipelines can extract individual fields with `jq`:

```bash
# Print the spoken text of every cue.
jq -r '.spoken_text' cues.jsonl

# Print the speaker of each dialogue-with-attribution cue.
jq -r 'select(.kind == "dialogue_with_attribution") | .speaker' cues.jsonl
```

## Configuration

Prosidy Darn reads layered configuration so that project defaults, named
profiles, and per-invocation overrides compose predictably. Library callers
pass options directly and bypass this machinery; the layers below apply to the
CLI.

### Configuration file

A project may define settings in a `prosidy-darn.toml` file under the
`[tool.prosidy-darn]` key. The CLI searches the working directory and its
parents for this file:

```toml
[tool.prosidy-darn]
profile = "audiobook_single_narrator"
timeout_seconds = 30
```

Named profiles live in an XDG profile store at
`${XDG_CONFIG_HOME:-~/.config}/prosidy-darn/profiles.toml`. The CLI also
exposes available profile names through `agent-context`, so agents can discover
configuration without reading local files.

### Precedence

Settings resolve in the following order, with earlier sources overriding later
ones:

1. explicit CLI flag,
2. `PROSIDY_DARN_*` environment variable,
3. project TOML under `[tool.prosidy-darn]`,
4. named profile from the XDG profile store,
5. Python default.

### Environment variables

Every CLI flag has a matching `PROSIDY_DARN_*` environment variable formed from
the `PROSIDY_DARN_` prefix and the upper-case flag name. The variables that
operators most often set are:

| Variable                         | Purpose                                              |
| -------------------------------- | ---------------------------------------------------- |
| `PROSIDY_DARN_TIMEOUT_SECONDS`   | Whole-operation timeout in seconds; expiry exits 10. |
| `PROSIDY_DARN_FEEDBACK_ENDPOINT` | HTTPS-only upstream endpoint for minimized feedback. |

_Table 1: Frequently used environment variables._

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
  "delivery_scheme": "file",
  "deliver_to": "./out.ssml",
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

### Profile management

The `profile` command group inspects and edits named profiles in the XDG
profile store:

- `profile list`: list available profile names.
- `profile get <name>`: print a single profile's settings.
- `profile save <name>`: create or update a named profile.
- `profile delete <name>`: remove a named profile.

Destructive operations require `--force`. Deleting a profile, and overwriting
an existing profile with `profile save`, both refuse to proceed unless
`--force` is supplied.

Three profiles are built in:

| Profile                     | ideal_seconds | hard_max_seconds | words_per_second |
| --------------------------- | ------------- | ---------------- | ---------------- |
| `audiobook_single_narrator` | 4.0-12.0      | 28.0             | 2.6              |
| `dramatized_multivoice`     | 3.0-10.0      | 20.0             | 2.9              |
| `low_latency_streaming`     | 2.0-6.0       | 10.0             | 2.8              |

_Table 2: Built-in profile duration and pacing parameters._

Custom profile rule expressions are not yet supported in v1. Profiles select
named rule weights only; arbitrary custom expressions remain pending ADR-003.

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

### Delivery

Commands that produce an artefact accept `--deliver` to choose where the
artefact goes. Three delivery targets are supported:

- `stdout`: write the artefact to standard output.
- `file`: write the artefact atomically to a path given by `--deliver-to`.
- `webhook`: POST the artefact to an HTTPS URL given by `--deliver-to`.

```plaintext
--deliver stdout
--deliver file --deliver-to ./story.ssml
--deliver webhook --deliver-to https://example.test/hook
```

`--deliver-to` is required when `--deliver` is `file` or `webhook`, and must be
absent for `stdout`. Colon-packed syntax such as `file:./story.ssml` is not
accepted; the target and its destination are always separate arguments. Webhook
URLs must use HTTPS; plain HTTP URLs are rejected before any request is made.

### Exit codes

The CLI uses a stable exit-code taxonomy:

| Code | Meaning                                    |
| ---: | ------------------------------------------ |
| 0    | Success.                                   |
| 1    | Unexpected internal error.                 |
| 2    | Invalid invocation or malformed flags.     |
| 3    | Input file or output path error.           |
| 4    | Input parsing failed.                      |
| 5    | No valid segmentation path exists.         |
| 6    | Rendering failed.                          |
| 7    | Configuration or profile error.            |
| 8    | Delivery failed after rendering.           |
| 9    | Feedback persistence or submission failed. |
| 10   | Operation timed out.                       |

_Table 3: CLI exit-code taxonomy._

Exit code 10 indicates that a whole-operation timeout, configured with
`--timeout-seconds` or `PROSIDY_DARN_TIMEOUT_SECONDS`, expired before the
command finished.

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

### Low-latency streaming example

The `low_latency_streaming` profile favours short cue units for incremental
synthesis. Segment the same source with that profile:

```bash
prosidy-darn segment \
  --input story.md \
  --profile low_latency_streaming \
  --json > cues.jsonl
```

Compared with `audiobook_single_narrator`, this profile produces:

- shorter units, because it prefers short spans;
- a narrower duration window, with an ideal range of 2.0-6.0 seconds and a hard
  maximum of 10.0 seconds rather than the audiobook 4.0-12.0 and 28.0 second
  envelope;
- no semantic-break scoring, because semantic breaks are disabled for this
  profile.

Reach for `low_latency_streaming` when responsiveness matters, such as
streaming synthesis where speech must begin before the whole document is
processed. Prefer `audiobook_single_narrator` when longer, evenly paced units
and semantic-break awareness produce a smoother listening experience.

## Troubleshooting and FAQ

### Why does the current package print `hello from Rust`?

The package includes a small optional Rust extension built with maturin and
PyO3. The current function is still only a smoke test; the extension exists so
maintainers can validate native wheel builds before later parser and runtime
work depends on them. If the extension is absent, the package falls back to the
pure-Python smoke-test implementation.

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

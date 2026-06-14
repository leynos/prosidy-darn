"""Tests for maintainer-facing documentation contracts."""

from __future__ import annotations

import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DEVELOPERS_GUIDE = DOCS_DIR / "developers-guide.md"
MARKDOWN_PARSER_ADR = DOCS_DIR / "adr-001-markdown-parser-boundary.md"
TOKENIZER_POLICY_ADR = DOCS_DIR / "adr-002-tokenizer-and-semantic-scoring-policy.md"
IMPORT_BOUNDARY_ADR = DOCS_DIR / "adr-004-import-boundary-fitness-check.md"
ROADMAP = DOCS_DIR / "roadmap.md"

INITIAL_ADR_PATHS = (
    "docs/adr-001-markdown-parser-boundary.md",
    "docs/adr-002-tokenizer-and-semantic-scoring-policy.md",
    "docs/adr-003-profile-rule-expression-policy.md",
    "docs/adr-004-import-boundary-fitness-check.md",
)

PHASE_ONE_QUALITY_GATES = (
    "make check-fmt",
    "make typecheck",
    "make lint",
    "make test",
    "make markdownlint",
    "make nixie",
)


def read_document(path: pathlib.Path) -> str:
    """Read a Markdown document using the repository's documentation encoding."""
    return path.read_text(encoding="utf-8")


def normalise_whitespace(text: str) -> str:
    """Collapse Markdown wrapping so contract checks ignore line reflow."""
    return re.sub(r"\s+", " ", text).strip()


def test_developers_guide_exists() -> None:
    """Provide a stable maintainer-facing guide for Phase 1 contributors."""
    assert DEVELOPERS_GUIDE.is_file(), f"missing developer guide: {DEVELOPERS_GUIDE}"


def test_initial_adr_locations_exist() -> None:
    """Keep Phase 1 ADR review locations stable before decision work starts."""
    missing_paths = [
        adr_path
        for adr_path in INITIAL_ADR_PATHS
        if not (REPO_ROOT / adr_path).is_file()
    ]

    assert missing_paths == [], f"missing ADR files: {missing_paths}"


def test_initial_adrs_are_discoverable_from_developers_guide() -> None:
    """Link blocking Phase 1 ADRs from the maintainer-facing guide."""
    developers_guide = read_document(DEVELOPERS_GUIDE)

    missing_links = [
        adr_path for adr_path in INITIAL_ADR_PATHS if adr_path not in developers_guide
    ]

    assert missing_links == [], (
        f"missing ADR links in {DEVELOPERS_GUIDE}: {missing_links}"
    )


def test_initial_adrs_are_discoverable_from_roadmap() -> None:
    """Keep the roadmap and developer guide aligned on blocking ADR paths."""
    roadmap = read_document(ROADMAP)
    missing_links = [
        adr_path for adr_path in INITIAL_ADR_PATHS if adr_path not in roadmap
    ]

    assert missing_links == [], f"missing ADR links in {ROADMAP}: {missing_links}"


def test_phase_one_quality_gates_are_documented() -> None:
    """Document the commands contributors must run for Phase 1 work."""
    developers_guide = read_document(DEVELOPERS_GUIDE)
    missing_gates = [
        gate for gate in PHASE_ONE_QUALITY_GATES if gate not in developers_guide
    ]

    assert missing_gates == [], f"missing documented quality gates: {missing_gates}"


def test_markdown_parser_boundary_adr_is_accepted() -> None:
    """Ensure roadmap item 1.1.1 has a settled parser-boundary decision."""
    markdown_parser_adr = read_document(MARKDOWN_PARSER_ADR)

    assert "## Status" in markdown_parser_adr
    assert "Accepted on" in markdown_parser_adr


def test_markdown_parser_boundary_adr_defines_v1_adapter_order() -> None:
    """Keep the selected Markdown parser order explicit before adapter work."""
    markdown_parser_adr = normalise_whitespace(read_document(MARKDOWN_PARSER_ADR))
    required_phrases = (
        "V1 ships one Markdown-aware parser adapter plus a plain-text fallback",
        (
            "The initial Markdown-aware adapter is `mdast` when its version and "
            "compatibility probe pass"
        ),
        (
            "PyO3 `markdown-rs` range extractor is a contingency, not a "
            "concurrent v1 adapter"
        ),
        "must report degradation when used for Markdown input",
    )

    missing_phrases = [
        phrase
        for phrase in required_phrases
        if normalise_whitespace(phrase) not in markdown_parser_adr
    ]

    assert missing_phrases == [], (
        f"missing parser-boundary commitments in {MARKDOWN_PARSER_ADR}: "
        f"{missing_phrases}"
    )


def test_markdown_parser_boundary_roadmap_item_is_closed() -> None:
    """Mark roadmap item 1.1.1 done only once ADR-001 is accepted."""
    roadmap = read_document(ROADMAP)
    markdown_parser_adr = read_document(MARKDOWN_PARSER_ADR)

    assert "Accepted on" in markdown_parser_adr
    assert "- [x] 1.1.1. Record the Markdown parser boundary as an ADR." in roadmap


def test_tokenizer_policy_adr_is_accepted() -> None:
    """Ensure roadmap item 1.1.2 has a settled tokenizer-and-scoring decision."""
    tokenizer_policy_adr = read_document(TOKENIZER_POLICY_ADR)

    assert "## Status" in tokenizer_policy_adr
    assert "Accepted on" in tokenizer_policy_adr


def test_tokenizer_policy_adr_defines_v1_adapter_policy() -> None:
    """Lock the accepted ADR-002 policy before downstream adapter work."""
    tokenizer_policy_adr = normalise_whitespace(read_document(TOKENIZER_POLICY_ADR))
    required_phrases = (
        "`tiktoken` is the first v1 `TokenCounter` candidate behind the port",
        (
            "`tokenizers`, `transformers` `AutoTokenizer`, and "
            "`sentence-transformers` remain eligible future adapters behind "
            "the same ports and are not adopted in v1"
        ),
        (
            "optional dependencies are declared via PEP 621 "
            "`[project.optional-dependencies]`"
        ),
        "pip install prosidy-darn[<extra>]",
        (
            "default `TokenCounter` and `SemanticScorer` adapters are disabled "
            "and return a neutral or empty result"
        ),
        (
            "optional adapters use lazy imports inside the adapter "
            "implementation and raise an `ImportError` naming the extra to "
            "install when the dependency is missing"
        ),
        (
            "domain and application modules must not import any optional "
            "tokenizer or embedding package at module import time"
        ),
        (
            "the public segmentation API does not change with extras "
            "installed or omitted"
        ),
    )

    missing_phrases = [
        phrase
        for phrase in required_phrases
        if normalise_whitespace(phrase) not in tokenizer_policy_adr
    ]

    assert missing_phrases == [], (
        f"missing policy commitments in {TOKENIZER_POLICY_ADR}: {missing_phrases}"
    )


def test_tokenizer_policy_roadmap_item_is_closed() -> None:
    """Mark roadmap item 1.1.2 done only once ADR-002 is accepted."""
    roadmap = read_document(ROADMAP)
    tokenizer_policy_adr = read_document(TOKENIZER_POLICY_ADR)

    assert "Accepted on" in tokenizer_policy_adr
    assert (
        "- [x] 1.1.2. Record the token-limit and semantic-scoring dependency "
        "policy." in roadmap
    )


def test_import_boundary_adr_is_accepted() -> None:
    """Ensure roadmap item 1.1.3 has a settled import-boundary decision."""
    import_boundary_adr = read_document(IMPORT_BOUNDARY_ADR)

    assert "## Status" in import_boundary_adr
    assert "Accepted on" in import_boundary_adr


def test_import_boundary_adr_defines_hecate_decision() -> None:
    """Lock the accepted ADR-004 hecate decision before adapter work."""
    import_boundary_adr = normalise_whitespace(read_document(IMPORT_BOUNDARY_ADR))
    required_phrases = (
        "hecate is the v1 import-boundary fitness function",
        (
            "hecate is pinned by a full 40-character commit SHA and run "
            "out-of-process through `uv tool run`"
        ),
        ("import-linter is the vetted fallback behind a stable `check-imports` seam"),
        (
            "hecate is never added to `pyproject.toml` and is never referenced "
            "by bare name, because the PyPI `hecate` is an unrelated project"
        ),
        (
            "The production policy models five groups: `domain`, `ports`, "
            "`application`, `adapters`, and `config`"
        ),
        (
            "`domain`, `application`, and `ports` must not import adapters, "
            "Cyclopts, Rich, the Markdown parser package, renderer "
            "infrastructure, or delivery code, while `config` may"
        ),
        (
            "hecate exits 0 when the check passes, 1 when it finds violations, "
            "and 2 on a configuration or input error"
        ),
    )

    missing_phrases = [
        phrase
        for phrase in required_phrases
        if normalise_whitespace(phrase) not in import_boundary_adr
    ]

    assert missing_phrases == [], (
        f"missing import-boundary commitments in {IMPORT_BOUNDARY_ADR}: "
        f"{missing_phrases}"
    )


def test_import_boundary_adr_roadmap_item_is_closed() -> None:
    """Mark roadmap item 1.1.3 done only once ADR-004 is accepted."""
    roadmap = read_document(ROADMAP)
    import_boundary_adr = read_document(IMPORT_BOUNDARY_ADR)

    assert "Accepted on" in import_boundary_adr
    assert "- [x] 1.1.3. Record the import-boundary enforcement decision." in roadmap

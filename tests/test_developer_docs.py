"""Tests for maintainer-facing documentation contracts."""

from __future__ import annotations

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DEVELOPERS_GUIDE = DOCS_DIR / "developers-guide.md"
MARKDOWN_PARSER_ADR = DOCS_DIR / "adr-001-markdown-parser-boundary.md"
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
    markdown_parser_adr = read_document(MARKDOWN_PARSER_ADR)
    required_phrases = (
        "V1 ships one Markdown-aware parser adapter plus a\nplain-text fallback",
        (
            "The initial Markdown-aware adapter is `mdast` when its\n"
            "version and compatibility probe pass"
        ),
        (
            "PyO3 `markdown-rs` range\n"
            "extractor is a contingency, not a concurrent v1 adapter"
        ),
        "must report degradation when used for Markdown input",
    )

    missing_phrases = [
        phrase for phrase in required_phrases if phrase not in markdown_parser_adr
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

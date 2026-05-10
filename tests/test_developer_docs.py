"""Tests for maintainer-facing documentation contracts."""

from __future__ import annotations

import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
DEVELOPERS_GUIDE = DOCS_DIR / "developers-guide.md"
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
    assert DEVELOPERS_GUIDE.is_file()


def test_initial_adr_locations_exist() -> None:
    """Keep Phase 1 ADR review locations stable before decision work starts."""
    missing_paths = [
        adr_path
        for adr_path in INITIAL_ADR_PATHS
        if not (REPO_ROOT / adr_path).is_file()
    ]

    assert missing_paths == []


def test_initial_adrs_are_discoverable_from_developers_guide() -> None:
    """Link blocking Phase 1 ADRs from the maintainer-facing guide."""
    developers_guide = read_document(DEVELOPERS_GUIDE)

    missing_links = [
        adr_path for adr_path in INITIAL_ADR_PATHS if adr_path not in developers_guide
    ]

    assert missing_links == []


def test_initial_adrs_are_discoverable_from_roadmap() -> None:
    """Keep the roadmap and developer guide aligned on blocking ADR paths."""
    roadmap = read_document(ROADMAP)
    missing_links = [adr_path for adr_path in INITIAL_ADR_PATHS if adr_path not in roadmap]

    assert missing_links == []


def test_phase_one_quality_gates_are_documented() -> None:
    """Document the commands contributors must run for Phase 1 work."""
    developers_guide = read_document(DEVELOPERS_GUIDE)
    missing_gates = [
        gate for gate in PHASE_ONE_QUALITY_GATES if gate not in developers_guide
    ]

    assert missing_gates == []

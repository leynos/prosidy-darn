"""Subprocess demonstration that hecate enforces the import boundary.

The test invokes the pinned ``leynos/hecate`` checker out-of-process through
``uv tool run`` so the tool's own Cyclopts dependency never enters the project
virtual environment. It proves the architecture-fitness criterion recorded in
ADR-004: a clean fixture tree passes (exit 0) while a tree with forbidden
domain-to-adapter and domain-to-external edges fails (exit 1). A configuration
or input error (exit 2) is treated as a harness failure, not a boundary
violation.
"""

from __future__ import annotations

import functools
import json
import os
import pathlib
import re
import shutil
import subprocess  # noqa: S404 - fixed argument vectors, no shell, trusted inputs
import typing as typ

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES_DIR = pathlib.Path(__file__).resolve().parent / "fixtures" / "import_boundary"
CLEAN_TREE = FIXTURES_DIR / "clean"
DIRTY_TREE = FIXTURES_DIR / "dirty"
CLEAN_CONFIG = CLEAN_TREE / "hecate.toml"
DIRTY_CONFIG = DIRTY_TREE / "hecate.toml"
MAKEFILE = REPO_ROOT / "Makefile"

HECATE_REPO_URL = "git+https://github.com/leynos/hecate.git"
GIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
HECATE_REF_PATTERN = re.compile(
    r"^HECATE_REF\s*\?=\s*(?P<ref>[0-9a-f]{40})\s*$",
    flags=re.MULTILINE,
)

EXIT_CLEAN = 0
EXIT_VIOLATIONS = 1
EXIT_CONFIG_ERROR = 2

# hecate is fetched and built on the first invocation; relax the strict default
# per-test timeout so a cold `uv tool run` does not trip the harness clock.
pytestmark = pytest.mark.timeout(300)


@functools.cache
def _hecate_ref() -> str | None:
    """Return the pinned hecate git reference from the environment or Makefile."""
    if (env_ref := os.environ.get("HECATE_REF")) and GIT_SHA_PATTERN.fullmatch(env_ref):
        return env_ref

    makefile = MAKEFILE.read_text(encoding="utf-8")
    match = HECATE_REF_PATTERN.search(makefile)
    if match is None:
        return None
    return match.group("ref")


def _hecate_command(*args: str) -> list[str]:
    """Build the ``uv tool run`` command that invokes the pinned hecate."""
    uv = shutil.which("uv") or "uv"
    spec = f"{HECATE_REPO_URL}@{_hecate_ref()}"
    return [uv, "tool", "run", "--python", "3.14", "--from", spec, "hecate", *args]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a fixed hecate command, capturing text output without a shell."""
    return subprocess.run(  # noqa: S603 - fixed argument vector, no shell, trusted inputs
        command,
        capture_output=True,
        text=True,
        check=False,
    )


@functools.cache
def _hecate_unavailable_reason() -> str | None:
    """Return why hecate cannot run, or ``None`` when it is available.

    A successful ``hecate --version`` confirms ``uv tool run`` can fetch and
    execute the pinned tool, so any later non-result exit code is a genuine
    checker error rather than a tool-fetch failure.
    """
    if _hecate_ref() is None:
        return "HECATE_REF is not set and no Makefile HECATE_REF pin was found"
    if shutil.which("uv") is None:
        return "uv executable is not available on PATH"
    try:
        probe = _run(_hecate_command("--version"))
    except OSError as error:  # pragma: no cover - environment-dependent
        return f"could not launch uv tool run: {error}"
    if probe.returncode != 0:
        return (
            f"uv tool run could not fetch hecate (exit {probe.returncode}): "
            f"{probe.stderr.strip()}"
        )
    return None


def _require_hecate() -> None:
    """Skip the calling test when the pinned hecate tool cannot run."""
    reason = _hecate_unavailable_reason()
    if reason is not None:
        pytest.skip(reason)


def _run_import_boundary_check(config: pathlib.Path) -> tuple[int, dict[str, object]]:
    """Run hecate against one fixture config, returning its exit code and JSON."""
    result = _run(_hecate_command("check", "--config", str(config), "--format", "json"))
    if result.returncode == EXIT_CONFIG_ERROR:
        pytest.fail(
            "hecate reported a configuration or input error (exit 2) for "
            f"{config}: {result.stderr.strip()}"
        )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        pytest.fail(
            f"hecate did not emit JSON for {config} (exit {result.returncode}): "
            f"{error}; stdout={result.stdout!r}; stderr={result.stderr.strip()!r}"
        )
    if not isinstance(data, dict):
        pytest.fail(f"hecate JSON for {config} was not an object: {data!r}")
    return result.returncode, typ.cast("dict[str, object]", data)


def _violation_edges(payload: dict[str, object]) -> set[tuple[str, str]]:
    """Extract the ``(importer, imported)`` edges from a hecate JSON payload."""
    violations = payload["violations"]
    assert isinstance(violations, list)
    edges: set[tuple[str, str]] = set()
    for entry in violations:
        assert isinstance(entry, dict)
        violation = typ.cast("dict[str, object]", entry)
        edges.add((str(violation["importer"]), str(violation["imported"])))
    return edges


def test_clean_tree_passes_import_boundary_check() -> None:
    """Prove hecate exits 0 with no violations on the allowed-edge fixture."""
    _require_hecate()

    exit_code, payload = _run_import_boundary_check(CLEAN_CONFIG)

    assert exit_code == EXIT_CLEAN
    assert payload["ok"] is True
    assert payload["violations"] == []


def test_dirty_tree_fails_import_boundary_check() -> None:
    """Prove hecate exits 1 naming the forbidden edges on the dirty fixture."""
    _require_hecate()

    exit_code, payload = _run_import_boundary_check(DIRTY_CONFIG)

    assert exit_code == EXIT_VIOLATIONS
    assert payload["ok"] is False

    expected_edges = {
        (
            "fixture_pkg.fixture_domain.adapter_breach",
            "fixture_pkg.fixture_adapters.runtime",
        ),
        ("fixture_pkg.fixture_domain.external_breach", "pretend_framework"),
    }
    missing_edges = expected_edges - _violation_edges(payload)
    assert missing_edges == set(), f"missing forbidden edges: {missing_edges}"

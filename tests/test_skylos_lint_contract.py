"""Contract tests for the blocking Skylos dead-code lint gate."""

from __future__ import annotations

import os
import shutil
import subprocess  # noqa: S404 - regression tests execute Make without a shell
import tomllib
import typing as typ
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _pyproject() -> dict[str, object]:
    """Load the repository's Python project configuration."""
    return tomllib.loads(
        (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )


def test_skylos_is_a_pinned_external_tool() -> None:
    """Keep Skylos out of the project environment and pin its tool release."""
    config = _pyproject()
    dependency_groups = typ.cast("dict[str, list[str]]", config["dependency-groups"])

    assert not any(
        dependency.startswith("skylos") for dependency in dependency_groups["dev"]
    ), "Expected Skylos to be separately provisioned from development dependencies."
    makefile = (REPOSITORY_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "SKYLOS_VERSION ?= 4.33.2" in makefile, (
        "Expected the separately provisioned Skylos tool version to be exact."
    )
    assert "--from 'skylos==$(SKYLOS_VERSION)' skylos" in makefile, (
        "Expected Skylos to use its separately provisioned tool environment."
    )


def test_skylos_configuration_has_no_unexplained_exception() -> None:
    """Require a verified runtime-caller reason for every allowed symbol."""
    config = _pyproject()
    tool_config = typ.cast("dict[str, object]", config["tool"])
    skylos = typ.cast("dict[str, object]", tool_config["skylos"])
    whitelist = typ.cast("dict[str, object]", skylos["whitelist"])
    documented = typ.cast("dict[str, str]", whitelist["documented"])

    assert whitelist["names"] == [], "Expected no unexplained Skylos exceptions."
    assert all(reason.strip() for reason in documented.values()), (
        "Expected every documented Skylos exception to have a reason."
    )
    gate = typ.cast("dict[str, object]", skylos["gate"])
    assert gate["strict"] is True, "Expected the Skylos gate to run in strict mode."


def test_make_lint_runs_a_local_blocking_dead_code_scan() -> None:
    """Keep the Skylos invocation deterministic and production-only."""
    make_executable = shutil.which("make")
    assert make_executable is not None, "Expected Make to be available for the test."

    result = subprocess.run(  # noqa: S603 - test executes Make without a shell
        [make_executable, "--no-print-directory", "--dry-run", "lint"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Expected make lint dry run to succeed."
    required_fragments = (
        "skylos --config-file pyproject.toml prosidy_darn",
        "--category dead_code --gate",
        "--format concise --no-upload --no-provenance --no-grep-verify",
    )
    assert all(fragment in result.stdout for fragment in required_fragments), (
        "Expected one local, blocking Skylos command with its required flags."
    )
    assert result.stdout.count("skylos --config-file pyproject.toml") == 1, (
        "Expected make lint to expand exactly one Skylos command."
    )
    assert " tests --category dead_code" not in result.stdout, (
        "Expected tests to be excluded from the production Skylos graph."
    )


def test_skylos_allow_preserves_metacharacters_as_arguments(tmp_path: Path) -> None:
    """Keep untrusted allow-list values within their original arguments."""
    recorder = tmp_path / "skylos-recorder"
    capture = tmp_path / "arguments.txt"
    marker = tmp_path / "injected-command"
    recorder.write_text(
        '#!/bin/sh\nprintf \'%s\\n\' "$@" > "$SKYLOS_CAPTURE"\n',
        encoding="utf-8",
    )
    recorder.chmod(0o755)
    name = f'registered"; touch {marker}; printf "'
    reason = f"loaded by `touch {marker}` and $(touch {marker})"
    make_executable = shutil.which("make")
    assert make_executable is not None, "Expected Make to be available for the test."

    result = subprocess.run(  # noqa: S603 - arguments exercise shell injection safely
        [
            make_executable,
            "--no-print-directory",
            "skylos-allow",
            f"NAME={name}",
            f"REASON={reason}",
            f"SKYLOS={recorder}",
        ],
        cwd=REPOSITORY_ROOT,
        env={**os.environ, "SKYLOS_CAPTURE": str(capture)},
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Expected quoted metacharacters to reach Skylos."
    assert capture.read_text(encoding="utf-8").splitlines() == [
        "whitelist",
        name,
        "--reason",
        reason,
    ], "Expected NAME and REASON to remain single whitelist arguments."
    assert not marker.exists(), "Expected no injected shell command to execute."


@pytest.mark.parametrize(
    ("provided_assignment", "expected_error"),
    [
        (
            "REASON=loaded by the verified plugin registry",
            "Error: NAME is required for a named whitelist exception",
        ),
        (
            "NAME=registered_handler",
            "Error: REASON is required for a named whitelist exception",
        ),
    ],
)
def test_skylos_allow_rejects_missing_required_value(
    tmp_path: Path,
    provided_assignment: str,
    expected_error: str,
) -> None:
    """Reject a missing allow-list value before invoking Skylos."""
    recorder = tmp_path / "skylos-recorder"
    capture = tmp_path / "arguments.txt"
    recorder.write_text(
        '#!/bin/sh\nprintf \'%s\\n\' "$@" > "$SKYLOS_CAPTURE"\n',
        encoding="utf-8",
    )
    recorder.chmod(0o755)
    make_executable = shutil.which("make")
    assert make_executable is not None, "Expected Make to be available for the test."

    result = subprocess.run(  # noqa: S603 - tests validate Make safely
        [
            make_executable,
            "--no-print-directory",
            "skylos-allow",
            provided_assignment,
            f"SKYLOS={recorder}",
        ],
        cwd=REPOSITORY_ROOT,
        env={**os.environ, "SKYLOS_CAPTURE": str(capture)},
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2, "Expected missing values to return status 2."
    assert expected_error in result.stderr, "Expected the missing-value diagnostic."
    assert not capture.exists(), "Expected Skylos not to run after validation fails."


def test_skylos_cache_is_ignored() -> None:
    """Keep local Skylos cache files out of version control."""
    gitignore = (REPOSITORY_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert ".skylos/" in gitignore.splitlines(), (
        "Expected the local Skylos cache directory to be ignored."
    )

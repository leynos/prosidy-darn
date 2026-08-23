"""Contract tests for Skylos dead-code detection in Make and CI.

Skylos scan options may precede a production target, but the standalone
``whitelist`` subcommand must appear immediately after ``skylos``. Skylos also
uses its own Python AST, so it must run with Python 3.14 to understand project
syntax. Makeutil parses the Makefile into structured rules and variables, so
these tests do not depend on whitespace or nearby source text.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess  # noqa: S404 - contract tests invoke fixed local commands.
import tomllib
import typing as typ
from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_MAKEUTIL_COMMAND: typ.Final = ("makeutil", "parse", "Makefile")
_MAKEUTIL_REVISION: typ.Final = "29fc5a1634ffbaa18a773eed9dff1b2838a45d9c"
_MAKEUTIL_TOOLCHAIN: typ.Final = "nightly-2026-05-28"
_MAKEUTIL_INSTALL_TOKENS: typ.Final = (
    "rustup",
    "toolchain",
    "install",
    "${MAKEUTIL_TOOLCHAIN}",
    "--profile",
    "minimal",
    "RUSTFLAGS=-Zpolonius=next",
    "cargo",
    "+${MAKEUTIL_TOOLCHAIN}",
    "install",
    "--git",
    "https://github.com/leynos/makeutil",
    "--rev",
    "${MAKEUTIL_REVISION}",
    "--locked",
    "--force",
    "makeutil",
)


def _makefile_report() -> dict[str, object]:
    """Return Makeutil's complete, successfully parsed Makefile report."""
    completed = subprocess.run(  # noqa: S603 - fixed parser command.
        _MAKEUTIL_COMMAND,
        capture_output=True,
        check=True,
        cwd=REPOSITORY_ROOT,
        text=True,
    )
    report = typ.cast("dict[str, object]", json.loads(completed.stdout))
    parse = _mapping(report.get("parse"), subject="Makeutil parse report")
    assert parse.get("status") == "complete", (
        f"Makeutil did not complete the Makefile parse: {parse!r}"
    )
    return report


def _mapping(value: object, *, subject: str) -> dict[str, object]:
    """Return a JSON object, naming the unexpected `subject` on failure."""
    assert isinstance(value, dict), f"Expected {subject} to be a JSON object."
    return typ.cast("dict[str, object]", value)


def _objects(value: object, *, subject: str) -> list[dict[str, object]]:
    """Return a JSON object array, naming the unexpected `subject` on failure."""
    assert isinstance(value, list), f"Expected {subject} to be a JSON array."
    return [_mapping(item, subject=f"{subject} item") for item in value]


def _text_sequence(value: object, *, subject: str) -> tuple[str, ...]:
    """Return a JSON string array, naming the unexpected `subject` on failure."""
    assert isinstance(value, list), f"Expected {subject} to be a JSON array."
    assert all(isinstance(item, str) for item in value), (
        f"Expected {subject} to contain only JSON strings."
    )
    return tuple(typ.cast("list[str]", value))


def _sole_variable(name: str) -> dict[str, object]:
    """Return Makeutil's sole variable fact for `name`."""
    variables = _objects(_makefile_report().get("variables"), subject="variables")
    matches = [variable for variable in variables if variable.get("name") == name]
    assert len(matches) == 1, (
        f"Expected one Makefile variable named {name!r}, found {len(matches)}."
    )
    return matches[0]


def _sole_recipe_rule(target: str) -> dict[str, object]:
    """Return the only parsed rule for `target` that has recipes."""
    rules = _objects(_makefile_report().get("rules"), subject="rules")
    matches = [
        rule
        for rule in rules
        if target in _text_sequence(rule.get("targets"), subject="rule targets")
        and _objects(rule.get("recipes"), subject="rule recipes")
    ]
    assert len(matches) == 1, (
        f"Expected one recipe-bearing Makefile rule named {target!r}, "
        f"found {len(matches)}."
    )
    return matches[0]


def _variable_tokens(name: str) -> tuple[str, ...]:
    """Return shell-like tokens from Makeutil's raw variable value."""
    value = _sole_variable(name).get("raw_value")
    assert isinstance(value, str), f"Expected {name!r} to have a string value."
    return tuple(shlex.split(value))


def _recipe_tokens(target: str) -> tuple[tuple[str, ...], ...]:
    """Return shell-like tokens for every recipe in `target`."""
    recipes = _objects(
        _sole_recipe_rule(target).get("recipes"), subject=f"{target} recipes"
    )
    return tuple(
        tuple(shlex.split(recipe_text.replace("\\\n", "")))
        for recipe in recipes
        if isinstance(recipe_text := recipe.get("text"), str)
    )


def _workflow_job(workflow_path: str, job_name: str) -> dict[str, object]:
    """Return the named job from a repository workflow."""
    workflow = yaml.safe_load((REPOSITORY_ROOT / workflow_path).read_text())
    workflow_mapping = _mapping(workflow, subject=f"{workflow_path} workflow")
    jobs = _mapping(workflow_mapping.get("jobs"), subject=f"{workflow_path} jobs")
    return _mapping(jobs.get(job_name), subject=f"{workflow_path} job {job_name!r}")


def _sole_workflow_step(
    job_name: str,
    step_name: str,
    *,
    workflow_path: str = ".github/workflows/ci.yml",
) -> dict[str, object]:
    """Return the sole named CI step from `job_name`."""
    job = _workflow_job(workflow_path, job_name)
    steps = _objects(
        job.get("steps"), subject=f"{workflow_path} job {job_name!r} steps"
    )
    matches = [step for step in steps if step.get("name") == step_name]
    assert len(matches) == 1, (
        f"Expected one {step_name!r} step in {workflow_path} job {job_name!r}, "
        f"found {len(matches)}."
    )
    return matches[0]


def _run_skylos_allow(*arguments: str) -> subprocess.CompletedProcess[str]:
    """Run the whitelist boundary without invoking Skylos on invalid input."""
    environment = {**os.environ, "NAME": "wsl-hostname"}
    environment.pop("REASON", None)
    environment.pop("SYMBOL", None)
    return subprocess.run(  # noqa: S603 - fixed Make executable and target.
        (_make_executable(), "skylos-allow", *arguments),
        capture_output=True,
        check=False,
        cwd=REPOSITORY_ROOT,
        env=environment,
        text=True,
    )


def _make_executable() -> str:
    """Return the absolute Make executable path required by boundary tests."""
    make_executable = shutil.which("make")
    assert make_executable is not None, "Expected Make to be available for the test."
    return make_executable


def _assert_makeutil_installation(command: object, *, contract: str) -> None:
    """Assert that `command` installs the pinned Makeutil parser."""
    assert isinstance(command, str), (
        f"{contract} must provide a Makeutil installation shell command."
    )
    assert (
        tuple(shlex.split(command.replace("\\\n", ""))) == _MAKEUTIL_INSTALL_TOKENS
    ), f"{contract} must pin the Makeutil installation command."


def test_skylos_is_a_pinned_external_tool() -> None:
    """Keep Skylos out of the project environment and pin its tool release."""
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as configuration_file:
        config = typ.cast("dict[str, object]", tomllib.load(configuration_file))

    dependency_groups = _mapping(config.get("dependency-groups"), subject="groups")
    development_dependencies = _text_sequence(
        dependency_groups.get("dev"), subject="development dependencies"
    )
    assert not any(
        dependency.startswith("skylos") for dependency in development_dependencies
    ), "Skylos must remain separately provisioned from development dependencies."


def test_lint_recipe_runs_the_production_dead_code_gate() -> None:
    """`make lint` must scan production code with Skylos's strict gate."""
    assert _variable_tokens("SKYLOS_VERSION") == ("4.33.2",), (
        "Skylos version contract must pin 4.33.2."
    )
    assert _variable_tokens("SKYLOS_PRODUCTION_TARGETS") == ("prosidy_darn",), (
        "Skylos production-target contract must scan prosidy_darn."
    )
    assert _variable_tokens("SKYLOS_EXCLUDE_FOLDERS") == ("tests",), (
        "Skylos exclusion contract must omit tests from the liveness graph."
    )
    skylos_commands = [
        command for command in _recipe_tokens("lint") if command[:1] == ("$(SKYLOS)",)
    ]
    assert skylos_commands == [
        (
            "$(SKYLOS)",
            "$(SKYLOS_PRODUCTION_TARGETS)",
            "--exclude",
            "$(SKYLOS_EXCLUDE_FOLDERS)",
            "--category",
            "dead_code",
            "--gate",
            "--format",
            "concise",
            "--no-upload",
            "--no-provenance",
            "--no-grep-verify",
        )
    ], "Skylos lint command contract must strictly scan only production dead code."


def test_whitelist_target_uses_skylos_subcommand_contract() -> None:
    """`skylos whitelist` must precede the symbol and omit scan-only options."""
    assert _variable_tokens("SKYLOS_CLI") == (
        "$(UV_ENV)",
        "$(UV)",
        "tool",
        "run",
        "--python",
        "3.14",
        "--from",
        "skylos==$(SKYLOS_VERSION)",
        "skylos",
    ), "Skylos CLI contract must pin Python 3.14 and its tool release."
    assert _variable_tokens("SKYLOS") == (
        "$(SKYLOS_CLI)",
        "--config-file",
        "pyproject.toml",
    ), "Skylos scan command contract must add only the configuration file."

    whitelist_commands = [
        command
        for command in _recipe_tokens("skylos-allow")
        if command[:1] == ("$(SKYLOS_CLI)",)
    ]
    assert whitelist_commands == [
        (
            "$(SKYLOS_CLI)",
            "whitelist",
            "$${SKYLOS_SYMBOL}",
            "--reason",
            "$${SKYLOS_REASON}",
        )
    ], "Skylos whitelist command contract must dispatch before --reason."


def test_skylos_allow_requires_symbol_and_reason() -> None:
    """The whitelist target must reject incomplete input without running Skylos."""
    for arguments, expected_error in (
        ((), "Error: SYMBOL is required for a named whitelist exception"),
        (
            ("SYMBOL=handler",),
            "Error: REASON is required for a named whitelist exception",
        ),
    ):
        completed = _run_skylos_allow(*arguments)

        assert completed.returncode == 2, (
            "Skylos whitelist boundary must reject missing required arguments."
        )
        assert expected_error in completed.stderr, (
            "Skylos whitelist boundary must name the missing required argument."
        )


def test_skylos_allow_dry_run_preserves_whitelist_argument_order() -> None:
    """A valid dry run must reveal the command without writing an exception."""
    completed = subprocess.run(  # noqa: S603 - fixed Make executable and arguments.
        (
            _make_executable(),
            "--dry-run",
            "skylos-allow",
            "SYMBOL=handler",
            "REASON=Loaded by plugin registry",
        ),
        capture_output=True,
        check=False,
        cwd=REPOSITORY_ROOT,
        text=True,
    )

    assert completed.returncode == 0, (
        "Skylos whitelist dry-run contract must accept complete input."
    )
    assert (
        'skylos whitelist "${SKYLOS_SYMBOL}" --reason "${SKYLOS_REASON}"'
        in completed.stdout
    ), "Skylos whitelist dry-run contract must preserve subcommand argument order."


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
    symbol = f'registered"; touch {marker}; printf "'
    reason = f"loaded by `touch {marker}` and $(touch {marker})"
    make_executable = shutil.which("make")
    assert make_executable is not None, "Expected Make to be available for the test."

    result = subprocess.run(  # noqa: S603 - arguments exercise shell injection safely.
        [
            make_executable,
            "--no-print-directory",
            "skylos-allow",
            f"SYMBOL={symbol}",
            f"REASON={reason}",
            f"SKYLOS_CLI={recorder}",
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
        symbol,
        "--reason",
        reason,
    ], "Expected SYMBOL and REASON to remain single whitelist arguments."
    assert not marker.exists(), "Expected no injected shell command to execute."


def test_skylos_configuration_requires_strict_explained_exceptions() -> None:
    """Require strict gates and verified reasons for documented exceptions."""
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as configuration_file:
        config = typ.cast("dict[str, object]", tomllib.load(configuration_file))

    tool_config = _mapping(config.get("tool"), subject="tool configuration")
    skylos = _mapping(tool_config.get("skylos"), subject="Skylos configuration")
    gate = _mapping(skylos.get("gate"), subject="Skylos gate configuration")
    assert gate.get("strict") is True, (
        "Skylos gate configuration must enable strict mode."
    )
    whitelist = _mapping(skylos.get("whitelist"), subject="Skylos allow list")
    documented = _mapping(
        whitelist.get("documented"), subject="documented Skylos exceptions"
    )
    assert all(
        isinstance(reason, str) and reason.strip() for reason in documented.values()
    ), "Every documented Skylos exception must name a verified runtime caller."


def test_ci_runs_lint_and_installs_makeutil_for_coverage() -> None:
    """CI must share the lint target and bootstrap Makeutil before full pytest."""
    lint_step = _sole_workflow_step(
        "lint-test", "Run Python lint and dead-code detection"
    )
    assert lint_step.get("run") == "make lint", (
        "CI lint-step contract must invoke the shared make lint target."
    )

    coverage_job = _workflow_job(".github/workflows/ci.yml", "lint-test")
    environment = _mapping(coverage_job.get("env"), subject="CI Makeutil environment")
    assert environment.get("MAKEUTIL_REVISION") == _MAKEUTIL_REVISION, (
        "CI coverage Makeutil revision contract must stay pinned."
    )
    assert environment.get("MAKEUTIL_TOOLCHAIN") == _MAKEUTIL_TOOLCHAIN, (
        "CI coverage Makeutil toolchain contract must stay pinned."
    )
    parser_step = _sole_workflow_step("lint-test", "Install Makefile parser")
    _assert_makeutil_installation(
        parser_step.get("run"), contract="CI coverage Makeutil-install contract"
    )

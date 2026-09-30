"""Contract tests for the Skylos Makefile and Continuous Integration wiring.

Makeutil parses the Makefile into structured rules and variables, so these
tests lock the command interface without depending on adjacent text or layout.
The executable whitelist boundary has its own focused test module.
"""

from __future__ import annotations

import json
import shlex
import subprocess  # noqa: S404 - contract tests invoke the fixed parser.
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
_TEST_PREREQUISITES: typ.Final = ("build", "uv", "$(VENV_TOOLS)", "makeutil")
_SKYLOS_VERSION_TOKENS: typ.Final = ("4.33.2",)
_SKYLOS_PRODUCTION_TARGET_TOKENS: typ.Final = ("prosidy_darn",)
_SKYLOS_EXCLUSION_TOKENS: typ.Final = ("tests",)
_SKYLOS_CLI_TOKENS: typ.Final = (
    "$(UV_ENV)",
    "$(UV)",
    "tool",
    "run",
    "--python",
    "3.14",
    "--from",
    "skylos==$(SKYLOS_VERSION)",
    "skylos",
)
_SKYLOS_SCAN_TOKENS: typ.Final = ("$(SKYLOS_CLI)", "--config-file", "pyproject.toml")
_SKYLOS_LINT_TOKENS: typ.Final = (
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
_SKYLOS_LOCK_TOKENS: typ.Final = (".skylos-whitelist.lock",)
_SKYLOS_WHITELIST_TOKENS: typ.Final = (
    "flock",
    "$(SKYLOS_WHITELIST_LOCK)",
    "env",
    "$(SKYLOS_CLI)",
    "whitelist",
    "$${SKYLOS_SYMBOL}",
    "--reason",
    "$${SKYLOS_REASON}",
)
_EXPECTED_DOCUMENTED_WHITELIST_NAMES: typ.Final = frozenset()
_EXPECTED_ENTRYPOINT_NAMES: typ.Final = frozenset()
_FULL_SUITE_WORKFLOW_JOBS: typ.Final = ((".github/workflows/ci.yml", "lint-test"),)


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


def _sole_rule_with_prerequisites(target: str) -> dict[str, object]:
    """Return the only parsed `target` rule that declares prerequisites."""
    rules = _objects(_makefile_report().get("rules"), subject="rules")
    matches = [
        rule
        for rule in rules
        if target in _text_sequence(rule.get("targets"), subject="rule targets")
        and _text_sequence(rule.get("prerequisites"), subject="rule prerequisites")
    ]
    assert len(matches) == 1, (
        f"Expected one prerequisite-bearing Makefile rule named {target!r}, "
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
    mapping = _mapping(workflow, subject=f"{workflow_path} workflow")
    jobs = _mapping(mapping.get("jobs"), subject=f"{workflow_path} jobs")
    return _mapping(jobs.get(job_name), subject=f"{workflow_path} job {job_name!r}")


def _sole_workflow_step(
    job_name: str, step_name: str, *, workflow_path: str = ".github/workflows/ci.yml"
) -> dict[str, object]:
    """Return the sole named CI step from `job_name`."""
    steps = _objects(
        _workflow_job(workflow_path, job_name).get("steps"),
        subject=f"{workflow_path} job {job_name!r} steps",
    )
    matches = [step for step in steps if step.get("name") == step_name]
    assert len(matches) == 1, (
        f"Expected one {step_name!r} step in {workflow_path} job {job_name!r}, "
        f"found {len(matches)}."
    )
    return matches[0]


def _assert_makeutil_installation(command: object, *, contract: str) -> None:
    """Assert that `command` installs the pinned Makeutil parser."""
    assert isinstance(command, str), (
        f"{contract} must provide a Makeutil installation command."
    )
    assert (
        tuple(shlex.split(command.replace("\\\n", ""))) == _MAKEUTIL_INSTALL_TOKENS
    ), f"{contract} must pin the Makeutil installation command."


def test_lint_recipe_runs_the_production_dead_code_gate() -> None:
    """`make lint` must scan production code with Skylos's strict gate."""
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as configuration_file:
        config = typ.cast("dict[str, object]", tomllib.load(configuration_file))
    dependencies = _text_sequence(
        _mapping(config.get("dependency-groups"), subject="groups").get("dev"),
        subject="development dependencies",
    )
    assert "hypothesis>=6.165.10,<7.0" in dependencies, (
        "Skylos forwarding contracts must pin bounded Hypothesis coverage."
    )
    assert not any(dependency.startswith("skylos") for dependency in dependencies), (
        "Skylos must remain separately provisioned from development dependencies."
    )
    prerequisites = _text_sequence(
        _sole_rule_with_prerequisites("test").get("prerequisites"),
        subject="test target prerequisites",
    )
    assert prerequisites == _TEST_PREREQUISITES, (
        "Make test prerequisite contract must require the Makeutil binary."
    )
    assert _variable_tokens("SKYLOS_VERSION") == _SKYLOS_VERSION_TOKENS, (
        "Skylos version contract must pin the supported tool release."
    )
    assert (
        _variable_tokens("SKYLOS_PRODUCTION_TARGETS")
        == _SKYLOS_PRODUCTION_TARGET_TOKENS
    ), "Skylos production-target contract must scan prosidy_darn."
    assert _variable_tokens("SKYLOS_EXCLUDE_FOLDERS") == _SKYLOS_EXCLUSION_TOKENS, (
        "Skylos exclusion contract must omit tests from the liveness graph."
    )
    commands = [
        command for command in _recipe_tokens("lint") if command[:1] == ("$(SKYLOS)",)
    ]
    assert commands == [_SKYLOS_LINT_TOKENS], (
        "Skylos lint command contract must strictly scan only production dead code."
    )


def test_whitelist_target_uses_the_command_only_skylos_cli() -> None:
    """`skylos whitelist` must lock and dispatch before scan-only options."""
    assert _variable_tokens("SKYLOS_CLI") == _SKYLOS_CLI_TOKENS, (
        "Skylos CLI contract must pin Python 3.14 and its tool release."
    )
    assert _variable_tokens("SKYLOS") == _SKYLOS_SCAN_TOKENS, (
        "Skylos scan command contract must add only the configuration file."
    )
    assert _variable_tokens("SKYLOS_WHITELIST_LOCK") == _SKYLOS_LOCK_TOKENS, (
        "Skylos whitelist contract must use a repository-local lock."
    )
    commands = [
        command
        for command in _recipe_tokens("skylos-allow")
        if command[:4] == _SKYLOS_WHITELIST_TOKENS[:4]
    ]
    assert commands == [_SKYLOS_WHITELIST_TOKENS], (
        "Skylos whitelist contract must lock and dispatch before --reason."
    )


def test_skylos_configuration_pins_verified_runtime_boundaries() -> None:
    """Strict configuration must preserve every verified Skylos exception."""
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as configuration_file:
        config = typ.cast("dict[str, object]", tomllib.load(configuration_file))
    skylos = _mapping(
        _mapping(config.get("tool"), subject="tool configuration").get("skylos"),
        subject="Skylos configuration",
    )
    gate = _mapping(skylos.get("gate"), subject="Skylos gate configuration")
    assert gate.get("strict") is True, (
        "Skylos gate configuration must enable strict mode."
    )
    whitelist = _mapping(skylos.get("whitelist"), subject="Skylos allow list")
    names = frozenset(
        _text_sequence(whitelist.get("names"), subject="allow-list names")
    )
    documented = _mapping(whitelist.get("documented"), subject="documented exceptions")
    assert names == _EXPECTED_DOCUMENTED_WHITELIST_NAMES, (
        "Skylos allow-list names must match the verified exception set."
    )
    assert frozenset(documented) == _EXPECTED_DOCUMENTED_WHITELIST_NAMES, (
        "Skylos documented exceptions must match the verified exception set."
    )
    assert all(
        isinstance(reason, str) and reason.strip() for reason in documented.values()
    ), "Every documented Skylos exception must name a verified runtime caller."
    dead_code = _mapping(skylos.get("dead_code", {}), subject="dead-code configuration")
    entry_points = _objects(
        dead_code.get("entrypoints", []), subject="Skylos entry points"
    )
    entry_point_names = frozenset(
        name
        for entry_point in entry_points
        for name in _text_sequence(
            entry_point.get("full_name"), subject="entry-point names"
        )
    )
    assert entry_point_names == _EXPECTED_ENTRYPOINT_NAMES, (
        "Skylos entry-point names must match verified implicit runtime callers."
    )
    assert all(
        isinstance(entry_point.get("type"), str)
        and isinstance(entry_point_reason := entry_point.get("reason"), str)
        and entry_point_reason.strip()
        for entry_point in entry_points
    ), "Every Skylos entry point must be typed and have a verified reason."


def test_ci_runs_lint_and_installs_makeutil_for_full_suite_jobs() -> None:
    """Every full-suite CI job must bootstrap the parser before pytest."""
    lint_step = _sole_workflow_step(
        "lint-test", "Run Python lint and dead-code detection"
    )
    assert lint_step.get("run") == "make lint", (
        "CI lint-step contract must invoke the shared make lint target."
    )
    for workflow_path, job_name in _FULL_SUITE_WORKFLOW_JOBS:
        job = _workflow_job(workflow_path, job_name)
        environment = _mapping(
            job.get("env"), subject=f"{workflow_path} Makeutil environment"
        )
        assert environment.get("MAKEUTIL_REVISION") == _MAKEUTIL_REVISION, (
            f"{workflow_path} {job_name} Makeutil revision contract must stay pinned."
        )
        assert environment.get("MAKEUTIL_TOOLCHAIN") == _MAKEUTIL_TOOLCHAIN, (
            f"{workflow_path} {job_name} Makeutil toolchain contract must stay pinned."
        )
        parser_step = _sole_workflow_step(
            job_name, "Install Makefile parser", workflow_path=workflow_path
        )
        _assert_makeutil_installation(
            parser_step.get("run"),
            contract=f"{workflow_path} {job_name} Makeutil-install contract",
        )

"""Executable boundary tests for the serialized Skylos whitelist helper."""

from __future__ import annotations

import json
import os
import shutil
import string
import subprocess  # noqa: S404 - boundary tests invoke fixed local commands.
import sys
import tomllib
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

import hypothesis as hyp
import hypothesis.strategies as st

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_SHELL_SENSITIVE_TEXT = st.builds(
    lambda prefix, content, suffix: prefix + content + suffix,
    st.text(alphabet=" \t", max_size=4),
    st.text(
        alphabet=string.ascii_letters + string.digits + "_$;|&'\"()[]{}*?!\\`",
        min_size=1,
        max_size=24,
    ),
    st.text(alphabet=" \t", max_size=4),
)


def _make_executable() -> str:
    """Return the absolute path to the required Make executable."""
    executable = shutil.which("make")
    assert executable is not None, "Skylos whitelist boundary tests require Make."
    return executable


def _write_argument_recorder(directory: Path) -> str:
    """Create a fake Skylos executable that serializes its received arguments."""
    recorder = directory / "skylos-recorder"
    recorder.write_text(
        f"#!{sys.executable}\n"
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n"
        "Path('skylos-arguments.json').write_text(\n"
        "    json.dumps(sys.argv[1:]), encoding='utf-8'\n"
        ")\n",
        encoding="utf-8",
    )
    recorder.chmod(0o755)
    return str(recorder)


def _whitelist_command(directory: Path, *, cli: str) -> tuple[str, ...]:
    """Build the isolated whitelist command with a temporary lock path."""
    return (
        _make_executable(),
        "--no-print-directory",
        "-f",
        str(REPOSITORY_ROOT / "Makefile"),
        f"SKYLOS_CLI={cli}",
        f"SKYLOS_WHITELIST_LOCK={directory / '.skylos-whitelist.lock'}",
        "skylos-allow",
    )


def _run_whitelist(
    directory: Path, *, symbol: str, reason: str, cli: str
) -> subprocess.CompletedProcess[str]:
    """Run the whitelist target in an isolated temporary directory."""
    return subprocess.run(  # noqa: S603 - fixed Makefile and target.
        _whitelist_command(directory, cli=cli),
        capture_output=True,
        check=False,
        cwd=directory,
        env={**os.environ, "NAME": "wsl-hostname", "REASON": reason, "SYMBOL": symbol},
        text=True,
    )


def _run_required_argument_check(
    *, symbol: str | None = None, reason: str | None = None
) -> subprocess.CompletedProcess[str]:
    """Run an invalid request without reaching the lock or Skylos executable."""
    environment = {**os.environ, "NAME": "wsl-hostname"}
    environment.pop("REASON", None)
    environment.pop("SYMBOL", None)
    if symbol is not None:
        environment["SYMBOL"] = symbol
    if reason is not None:
        environment["REASON"] = reason
    return subprocess.run(  # noqa: S603 - fixed Make target.
        (_make_executable(), "skylos-allow"),
        capture_output=True,
        check=False,
        cwd=REPOSITORY_ROOT,
        env=environment,
        text=True,
    )


def test_whitelist_requires_symbol_and_reason() -> None:
    """The helper must reject absent inputs despite WSL's `NAME` injection."""
    for symbol, reason, expected_error in (
        (None, None, "Error: SYMBOL is required for a named whitelist exception"),
        ("handler", None, "Error: REASON is required for a named whitelist exception"),
    ):
        completed = _run_required_argument_check(symbol=symbol, reason=reason)
        assert completed.returncode == 2, (
            "Skylos whitelist boundary must reject a missing required argument."
        )
        assert expected_error in completed.stderr, (
            "Skylos whitelist boundary must name the missing required argument."
        )


@hyp.settings(max_examples=25, deadline=None)
@hyp.given(value=st.text(alphabet=" \t", min_size=1, max_size=8))
def test_whitelist_rejects_whitespace_only_values(value: str) -> None:
    """Whitespace-only inputs must fail despite WSL's `NAME` injection."""
    for symbol, reason, expected_error in (
        (value, "Loaded by plugin registry", "Error: SYMBOL is required"),
        ("handler", value, "Error: REASON is required"),
    ):
        completed = _run_required_argument_check(symbol=symbol, reason=reason)
        assert completed.returncode == 2, (
            "Skylos whitelist boundary must reject a whitespace-only value."
        )
        assert expected_error in completed.stderr, (
            "Skylos whitelist boundary must name the whitespace-only argument."
        )


@hyp.settings(max_examples=25, deadline=None)
@hyp.example(symbol=" $(handler);* ", reason=' Loaded "$plugin" | registry ')
@hyp.given(symbol=_SHELL_SENSITIVE_TEXT, reason=_SHELL_SENSITIVE_TEXT)
def test_whitelist_forwards_exact_arguments(symbol: str, reason: str) -> None:
    """Forward valid environment values as exact Skylos command arguments."""
    original_pyproject = b"[tool.skylos.whitelist.documented]\n"
    with TemporaryDirectory() as temporary_directory:
        temporary_path = Path(temporary_directory)
        pyproject_path = temporary_path / "pyproject.toml"
        pyproject_path.write_bytes(original_pyproject)
        completed = _run_whitelist(
            temporary_path,
            symbol=symbol,
            reason=reason,
            cli=_write_argument_recorder(temporary_path),
        )
        recorded_arguments = json.loads(
            (temporary_path / "skylos-arguments.json").read_text(encoding="utf-8")
        )
        final_pyproject = pyproject_path.read_bytes()
    assert completed.returncode == 0, "Skylos recorder must accept complete input."
    assert recorded_arguments == ["whitelist", symbol, "--reason", reason], (
        "Skylos whitelist must receive unmodified SYMBOL and REASON arguments."
    )
    assert final_pyproject == original_pyproject, (
        "A valid Skylos whitelist command must not modify pyproject.toml."
    )


def test_whitelist_lock_preserves_concurrent_documented_entries(tmp_path: Path) -> None:
    """The lock must prevent concurrent documented updates from losing entries."""
    configuration = tmp_path / "pyproject.toml"
    configuration.write_text("[tool.skylos.whitelist.documented]\n", encoding="utf-8")
    writer = tmp_path / "write_whitelist_entry.py"
    writer.write_text(
        f"#!{sys.executable}\n"
        "from pathlib import Path\n"
        "import sys\n"
        "import time\n"
        "symbol = sys.argv[2]\n"
        "reason = sys.argv[4]\n"
        "path = Path('pyproject.toml')\n"
        "contents = path.read_text(encoding='utf-8')\n"
        "time.sleep(0.2)\n"
        "path.write_text(contents + f'{symbol} = {reason!r}\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    writer.chmod(0o755)
    requests = (("first", "first reason"), ("second", "second reason"))
    with ExitStack() as processes:
        running = [
            processes.enter_context(
                subprocess.Popen(  # noqa: S603 - fixed Makefile and target.
                    _whitelist_command(tmp_path, cli=str(writer)),
                    cwd=tmp_path,
                    env={**os.environ, "REASON": reason, "SYMBOL": symbol},
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            )
            for symbol, reason in requests
        ]
        outcomes = [process.communicate() for process in running]
        returncodes = [process.returncode for process in running]
    assert all(returncode == 0 for returncode in returncodes), (
        f"Concurrent Skylos whitelist updates must succeed: {outcomes!r}"
    )
    with configuration.open("rb") as configuration_file:
        documented = tomllib.load(configuration_file)["tool"]["skylos"]["whitelist"][
            "documented"
        ]
    assert documented == dict(requests), (
        "Skylos whitelist lock must preserve every concurrent documented entry."
    )

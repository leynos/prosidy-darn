"""Tests for maturin pin synchronization and wheel build output."""

from __future__ import annotations

import importlib
import shutil
import subprocess  # noqa: S404 - tests install a locally built wheel.
import sys
import typing as typ

import pytest

from tests.helpers.maturin import (
    MATURIN_VERSION,
    PYO3_VERSION,
    build_native_wheel_artifact,
    read_expected_maturin_version,
    read_maturin_pins,
    read_pyo3_versions,
    repo_root,
    toolchain_available,
    wheel_build_summary,
)

if typ.TYPE_CHECKING:
    import pathlib as pth

    from syrupy.assertion import SnapshotAssertion


def test_maturin_pins_are_synchronized() -> None:
    """Maturin version pins stay aligned across CI and packaging metadata."""
    pins = read_maturin_pins(repo_root())
    assert len(set(pins.values())) == 1, f"Expected one maturin pin, found {pins!r}"
    assert next(iter(pins.values())) == MATURIN_VERSION, (
        "Maturin pin constants must match repository packaging and CI pins"
    )


def test_installed_maturin_matches_expected_pin() -> None:
    """The active maturin CLI matches the pinned development dependency."""
    maturin_path = shutil.which("maturin")
    if maturin_path is None:
        pytest.skip("maturin is not installed.")
    expected = read_expected_maturin_version(repo_root())
    completed = subprocess.run(  # noqa: S603 - command list uses trusted executable.
        [maturin_path, "--version"],
        capture_output=True,
        check=True,
        text=True,
    )
    installed = completed.stdout.removeprefix("maturin ").strip()
    assert installed == expected, (
        f"Expected maturin {expected}, but {installed} is installed"
    )


def test_pyo3_pin_matches_lockfile() -> None:
    """The PyO3 manifest dependency and lockfile version stay aligned."""
    pins = read_pyo3_versions(repo_root())
    assert pins == {
        "rust/prosidy-darn-rs/Cargo.toml": PYO3_VERSION,
        "rust/Cargo.lock": PYO3_VERSION,
    }, "PyO3 manifest and lockfile pins must match the expected constant"


@pytest.mark.timeout(300)
def test_maturin_wheel_build_summary(
    tmp_path: pth.Path,
    snapshot: SnapshotAssertion,
) -> None:
    """Native wheel metadata and layout match the expected maturin output."""
    root = repo_root()
    expected = read_expected_maturin_version(root)
    if not toolchain_available():
        pytest.skip("Rust toolchain unavailable.")
    if sys.version_info >= (3, 15):
        pytest.fail(
            f"maturin {expected} must be updated and wheel contracts refreshed "
            "before native-wheel tests run on Python 3.15+",
        )

    wheel_path = build_native_wheel_artifact(root, tmp_path / "wheelhouse")
    summary = wheel_build_summary(wheel_path)
    assert summary == snapshot, (
        "Native wheel metadata, SBOM, and extension layout must match the snapshot"
    )


@pytest.mark.timeout(300)
def test_rust_extension_hello_returns_expected_greeting(tmp_path: pth.Path) -> None:
    """Import the built Rust extension and execute its public function."""
    root = repo_root()
    expected = read_expected_maturin_version(root)
    if not toolchain_available():
        pytest.skip("Rust toolchain unavailable.")
    if sys.version_info >= (3, 15):
        pytest.fail(
            f"maturin {expected} must be updated and wheel contracts refreshed "
            "before native-wheel tests run on Python 3.15+",
        )

    wheel_path = build_native_wheel_artifact(root, tmp_path / "wheelhouse")
    site_dir = tmp_path / "site"
    subprocess.run(  # noqa: S603 - command list uses trusted paths and local wheel.
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            str(site_dir),
            str(wheel_path),
        ],
        check=True,
    )

    original_path = list(sys.path)
    previous_package = sys.modules.pop("prosidy_darn", None)
    previous_extension = sys.modules.pop("prosidy_darn._prosidy_darn_rs", None)
    try:
        sys.path.insert(0, str(site_dir))
        # End-to-end: exercises the real extension, not a mock.
        module = importlib.import_module("prosidy_darn")

        assert module.hello() == "hello from Rust", (
            "Installed public API must select the Rust extension greeting"
        )
    finally:
        sys.path[:] = original_path
        sys.modules.pop("prosidy_darn", None)
        sys.modules.pop("prosidy_darn._prosidy_darn_rs", None)
        if previous_package is not None:
            sys.modules["prosidy_darn"] = previous_package
        if previous_extension is not None:
            sys.modules["prosidy_darn._prosidy_darn_rs"] = previous_extension

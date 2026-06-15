"""Shared maturin and PyO3 build-validation helpers.

This module contains shared test helpers for validating maturin and PyO3
version-pin synchronisation and native wheel correctness. The helpers read
repository packaging metadata, build the Rust extension wheel with the pinned
maturin backend, and reduce wheel metadata to stable structures that tests can
compare without depending on platform-specific filenames.

The exported constants describe the expected package and extension identity.
``MATURIN_VERSION`` is checked against ``pyproject.toml``,
``.github/workflows/build-wheels.yml``, and
``.github/actions/build-wheels/action.yml``. ``PYO3_VERSION`` is checked
against ``rust/prosidy-darn-rs/Cargo.toml`` and ``rust/Cargo.lock``.
``PACKAGE_NAME`` names the distribution, ``PACKAGE_IMPORT_NAME`` names the
Python import package, and ``RUST_EXTENSION_NAME`` names the PyO3 extension
module expected inside built wheels.

Public functions
----------------
``repo_root``
    Return the repository root from this helper module's location.
``read_expected_maturin_version``
    Read the maturin development dependency pin from ``pyproject.toml``.
``read_maturin_pins``
    Read every maturin pin that must stay synchronised across packaging and
    wheel-build configuration.
``read_pyo3_versions``
    Read the PyO3 dependency version from the Rust crate manifest and lockfile.
``toolchain_available``
    Report whether the local process can resolve Rust and maturin build tools.
``build_native_wheel_artifact``
    Build a native wheel into a caller-provided output directory and return
    the single wheel path that build produced.
``wheel_build_summary``
    Inspect a built wheel and return normalised metadata, wheel settings, and
    archive entries.

The primary caller is ``tests/test_maturin_build.py``. Keep this module
separate from that test file because it is the reuse point for the next Rust
extension crate added under ``rust/``. A second extension test should import
``read_maturin_pins``, ``read_pyo3_versions``, ``toolchain_available``,
``build_native_wheel_artifact``, and ``wheel_build_summary`` from here rather
than duplicate the pin-synchronisation and wheel-validation pattern.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import pathlib
import re
import shutil
import subprocess  # noqa: S404 - tests invoke pinned maturin build commands.
import sys
import tomllib
import typing as typ
import zipfile

_logger = logging.getLogger(__name__)

MATURIN_VERSION = "1.13.3"
PYO3_VERSION = "0.28.3"
PACKAGE_NAME = "prosidy-darn"
PACKAGE_IMPORT_NAME = "prosidy_darn"
RUST_EXTENSION_NAME = "_prosidy_darn_rs"

__all__ = [
    "MATURIN_VERSION",
    "PACKAGE_IMPORT_NAME",
    "PACKAGE_NAME",
    "PYO3_VERSION",
    "RUST_EXTENSION_NAME",
    "PinSynchronisationError",
    "WheelMetadataError",
    "build_native_wheel_artifact",
    "read_expected_maturin_version",
    "read_maturin_pins",
    "read_pyo3_versions",
    "repo_root",
    "toolchain_available",
    "wheel_build_summary",
]

_WORKFLOW_PIN_RE = re.compile(r'MATURIN_VERSION:\s*"(\d+\.\d+\.\d+)"')
_ACTION_PIN_RE = re.compile(
    r"^  maturin-version:\n"
    r"^    description: .*\n"
    r"^    required: false\n"
    r'^    default: "(\d+\.\d+\.\d+)"$',
    re.MULTILINE,
)
_GENERATOR_RE = re.compile(r"^Generator:\s*maturin\s*\(([^)]+)\)\s*$", re.MULTILINE)
_EXTENSION_MODULE_RE = re.compile(
    rf"^{PACKAGE_IMPORT_NAME}/{RUST_EXTENSION_NAME}\.(?:cpython|cp)[^/]+\.(?:pyd|so)$",
)


class WheelMetadataError(ValueError):
    """Raised when wheel or packaging metadata fails a structural validation check."""


class PinSynchronisationError(ValueError):
    """Raised when maturin or PyO3 version pins are not synchronised across repository files."""  # noqa: E501


def repo_root() -> pathlib.Path:
    """Return the repository root path.

    Examples
    --------
    >>> repo_root().joinpath("pyproject.toml").is_file()
    True
    """
    return pathlib.Path(__file__).resolve().parents[2]


def _read_toml(path: pathlib.Path) -> dict[str, typ.Any]:
    """Read a TOML file into a plain dictionary."""
    return tomllib.loads(path.read_text(encoding="utf-8"))


def read_expected_maturin_version(root: pathlib.Path) -> str:
    """Read the maturin version pinned in ``pyproject.toml``."""
    pyproject = _read_toml(root / "pyproject.toml")
    dependencies = pyproject["dependency-groups"]["dev"]
    maturin_pins = [
        dependency.removeprefix("maturin==")
        for dependency in dependencies
        if dependency.startswith("maturin==")
    ]
    if len(maturin_pins) != 1:
        message = f"Expected one maturin dev dependency pin, found {maturin_pins!r}"
        raise PinSynchronisationError(message)
    return maturin_pins[0]


def _require_pin_match(match: re.Match[str] | None, location: str) -> str:
    """Extract a version from a regex match or raise with source context."""
    if match is None:
        message = f"Could not locate maturin version pin in {location}"
        raise PinSynchronisationError(message)
    return match.group(1)


def read_maturin_pins(root: pathlib.Path) -> dict[str, str]:
    """Read maturin version pins from synchronized locations."""
    pyproject = _read_toml(root / "pyproject.toml")
    workflow = (root / ".github/workflows/build-wheels.yml").read_text(
        encoding="utf-8",
    )
    action = (root / ".github/actions/build-wheels/action.yml").read_text(
        encoding="utf-8",
    )
    build_system_requirements = pyproject["build-system"]["requires"]
    build_system_maturin_pins = [
        requirement.removeprefix("maturin==")
        for requirement in build_system_requirements
        if requirement.startswith("maturin==")
    ]
    if len(build_system_maturin_pins) != 1:
        message = (
            "Expected one maturin build backend pin, found "
            f"{build_system_maturin_pins!r}"
        )
        raise PinSynchronisationError(message)
    return {
        "pyproject dev": read_expected_maturin_version(root),
        "pyproject build-system": build_system_maturin_pins[0],
        "build-wheels.yml": _require_pin_match(
            _WORKFLOW_PIN_RE.search(workflow),
            ".github/workflows/build-wheels.yml",
        ),
        "build-wheels/action.yml": _require_pin_match(
            _ACTION_PIN_RE.search(action),
            ".github/actions/build-wheels/action.yml",
        ),
    }


def read_pyo3_versions(root: pathlib.Path) -> dict[str, str]:
    """Read PyO3 versions from the Rust manifest and lockfile."""
    manifest = _read_toml(root / "rust/prosidy-darn-rs/Cargo.toml")
    lockfile = _read_toml(root / "rust/Cargo.lock")
    pyo3_dependency = manifest["dependencies"]["pyo3"]
    pyo3_package = next(
        (package for package in lockfile["package"] if package["name"] == "pyo3"),
        None,
    )
    if pyo3_package is None:
        message = "Could not locate pyo3 package in rust/Cargo.lock"
        raise PinSynchronisationError(message)
    return {
        "rust/prosidy-darn-rs/Cargo.toml": pyo3_dependency["version"],
        "rust/Cargo.lock": pyo3_package["version"],
    }


def _maturin_module_available() -> bool:
    """Return whether the maturin module can be resolved."""
    try:
        return importlib.util.find_spec("maturin") is not None
    except ImportError:
        return False


def toolchain_available() -> bool:
    """Return whether Rust and maturin are available for local wheel builds."""
    return (
        shutil.which("cargo") is not None
        and shutil.which("rustc") is not None
        and _maturin_module_available()
    )


def build_native_wheel_artifact(
    root: pathlib.Path,
    out_dir: pathlib.Path,
) -> pathlib.Path:
    """Build a native wheel with the pinned maturin version."""
    out_dir.mkdir(parents=True, exist_ok=True)
    build_env = os.environ | {"CARGO_TARGET_DIR": str(out_dir / "target")}
    command = [
        sys.executable,
        "-m",
        "maturin",
        "build",
        "--release",
        "--out",
        str(out_dir),
        "--manifest-path",
        str(root / "rust/prosidy-darn-rs/Cargo.toml"),
    ]
    _logger.debug("build_native_wheel_artifact: running %s", command)
    subprocess.run(  # noqa: S603 - command list uses trusted paths and pinned maturin.
        command,
        check=True,
        cwd=root,
        env=build_env,
    )
    _logger.debug(
        "build_native_wheel_artifact: completed; output dir contains %s",
        sorted(out_dir.iterdir()),
    )
    wheels = sorted(out_dir.glob("*.whl"))
    if len(wheels) != 1:
        message = f"Expected exactly one wheel in {out_dir}, found {wheels!r}"
        raise WheelMetadataError(message)
    return wheels[0]


def _header_value(headers: dict[str, list[str]], key: str) -> str | None:
    """Return the first header value for ``key``, or None if absent."""
    values = headers.get(key)
    if values is None:
        return None
    return values[0]


def _parse_metadata(raw_metadata: str) -> dict[str, typ.Any]:
    """Parse RFC 2822-style metadata headers into a normalised dictionary."""
    headers: dict[str, list[str]] = {}
    current_key: str | None = None
    for line in raw_metadata.splitlines():
        if line.startswith((" ", "\t")) and current_key is not None:
            headers[current_key][-1] = f"{headers[current_key][-1]} {line.strip()}"
            continue
        if ":" not in line:
            break
        key, value = line.split(":", 1)
        current_key = key.strip()
        headers.setdefault(current_key, []).append(value.strip())

    return {
        "name": _header_value(headers, "Name"),
        "version": _header_value(headers, "Version"),
        "requires_python": _header_value(headers, "Requires-Python"),
        "requires_dist": sorted(headers.get("Requires-Dist", [])),
    }


def _normalise_wheel_entry(name: str) -> str:
    """Normalise platform and version-specific wheel entry names."""
    if _EXTENSION_MODULE_RE.match(name):
        return (
            f"{PACKAGE_IMPORT_NAME}/{RUST_EXTENSION_NAME}"
            ".cpython-<platform>.<extension>"
        )
    if "/sboms/" in name:
        return f"{PACKAGE_IMPORT_NAME}-<version>.dist-info/sboms/<sbom>.cyclonedx.json"
    if name.startswith(f"{PACKAGE_IMPORT_NAME}-") and ".dist-info/" in name:
        _, suffix = name.split(".dist-info/", 1)
        return f"{PACKAGE_IMPORT_NAME}-<version>.dist-info/{suffix}"
    return name


def _locate_dist_info_wheel(entry_names: list[str]) -> str:
    """Return the ``.dist-info/WHEEL`` entry name from a wheel archive."""
    wheel_name = next(
        (name for name in entry_names if name.endswith(".dist-info/WHEEL")),
        None,
    )
    if wheel_name is None:
        message = "wheel is missing .dist-info/WHEEL metadata"
        raise WheelMetadataError(message)
    return wheel_name


def _parse_wheel_header(
    wheel_payload: str,
    whl_path: pathlib.Path,
) -> tuple[str, str]:
    """Extract the maturin generator string and ``Root-Is-Purelib`` value."""
    generator_match = _GENERATOR_RE.search(wheel_payload)
    if generator_match is None:
        message = f"Could not parse maturin generator from WHEEL metadata: {whl_path}"
        raise WheelMetadataError(message)
    root_is_purelib = next(
        (
            line.removeprefix("Root-Is-Purelib: ")
            for line in wheel_payload.splitlines()
            if line.startswith("Root-Is-Purelib:")
        ),
        None,
    )
    if root_is_purelib is None:
        message = "wheel is missing Root-Is-Purelib metadata"
        raise WheelMetadataError(message)
    return generator_match.group(1), root_is_purelib


def wheel_build_summary(whl_path: pathlib.Path) -> dict[str, typ.Any]:
    """Return normalised wheel metadata and layout."""
    try:
        with zipfile.ZipFile(whl_path) as archive:
            entry_names = archive.namelist()
            wheel_name = _locate_dist_info_wheel(entry_names)
            metadata_name = wheel_name.replace("/WHEEL", "/METADATA")
            wheel_payload = archive.read(wheel_name).decode("utf-8")
            metadata_payload = archive.read(metadata_name).decode("utf-8")
    except (KeyError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
        message = f"Could not read required wheel metadata from {whl_path}"
        raise WheelMetadataError(message) from exc
    generator, root_is_purelib = _parse_wheel_header(wheel_payload, whl_path)
    return {
        "generator": generator,
        "metadata": _parse_metadata(metadata_payload),
        "wheel": {
            "root_is_purelib": root_is_purelib,
        },
        "entries": sorted(_normalise_wheel_entry(name) for name in entry_names),
    }

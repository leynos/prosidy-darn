MDLINT ?= markdownlint-cli2
NIXIE ?= nixie
MDFORMAT_ALL ?= mdformat-all
CARGO ?= cargo
WHITAKER ?= whitaker
RUFF_VERSION ?= 0.15.12
RUFF = $(UV_ENV) uv tool run --from ruff==$(RUFF_VERSION) ruff
TOOLS = $(MDFORMAT_ALL) ty $(MDLINT) uv
VENV_TOOLS = pytest
UV_ENV = UV_CACHE_DIR=.uv-cache UV_TOOL_DIR=.uv-tools
PYLINT_PYTHON ?= pypy
PYLINT_PACKAGE_TARGETS ?= prosidy_darn
PYLINT_TEST_TARGETS ?= tests
# Add future Python tooling or script paths here so the PyPy-backed Pylint tier
# expands with the repository instead of silently checking only package code.
PYLINT_EXTRA_TARGETS ?=
PYLINT_TARGETS ?= $(PYLINT_PACKAGE_TARGETS) $(PYLINT_TEST_TARGETS) $(PYLINT_EXTRA_TARGETS)
PYLINT_PYPY_SHIM_REF ?= 726d09f968b4d729ee4b29c71fc732e744854f3b
PYLINT_PYPY_SHIM = git+https://github.com/leynos/pylint-pypy-shim.git@$(PYLINT_PYPY_SHIM_REF)
PYLINT = $(UV_ENV) uv tool run --python $(PYLINT_PYTHON) --from '$(PYLINT_PYPY_SHIM)' pylint-pypy

.PHONY: help all clean build build-release lint lint-rust fmt check-fmt \
        markdownlint nixie test typecheck $(TOOLS) $(VENV_TOOLS)

.DEFAULT_GOAL := all

all: build check-fmt lint typecheck test

.venv: pyproject.toml
	$(UV_ENV) uv venv --clear

build: uv .venv ## Build virtual-env and install deps
	$(UV_ENV) uv sync --group dev

build-release: build ## Build artefacts (sdist & wheel)
	$(UV_ENV) uv run maturin build --release --sdist --out dist \
	  --manifest-path rust/prosidy-darn-rs/Cargo.toml

clean: ## Remove build artifacts
	rm -rf build dist *.egg-info \
	  .mypy_cache .pytest_cache .coverage coverage.* \
	  lcov.info htmlcov .venv
	find . -type d -name '__pycache__' -print0 | xargs -0 -r rm -rf

define ensure_tool
	@command -v $(1) >/dev/null 2>&1 || { \
	  printf "Error: '%s' is required, but not installed\n" "$(1)" >&2; \
	  exit 1; \
	}
endef

define ensure_tool_venv
	@$(UV_ENV) uv run which $(1) >/dev/null 2>&1 || { \
	  printf "Error: '%s' is required in the virtualenv, but is not installed\n" "$(1)" >&2; \
	  exit 1; \
	}
endef

ifneq ($(strip $(TOOLS)),)
$(TOOLS): ## Verify required CLI tools
	$(call ensure_tool,$@)
endif


ifneq ($(strip $(VENV_TOOLS)),)
.PHONY: $(VENV_TOOLS)
$(VENV_TOOLS): ## Verify required CLI tools in venv
	$(call ensure_tool_venv,$@)
endif

fmt: uv $(MDFORMAT_ALL) ## Format sources
	$(RUFF) format
	$(RUFF) check --select I --fix
	$(MDFORMAT_ALL)

check-fmt: uv ## Verify formatting
	$(RUFF) format --check
	# mdformat-all doesn't currently do checking

lint: uv ## Run linters
	$(RUFF) check
	$(PYLINT) $(PYLINT_TARGETS)

lint-rust: ## Lint the Rust workspace (Clippy and Whitaker)
	$(CARGO) clippy --manifest-path rust/Cargo.toml --all-targets --all-features -- -D warnings
	cd rust && RUSTFLAGS="-D warnings" $(WHITAKER) --all -- --all-targets --all-features

typecheck: build ty ## Run typechecking
	ty --version
	ty check

markdownlint: $(MDLINT) ## Lint Markdown files
	$(MDLINT) '**/*.md'

nixie: ## Validate Mermaid diagrams
	$(call ensure_tool,nixie)
	$(NIXIE) --no-sandbox

test: build uv $(VENV_TOOLS) ## Run tests
	$(UV_ENV) uv run pytest -v -n auto

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS=":"; printf "Available targets:\n"} {printf "  %-20s %s\n", $$1, $$2}'

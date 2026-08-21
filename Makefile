MDLINT ?= markdownlint-cli2
# `make fmt` and `make check-fmt` call mdtablefix directly. `--git` selects the
# Markdown files Git tracks and `--include-untracked` adds the untracked files
# Git does not ignore, so a new document is formatted before it is staged.
# Both modes need mdtablefix 0.6.0 or later; CI pins the version at the
# install-mdtablefix step.
MDTABLEFIX ?= mdtablefix
MDTABLEFIX_SELECT = --git --include-untracked
MDTABLEFIX_RULES = --wrap --renumber --breaks --ellipsis --fences
NIXIE ?= nixie
CARGO ?= cargo
WHITAKER ?= whitaker
UV ?= uv
RUFF_VERSION ?= 0.15.12
TYPOS_CONFIG_BUILDER_VERSION ?= v0.1.3
TYPOS_CONFIG_BUILDER = $(UV_ENV) $(UV) tool run --python 3.14 --from \
	"git+https://github.com/leynos/typos-config-builder.git@$(TYPOS_CONFIG_BUILDER_VERSION)" \
	typos-config-builder
RUFF = $(UV_ENV) uv tool run --from ruff==$(RUFF_VERSION) ruff
TOOLS = ty $(MDLINT) uv
VENV_TOOLS = pytest
UV_ENV = UV_CACHE_DIR=.uv-cache UV_TOOL_DIR=.uv-tools
PYLINT_PYTHON ?= pypy@3.12
PYLINT_VERSION ?= 4.0.9
PYLINT_PACKAGE_TARGETS ?= prosidy_darn
PYLINT_TEST_TARGETS ?= tests
# Add future Python tooling or script paths here so the PyPy-backed Pylint tier
# expands with the repository instead of silently checking only package code.
PYLINT_EXTRA_TARGETS ?=
PYLINT_TARGETS ?= $(PYLINT_PACKAGE_TARGETS) $(PYLINT_TEST_TARGETS) $(PYLINT_EXTRA_TARGETS)
PYLINT = $(UV_ENV) uv tool run --managed-python --python $(PYLINT_PYTHON) --from 'pylint==$(PYLINT_VERSION)' pylint
SKYLOS_VERSION ?= 4.33.2
SKYLOS = $(UV_ENV) $(UV) tool run --from 'skylos==$(SKYLOS_VERSION)' skylos \
	--config-file pyproject.toml
SKYLOS_PRODUCTION_TARGETS ?= prosidy_darn

.PHONY: help all clean build build-release lint lint-rust fmt check-fmt \
        markdownlint nixie spelling skylos-allow test typecheck \
        $(TOOLS) $(VENV_TOOLS)

.DEFAULT_GOAL := all

all: build check-fmt lint typecheck test spelling

.venv: pyproject.toml
	$(UV_ENV) uv venv --clear

build: uv .venv ## Build virtual-env and install deps
	$(UV_ENV) uv sync --group dev

build-release: build ## Build artefacts (sdist & wheel)
	$(UV_ENV) uv run maturin build --release --sdist --out dist \
	  --manifest-path rust/prosidy-darn-rs/Cargo.toml

clean: ## Remove build artefacts
	rm -rf build dist *.egg-info \
	  .mypy_cache .pytest_cache .coverage coverage.* \
	  lcov.info htmlcov .venv .uv-cache .uv-tools
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

fmt: uv ## Format sources
	$(RUFF) format
	$(RUFF) check --select I --fix
	$(MDTABLEFIX) --in-place $(MDTABLEFIX_SELECT) $(MDTABLEFIX_RULES)
	@unset FORCE_COLOR; $(MDLINT) --fix "**/*.md"

check-fmt: uv ## Verify formatting
	$(RUFF) format --check
	$(MDTABLEFIX) --check $(MDTABLEFIX_SELECT) $(MDTABLEFIX_RULES)

lint: uv ## Run linters
	$(RUFF) check
	$(PYLINT) $(PYLINT_TARGETS)
	$(SKYLOS) $(SKYLOS_PRODUCTION_TARGETS) --category dead_code --gate \
		--format concise --no-upload --no-provenance --no-grep-verify

skylos-allow: export SKYLOS_NAME = $(value NAME)
skylos-allow: export SKYLOS_REASON = $(value REASON)
skylos-allow: ## Document one named Skylos exception, not an entry point
	@test -n "$${SKYLOS_NAME}" || { \
		printf "Error: NAME is required for a named whitelist exception\\n" >&2; \
		exit 2; \
	}
	@test -n "$${SKYLOS_REASON}" || { \
		printf "Error: REASON is required for a named whitelist exception\\n" >&2; \
		exit 2; \
	}
	$(SKYLOS) whitelist "$${SKYLOS_NAME}" --reason "$${SKYLOS_REASON}"

lint-rust: ## Lint the Rust workspace (Clippy and Whitaker)
	$(CARGO) clippy --manifest-path rust/Cargo.toml --all-targets --all-features -- -D warnings
	cd rust && RUSTFLAGS="-D warnings" $(WHITAKER) --all -- --all-targets --all-features

typecheck: build ty ## Run typechecking
	ty --version
	ty check

markdownlint: spelling $(MDLINT) ## Lint Markdown files and enforce spelling
	$(MDLINT) '**/*.md'

spelling: ## Enforce en-GB-oxendict spelling and shared phrase corrections
	$(TYPOS_CONFIG_BUILDER) gate --repository .





nixie: ## Validate Mermaid diagrams
	$(call ensure_tool,nixie)
	$(NIXIE) --no-sandbox

test: build uv $(VENV_TOOLS) ## Run tests
	$(UV_ENV) uv run pytest -v -n auto

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS=":"; printf "Available targets:\n"} {printf "  %-20s %s\n", $$1, $$2}'

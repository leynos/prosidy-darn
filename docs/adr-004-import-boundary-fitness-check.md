# Architectural decision record (ADR) 004: Import-boundary fitness check

## Status

Accepted on 2026-06-14. hecate is the v1 import-boundary fitness function, and
import-linter is the vetted fallback behind a stable `check-imports` seam. The
checker is run out-of-process through `uv tool run` so its own dependencies
never enter the project virtual environment.

## Date

2026-06-14.

## Context and problem statement

The technical design requires `prosidy_darn.domain` and
`prosidy_darn.application` to stay independent of adapters, Cyclopts, parser
packages, filesystem delivery, HTTP clients, and vendor integrations (technical
design §§4, 9, and 16). The repository needs a local and continuous-integration
(CI) fitness check before non-trivial adapters land, because the hexagonal
dependency rule is cheap to enforce before adapters exist and expensive to
retrofit afterwards.

A "fitness function", in the sense of Ford, Parsons, and Kua's _Building
Evolutionary Architectures_, is an automated check that holds an architectural
characteristic true as the system evolves. For Prosidy Darn the characteristic
is the hexagonal dependency rule: all source dependencies point inward, so the
pure domain and the application layer never name an adapter, a framework, or a
vendor library.

This ADR closes the open decision recorded in technical design §18 and selects
the v1 enforcement tool. It does not create the real package layout (roadmap
task 1.2.1), add runtime dependencies (1.2.2), or wire the check into a
Makefile gate over real source (1.2.3).

## Decision drivers

- Enforce the hexagonal dependency rule automatically and directionally, so the
  domain may import ports but not the reverse-facing adapters.
- Produce actionable, machine-readable diagnostics for boundary violations.
- Keep the check lightweight and reproducible for local gates.
- Avoid importing optional adapter dependencies merely to inspect imports, and
  avoid pulling the checker's own framework dependency into the project virtual
  environment.
- Express a composition-root exception so `config` may wire adapters while the
  domain may not.

## Options considered

### Option A: hecate

`leynos/hecate` is a df12 house tool purpose-built for the hexagonal-group
model. It parses package roots with the standard-library `ast` module,
classifies each import into ordered `[tool.hecate]` groups (`name`, `prefixes`,
`allowed`), supports `include_external_packages` to classify external prefixes
such as `cyclopts`, supports `ignore_imports` for documented composition-root
exceptions, expands `__init__.py` re-exports, emits `text` or `json` through
`--format`, runs natively on Python 3.14, and aligns with the existing pinned
git-reference tooling pattern (ADR-008).

### Option B: import-linter

`import-linter` 2.11 is a Production/Stable, BSD-2-licensed PyPI package that
supports Python 3.14. Its `forbidden` contract with
`include_external_packages = True` expresses the directional rule, and its
companion `grimp` builds the transitive import graph. Its CLI is
`lint-imports`; it exits non-zero on a broken contract but has no documented
machine-readable output format.

### Option C: tach

`tach` enforces first-party module boundaries via `tach.toml` and can check
external dependencies, but its model is module-graph-centric rather than the
hexagonal-group model, so it fits the layering less directly.

### Option D: PyTestArch or a custom `ast` walker

Both are viable but require bespoke maintenance and re-implement what hecate
already provides for df12 projects.

### Option E: Ruff `flake8-tidy-imports` `banned-api`

TID251 is a global ban table with no per-source-module direction, so it cannot
express "config may import adapters but domain may not" without brittle
per-directory carve-outs. It is disqualified for the directional rule.

| Topic                       | hecate            | import-linter | tach        | PyTestArch / custom | Ruff banned-api |
| --------------------------- | ----------------- | ------------- | ----------- | ------------------- | --------------- |
| Directional first-party ban | Yes               | Yes           | Yes         | Yes                 | No              |
| External package ban        | Yes               | Yes           | Partial     | Manual              | Yes             |
| Composition-root exception  | `ignore_imports`  | Per contract  | Manual      | Manual              | Carve-outs      |
| Machine-readable output     | JSON              | None          | JSON        | Manual              | Text            |
| Python 3.14 support         | Required          | Yes           | Yes         | Yes                 | Yes             |
| Barrel re-export handling   | Yes               | Via grimp     | Partial     | Manual              | No              |
| Supply-chain cost           | Single maintainer | PyPI vetted   | PyPI vetted | In-repo             | Already present |

_Table 1: Import-boundary checker options against the project's concrete
requirements._

## Decision outcome / proposed direction

Choose hecate. hecate is the v1 import-boundary fitness function. It is the
df12 house tool that models the hexagonal-group rule directly, expresses the
composition-root exception, expands barrels, emits JSON, and runs on Python
3.14.

hecate is pinned by a full 40-character commit SHA and run out-of-process
through `uv tool run`, with `--python 3.14` pinning the interpreter, mirroring
the `pylint-pypy-shim` precedent in ADR-008. Running it out-of-process keeps
its Cyclopts dependency out of the project virtual environment, which is the
very boundary this decision enforces.

hecate is never added to `pyproject.toml` and is never referenced by bare name,
because the PyPI `hecate` is an unrelated project (an ncurses CLI tester). A
bare `uv add hecate`, `pip install hecate`, or requirements entry would install
the wrong project; only the pinned
`git+https://github.com/leynos/hecate.git@<sha>` specifier is correct.

import-linter is the vetted fallback behind a stable `check-imports` seam. If
hecate must be replaced, the seam name `make check-imports` and the `HECATE_REF`
/`HECATE_SPEC`/`HECATE` Makefile surface let the underlying tool be swapped
without a documentation rewrite, using an import-linter `forbidden` contract
over the same source and forbidden modules.

hecate exits 0 when the check passes, 1 when it finds violations, and 2 on a
configuration or input error. This exit-code contract is distinct from the
application CLI's own taxonomy; the demonstration test treats exit 2 as a
harness failure rather than a boundary violation.

## Production configuration

The production policy models five groups: `domain`, `ports`, `application`,
`adapters`, and `config`, ordered so specific prefixes precede general ones.
`domain`, `application`, and `ports` must not import adapters, Cyclopts, Rich,
the Markdown parser package, renderer infrastructure, or delivery code, while
`config` may import them as the composition root, and the relevant adapter
groups may import the external frameworks they own.

External frameworks are banned from the inward layers by their absence from
those groups' `allowed` lists, not by an explicit deny rule. Each external
group's prefix is the top-level import name, which must be verified against the
installed package when task 1.2.3 wires the gate, because the import name can
differ from the PyPI distribution name.

The configuration that task 1.2.3 commits against the real tree is:

```toml
[tool.hecate]
root_packages = ["prosidy_darn"]
include_external_packages = true

# Order matters: specific prefixes before general ones.
[[tool.hecate.groups]]
name = "domain"
prefixes = ["prosidy_darn.domain"]
allowed = ["domain", "ports"]

[[tool.hecate.groups]]
name = "ports"
prefixes = ["prosidy_darn.ports"]
allowed = ["ports", "domain"]

[[tool.hecate.groups]]
name = "application"
prefixes = ["prosidy_darn.application"]
allowed = ["application", "domain", "ports"]

[[tool.hecate.groups]]
name = "adapters"
prefixes = ["prosidy_darn.adapters"]
allowed = ["adapters", "application", "ports", "domain", "cyclopts", "rich", "markdown_parser", "delivery"]

[[tool.hecate.groups]]
name = "config"
prefixes = ["prosidy_darn.config"]
allowed = ["config", "adapters", "application", "ports", "domain", "cyclopts", "rich", "markdown_parser", "delivery"]

# External frameworks and infrastructure, banned from domain/application/ports
# by their absence from those groups' allowed lists. Each external group's
# prefix is the top-level IMPORT name, verified against the installed package
# during implementation. Every group named in an "allowed" list above is defined
# below, so the policy is self-consistent.
[[tool.hecate.groups]]
name = "cyclopts"
prefixes = ["cyclopts"]
allowed = ["cyclopts"]

[[tool.hecate.groups]]
name = "rich"
prefixes = ["rich"]
allowed = ["rich"]

[[tool.hecate.groups]]
name = "markdown_parser"
prefixes = ["mdast"]
allowed = ["markdown_parser"]

# Illustrative HTTP/webhook client for delivery sinks; confirm the actual import
# name when task 4.3.3 selects the delivery library.
[[tool.hecate.groups]]
name = "delivery"
prefixes = ["httpx"]
allowed = ["delivery"]
```

## Goals and non-goals

- Goals:
  - select one v1 import-boundary fitness function and name a reversible
    fallback;
  - prove the success criterion with a durable, re-runnable fixture
    demonstration;
  - document the production five-group configuration and the pin-update
    discipline.
- Non-goals:
  - create the real `prosidy_darn` domain, application, ports, adapters, or
    config packages (task 1.2.1);
  - add Cyclopts, Rich, or the checker to `pyproject.toml` (task 1.2.2);
  - wire the check into `make lint`, `make all`, or any gate over real source
    (task 1.2.3).

## Migration plan

1. Pin hecate in the Makefile through `HECATE_REF`, `HECATE_SPEC`, and `HECATE`,
   and export `HECATE_REF` to the `test` target so the fixture test can run the
   checker out-of-process.
2. Prove the criterion with a self-contained architecture fixture and a
   subprocess pytest test that asserts exit 0 on a clean tree and exit 1 on a
   tree with forbidden domain-to-adapter and domain-to-external edges.
3. When task 1.2.1 creates the real packages, commit the production
   `[tool.hecate]` configuration above and verify each external import name.
4. When task 1.2.3 wires the gate, expose it as `make check-imports`; keep it a
   distinct third gate, separate from the two lint tiers, because the Pylint
   tier runs under managed PyPy (ADR-008) and cannot run hecate.
5. If hecate must be replaced, swap import-linter behind the same
   `check-imports` seam without rewriting this ADR.

## Known risks and limitations

- Single-maintainer, off-PyPI supply chain. hecate is a df12-internal tool
  pinned by git SHA. Mitigation: pin a full SHA, name import-linter as the
  capability-equivalent fallback, and note that hecate is small stdlib-`ast`
  code that is cheap to fork or vendor.
- PyPI name collision. A future bare-name install would fetch an unrelated
  package. Mitigation: the bare-name prohibition is stated here, in the
  Makefile comment, and in the developers' guide.
- Static-analysis blind spot. hecate, like every static checker, cannot see
  dynamic imports (`importlib.import_module`, `__import__`). Mitigation: keep
  dynamic imports in `config` or `_runtime` and rely on code review.
- Interpreter isolation. hecate requires Python 3.14 and imports Cyclopts, so it
  must run as an isolated `uv tool run --python 3.14` subprocess and must not
  be folded into `make lint`.
- `TYPE_CHECKING`-only imports. Whether type-only imports of adapters from the
  domain are permitted is determined against the fixture during implementation;
  the strict default is to forbid them.
- Fixture proves capability, not production-config correctness. Because the real
  packages do not exist until task 1.2.1, a green fixture demonstrates the tool
  works but says nothing about whether the production groups are right; that
  proof is task 1.2.3's success criterion.

## Architectural rationale

The decision keeps the dependency rule machine-checkable before adapters land.
Modelling five groups grants `domain` and `application` an inward edge to
`ports` without leaving `ports` unclassified, and placing external prefixes in
the `allowed` lists of `config` and the specific adapter groups expresses the
composition-root exception precisely. Asserting on hecate's JSON output rather
than its human-readable text keeps the demonstration robust against wording and
path-rendering changes.

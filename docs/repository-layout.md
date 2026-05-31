# Repository layout

This document explains the responsibilities of the main repository paths. It is
an orientation aid for contributors; it is not a complete file manifest.

## Tree

```plaintext
.
├── .github/                 # GitHub Actions workflows and reusable actions
├── .rules/                  # Python style, typing, and language-specific rules
├── docs/                    # User, maintainer, design, and planning documents
│   └── execplans/           # Task-specific execution plans
├── prosidy_darn/            # Runtime package source code
├── tests/                   # Unit, behavioural, and integration tests
├── AGENTS.md                # Repository instructions for coding agents
├── Makefile                 # Canonical build, lint, test, and documentation gates
├── pyproject.toml           # Python packaging and tool configuration
├── README.md                # Project overview for repository visitors
└── uv.lock                  # Locked Python dependency resolution
```

_Figure 1: Simplified repository tree for contributor orientation._

## Path responsibilities

| Path              | Responsibility                                                                                                                                                    |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.github/`        | Holds continuous integration workflows and reusable GitHub automation. Keep repository automation here rather than scattering scripts through source directories. |
| `.rules/`         | Records detailed Python development rules that complement `AGENTS.md`. Update these when language-specific policy changes.                                        |
| `docs/`           | Contains long-lived documentation, including guides, design material, architectural decision records, and roadmap documents. Use `docs/contents.md` as the index. |
| `docs/execplans/` | Stores task-specific execution plans. These are living implementation records, not general reference documents.                                                   |
| `prosidy_darn/`   | Contains the application package. Keep production code grouped by feature and maintain clear module boundaries.                                                   |
| `tests/`          | Contains the test suite. Place unit, behavioural, and integration coverage close to the behaviour it validates.                                                   |
| `AGENTS.md`       | Defines repository-local instructions for automated coding agents. Keep this synchronized with the current agent template when template policy changes.           |
| `Makefile`        | Provides the canonical command surface for build, lint, format, typecheck, test, and documentation validation. Prefer these targets over direct tool invocation.  |
| `pyproject.toml`  | Defines package metadata, Python version requirements, dependency groups, and tool configuration.                                                                 |
| `README.md`       | Introduces the project for readers who start at the repository root. Keep detailed usage in `docs/users-guide.md`.                                                |
| `uv.lock`         | Pins dependency resolution for reproducible development environments. Regenerate it through the project dependency workflow rather than editing it manually.      |

_Table 1: Repository paths and their responsibilities._

## Documentation conventions

Use [documentation contents](contents.md) to place new or renamed documents in
context. Add user-facing behaviour to [users' guide](users-guide.md),
maintainer workflows to [developers' guide](developers-guide.md), and design
rationale to [Prosidy Darn technical design](prosidy-darn-technical-design.md)
or a focused architectural decision record.

## Generated and transient files

Do not commit local virtual environments, tool caches, test caches, build
artefacts, or temporary logs. Use `/tmp` for scratch command output, and keep
repository files focused on source, tests, configuration, and long-lived
reference material.

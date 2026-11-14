# Assistant instructions

## Code style and structure

- **Code is for humans.** Write code with clarity and empathy—assume a
  tired teammate will need to debug it at 3 a.m.
- **Comment *why*, not *what*.** Explain assumptions, edge cases, trade-offs, or
  complexity. Don't echo the obvious.
- **Clarity over cleverness.** Be concise, but favour explicit over terse or
  obscure idioms. Prefer code that's easy to follow.
- **Use functions and composition.** Avoid repetition by extracting reusable
  logic. Prefer generators or comprehensions, and declarative code to
  imperative repetition when readable.
- **Small, meaningful functions.** Functions must be small, clear in purpose,
  single responsibility, and obey command/query segregation.
- **Clear commit messages.** Commit messages should be descriptive, explaining
  what was changed and why.
- **Name things precisely.** Use clear, descriptive variable and function names.
  For booleans, prefer names with `is`, `has`, or `should`.
- **Structure logically.** Each file should encapsulate a coherent module. Group
  related code (e.g., models + utilities + fixtures) close together.
- **Group by feature, not layer.** Colocate views, logic, fixtures, and helpers
  related to a domain concept rather than splitting by type.
- **Use clear file boundaries.** Each module, component, and package should have
  an obvious responsibility and avoid accidental coupling.
- **Use consistent spelling and grammar.** Comments must use en-GB-oxendict
  ("-ize" / "-yse" / "-our") spelling and grammar, with the exception of
  references to external APIs. See [Spelling](#spelling).
- **Illustrate with clear examples.** Function documentation must include clear
  examples demonstrating the usage and outcome of the function. Test
  documentation should omit examples where the example serves only to reiterate
  the test logic.
- **Keep file size manageable.** No single code file may be longer than 400
  lines.  Long switch statements or dispatch tables should be broken up by
  feature and constituents colocated with targets. Large blocks of test data
  should be moved to external data files.

## Documentation maintenance

- **Reference:** Use the markdown files within the `docs/` directory as a
  knowledge base and source of truth for project requirements, dependency
  choices, and architectural decisions. Start with
  [documentation contents](docs/contents.md) and
  [repository layout](docs/repository-layout.md) when orienting within the
  project.
- **Update:** When new decisions are made, requirements change, libraries are
  added/removed, or architectural patterns evolve, **proactively update** the
  relevant file(s) in the `docs/` directory to reflect the latest state. Ensure
  the documentation remains accurate and current.
- **Design decisions:** Record design decisions in the relevant design
  document. When a decision is substantive, capture it in an Architectural
  Decision Record (ADR) following the documentation style guide, and reference
  that ADR from the design document.
- **User-facing behaviour:** Update [users' guide](docs/users-guide.md) for
  behaviour or user-interface changes that users should know about. Add
  migration guidance for compatibility or usage changes, and keep maintained
  translations synchronized.
- **Internal interfaces:** Document internally facing interfaces in the
  relevant component architecture document. Document internally facing
  conventions and practices in [developers' guide](docs/developers-guide.md).
- **Build tooling:** When changing build tooling, document the effective
  toolchain, inherited flags, backend and linker selection, and deliberate
  differences between validation commands.
- **Style:** All documentation must adhere to the
  [documentation style guide](docs/documentation-style-guide.md).
- **Accuracy:** Verify changed examples, commands, imports, links, paths, and
  stated guarantees against the implementation. Update maintained copies and
  indexes when names or locations change. Keep transient validation results in
  the PR or execution record.
- **Decision history:** Preserve accepted ADR decisions; record subsequent
  changes through the
  [ADR process](docs/documentation-style-guide.md#architectural-decision-records-adrs).
  Capture proof-driven API, representation, and invariant decisions in the
  design documentation.
- **Completed execplans:** Completed execplans are historical documents and
  should reflect the state of the repository at time of implementation. Do not
  retroactively update completed execplan documents to reflect subsequent
  changes in API, structures, or behaviour.

## Planning and verification

- For non-trivial work, prepare or update a self-contained ExecPlan using the
  available planning guidance. Identify the outcome, relevant roadmap and
  design references, prerequisites, scope exclusions, and observable acceptance
  criteria. Signpost relevant documentation and skills.
- Identify affected behavioural contracts, invariants, and failure modes before
  choosing the implementation. Use these to pressure-test the proposed API and
  verification strategy.
- Plan the smallest useful increment. Preserve decision gates and stopping
  conditions; defer abstractions, dependencies, macros, or published components
  until the preceding evidence justifies them.
- Where formal verification is selected, first sketch the independent model,
  premises, invariants, representation relationships, and principal proof
  obligations. Treat proposed lemmas as provisional. Defer detailed proof
  engineering until implementation exposes the verification conditions; do not
  add assumptions, admissions, or trusted proof bodies merely to make
  incomplete proofs pass. Unproved statements may remain in the plan until that
  milestone.
- Give each major milestone explicit acceptance commands, including applicable
  proof checks and the formatting, linting, and test gates. Keep commits
  coherent and useful as rollback points.
- When plan approval is required, deliver the plan for review and wait for
  approval before implementation. Keep the active plan current, and mark
  relevant roadmap entries complete only after their acceptance criteria pass.

## Change quality and committing

- **Atomicity:** Aim for small, focused, atomic changes. Each change (and
  subsequent commit) should represent a single logical unit of work.
- **Quality gates:** Before considering a change complete or proposing a
  commit, ensure all of the following are met:
  - New functionality or behaviour changes are fully validated by relevant unit
    and behavioural tests.
  - Bug fixes include a failing test before the fix and a passing test
    afterwards.
  - Code passes lint checks.
  - Formatting is correct and validated.
- **For Python files:**
  - **Testing:** Passes all relevant unit and behavioural tests (`make test`).
  - **Linting:** Passes Ruff, PyPy-backed Pylint, and the blocking Skylos
    dead-code scan (`make lint`). Investigate every Skylos finding and remove
    genuine dead code. Prefer a typed `[tool.skylos.dead_code.entrypoints]`
    rule for an implicit runtime caller. Only when that rule cannot model the
    boundary, record a verified false positive and caller in the Skylos allow
    list with `make skylos-allow SYMBOL=handler REASON="Loaded by plugin
    registry"`. The helper rejects missing and whitespace-only values for both
    `SYMBOL` and `REASON`, and serializes documented allow-list writes with
    `flock` on a repository-local lock file.
  - **Formatting:** Adheres to formatting standards (`make check-fmt`; use
    `make fmt` to apply fixes).
  - **Typechecking:** Passes type checking (`make typecheck`).
- **For Rust files (the extension crate under `rust/`):**
  - **Linting:** Passes Clippy (`make lint-clippy`, also run by `make lint`) and
    the Whitaker Dylint suite (`make lint-rust`, which CI runs). See
    [Rust specific guidance](#rust-specific-guidance).
- **For Markdown files (`.md` only):**
  - **Linting:** Passes markdown lint checks (`make markdownlint`).
  - **Spelling:** Passes `make spelling`, which runs as part of
    `make markdownlint`; see [Spelling](#spelling).
  - **Mermaid diagrams:** Passes validation using nixie (`make nixie`).
- **Before review:** Inspect the complete diff, including tests, fixtures,
  scripts, examples, and documentation. Check file-size limits, module
  documentation, doc-comment placement, assertion diagnostics, duplicated test
  setup, and applicable spelling and formatting gates. Link relevant roadmap
  entries, issues, and the ExecPlan in the PR description.
- **Committing:**
  - Only changes that meet all quality gates should be committed.
  - Write clear, descriptive commit messages that summarize the change,
    following:
    - **Imperative mood** in the subject line (for example, "Fix bug", "Add feature").
    - **Subject line length:** around 50 characters or fewer.
    - **Body:** Separate subject from body with a blank line. Explain *what* and
      *why* in wrapped lines (approximately 72 columns).
    - **Formatting:** Use Markdown for formatted text inside the message body.
  - Do not commit changes that fail any quality gate.

## Refactoring heuristics and workflow

- **Recognizing refactoring needs:** regularly assess the codebase for potential
  refactoring opportunities. Consider refactoring when you observe:
  - **Long methods/functions:** functions that are excessively long or try to do
    too many things.
  - **Duplicated code:** identical or very similar code blocks appearing in
    multiple places.
  - **Complex conditionals:** deeply nested or overly complex `if`/`else` or
    `switch` statements.
  - **Large code blocks for single values:** significant logic blocks dedicated
    to calculating or deriving one value.
  - **Primitive obsession / data clumps:** groups of simple variables that are
    frequently passed together, which may indicate a missing abstraction.
  - **Excessive parameters:** functions or methods requiring too many
    parameters.
  - **Feature envy:** methods that focus more on other data than their own.
  - **Shotgun surgery:** one change that forces many files to be edited.
- **Abstraction / port / helper policy:** before adding a new abstraction, port,
  or helper:
  - Sweep the repository and approved dependencies for equivalent behaviour.
    Reuse it unless demonstrably unsuitable. New abstractions must simplify the
    current change or have a concrete reuse case.
  - Document the new abstraction's intended scope and re-use policy.
  - Record the decision in architecture, design, or developers-guide docs using
    `docs/contents.md` as the index.
- **Post-commit review:** after functional changes or bug fixes that meet
  quality gates, review changed code and adjacent areas using these heuristics.
- **Separate atomic refactors:** if refactoring is required, implement it in a
  separate atomic commit after the functional change and ensure it passes all
  relevant gates.

## Architecture and operational boundaries

- Keep domain policy separate from filesystem, process, network, framework,
  and telemetry adapters. Inject dependencies where needed through existing
  interfaces or narrow closures; avoid speculative layers and dependency cycles.
- Make fallibility, mutation, and side-effects explicit in APIs. Preserve I/O,
  parsing, and permission errors rather than silently converting them into
  absence, `false`, or empty success. Compose side-effects at orchestration
  boundaries; queries must not hide writes or unrelated workflow policy.
- For streams, subprocesses, retries, caches, queues, and background tasks,
  define applicable size limits, deadlines, ownership, cancellation, and
  cleanup. A timeout does not bound accumulated bytes. Include waiting and
  cleanup in the operation's budget. Define partial-failure and retry behaviour
  where updates span multiple effects; keep locks narrow and ordered, avoiding
  holds across awaits or external calls unless explicitly justified.
- Validate untrusted inputs before privileged effects, use structured APIs
  instead of executable string construction, and grant only required
  permissions.
- When performance materially motivates a change, measure realistic inputs and
  distinguish build, execution, queueing, and cache state. Avoid repeated I/O
  or unnecessary allocation in per-item loops and blocking work on async
  executors.

## Python verification and testing

- For Python work, use `pytest` for unit tests and `pytest-bdd` for behavioural
  tests. Cover happy paths, unhappy paths, and relevant edge cases.
- Snapshot tests (using `syrupy`) should be provided where multivariant output
  format consistency is relevant to the requirements.
- Add end-to-end tests where a change affects externally observable workflows,
  integration contracts, persistence, command-line behaviour, network
  boundaries, user interface flows, or other system-level behaviour.
- Use property tests with `hypothesis` or `CrossHair` when a change introduces
  an invariant over a range of inputs, states, orderings, or transitions.
- Run relevant unit, behavioural, property, and end-to-end suites before and
  after each change.
- For each changed behaviour, identify a plausible incorrect implementation
  and ensure the test rejects it. Assert observable results, errors, and
  side-effects; mock calls or configuration text alone do not prove execution.
  Negative tests must establish the precondition that would expose the defect.
- Exercise the boundary that owns the promise: public API, executable, or
  protocol adapter. Private-helper tests complement this coverage. Fakes must
  support relevant failures and verify their propagation through orchestration.
  Test local integration contracts rather than third-party tools themselves.
- Test relevant partial failures, cancellation, shutdown, and cleanup with
  deterministic coordination where practical. Avoid relying solely on sleeps or
  exact deltas from shared global counters. Restore fixture resources even when
  assertions fail, and account for host capabilities and privileges.

## Rust specific guidance

The native extension is written in Rust under `rust/` (the extension crate is
`rust/prosidy-darn-rs`, built with maturin and PyO3). The Rust workspace denies
`missing_docs` and forbids `unsafe_code`. Contributors should follow these
practices when working on it:

- Run `make lint` (which includes `make lint-clippy`) and `make lint-rust`
  before committing Rust changes:
  - `make lint-clippy` executes:

    ```sh
    cargo clippy --manifest-path rust/Cargo.toml --all-targets --all-features -- -D warnings
    ```

    linting every target with all features enabled. Clippy warnings fail the
    command.
  - `make lint-rust` runs `make lint-clippy`, then executes:

    ```sh
    cd rust && RUSTFLAGS="-D warnings" whitaker --all -- --all-targets --all-features
    ```

    so Whitaker findings fail the command. CI runs `make lint-rust`.
- Clippy warnings MUST be disallowed.
- Fix any warnings emitted during tests in the code itself rather than
  silencing them.
- Where a function is too long, extract meaningfully named helper functions
  adhering to separation of concerns and CQRS.
- Where a function has too many parameters, group related parameters in
  meaningfully named structs.
- Keep returned error types semantically focused and small. If a necessary
  payload makes an error variant large, place that payload behind `Box`; use
  `Arc` only when shared ownership or cheap cloning is required.
- Ensure that new Rust behaviour is validated with unit tests using `rstest`
  where applicable. Cover happy paths, unhappy paths, and relevant edge cases,
  and test it through the Python API as well where the extension exposes it.
- Select verification proportionately: named examples or `rstest` tables for
  finite contracts, `proptest` for broad input spaces or operation sequences,
  and `kani` for exhaustive exploration within explicit bounds. Use `verus` for
  selected lemmas or contractual invariants requiring unbounded proof over a
  suitable semantic model. Proofs must establish the property from appropriate
  premises, not restate or assume it. Straightforward integration and
  presentation work must not acquire artificial proof obligations. Keep
  executable integration and behavioural tests alongside proofs.
- Every module **must** begin with a module level (`//!`) comment explaining the
  module's purpose and utility, including test modules and fixture crate roots.
- Document public APIs using Rustdoc comments (`///`) so documentation can be
  generated with cargo doc.
- Prefer immutable data and avoid unnecessary `mut` bindings.
- Clone to express intentional ownership, sharing, or snapshot semantics;
  prefer borrowing or ownership transfer when a new owned value is unnecessary.
- Use explicit version ranges in `Cargo.toml` and keep dependencies up-to-date.
  All crate versions must use SemVer-compatible caret requirements; wildcard
  (`*`) and open-ended inequality (`>=`) requirements are forbidden.
- Place function attributes **after** doc comments.
- Do not use `return` in single-line functions.
- Use predicate functions for conditional criteria with more than two branches.
- Lints must not be silenced except as a **last resort**.
- Use item-scoped `#[expect(lint, reason = "...")]`; blanket allowances and
  artificial references that hide unused code are forbidden. Narrow feature and
  test-support compilation boundaries instead. Delete unused helpers unless
  concrete tracked work justifies a temporary expectation linked to that work.
- Use `concat!()` to combine long string literals rather than escaping newlines
  with a backslash.
- Prefer semantic error enums (via `thiserror`) for any condition the caller
  might inspect or retry. In production code and shared fixtures, avoid
  `.expect()`: return `Result` and use `?` to propagate errors. In tests, prefer
  `.expect(...)` over `.unwrap()`.

## Markdown guidance

- Validate Markdown files using `make markdownlint`.
- Run `make fmt` after any documentation changes to format all Markdown
  files and fix table markup.
- Validate Mermaid diagrams in Markdown files by running `make nixie`.
- Markdown paragraphs and bullet points must be wrapped at 80 columns.
- Code blocks must be wrapped at 120 columns.
- Tables and headings must not be wrapped.
- Use dashes (`-`) for list bullets.
- Use GitHub-flavoured Markdown footnotes (`[^1]`) for references and
  footnotes.
- Avoid first-person prose outside README and BDD feature files; allow
  second-person prose in README, AGENTS, BDD feature files, and agent skill
  directories. These exceptions qualify the documentation style guide.
- Quoted API names and identifiers retain upstream spelling. Mark them as
  code using backticks or fenced blocks rather than adding spelling exceptions.

<!-- typos-config-builder:agents-md:start -->

## Spelling

- `make spelling` runs the pinned `typos-config-builder gate`, which
  regenerates `typos.toml` from the shared en-GB-oxendict dictionary and
  `typos.local.toml`, then checks spelling and the shared phrase corrections.
- `typos.toml` is generated: never edit it by hand. Put narrow
  repository-specific exceptions in `typos.local.toml`, as exact or full-line
  patterns rather than bare accepted words.
- When `make spelling` changes `typos.toml`, commit the regenerated file. If
  the change is unrelated to your work, commit it in a separate base pull
  request and stack your branch on it, so each review diff stays focused.

<!-- typos-config-builder:agents-md:end -->

## Project documentation

Record design decisions in the design document. Where a decision is
substantive, record it in an ADR document following the documentation style
guide, then reference that ADR from the design document.

Update `docs/users-guide.md` for any change to application behaviour or user
interface that users should know about. Document internally facing interfaces
or practices in the relevant component architecture document. Document
internally facing conventions or practices in `docs/developers-guide.md`.

## Python development guidelines

For Python development, refer to the detailed guidelines in the `.rules/`
directory:

- [Python code style guidelines](.rules/python-00.md) - Core Python 3.13 style
  conventions.
- [Python context managers](.rules/python-context-managers.md) - Best practices
  for context managers.
- [Python exceptions and logging][python-exceptions] -
  Raising and handling exceptions and logging.
- [Python generators](.rules/python-generators.md) - Generator and iterator
  patterns.
- [Python project configuration](.rules/python-pyproject.md) -
  `pyproject.toml` and packaging.
- [Python return patterns](.rules/python-return.md) - Function return
  conventions.
- [Python typing](.rules/python-typing.md) - Type annotation best practices.

[python-exceptions]: .rules/python-exception-design-raising-handling-and-logging.md

Additional docs:

- [Scripting standards](docs/scripting-standards.md) - Guidance for writing
  robust scripts, including secure command execution via `cuprum`, catalogue
  allowlisting, and command mocking patterns with `cmd-mox`.
- Before adding or updating helper scripts, read the scripting standards guide
  and follow its `Cyclopts`, `cuprum`, `pathlib`, and `cmd-mox` conventions.

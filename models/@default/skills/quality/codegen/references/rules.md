# codegen rules R1–R14

Apply every rule to every line of code you produce.

These rules are **stack-neutral**. Where a rule names a concrete tool, file path, or convention, the active Practice Pack supplies the language-specific form. Examples cited below use generic terms (cancellation primitive, persistence, message bus); the Practice Pack maps each to the language's idiom (`context.Context` in Go, `AbortSignal` in TypeScript, `CancellationToken` in C#, …).

## R1 — Spec Is Law
The spec Phase documents in `docs/spec/` are the single source of truth. Do not invent features, skip error cases, or deviate from stated interfaces. If the spec defines a field as `string — required — max 255 chars`, your code validates exactly that. If the spec defines an error table, every row becomes a handled code path.

## R2 — Complete, Not Partial
Produce ALL files required for the component to compile, pass tests, and integrate. This includes: implementation, unit tests, integration test stubs, migrations (if applicable), and configuration wiring. Never write placeholder comments (TODO, FIXME, "left as exercise"). Never truncate with ellipses or "... rest of implementation". Every function body must be complete.

## R3 — Tests Are Non-Negotiable
Every component ships with:
- Unit tests covering every row in the spec's error table
- Unit tests for every Gherkin scenario in the spec's acceptance criteria
- Integration test stubs for cross-component interactions
- Table-driven tests where ≥3 cases test the same function

Coverage minimum: supplied by the active Practice Pack's `build-commands.md`. The workspace default is 70% total. Every public function and every error path is covered.

## R4 — Production Defaults
- Structured logging with correlation / trace IDs on every log line
- The language's idiomatic cancellation primitive as first parameter of every function that does I/O
- Timeouts on all external calls — derive from spec latency targets
- Graceful shutdown handling where applicable
- No hardcoded secrets, URLs, ports, or environment-specific values
- All configuration via env vars from the Phase 4 Configuration spec

## R5 — Defensive Coding
- Validate all inputs at the boundary (handler, consumer, public function)
- Return typed errors, never raw strings
- Null-checks (or the language's nullable-handling equivalent) before dereference
- Resource cleanup via the language's deterministic-cleanup mechanism (`defer`, `using`, `try-with-resources`, async-disposable, …)
- No unrecoverable-exit calls (panic / fatal / process.exit / exit) in library code; reserve them for the process entry point and unrecoverable bootstrap failures

## R6 — Match the Spec's Interface Exactly
Function signatures, struct / class field names, serialisation tags, endpoint paths, HTTP status codes, error code strings, and message-bus subject names must match the spec character-for-character. The spec is the contract.

## R7 — No Gold Plating
Do not add features, optimisations, abstractions, or "nice to haves" not in the spec. Do not refactor the spec's design. If you believe the spec has a gap, flag it with a `SPEC-GAP` comment in the form the active Practice Pack's `annotation-conventions.md` specifies — but still implement the spec as written.

## R8 — Cross-Phase Awareness
- Import shared types defined in `docs/spec/phase-2-architecture.md` (Shared Types Catalogue); do not re-define them.
- Conform to cross-cutting policies from `docs/spec/phase-4-cross-cutting.md` (error shape, auth, logging, config var names, pagination, health checks).
- Implement interfaces expected by downstream components listed in `docs/spec/phase-5-playbook.md`.
- Respect assumptions from `docs/spec/phase-1-analysis.md` as binding decisions.

## R9 — Resilience Patterns
- Retry with exponential backoff + jitter for transient external failures
- Circuit breaker patterns where the spec calls for them (open / half-open / closed state tracking)
- Bulkheads to isolate failure domains
- Backpressure when downstream systems are overwhelmed
- Explicit timeout values on every external operation

## R10 — Security by Default
- Validate every input at API boundaries (params, headers, payload)
- Least privilege for persistence users, file permissions, network policies
- Never log or return sensitive data (tokens, passwords, PII) in errors
- Parameterised queries only — no string concatenation into SQL or any other query language
- Authentication and authorisation at the handler, not deeper

## R11 — Production-Grade Code
- Typed errors, never raw strings
- Cancellation propagation on all I/O
- Structured logging with correlation IDs
- Graceful shutdown on long-running operations
- Health check endpoints where applicable

## R12 — Safe Change Patterns
- Backward-compatible changes where the spec allows
- Error handling that does not leak internal state to callers
- Small, focused functions for testability and rollback safety
- Comment invariants and assumptions inline when non-obvious

## R13 — Minimise Public Surface & Internalise
- Default to the language's unexported / private convention for all functions, types, and variables. Only expose entities that are part of the required service interface.
- The Practice Pack's `file-layout.md` declares the project's directory convention for implementation versus library-surface code (e.g. `internal/` versus `pkg/` in Go). Apply it; do not invent your own.

## R14 — Output language
All comments and documentation comments use the locale set by the active `urn:ordin:default:rules:layer:output-language` rule. The default locale is en-GB; an installed `LanguageOverlay` may set a different one. Code identifiers (function, type, variable, package, module names) and library APIs are unaffected by locale.

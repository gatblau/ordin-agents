# Code-evidence intake

Loaded by `designgen` when the active mode is `code-evidence`. This reference governs how the skill walks an existing codebase to draft an as-built HLD plus a Requirements section, without inventing intent.

The discipline is the same as the rest of CSPA: **observe before infer, infer before plan, never fabricate identifiers**. The novelty here is that the input is a body of code rather than a problem statement, and the output documents *what is*, not *what should be*.

## Scan order

Walk the supplied code paths in this order. Stop at any layer if it provides enough material for the design — do not over-scan.

1. **Module / package graph.** What top-level packages, modules, or services exist? What depends on what? This produces the spine of the Domain Model and the section ordering of the HLD.
2. **Public surfaces.** Delegate to the existing surface-detection rules in `@default/skills/analysis/apidiff/references/surface-detection.md`. Identify exported functions, types, HTTP routes, gRPC services, NATS subjects, CLI commands, env vars. Each becomes a candidate row in the *Interfaces (external)* section of the design.
3. **Data model.** Delegate to `urn:ordin:default:skills:analysis:dbaudit` for SQL schemas (tables, columns, constraints, foreign keys, indexes, views). For non-SQL stores, identify the persistence layer's type definitions and serialised shapes. Each becomes a row in the *Domain Model* section.
4. **Entry points and triggers.** `main()`, HTTP handler registrations, message subscribers, schedulers, CLI command parsers, webhook receivers. Each becomes a row in *Actors and Triggers*.
5. **Flows.** Trace one or two representative request/event paths from entry point to side effect (write, message, response). Each becomes a *Flow* in the design.
6. **Cross-cutting.** Look for middleware, interceptors, decorators, init blocks, and configuration loaders. These reveal the project's actual stance on auth, logging, metrics, tracing, rate limiting, error envelopes, and so on. Each becomes a stance in *Cross-cutting Concerns*.
7. **Deployment topology.** Dockerfiles, Helm charts, compose files, infra-as-code. These inform *Non-functional Requirements* (region count, replica count, resource limits) and *Dependencies*.
8. **Tech-stack signals.** Build files, lockfiles, package manifests, container base images. `go.mod`, `package.json`, `pyproject.toml`, `Cargo.toml`, `requirements.txt`, `Dockerfile` `FROM` lines, observed framework imports. Each becomes a row in the HLD *Tech Stack* table. This layer is high-yield for code-evidence mode — the stack is almost always fully recoverable from these files.
9. **ADR-rationale signals (low-yield).** Look for `docs/adr/`, `decisions/`, `ARCHITECTURE.md`, `DESIGN.md`, prominent PR descriptions, or in-code comments that justify a choice. These are the only acceptable witnesses for ADR entries in the as-built HLD. Choices made without recorded rationale (almost always the majority) land in the *Gaps* section of the Requirements — surfaced as candidate ADRs for the interview to confirm, not invented retroactively.

If a layer is empty or absent, write `N/A — <reason>` in the corresponding design section. Do not invent content to fill it.

## Evidence tagging

Every claim in the design body must carry an evidence tag or be moved to the *Gaps* section.

- **Direct evidence** — the claim is verifiable by reading a single file. Tag inline: `[evidence: cmd/server/main.go:42]`. Use repo-relative paths and line numbers.
- **Aggregate evidence** — the claim summarises a pattern across multiple files. Tag inline: `[evidence: pattern across internal/auth/*.go (n=7)]` and name the directory plus the count.
- **External evidence** — the claim depends on a contract or document outside the code (vendor doc, captured wire trace, infra spec). Tag inline: `[evidence: vendor:Payments API v2]` or `[evidence: trace: docs/captures/payment-2026-01-12.json]`.
- **No evidence** — the claim is suspected from naming, comments, or partial signals but cannot be confirmed. Move it to the *Gaps* section. Do not include it in the design body.

The `identifier-verification` layer rule still applies. Names of functions, types, routes, env vars, tables, columns, and so on must be visible in the cited evidence. If an identifier is mentioned in the design but never cited, it is a fabrication and must be removed.

## Required vs Observed classification

The Requirements section (see `design-template.md`) classifies each behaviour as one of four kinds. Use these rules to decide:

- **Must preserve** — the behaviour is *required* by an external contract, a passing test, an explicit user statement, or a regulatory obligation. The rewrite must implement it.
  - Witness: a test, a contract document, a user confirmation in the interview, or a compliance reference.
  - Default: do not promote a behaviour to *Must preserve* without one of these witnesses.
- **Observed but not required** — the behaviour is present in the code but has no test, no contract, no user confirmation. It might be intentional or it might be accidental.
  - This is the safe default for any behaviour read from code without a witness.
  - Surface every entry to the user; ask "is this intentional?". A *yes* promotes the entry to *Must preserve*; a *no* moves it to *Drop candidates*.
- **Drop candidates** — the user has explicitly said the rewrite should not preserve this behaviour. Populated only after a human pass.
  - Empty in the initial draft. The skill never moves an entry here on its own.
- **Gaps** — a behaviour is suspected but unverifiable from the code. Naming, comments, or partial signals point at it; no evidence confirms it.
  - Treat the same as *Gaps* in greenfield mode: the work cannot proceed without a witness or a user decision.

## Anti-patterns

These are the failure modes most likely to corrupt a code-evidence-mode design. Refuse to produce any of them.

- **Inferring intent from comments.** A comment that says "TODO: handle retry" is evidence that retry is *not* handled, not evidence that retry is required. Code comments document the past; they do not bind the future.
- **Promoting Observed to Required without a witness.** If you cannot point at a test, a contract, or a user confirmation, the behaviour stays *Observed*. Re-reading the code more carefully does not count as a witness.
- **Inventing names from convention.** A package called `auth` that lacks a function called `Authenticate` does not contain `Authenticate`. Read the code; do not pattern-match on naming.
- **Conflating as-built with as-intended.** The design body documents *what is*. The Requirements section is the only place where *what should be preserved* is asserted. Do not let intent leak into the body.
- **Treating tests as specifications.** Tests document current behaviour, not desired behaviour. A passing test promotes a behaviour to *Must preserve* only because the contract is "tests must keep passing"; if the user says the test encodes a bug, the entry moves to *Drop candidates* and the test is flagged for deletion.
- **Filling Gaps by reading harder.** If a behaviour cannot be confirmed from the available evidence, the fix is to widen the evidence (more code paths, more interviews) or to ask the user — not to relax the verification standard.

## Hand-off to the interview

After the scan and the initial classification, run Phase 2 of the skill (the interview) with the code-evidence question set in `interview-questions.md` §6. The interview's job here is **not** discovery — it is *intent confirmation* against a specific list of observed behaviours. Frame each question around an entry: "the code does X; is X intentional?"

Record each answer:

- *yes* → promote *Observed* to *Must preserve*.
- *no* → demote *Observed* to *Drop candidates*.
- *unsure* → leave in *Observed*, flag in *Gaps* with the unresolved question.

Do not promote any entry to *Must preserve* without an explicit *yes* or a non-user witness (test, contract, regulation).

## When to escalate

Escalate to the user — do not draft — if any of the following hold:

- The supplied code paths return no readable code (empty, binary-only, all `vendor/`, all generated).
- The codebase uses runtime reflection, code generation, or DSLs to a degree that the static reading of source cannot determine the public surface or the data model. Naming the limitation is more useful than producing a fabricated design.
- More than half of the candidate behaviours in the initial scan land in *Gaps*. This signals the evidence is too thin for the as-built design to be load-bearing; either widen the scope or stop and ask.

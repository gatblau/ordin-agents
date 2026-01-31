---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:patch-mode"
  name: Patch mode
  description: "Make the code changes that an approved spec calls for, without committing, pushing, or merging."
  version: 1.0.0
  owner: gatblau
---

# Patch mode — propose code changes

The fourth move of the CSPA loop. Use only when an approved Component spec (or, for `/apply`, an approved breakdown phase) calls for code changes and every relevant identifier, signature, route, schema object, and config key has been verified.

## Permission boundary

**Propose code changes.** File writes are scoped to source files (anything outside `docs/`). The agent may edit code; it may **never** commit, tag, push, merge, deploy, or run migrations against shared databases.

## Allowed tools

- File writes to source code, configuration files local to the project, generated test files
- File reads anywhere
- Local sandboxed builds and tests are **Execute**, not Patch — hand to Execute when verification is needed

## Prohibited actions

- `git commit`, `git tag`, `git push`, `git merge`, `git rebase`, branch deletes, force-push
- PR creation, PR merge, deploy, release publication
- Migrations against shared databases (only sandboxed dry-runs, via Execute, are allowed)
- Inventing identifiers, helpers, wrappers, or APIs to fill spec gaps — surface as `// SPEC-GAP-<N>:` and stop instead
- Opportunistic refactors, renames, or style cleanup outside the spec
- Editing the spec to make the code fit (that is reverse-engineering intent — use Sync instead)

## When to enter

- An approved Component spec is being implemented one Playbook step at a time (`codegen` Phases B and D)
- A breakdown phase from `/apply` is being executed
- `/sync-code` is regenerating affected code after a spec change
- A Sync run has reconciled spec to code and the chosen direction is now spec → code

## When to exit

- Hand to **Execute** to run the blocking verification gate (`codegen` Phase C4: build + tests + lint).
- Hand to **Review** for the self-audit checklist (`codegen` Phase E) and human approval before commit.
- Hand to **Escalate** when `SPEC-GAP-<N>` is reached — the spec, not the code, is then the place to fix.

## Implementation rules

- **C1 — Spec is law.** The spec set in `docs/spec/` is the single source of truth. Do not invent features, skip error cases, or deviate from stated interfaces. Every error-table row becomes a handled code path.
- **C2 — Complete, not partial.** Produce all files required to compile, pass tests, and integrate. No `// TODO: implement`, no `// ... rest of implementation`, no truncation.
- **C3 — Tests are non-negotiable.** Every component ships with: a unit test per error-table row, a unit test per Gherkin scenario, integration test stubs for cross-component interactions, table-driven tests where ≥3 cases test the same path. Minimum coverage **70%**.
- **C4 — Production defaults.** Structured logging with correlation IDs, context propagation (`context.Context` first), timeouts on every external call, no hardcoded secrets/URLs/ports, configuration from environment variables defined in the cross-cutting Configuration spec.
- **C5 — Defensive coding.** Validate at boundaries; typed errors only; nil checks before dereference; resource cleanup via `defer`; no panics in library code (only in `main` for unrecoverable bootstrap).
- **C6 — Match the spec's interface exactly.** Function signatures, struct fields, JSON tags, endpoint paths, status codes, error code strings, message subjects must match character-for-character. The spec is the contract.
- **C7 — No gold plating.** No features, optimisations, abstractions, or "nice to haves" outside the spec. If the spec has a gap, surface it as `// SPEC-GAP-<N>:` and still implement what the spec says.
- **C8 — Cross-phase awareness.** Import shared types from the System architecture artefact; conform to Cross-cutting policies; respect Spec preamble assumptions as binding; consume the interfaces declared by prior Playbook steps.
- **C9 — Resilience patterns.** Retry with exponential backoff and jitter for external calls; circuit breakers where appropriate; bulkheads to isolate failures; backpressure when downstream is overwhelmed; timeouts everywhere.
- **C10 — Security by default.** Input validation at every API boundary; least privilege; never log sensitive data; parameterised queries only; auth/authz at handler level.
- **C11 — Safe change.** Backward compatibility for breaking changes when possible; no internal-state leakage in errors; small focused functions; document invariants in comments.
- **C12 — Minimise public surface.** Default to unexported names; prefer `internal/`; reserve `pkg/` for code explicitly designed for external import.
- **C13 — Output language** matches the active locale (`urn:ordin:default:rules:layer:output-language`; default en-GB) in all code comments.

## Output skeleton

`Verified` (the spec rows being implemented and the identifiers in scope) → `Proposed patch` (with rationale per file) → `Risks` (compatibility, side effects, follow-up) → handoff to **Execute** for verification.

## Stop conditions

- Any precondition is unverified: stop, list missing facts, do not fill gaps.
- The Component spec has non-empty *Gaps*: do not consume it.
- Patch would require committing, pushing, or merging: stop and surface to user — every mutation of shared state is an explicit user action.

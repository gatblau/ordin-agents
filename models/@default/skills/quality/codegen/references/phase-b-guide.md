# Phase B — Code Generation guide

Produce every file listed in A6 in the sub-order supplied by the active Practice Pack's `file-layout.md`. Skip sub-phases that do not apply (a middleware component may only need errors, service, handler, wire-up).

This guide is **stack-neutral**. Concrete file names, packaging conventions, annotation forms, and language-specific patterns come from the active Practice Pack — typically `file-layout.md`, `annotation-conventions.md`, and the pack's library / framework references.

## Sub-phase ordering (template)

The Practice Pack's `file-layout.md` names the actual files in the language and layout the project uses. The shape below is the template the workspace asks every Practice Pack to fill:

```
B1. Errors          — Typed error definitions + error code constants
B2. Model           — Data models and validation
                      (import Phase 2 shared types; do NOT redefine)
B3. Repository      — Persistence access (queries, transactions)
B4. Service         — Business logic orchestration
B5. Handler         — Entry point: HTTP handler / message-bus consumer / CLI command
B6. Wire-up         — Constructors and dependency injection
B7. Migrations      — Paired forward / reverse migrations under the project's migrations directory
```

If the Practice Pack mandates a different sub-order (some stacks combine repository + service, some split handler from router, etc.), follow the pack.

## Per-file requirements

Every generated file must:

1. Start with the **file-marker comment** in the form the active Practice Pack's `annotation-conventions.md` specifies. The marker carries the repo-relative path so a reviewer can map the generated file to its target at a glance.
2. Declare its module / package / namespace per the project's convention, then imports.
3. Use **spec-linking comments** at key sites, in the comment syntax the Practice Pack specifies:
   - The "implements behaviour step N" form above logic that fulfils a numbered step in the spec's Internal Logic.
   - The "error table row" form at every error-handling site.
   - The "Phase 4 cross-cutting" form where a cross-cutting policy is applied (auth check, error envelope, log correlation ID, config read, metric emission).
4. Give every exported / public symbol a documentation comment in the active locale (see `urn:ordin:default:rules:layer:output-language`). The exact form (GoDoc, JSDoc, docstring, XML doc, …) is supplied by the Practice Pack's `annotation-conventions.md`.
5. Apply API-spec annotations on every entry-point handler matching the spec's API contract exactly. The form (Swag, OpenAPI decorators, JAX-RS, FastAPI Pydantic, …) is supplied by the Practice Pack.

## TechOps requirements for generated code

Apply these patterns in every applicable file. The patterns are stack-neutral; the idiomatic implementation comes from the Practice Pack:

- **Resilience (R9):** explicit timeouts on every external call; retry with exponential backoff + jitter for transient errors; circuit breaker state where the spec calls for it; backpressure on overwhelmed downstreams.
- **Security (R10):** input validation at the boundary; parameterised queries (never string concatenation against user input); auth checks at the handler layer; never log secrets or PII; constant-time comparisons for secret material.
- **Production (R4, R11):** structured logs with correlation / trace IDs; the language's idiomatic cancellation / context primitive propagated as the first parameter on every I/O function; no hardcoded config; typed errors.
- **Safe change (R12):** backward-compatible request / response shapes where the spec allows; error messages that do not leak internal state; small functions.

## Migrations

- Paired files: `<timestamp>_<name>.up.<ext>` and `<timestamp>_<name>.down.<ext>`. Timestamp in `YYYYMMDDHHMMSS`. The file extension and migrations-directory layout come from the Practice Pack.
- `down` must be a true reverse of `up`. For destructive changes (drop, data-losing alter), include a rollback note comment at the top of the up file.
- Reference the exact table / column / object names from the spec's Data Model section; do not infer names from patterns.

## What NOT to produce in Phase B

- Package-level documentation files — that is Phase D.
- Test files — that is Phase C.
- README or design notes — not produced by this skill.
- Any file not listed in A6. If Phase B discovers a need for an unplanned file, return to Phase A and revise A6 before generating it.
- Stack-specific scaffolding the Practice Pack does not authorise. If the Practice Pack does not name a particular file or convention, do not invent one.

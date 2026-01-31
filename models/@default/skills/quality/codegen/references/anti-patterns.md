# Anti-patterns — forbidden in generated code

Never produce any of the following. Use as a final filter before Phase E.

This list is **stack-neutral**. Where a pattern names a generic concept (e.g. "ignored close error", "unrecoverable-exit in library code"), the active Practice Pack supplies the language-specific examples and may add language-specific anti-patterns of its own.

| Anti-pattern | Why it is forbidden |
|---|---|
| Ellipsis comments ("... remaining implementation similar", "rest of the code") | R2 — write every line |
| Placeholder comments (`TODO`, `FIXME`, `XXX`, "left as exercise") | R2 — add the implementation now or flag `SPEC-GAP` |
| Unrecoverable-exit calls (panic / fatal / process.exit / `System.exit`) in library code | R5 — return the error; reserve unrecoverable exit for the process entry point |
| Untyped containers (`interface{}`, `any`, `Object`, `dynamic`) when the spec names a concrete type | R6 — use the concrete type |
| Detached cancellation (background context, `null` token, fresh `AbortController`) in non-entry-point code | R4 — propagate the caller's cancellation primitive |
| Ignored cleanup-error returns (close, dispose, rollback, unlock) | R5 — at minimum log the error |
| Raw query construction via string concatenation or formatted strings against caller-controlled input | R10 — parameterise the query |
| Inventing endpoints, fields, events, or subjects not in the spec | R1 — spec is law |
| Skipping tests for "simple" functions | R3 — simple functions get simple tests |
| Adding dependencies not listed in PROJECT CONSTANTS or the active Practice Pack's approved-libraries list | Flag as `SPEC-GAP` if truly needed |
| Redefining a Phase 2 shared type | R8 — import it |
| Ignoring a Phase 4 cross-cutting spec | R8 — apply it |
| Contradicting a Phase 1 assumption | R8 — respect it |
| Exposing symbols that are not part of the required service interface | R13 — default to unexported / private |
| Placing implementation in the project's library-surface directory when it is not designed for external import | R13 — use the implementation directory the Practice Pack's `file-layout.md` specifies |
| Comments not in the active locale (mixed spellings, wrong locale) | R14 — match the active locale (`urn:ordin:default:rules:layer:output-language`) |
| Swallowing errors silently (return null / nil / undefined on error without wrapping) | R5 — wrap and return typed errors |
| Hardcoded URLs, ports, paths, or credentials | R4 — read from Phase 4 Configuration spec |
| Forward migration without a corresponding reverse migration | R12 — every change must be reversible |
| Stack-specific bad patterns the Practice Pack flags (e.g. Go: `goroutine` started without a context cancellation path; TS: `await` inside a `forEach`) | Per the active Practice Pack |

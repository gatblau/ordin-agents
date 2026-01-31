# Phase 6 — self-audit checklist

Tick each item explicitly. If any item fails, fix the relevant spec and re-audit. Do not deliver output with unchecked items.

```
[ ] Every entity has a complete data model with types and constraints.
[ ] Every action has defined inputs, outputs, numbered steps, and errors.
[ ] No banned phrases remain (see banned-phrases.md).
[ ] Every component has ≥3 Gherkin acceptance criteria (happy, edge, error).
[ ] Every component has an error table with ≥2 rows.
[ ] Every cross-component interaction is documented on BOTH sides.
[ ] Build order (Phase 2B) is a valid DAG — no circular dependencies.
[ ] Every config value / env var listed with type, default, required flag, and owner component.
[ ] Every spec is self-contained — implementable from its section alone.
[ ] Assumptions register is complete; open questions are truly blocking only.
[ ] Example I/O provided for every component with non-trivial logic.
[ ] Shared types defined once in Phase 2C, referenced by name elsewhere but duplicated into "Shared Context" of each consuming spec.
[ ] Security addressed for every entry point (HTTP handler, NATS subscriber, CLI command).
[ ] Performance targets stated for every latency-sensitive component.
[ ] All specifications use the active locale (see `urn:ordin:default:rules:layer:output-language`; default en-GB).
[ ] Destructive schema changes (DROP, data-losing ALTER, NOT NULL backfills) surface rollback considerations.
[ ] Every Component, Cross-cutting, and Preamble spec carries a `derivedFromHld: <revision>` preamble field.
[ ] No spec body contains an ADR-shaped paragraph (Decision · Context · Consequences · Alternatives pattern); every such paragraph has been promoted to HLD `09-decisions.md` via the HLD-impact-pass.
[ ] Every glossary term used in any spec is present in the HLD glossary (HLD `00-overview.md` in folder form, the Glossary section in single-file form).
[ ] No HLD revision declaring it `affects:` this spec set is newer than the set's `derivedFromHld:` pin. (A newer revision that does not name this set advances the HLD without obliging it, and is not a failure. Where exactly one spec set derives from the HLD, `affects:` is implicit and the pin must equal the current `revision:`.)
[ ] In folder-form HLDs: every revision bump recorded in the HLD `README.md` has a corresponding line in `99-changelog.md`.
```

Output format for Phase 6: reproduce the checklist with `[x]` or `[ ]` and, for any unchecked item, a one-line note explaining what was fixed or why it remains open.

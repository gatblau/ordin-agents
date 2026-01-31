# Annotation conventions (Go)

Cited by `urn:ordin:default:skills:quality:codegen` Phase B and Phase E. The workspace skill names a generic "documentation comment on every exported symbol" requirement; this file makes the requirement concrete for Go.

## GoDoc on exported symbols

Every exported type and function carries a GoDoc comment:

- The first sentence starts with the symbol's name and ends with a full stop.
- Wraps at the project's column convention (typically 100).
- Prose is in the active locale (per `urn:ordin:default:rules:layer:output-language` — default en-GB; supersedable by an installed `LanguageOverlay`).
- A `// Example` GoDoc block is added only when the API is non-obvious.

Package-level GoDoc lives in `doc.go` at the package root.

## Swag annotations on HTTP handlers

Every HTTP handler carries Swag annotations matching the spec's API contract character-for-character. The handler's router shape (e.g. the Echo handler signature) is the active **library** pack's concern (`router-conventions.md`); this file fixes only the Swag annotation mechanics that sit on it:

- `@Summary` — one-line description.
- `@Description` — optional, longer.
- `@Param` — one per request parameter (path, query, body), with type and required/optional.
- `@Success` — one per documented success status, with response schema.
- `@Failure` — one per error-table row, with error code.
- `@Router` — exact method + path matching the spec's Public Interface section.

Mismatches between Swag annotations and the spec's Public Interface are caught by `sync-check`'s S2 (HTTP routes) and S3 (JSON field names) aspects.

## Spec anchors

The machine-resolvable citation, fixed by `urn:ordin:default:rules:layer:spec-anchors`. In Go the leader is `//`:

```go
// spec: workflows/phase-3-components#MP-WF-22
func celCostOverrideValidator(v any) (any, error) { … }
```

One anchor per line; stack lines for several assertions. The directive line carries the citation and nothing else — narrative goes on its own lines, above or below. Place it immediately above the declaration it labels, or at end-of-line for a struct field:

```go
ApprovedVersion *int `json:"approved_version,omitempty"` // spec: lexor/phase-3-components#LX-26
```

Anchors sit **beside** the prose forms below, not instead of them: the prose explains, the anchor resolves. `codegen` Phase B emits both; `sync-check` aspect S11 resolves the anchor and reports a dangling one as `TRACE-DANGLING`.

Never write an anchor for an id you have not read in the spec document — pattern-completing from a sibling id is exactly the failure `layer:identifier-verification` forbids.

## Spec-linking comments

Three comment forms link generated code back to the spec it implements. They are emitted by `codegen` Phase B and consumed by reviewers (and by `sync-check`'s drift detection):

| Comment | Where | Purpose |
|---|---|---|
| `// Implements SPEC behaviour step N` | Above the function or block that fulfils numbered step N of the spec's Internal Logic | Maps code to spec step |
| `// Error table row: <Condition>` | At every error-handling site | Maps code to spec error-table row |
| `// Phase 4: <Spec Name>` | At every cross-cutting application site (auth check, error envelope, log correlation, config read, metric emission) | Maps code to Phase 4 cross-cutting spec |

In code-evidence-mode specs (per `urn:ordin:default:skills:quality:specgen` Branch C) two additional comment forms apply:

| Comment | Where | Purpose |
|---|---|---|
| `// SPEC-OBSERVED: <one-line>` | Above any `[Observed]` assertion `codegen` carries forward best-effort | Tells the downstream reader this implementation has no witness |
| `// SPEC-GAP-<N>:` | Inline, where the spec marks a `[Gap]` that codegen could not resolve | Surfaces the spec gap in the source so a reader cannot miss it |

## Forbidden

- Untranslated example identifiers in GoDoc (e.g. an `Example` block that uses an English variable name when the active locale is fr). The locale rule applies to GoDoc prose; identifiers stay as-authored.
- Swag annotations that disagree with the spec's Public Interface. Either fix the annotation or fix the spec; do not let them drift.
- A `// spec:` anchor citing an id that has not been read in the spec document, or one carrying explanatory prose on the directive line. The first is fabrication; the second breaks extraction.
- Hand-rolled documentation comments that omit the symbol name in the first sentence. Tooling depends on the convention.

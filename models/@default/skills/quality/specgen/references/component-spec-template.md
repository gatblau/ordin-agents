# Component spec template (Phase 3 & 4)

Produce one section per component using this exact structure.

The template has one mode-driven element: in `code-evidence` mode every assertion in *Public Interface*, *Internal Logic*, *Error Table*, and *Acceptance Criteria* carries a classification tag. See *Mode-driven sections* at the bottom of this file.

```markdown
### SPEC: <ComponentName>
**File:** `<path/to/file.go>` | **Package:** `<package_name>` | **Phase:** <N> | **Dependencies:** <list>

> **Mode:** {greenfield | code-evidence}
> **derivedFromHld:** <hld-revision>  <!-- the HLD's `revision:` at the time this spec was drafted (provenance); sync-check D-HLD-3 fires if a revision declaring it affects this spec set is newer than this -->
> **Classification summary** (code-evidence only): Required: N | Observed: N | Not implemented: N | Gap: N

#### Purpose
<One paragraph. What this component does and why it exists.>

#### Approach
<One short paragraph stating the chosen design direction at component level, plus one or two alternatives that were considered and rejected with a one-line reason each. This is the *why-this-not-that* at component scope; system-level rationale belongs in the design document, not here. Examples of valid Approach content: which library/framework was chosen and what was discarded; which pattern (state machine, pipeline, table-driven) governs the Internal Logic; whether the component owns its own state or delegates to a shared store. Do not restate Purpose. Do not describe alternatives the design document already settled.>

#### Shared Context
<Duplicate the shared types, config keys, and env vars this spec references. Do not cross-link to Phase 2C — copy them in. A reader must implement from this section alone.>

#### Public Interface
<Exact signatures: function names, parameters, return types. For HTTP: method + path + request/response schema. For message consumers: subject pattern + payload schema.

In code-evidence mode, every entry carries a classification tag — `[Required]`, `[Observed]`, `[Not implemented]`, or `[Gap]` — followed by a witness or evidence citation. See `code-evidence-classification.md` §Witness types for citation format.>

##### Example
<Concrete request/response or input/output. Real values, not placeholders.>

#### Internal Logic
<Numbered step-by-step. Each step states: what is done, which dependency is called, which errors are possible, what is logged.

In code-evidence mode, every numbered step carries a classification tag at the end of the step: `[Required: <witness>]`, `[Observed: <evidence>]`, `[Not implemented]`, or `[Gap: <what is missing>]`.>

#### Data Model
<DDL for tables owned by this component (CREATE TABLE, indexes, constraints). Include rollback considerations for destructive changes.

In code-evidence mode, the DDL block is followed by a per-table classification line stating the class for the schema as a whole and citing evidence (the migration file, the schema dump, or the as-built design's Domain Model section).>

#### Error Table
| Condition | Status | Code | Response Body | Class (code-evidence only) |
|-----------|--------|------|---------------|----------------------------|
| <e.g. JSON parse failure> | 400 | VAL_ERR | `{"error":"...", "code":"VAL_ERR"}` | <`[Required: test:...]` / `[Observed: ...]` / `[Not implemented]` / `[Gap]`> |
| <e.g. DB unavailable> | 503 | DB_DOWN | `{"error":"...", "code":"DB_DOWN"}` | |

Minimum two rows. Include every failure mode the Internal Logic references. The Class column is mandatory in code-evidence mode and omitted in greenfield mode.

#### Acceptance Criteria (Gherkin)
Feature: <ComponentName>

  # In code-evidence mode, every Scenario header carries a classification tag in a comment:
  #   Scenario: Happy path  # [Required: test:internal/payment/processor_test.go:TestHappyPath]
  #   Scenario: Edge case — empty list  # [Observed: pattern across handlers/list.go]
  #   Scenario: Error path — DB down  # [Not implemented]
  #   Scenario: Edge case — concurrent writes  # [Gap: cannot determine current behaviour]

  Scenario: Happy path
    Given ...
    When ...
    Then ...

  Scenario: Edge case — <describe>
    Given ...
    When ...
    Then ...

  Scenario: Error path — <describe>
    Given ...
    When ...
    Then ... returns <status> with code <CODE>

Minimum three scenarios: happy, edge, error.

#### Performance, Security, Observability
- **Performance targets:** <p95 latency, throughput, memory ceiling>
- **Security:** <auth required, input validation, PII handling, rate limits>
- **Observability:** <metric names with labels, log fields, trace span names>

#### Gaps
<List anything this Component spec cannot verify in source. Each entry: one line. Categories:
- **Missing identifier** — a function, type, route, env var, table, or column the spec needs but cannot locate in the repo. Cite the section that needed it.
- **Ambiguous requirement** — a behaviour the design document leaves underspecified that materially affects implementation.
- **Unconfirmed assumption** — an assumption the spec relied on (config default, performance budget, dependency version) that has not been validated against the source.

If empty, write `None.` Gaps that cannot be resolved at component level escalate to the Spec preamble's *Open Questions* section (artefact 2). **Gaps must be empty before `codegen` is allowed to consume this spec — this is a blocking gate.**>
```

## Rules when applying this template

- Every section is mandatory. If a section genuinely does not apply (e.g. no DDL for a pure in-memory component), write `N/A — <reason>` rather than omitting.
- **Approach** is short — one paragraph. If alternatives consume more than two lines each, the rationale belongs in the design document, not here.
- **Gaps** is a blocking gate for downstream code generation. A Component spec with a non-empty Gaps section is *Draft*, never *Approved*. `codegen` refuses to consume a spec with non-empty Gaps. Items that cannot be resolved at component level escalate to the Spec preamble's *Open Questions*. The `[Gap]` classification tag (code-evidence mode) is the per-assertion form of this same blocking gate — any unresolved `[Gap]` keeps the spec at *Draft*.
- Keep each component spec self-contained: a code-generating LLM must be able to implement it with only this section in context.
- Use the active locale throughout (see `urn:ordin:default:rules:layer:output-language`).
- No banned phrases (see `banned-phrases.md`).

## Mode-driven sections

The template has one part that changes shape with the active mode of the underlying skill: per-assertion classification tags.

### Mode banner (always present)

The banner immediately under the header declares the active mode and (in code-evidence mode) the assertion-class summary.

| Mode | Banner reads | Classification summary |
|---|---|---|
| `greenfield` | `Mode: greenfield` | omitted |
| `code-evidence` | `Mode: code-evidence` | `Required: N \| Observed: N \| Not implemented: N \| Gap: N` |

The greenfield mode covers both the original `interview` / `draft` flow and the `change-request` flow against an existing spec set — anything that is not authoring against an existing codebase.

### Per-assertion classification tags (code-evidence only)

In `code-evidence` mode, every assertion in *Public Interface*, every numbered step in *Internal Logic*, every row in *Error Table*, and every Gherkin *Scenario* carries one of four classification tags. The classification rules and the relationship to `sync-check`'s drift labels live in `code-evidence-classification.md`. Do not duplicate them here.

Tags:

- **`[Required: <witness>]`** — assertion present in code AND has a witness.
- **`[Observed: <evidence>]`** — assertion present in code, no witness; safe default.
- **`[Not implemented]`** — assertion required by the design's *Must preserve* but no matching code.
- **`[Gap: <what is missing>]`** — suspected but unverifiable; blocks promotion to *Approved*.

In greenfield mode the tags are omitted entirely. The Class column in *Error Table* is omitted from the rendered table in greenfield mode (the `| Class |` header and column data are simply not produced).

### The Gaps section vs `[Gap]` tags

The legacy *Gaps* section at the bottom of every component spec remains in both modes. It captures section-level gaps (an entire spec section that cannot be drafted from the available evidence). The per-assertion `[Gap]` tag captures finer-grained gaps inside a section. Both gate promotion to *Approved*; both must be empty before `codegen` will consume the spec.

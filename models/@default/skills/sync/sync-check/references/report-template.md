# Report template

Output format for every `sync-check` run. Reports are Markdown, printed in the response. Do not write a file unless the user explicitly asks.

## Header

```markdown
# sync-check report

- **Scope:** <all | design-spec | spec-code | component name>
- **Mode:** <report | fix>
- **Git HEAD:** <short SHA> (<branch>)
- **Since:** <ref> | full tree
- **Timestamp:** <ISO 8601 UTC>

## Toolchain

| Tier | Available | Used for |
|---|---|---|
| T1 Filesystem | yes | always |
| T2 Regex | yes | always |
| T3 tree-sitter | yes / no (not installed) | <languages covered> |
| T4 go AST | yes / no | Go signature adjudication |
| T4 tsc | yes / no | TypeScript signature adjudication |
| T4 python ast | yes / no | Python signature adjudication |
| T4 cargo check | yes / no | Rust signature adjudication |
```

If any tier is unavailable, add a one-line note under the table:

> Missing tiers downgrade affected findings to lower-confidence tiers. Install `<tool>` to raise confidence.

## Summary counts

```markdown
## Summary

| Label | Count |
|---|---|
| INTENT-DRIFT | N |
| CONTRACT-DRIFT | N |
| REALITY-DRIFT | N |
| SCOPE-GAP | N |
| D-HLD-1 (glossary gap) | N |
| D-HLD-2 (hidden ADR) | N |
| D-HLD-3 (unabsorbed HLD revision) | N |
| D-HLD-4 (orphan HLD component) | N |
| D-HLD-5 (sibling inconsistency) | N |
| D-HLD-6 (changelog gap) | N |
| **Total findings** | N |

Components inspected: N   ·   Source files inspected: N   ·   Migrations inspected: N
```

When `scope` includes `traceability`, also emit the **Traceability** count block (§13-Q8 — see `traceability-checks.md`):

```markdown
## Traceability (scope: traceability)

| Label | Count |
|---|---|
| ORPHAN-FORWARD (requirement with no test) | N |
| ORPHAN-REVERSE (test with no requirement) | N |
| TRACE-DANGLING (cited id not found) | N |
| **Total traceability findings** | N |

FR → HLD-goal: <verified | unverifiable — FR register not installed>
Members inspected: N   ·   Chain: HLD-goal → AC → test
```

If total findings = 0:

> No drift detected at this scope. HLD, LLD spec set, and code are consistent within the limits of code inspection (sync-check does not execute code).

## HLD revision lineage

For every HLD topic in scope, emit a lineage block:

```markdown
## HLD revision lineage

### <topic>

- **HLD path:** `docs/design/<topic>/` (folder form) | `docs/design/<topic>.md` (single-file form)
- **Current revision:** <semver> · **Last updated:** <ISO date>
- **Changelog lines:** <N> (folder form only)

| Spec phase | derivedFromHld | Status |
|---|---|---|
| docs/spec/phase-3-component-X.md | <semver> | current / **unabsorbed (D-HLD-3)** / **unadjudicated (D-HLD-3)** / **missing pin** |
| docs/spec/phase-4-cross-cutting.md | <semver> | ... |
```

Stale and missing-pin rows are highlighted; a single stale phase blocks promotion of the spec set even if every other check passes.

## Findings

Group by component. For each component with findings:

```markdown
### <ComponentName> (Phase 3 section / Phase 4 section)

Spec file: `docs/spec/phase-3-components.md` · Source: `internal/domain/component/`
Likely drift source: <layer>  (spec mtime: <date>, code mtime: <date>, design mtime: <date>)

| # | Aspect | Expected (spec) | Actual (code) | Label | Tier | Action |
|---|---|---|---|---|---|---|
| 1 | Route | `POST /api/v1/projects` | `POST /api/v1/project` | CONTRACT-DRIFT | T2 | Run `/codegen step: "3: ProjectHandler"` |
| 2 | JSON tag | `project_id` | `projectId` | CONTRACT-DRIFT | T3 | Run `/codegen step: "3: ProjectHandler"` |
| 3 | Error code | `PROJ_NOT_FOUND` | (not found in code) | REALITY-DRIFT | T2 | See reconciliation options below |
```

For every REALITY-DRIFT row, follow the table with a Reconciliation Options block:

```markdown
#### Reconciliation: <ComponentName> / <Aspect>

**Option A — Revert code to spec:**
Diff preview:
  <unified diff against the code file>

**Option B — Update spec to match code:**
Diff preview:
  <unified diff against the spec file>

No automatic action taken. Reply with "apply A" or "apply B" to proceed.
```

For every SCOPE-GAP, follow the table with a Triage block:

```markdown
#### Triage: <ComponentName> / <Aspect>

Orphan: <what was found in which layer>

1. **Fill the gap** — <specific action, e.g. add Phase 3 component spec / run /codegen / write migration>.
2. **Delete the orphan** — <specific file or section to remove>.
3. **Mark as intentional** — add a row to Phase 1A Assumptions: <suggested wording>.

No automatic action taken.
```

When `scope` includes `traceability`, follow the component Findings with a **Traceability findings** section (§13-Q8), grouped by link (and, for a journey, by member workspace):

```markdown
## Traceability findings (scope: traceability)

### Link: HLD-goal → AC → test   (member: <workspace> | whole-project)

| # | Label | Artefact (id) | At link | Detail |
|---|---|---|---|---|
| 1 | ORPHAN-FORWARD | HLD-goal `G-003` | HLD-goal → AC | no AC cites G-003 (requirement ends in no test) |
| 2 | ORPHAN-REVERSE | test `TestFoo` | AC → test | cites no AC id (test verifies no stated requirement) |
| 3 | TRACE-DANGLING | test `TestBar` | AC → test | cites `AC-099` — no such AC |

FR → HLD-goal: unverifiable — FR register not installed (graceful degradation; not counted as orphans).

No automatic action taken — close an orphan by authoring the missing test/AC/goal, or remove the orphan (human decision).
```

## Footer

```markdown
## Next steps

<One of these, whichever applies>

- Run `/sync-check mode: fix` to see proposed patches grouped by drift label.
- Run `/codegen step: "<N>: <Component>"` for each CONTRACT-DRIFT component — suggested order:
  1. <ComponentA>
  2. <ComponentB>
- Resolve REALITY-DRIFT and SCOPE-GAP findings with human judgement before re-running sync-check.
- Re-run `/sync-check` after applying changes to confirm zero remaining drift.
```

## Rules for the report

- Never hide findings to keep the report short. Always list every finding.
- Never invent a tier. If an aspect could not be extracted, emit a SCOPE-GAP with "aspect could not be extracted at any available tier" rather than guessing.
- Never combine findings across components into one row. One row = one (component, aspect, expected, actual) tuple.
- Always phrase drift-source as "likely", never as fact.
- When a suggested action is `/codegen`, include the exact playbook step number from Phase 2B inventory — do not paraphrase.

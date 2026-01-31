---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:analysis:dbaudit"
  name: dbaudit
  description: "Produces a ranked review of a SQL codebase: tables, constraints, types, indexes, views, and functions, by reading only. Never runs SQL."
  version: 2.0.0
  owner: gatblau
description: Critique a SQL codebase — DDL, constraints, indexes, views, and stored functions — for relational patterns, domain modelling, attribute choices, integrity, indexing/performance, function correctness, and overall coherence. Produces a ranked, classified findings report with recommendations, optionally shaped for direct handoff to `/breakdown`. Stack-neutral SQL audit shell — engine-specific concerns (Postgres, MySQL, SQLite, …) come from the active database Practice Pack; without one the skill produces a generic SQL critique. Trigger on phrases like "dbaudit", "database code audit", "audit the schema", "critique the SQL", "review the DDL", or when the user asks for a coherence/performance critique of the SQL under the project's schema directory. Do NOT trigger for application call-site concerns, design/spec/code drift (that is `sync-check`), writing a specific migration (that is `schemagen`), or broad security reviews outside SQL (that is `secscan`).
---

# dbaudit — SQL codebase critique

Produce a ranked, classified critique of a SQL codebase: tables, constraints, types, indexes, views, and stored functions. Static inspection only — never runs SQL, never opens a connection, never writes migrations. Output is shaped to be pasted straight into `/breakdown` when the user wants to turn findings into a migration plan (which `/breakdown` then routes through `schemagen` for the DDL author step).

This skill is **stack-neutral by frame** and **engine-specific by reference**. The skill itself names no database engine. Engine-specific rule sets — Postgres / PL-pgSQL, MySQL / InnoDB, SQLite, MSSQL / T-SQL, Oracle / PL-SQL — live in **database Practice Packs** (e.g. `@default/practice-packs/database/postgres`). Without a database Practice Pack the skill produces a generic, engine-neutral SQL critique grounded in ANSI SQL primitives; with one, it produces a full engine-aware critique using the pack's references.

The `sql-safety` layer rule is always-on for this skill: do not name a table, column, index, trigger, view, constraint, sequence, or function unless it is directly visible in the repo, and surface rollback considerations on anything destructive.

## Scope

Default scope: the project's schema directory (typically `schema/**/*.sql`, `db/**/*.sql`, `migrations/**/*.sql`, or whatever the active Practice Pack declares). Works against any project layout that groups SQL by concern — table files, function files, view files.

**Out of scope:**

| Concern | Use instead |
|---|---|
| Writing a specific migration (`ALTER TABLE …` authoring) | `schemagen` |
| Drift between design / spec / code / schema | `sync-check` |
| Application code that accesses the DB (pool, transactions, scans) | out of scope for this skill |
| Generic security audit (secrets, auth, transport) | `secscan` |
| Test coverage over DB code | `testgen` |
| Turning dbaudit findings into an incremental plan | feed this report into `/breakdown` |

## Arguments

- `scope`: default the project's schema directory (per the active Practice Pack). Accepts a path, a single file, or a concern keyword (`tables`, `constraints`, `indexes`, `views`, `functions`, `coherence`).
- `mode`:
  - `report` (default) — findings only.
  - `recommendations` — findings + a short "Suggested remediation" block per finding (text only — no DDL diffs).
  - `breakdown-ready` — findings + a "Handoff to /breakdown" block pre-formatted for that command (see `references/breakdown-handoff.md`).
- `severity-floor`: default `low`. Suppresses findings below this threshold. One of `info`, `low`, `medium`, `high`, `critical`.

## Active modes

**Observe → Infer → Review**, with the `sql-safety` layer rule always-on.

- **Observe** for Phases 1–3: scope discovery, file reads, DDL extraction, line-numbered evidence. No external writes.
- **Infer** for the severity-classification pass inside Phase 4: "worst-case outcome given this schema shape, under what preconditions". Hypothesis-tagged with stated pre-conditions; never asserted as verified.
- **Review** for the consolidated findings report and the optional `breakdown-ready` handoff shape.

The skill never enters Patch — even `recommendations` mode emits prose, not DDL. When the user wants the actual migration, `/breakdown` routes to `schemagen`, which is the only author of DDL in this workflow. **Escalate** is used when the SQL surface is too large to audit within scope, when a finding requires a user decision (accepted denormalisation, intentional missing index), or when the engine is unrecognised and no database Practice Pack supplies a reference set.

## Hard rules

- **Static inspection only.** No `psql`, no `\d`, no connection to any database, no `EXPLAIN`.
- **Never invent identifiers.** Every named table, column, index, constraint, sequence, view, function, or trigger must be directly visible in the repo. Unverified names are flagged "regex-confidence — verify manually"; if the name cannot be confirmed at all, the finding is downgraded to `info` or dropped.
- **Every finding cites file:line.** A claim without a concrete location is not a finding.
- **Severity must be justified.** Every finding states (a) the worst-case outcome, (b) the preconditions for it, (c) why this severity not the adjacent one.
- **Rollback considerations on destructive remediations.** When a suggested remediation is a `DROP`, `ALTER ... DROP COLUMN`, `ALTER ... TYPE`, or a `NOT NULL` backfill, the recommendation text must name the rollback hazard explicitly (data loss, locks held, dependent views/functions). The user and `schemagen` decide how to mitigate — dbaudit only flags.
- **Do not propose DDL diffs.** In `recommendations` mode, remediations are short English sentences naming the target file and the intended change. No `CREATE`/`ALTER`/`DROP` statements in the report. Producing actual DDL is `schemagen`'s job.
- **Respect confidentiality.** If a SQL file contains what looks like a live credential or seed user password, report only file path and line. Never echo the secret.

## Taxonomy (labels)

Every finding carries exactly one label. Pick the primary harm.

| Label | Meaning |
|---|---|
| MODELLING | Relational or domain-model flaw: wrong entity boundary, normalisation issue, broken multi-tenancy, missing or duplicated concept. |
| INTEGRITY | Missing or incorrect constraint: FK, UNIQUE, NOT NULL, CHECK, cascade policy. |
| TYPES | Column-type, nullability, or default-value choice that will surprise at scale or corrupt semantics. |
| PERFORMANCE | Indexing or shape decision that produces a seq scan / bloat / lock hazard at expected load. |
| CORRECTNESS | Stored-function or view logic bug that yields wrong results or silent failure. |
| SECURITY | Dynamic SQL injection in a function, missing search-path hygiene on definer-rights functions, PII stored without masking, row-level security absent on a tenant-scoped surface. |
| COHERENCE | Convention drift, dead code, naming/grouping inconsistency, missing comments, deploy-order hazard. |

The engine-specific examples for each label come from the active database Practice Pack. The Postgres pack, for example, contributes "missing index on a FK column (Postgres does not auto-index FKs)" under PERFORMANCE.

## Severity matrix

| Severity | Criteria |
|---|---|
| Critical | Demonstrable data-loss path, SQL injection in a function reachable from the app, broken multi-tenancy (rows of one tenant reachable via a missing FK/filter), plaintext live credential. |
| High | Missing constraint on a user-visible invariant; missing index on a hot FK; view/function whose logic is visibly wrong on the primary use case. |
| Medium | Latent bug requiring specific inputs or scale; redundant-index bloat on a large table; TYPE mismatch that will bite during precision edge cases; definer-rights function with missing search-path hygiene on a function not yet exposed broadly. |
| Low | Coherence/style/defence-in-depth gap with no direct failure path. |
| Info | Observation with no stated threat, bug, or performance impact. |

Every finding records the reasoning. A finding that cannot distinguish its assigned severity from the next-lower one is downgraded.

## Process

### Phase 1 — Engine and layout probe

Determine, from files only:

- **Engine.** Look for engine signals: extension declarations, dialect-specific functions, vendor-specific casts. If a database Practice Pack is installed, confirm the engine matches; if no pack is installed, record the detected engine and proceed in **engine-neutral mode** (ANSI SQL only). Record the engine in the report header.
- **Layout.** Where tables, functions, views, content/seed data live. The Practice Pack may declare the canonical layout; otherwise infer from the project tree.
- **Deploy-order source of truth.** Manifest file, migration list, deploy script. Record the file. Later phases cross-reference it for COHERENCE findings.
- **Conventions probe.** Idempotency wrappers, sequence-start convention, naming style, timestamp policy, FK-naming pattern. The active Practice Pack may declare some of these; the rest are inferred from existing files.

Record these facts in the report header. They are the baseline against which COHERENCE findings are measured.

### Phase 2 — Object inventory

Enumerate every object the scope implies, with `path:line`:

- **Tables**: columns with types/nullability/defaults, PK, all constraints, all indexes, sequences, storage options, comments if present.
- **Views**: referenced tables/columns; whether the view itself is queried by functions.
- **Functions / stored procedures**: signature, language, security context, search-path hygiene, volatility, return type, exception blocks, dynamic SQL usage. Engine-specific volatility / security-context detail comes from the active Practice Pack.
- **Sequences** declared outside tables.
- **Triggers** and trigger functions.
- **Seed/i18n content** files — scanned for live credentials and for references to tables/columns that must exist.

The inventory is the ground truth for every finding. If an object named in a finding is not in the inventory, the finding is dropped.

### Phase 3 — Concern-driven scan

Run each concern the scope implies. Load the matching reference on demand. The workspace ships only the engine-neutral references; engine-specific references are loaded from the active database Practice Pack.

| Concern | Workspace reference (engine-neutral) | Practice-Pack reference (engine-specific) |
|---|---|---|
| Relational patterns, domain model, multi-tenancy, audit/log tables | — | `relational-patterns.md` |
| Attributes — types, nullability, defaults, timestamps | — | `attributes-and-types.md` |
| Constraints & integrity — PK, FK, UNIQUE, CHECK, cascade | — | `constraints-and-integrity.md` |
| Indexing & performance | — | `indexing-and-performance.md` |
| Views | — | `views.md` |
| Stored functions / procedures | — | `functions-plpgsql.md` (Postgres pack); equivalents in other packs |
| Coherence & conventions | `references/coherence-and-conventions.md` | (pack may add engine-specific naming patterns) |

If `scope` is a single concern keyword, run only that reference. Otherwise run all applicable concerns. In **engine-neutral mode** (no database Practice Pack installed), only the workspace reference is loaded — `coherence-and-conventions.md` always runs; the rest produce a stripped report that flags ANSI SQL issues only and explicitly notes engine-specific concerns are unchecked.

### Phase 4 — Classification, severity, confidence

For each finding:

1. Assign exactly one taxonomy label (pick the primary harm).
2. Assign severity using the matrix above. Record the preconditions that justify that severity and the reason it is not the adjacent one.
3. Tag confidence:
   - `high` — objects directly visible and behaviour determinable from the DDL alone.
   - `regex-confidence` — pattern-matched; verify manually (names, join conditions, dynamic-SQL fragments).
   - `inferred` — depends on caller behaviour, runtime data volume, or config not visible in the repo. Cap severity at `medium`.
4. Drop findings below `severity-floor`.

### Phase 5 — Report assembly

Emit in this shape:

```markdown
# dbaudit report

**Scope:** {{scope}}
**Severity floor:** {{floor}}
**Mode:** {{mode}}
**Engine:** {{detected engine, plus active Practice Pack id if any}}
**Engine-neutral mode:** {{yes/no — yes when no database Practice Pack is installed}}
**Layout:** {{tables=…, funcs=…, views=…, manifest=…}}
**Conventions probed:** {{idempotency wrapper=…, seq start=…, naming=…, timestamp policy=…}}
**Generated:** {{UTC timestamp}}
**Git HEAD:** {{short sha}}

## Summary
- By severity: critical={{n}} high={{n}} medium={{n}} low={{n}} info={{n}}
- By label: MODELLING={{n}} INTEGRITY={{n}} TYPES={{n}} PERFORMANCE={{n}} CORRECTNESS={{n}} SECURITY={{n}} COHERENCE={{n}}

## Findings

### F-001 — {{short title}}  ({{severity}}, {{label}})
- **Location:** `<file:line>`
- **Concern:** {{concern category}}
- **Observation:** {{what the DDL says, 1–2 sentences, no speculation}}
- **Why it matters:** {{worst-case outcome}}
- **Preconditions:** {{load, data shape, caller behaviour required}}
- **Confidence:** {{high | regex-confidence | inferred}}
- **Evidence:**
  ```sql
  {{minimal quoted DDL}}
  ```
- **Suggested remediation** (modes `recommendations` and `breakdown-ready` only):
  {{prose — target file, intended change, rollback hazard if destructive. No DDL.}}

### F-002 — …
```

Sort findings by severity descending, then by label, then by file path. Number them `F-001`, `F-002`, … so the `/breakdown` handoff can reference them stably.

### Phase 6 — /breakdown handoff (`breakdown-ready` mode only)

Load `references/breakdown-handoff.md`. Append a **Handoff to /breakdown** section that names the anchor finding(s), lists verified context, flags open assumptions, gives a ready-to-run `/breakdown` invocation, and includes the diagnosis body for the user to paste. The handoff makes clear that DDL remediations are authored by `schemagen` downstream of `/breakdown`, never directly.

dbaudit does not invoke `/breakdown` itself. It stages the handoff and stops.

## What dbaudit does not do

- Does not execute SQL, connect to a database, or run `EXPLAIN`.
- Does not author migrations — that is `schemagen`'s job.
- Does not modify any SQL file.
- Does not compare against design docs or specs — that is `sync-check`.
- Does not audit application code that calls the database.
- Does not invoke `/breakdown` — it only stages the handoff.
- Does not produce engine-specific findings without an installed database Practice Pack — in engine-neutral mode it explicitly notes which concerns went unchecked.

## References (load on demand)

Workspace references (engine-neutral, always available):

- `references/breakdown-handoff.md` — format of the `/breakdown` handoff block, with routing to `schemagen` for DDL steps.
- `references/coherence-and-conventions.md` — naming, grouping, deploy order, dead code, documentation. Stack-neutral cross-file checks.

Practice-Pack references (engine-specific, loaded from the active database Practice Pack — example file names from `@default/practice-packs/database/postgres/`):

- `relational-patterns.md` — domain modelling, multi-tenancy, audit/log separation, key strategy.
- `attributes-and-types.md` — column types, nullability, defaults, timestamp policy.
- `constraints-and-integrity.md` — PK, FK (with cascade), UNIQUE, NOT NULL, CHECK.
- `indexing-and-performance.md` — missing/duplicate/redundant indexes, FK indexing, view-join support.
- `views.md` — view shape, performance, break-risk, materialisation opportunities.
- `functions-plpgsql.md` (or engine equivalent) — stored-function correctness, volatility labelling, exception handling, dynamic SQL, definer-rights hygiene.

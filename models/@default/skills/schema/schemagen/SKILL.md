---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:schema:schemagen"
  name: schemagen
  description: "Produces the smallest schema change for a requested evolution, plus the spec and code updates that follow from it."
  version: 2.0.0
  owner: gatblau
description: Produce a database schema change (migration up/down pair) plus the downstream updates it requires — Phase 2C shared types, Phase 3 component data models, and the list of codegen re-invocations needed. Validates the migration against a scratch database before proposing. Stack-neutral migration shell — engine-specific templates, scratch-DB tooling, and engine-specific change-type addenda come from the active database Practice Pack; without one the skill stops and asks the user. Trigger on phrases like "add column X to table Y", "new migration for Z", "schemagen", "change schema to support W", or when the user asks for a schema evolution. Do NOT trigger on drift-detection requests (that is sync-check) or on initial schema creation from specs (that is codegen B7).
---

# schemagen — Schema change with downstream updates

Produce the minimal schema change that implements a requested evolution, plus the spec and code updates that ripple from it. Heavy integration with the `sql-safety` layer rule — this skill is the reason that layer exists.

> **Guardrails:** destructive migrations require human approval (`migration.destructive`, gated by a Safeguard waiver).

This skill is **stack-neutral**. The skill names no database engine. Engine-specific concerns — exact migration template syntax, transactional-DDL semantics, lock behaviour, scratch-DB validation tooling, fast-path eligibility, enum-removal limits — live in the active **database Practice Pack** (e.g. `@default/practice-packs/database/postgres`). Without a database Practice Pack the skill **stops and asks the user** at Phase 3 — there is no useful "engine-neutral migration" output. The neutral parts (change-type classification, downstream-ripple analysis, paired up/down requirement, multi-step patterns) are workspace-level.

## Arguments

- `change` (required): description of the desired schema change. Accepts natural language ("add column `email` to `users`"), a target state ("users should have an email column, NOT NULL, unique"), or a Phase 2D env var / Phase 3 Data Model delta from a spec.
- `migrations-dir`: default supplied by the active database Practice Pack (typically `migrations/`, `db/migrations/`, or `schema/migrations/`); override per project layout.
- `mode`: `propose` (default — produce migration + spec deltas, do not write) | `write` (write the files after user confirmation on each destructive change).

## Active modes

**Plan → Patch → Review**, with the `sql-safety` layer rule always-on.

- **Plan** for the proposal phase: read the current schema, draft the migration up/down pair and the ripple table (Phase 2C / Phase 3 spec deltas, codegen re-invocation list). Outputs are proposed artefacts, not yet committed.
- **Patch** for `mode: write`: the migration file and downstream spec deltas are written to disk after explicit user confirmation on each destructive change.
- **Review** for Phase 5: round-trip the migration on a scratch database, confirm up/down symmetry, surface rollback considerations.

The skill enters **Execute** transiently inside the scratch-DB round-trip (sandboxed dry-run only — no real apply against a shared database; that is a user action). **Escalate** stops the skill on a destructive change without an approved Safeguard waiver, on a scratch round-trip failure, and **on the absence of a database Practice Pack** (the skill cannot produce a migration without engine-specific templates and validation tooling). `sql-safety` is non-optional — destructive changes carry an explicit ROLLBACK CONSIDERATIONS block.

## Hard rules (layered over sql-safety)

- **Every change ships as a pair.** A forward migration file plus a reverse migration file in the project's idiomatic naming. The down must be a true reverse of the up.
- **Never invent object names.** Tables, columns, indexes, constraints must be verified against existing SQL files before referencing them. If the requested change touches an object not found in the project's schema directory, stop and tell the user.
- **Destructive changes surface rollback considerations.** DROP COLUMN, DROP TABLE, ALTER TYPE with data loss, NOT NULL backfills on populated tables — each requires an explicit rollback note at the top of the up migration and a warning in the summary.
- **Additive first, then backfill, then constrain.** For NOT NULL additions on populated tables, propose three migrations, not one: (1) add column nullable, (2) backfill, (3) add NOT NULL. The user picks whether to collapse or keep separate based on table size.
- **No migration without a database Practice Pack.** The skill cannot produce safe SQL without engine-specific templates and lock-aware notes. Stop and ask the user to install one.

## Process

### Phase 1 — Parse the change
Load `references/change-types.md`. Classify the request into one of:

| Type | Examples |
|---|---|
| Additive | Add column (nullable), add table, add index, add extension |
| Extension | Widen a type, raise precision |
| Destructive | DROP column/table/index, NOT NULL on populated column, ALTER TYPE narrowing, remove enum value |
| Rename | Rename column/table (non-destructive but ripple-heavy) |
| Constraint | Add/drop FK, UNIQUE, CHECK |

Also load the active database Practice Pack's `change-types-addenda.md` (if present) for engine-specific refinements (lock strengths, fast-path eligibility, non-blocking variants, version dependencies, engine-specific destructive limits).

State the classification in the output. Destructive and rename changes get extra scrutiny. State the active database Practice Pack's id and engine version in the report header.

### Phase 2 — Verify current state
Read the existing schema for the affected tables in the project's schema directory. Read the specific files involved, not the whole tree. Record:

- Exact current column definitions (name, type, nullability, default, constraints).
- Indexes touching the column.
- Foreign keys referencing the column or table.
- Views, functions, or triggers referencing the column.
- Rows count if known (ask the user for production scale if not stated — affects backfill strategy).

If anything the change refers to is not found, stop and list the missing objects. Never infer names from pattern ("there's probably a column named X").

### Phase 3 — Design the migration
Load the active database Practice Pack's `migration-templates.md`. Construct:

- **Timestamp:** `YYYYMMDDHHMMSS` in UTC at the moment of generation.
- **Name:** short kebab-case description of the change (e.g. `add-email-to-users`).
- **Up SQL:** parameterised, explicit. Apply the engine's transactional-DDL conventions exactly as the Practice Pack's templates show — including the cases where transactions are forbidden (e.g. concurrent index creation in some engines).
- **Down SQL:** the true inverse. Where true inverse is impossible (e.g. you cannot recover dropped data), the down restores structure but cannot restore data — mark this explicitly at the top of the down file.

For destructive or rename changes, write the up file with a `ROLLBACK CONSIDERATIONS` block as defined in the Practice Pack's templates, including the lock-awareness notes from `change-types-addenda.md`.

If no database Practice Pack is installed, **stop here**. The skill has no engine-specific template to apply. Ask the user to install a database Practice Pack (e.g. `@default/practice-packs/database/postgres`).

### Phase 4 — Downstream ripple analysis
Load `references/downstream-updates.md`. Cross-reference the change against:

- **Phase 2C Shared Types** in `docs/spec/phase-2-architecture.md` — if the affected table has a corresponding shared type, list the field additions/removals/renames needed. The exact serialisation-tag form (Go struct tags, TypeScript decorators, Python dataclass annotations, …) comes from the active language Practice Pack's `annotation-conventions.md`.
- **Phase 3 Data Model sections** in `docs/spec/phase-3-components.md` (or `docs/spec/components/*.md`) — list every component spec whose Data Model references the changed table. Those specs need an edit.
- **Codegen components** — list the components whose generated code needs regeneration. Give exact `/codegen step: "<N>: <Component>"` invocations. The component-directory layout comes from the language Practice Pack's `file-layout.md`.
- **Handler/API impact** — if the change affects request/response shape, list the handlers that need updating and the Phase 3 API contract section to revise.
- **Test impact** — existing integration tests that exercise the table may need fixture updates.

Produce the ripple table per `references/downstream-updates.md`.

### Phase 5 — Scratch-DB validation
Load the active database Practice Pack's `scratch-validation.md`. Run the round-trip script the Practice Pack defines (it spins up a throwaway engine instance, applies the existing baseline, applies the proposed up, applies the proposed down, re-applies the up, and tears down). The script is engine-specific because the bring-up tooling, readiness probe, and introspection commands are engine-specific.

If any step fails, fix the migration and re-run. Do not propose a migration that has not round-tripped up → down → up successfully on a scratch DB.

For large / destructive migrations, the scratch validation confirms the SQL parses and executes — it does NOT confirm the migration is safe under production load. State that distinction in the summary, citing the lock-awareness notes from the Practice Pack's `change-types-addenda.md`.

### Phase 6 — Propose or write
Produce the final output:

- The two migration files (paths + full content).
- The ripple table.
- The scratch validation result.
- The exact `/codegen` invocations needed to regenerate affected components.
- For destructive changes, an explicit "DESTRUCTIVE — confirm before writing" prompt.

In `mode: propose`: stop. The user reviews and approves.

In `mode: write`: for each destructive change, ask for explicit approval before writing. Write the migration files. Do not edit spec or code files directly — the ripple table tells the user (or the next skill invocation) what to edit.

## Output file naming

The migration file extension and timestamp convention come from the active database Practice Pack's `migration-templates.md`. Examples of what a Practice Pack might supply:

- *(Postgres pack)* `<migrations-dir>/<YYYYMMDDHHMMSS>_<name>.up.sql` + `.down.sql`.
- *(MySQL pack)* could use the same `up.sql` / `down.sql` convention or follow a tool-specific format (Flyway `V<version>__<name>.sql`, Liquibase changesets, …).

Inspect the project's existing migrations directory before writing. If the migrations pattern is not already established, confirm the destination with the user.

## References (load on demand)

Workspace references (stack-neutral, always available):

- `references/change-types.md` — classification rules for schema change types. Load at Phase 1.
- `references/downstream-updates.md` — where ripple effects land (specs, code, tests). Load at Phase 4.

Database Practice Pack references (engine-specific, loaded from the active database Practice Pack — example file names from `@default/practice-packs/database/postgres/`):

- `migration-templates.md` — `up` / `down` templates per change type, with engine-specific syntax and transactional conventions.
- `scratch-validation.md` — end-to-end scratch DB flow: bring-up tooling, readiness probe, round-trip script, introspection commands.
- `change-types-addenda.md` — engine-specific refinements: lock strengths, fast-path eligibility, non-blocking variants, version dependencies, destructive limits.

## What schemagen does not do

- Does not write application code (use `/codegen` for the regeneration the ripple table points to).
- Does not edit spec files directly (surface the required edits; human or specgen owns the write).
- Does not run migrations against non-scratch databases — never against staging, never against production.
- Does not reorganise the existing schema layout.
- Does not produce a migration without an active database Practice Pack — the skill stops and asks the user.

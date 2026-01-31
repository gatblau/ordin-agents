# Schema change classification

Use this reference at Phase 1 to classify the requested change. Classification drives template choice (Phase 3) and ripple-depth (Phase 4).

This reference is **stack-neutral**. The classes (Additive, Extension, Destructive, Rename, Constraint) and the multi-step patterns apply to any SQL engine. Engine-specific addenda (e.g. Postgres locking behaviour, MySQL online-DDL semantics, SQLite's `ALTER` limits) live in the active database Practice Pack — typically a `change-types-addenda.md` reference. Read both when classifying.

## Additive (low risk)

Safe, reversible, no data at risk.

- `ADD COLUMN` nullable, no default OR with constant default (subject to the engine's fast-path support — see Practice Pack addenda).
- `CREATE TABLE`.
- `CREATE INDEX` (the engine may offer a non-blocking variant — `CONCURRENTLY` in Postgres, `ALGORITHM=INPLACE, LOCK=NONE` in MySQL — preferred on populated tables; the Practice Pack documents what the engine supports).
- Adding a new enum value (engine-specific syntax; some engines require type recreation).
- Engine-specific extensions that are reversible (`CREATE EXTENSION` in Postgres, `INSTALL` plugins, etc.).

Down-migration: straightforward `DROP`.

## Extension (low risk with caveats)

- Widening a type (`VARCHAR(100)` → `VARCHAR(200)`, `INT` → `BIGINT`): generally safe, but rewrites the table on some engines — note if the table is large.
- Raising a precision (`NUMERIC(10,2)` → `NUMERIC(14,2)`).

Down-migration: may truncate data; always mark as lossy.

## Destructive (high risk)

Requires ROLLBACK CONSIDERATIONS block in up.sql and explicit user approval.

- `DROP COLUMN` / `DROP TABLE` / `DROP INDEX`.
- `ALTER COLUMN TYPE` narrowing (`BIGINT` → `INT`, `TEXT` → `VARCHAR(50)`).
- Adding `NOT NULL` to a populated nullable column.
- Removing an enum value (engine-specific — many engines do not support direct removal; the Practice Pack addenda documents the engine's behaviour and recovery path).
- Changing a column default when application relies on existing default.

Down-migration restores structure but cannot restore data. Mark explicitly.

## Rename (non-destructive, ripple-heavy)

- `ALTER TABLE ... RENAME COLUMN` / `RENAME TO`.
- `ALTER INDEX ... RENAME TO`.

Breaks every consumer referencing the old name. Ripple table must be exhaustive — every spec, every `SELECT`, every ORM binding.

## Constraint

- Add/drop `FOREIGN KEY`, `UNIQUE`, `CHECK`, `PRIMARY KEY`.
- Adding FK or UNIQUE on a populated table may fail if existing rows violate — always validate on scratch DB with representative data if possible.
- Some engines support a two-step add (`ADD CONSTRAINT ... NOT VALID` then `VALIDATE CONSTRAINT`) that avoids long-held strong locks; the Practice Pack documents what the engine supports.
- Dropping a constraint is reversible only if the constraint was explicitly named (otherwise the generated name must be looked up).

## Multi-step patterns

Certain single-intent changes must be split into multiple migrations:

### NOT NULL on populated column
1. Add column nullable with a default (or leave nullable).
2. Backfill existing rows.
3. Add NOT NULL constraint.

### Column rename with zero-downtime consumers
1. Add new column.
2. Dual-write in app.
3. Backfill.
4. Switch reads.
5. Drop old column.

Schemagen proposes the migrations; the user decides whether to collapse based on deployment constraints.

### Type narrowing with validation
1. Add CHECK constraint enforcing the narrower range.
2. Validate (may be slow).
3. Alter type.
4. Drop CHECK.

## Engine-specific addenda

For each classification class, the active database Practice Pack contributes engine-specific notes:

- **Lock strengths** — what lock the statement acquires and for how long.
- **Fast-path eligibility** — which `ADD COLUMN ... DEFAULT` shapes avoid a table rewrite.
- **Non-blocking variants** — concurrency-friendly forms of `CREATE INDEX`, `ADD CONSTRAINT`, etc.
- **Engine version dependencies** — which features require which minimum engine version.
- **Engine-specific destructive limits** — e.g. enum-value removal, partition-key changes, system-catalogue restrictions.

The Postgres pack supplies these as `@default/practice-packs/database/postgres/change-types-addenda.md`. Other engine packs follow the same naming convention.

## Classification output

State in the final summary:
```
Classification: <Additive|Extension|Destructive|Rename|Constraint>
Multi-step: <yes|no>  (if yes, list the steps)
Reversible: <fully|structure-only|not>
Engine-specific notes: <pack reference cited|none — engine-neutral mode>
```

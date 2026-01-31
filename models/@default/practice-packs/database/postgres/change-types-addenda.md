# Change types — Postgres addenda

Cited by `urn:ordin:default:skills:schema:schemagen` Phase 1. The workspace skill ships a stack-neutral change-type classification (`change-types.md`); this file adds Postgres-specific notes that refine the classification at the engine level.

Read this file alongside the workspace's `change-types.md`, not in place of it.

## Additive — Postgres specifics

- **`ADD COLUMN ... DEFAULT <const>`** — fast path on PG11+. Does not rewrite the table. Earlier versions rewrite — flag if the project pins an older PG.
- **`CREATE INDEX CONCURRENTLY`** — preferred on populated tables; cannot run inside a transaction (`BEGIN`/`COMMIT`). The migration template under `migration-templates.md` omits the transaction block for this case.
- **`CREATE EXTENSION IF NOT EXISTS`** — additive; reversible with `DROP EXTENSION` only when no other object depends on it.

## Extension — Postgres specifics

- **Widening a type** (`VARCHAR(N)` → `VARCHAR(M)`, `INT` → `BIGINT`) does **not** rewrite the table for compatible widenings (PG12+ for many cases). It does rewrite for narrowings or for type-class changes — flag accordingly.
- **`NUMERIC(p, s)` precision raise** is metadata-only.

## Destructive — Postgres specifics

- **Removing an enum value** is not directly supported. The down migration is a no-op with an explanatory comment; reversion requires recreating the enum type and updating every dependent column. The template's "Enum — add value" pair encodes this.
- **`ALTER COLUMN TYPE`** narrowing rewrites the table and acquires an `ACCESS EXCLUSIVE` lock — never safe under production write load.
- **`ADD NOT NULL`** to a populated nullable column scans the whole table under `ACCESS EXCLUSIVE` (PG11+ supports a constant-default fast path on `ADD COLUMN ... DEFAULT NOT NULL` but not on existing columns). Always use the three-step pattern from the workspace's `change-types.md` §"NOT NULL on populated column".

## Transactional DDL

Postgres supports DDL inside a transaction (`BEGIN ... COMMIT`) for almost all statements. Exceptions:

- `CREATE INDEX CONCURRENTLY` and `DROP INDEX CONCURRENTLY` — must run outside a transaction.
- `VACUUM`, `ANALYZE`, `REINDEX` (without `CONCURRENTLY`) — administrative, not DDL.
- Some `ALTER TYPE` operations on enums in older versions.

The migration templates wrap every statement in `BEGIN; ... COMMIT;` by default, with the noted exceptions called out per template.

## Lock awareness

Postgres acquires locks at varying strengths. The most common gotchas the migration must surface in its `ROLLBACK CONSIDERATIONS` block:

| Statement | Lock | Production hazard |
|---|---|---|
| `ALTER TABLE ... ADD COLUMN` (no default) | `ACCESS EXCLUSIVE`, brief | Brief blip — usually fine |
| `ALTER TABLE ... ADD COLUMN ... DEFAULT <const>` (PG11+) | `ACCESS EXCLUSIVE`, brief | Brief blip on the metadata change |
| `ALTER TABLE ... ADD COLUMN ... DEFAULT <volatile>` | `ACCESS EXCLUSIVE` for the duration of the rewrite | Avoid; split into add-nullable / backfill / constrain |
| `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL` | `ACCESS EXCLUSIVE` for the duration of the validation scan | Avoid on populated tables; use the three-step pattern with `ADD CONSTRAINT ... NOT VALID` then `VALIDATE CONSTRAINT` if available |
| `ALTER TABLE ... ALTER COLUMN ... TYPE` | `ACCESS EXCLUSIVE` for the rewrite | Production-hazardous; use a multi-step add-then-backfill-then-swap |
| `CREATE INDEX` | `SHARE` | Blocks writes — use `CONCURRENTLY` on populated tables |
| `CREATE INDEX CONCURRENTLY` | None blocking | Slow; can fail and leave invalid index — verify with `\di` |
| `ALTER TABLE ... ADD CONSTRAINT FOREIGN KEY ... NOT VALID` then `VALIDATE CONSTRAINT` | brief lock on `ADD`, `ROW SHARE` on `VALIDATE` | Preferred over single-step `ADD FOREIGN KEY` on populated tables |

Surface the relevant row in the `ROLLBACK CONSIDERATIONS` block when proposing the migration.

## Engine version detection

Read the project's `docker-compose.yml`, Helm chart, or `postgres:*` Dockerfile pin to determine the engine version. If multiple versions are pinned, ask the user. The version determines:

- Whether `ADD COLUMN ... DEFAULT <const>` is fast-path (PG11+).
- Whether `ALTER TYPE ... ADD VALUE` runs in a transaction (PG12+).
- Whether `MERGE` is available (PG15+).
- Whether `CREATE INDEX CONCURRENTLY` supports `IF NOT EXISTS` (PG11+).

Record the detected version in the `schemagen` report header.

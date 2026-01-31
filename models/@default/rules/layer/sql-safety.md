---
apiVersion: ai.enterprise/v1
kind: rule-layer
metadata:
  id: "urn:ordin:default:rules:layer:sql-safety"
  name: SQL & schema safety
  description: "Never treat a SQL table, column, index, or constraint name as real unless it is directly visible, and flag rollback risks for destructive changes."
  version: 1.0.0
  owner: gatblau
---

# SQL & schema safety (layer rule)

A **layer rule**: composes on top of whichever of the nine modes (`@default/rules/orchestrators/working-modes.md`) is active whenever the work touches SQL files, database migrations, or schema definitions. It does not replace the active mode; it adds non-negotiable constraints on top of it.

Activate automatically on edits to or reasoning about: `**/*.sql`, `schema/**`, `db/**`, `database/**`, `migrations/**`. Adapt the globs to the host project as needed.

## Constraints

- Never present a table / column / index / trigger / view / constraint / procedure / function name as verified unless it is directly visible in the repo or command output. Do not infer SQL object names from naming patterns. (Aligned with the `identifier-verification` layer rule.)
- Before proposing a migration or query change, verify the exact schema objects involved by reading the relevant SQL / migration file. If incomplete, mark assumptions as unverified and route them to *Gaps* or *Open Questions*.
- Prefer minimal changes over broad rewrites. Do not wrap SQL in new abstractions unless equivalents already exist in the codebase.
- For destructive changes (`DROP`, `ALTER` that loses data, `NOT NULL` backfills on populated tables, type narrowings, index removals on hot paths), surface rollback considerations explicitly. `schemagen` stops on a destructive change without an approved Safeguard waiver.
- Migrations against shared databases are user actions, not Patch / Execute outputs. Patch produces the migration file; Execute may dry-run it; the actual apply is the user.

## Mode interactions

- In **Observe** / **Review**: report verified schema facts vs unverified assumptions; never invent the missing pieces to complete the picture.
- In **Plan** (`schemagen`, `specgen` data-model section): every column, type, default, constraint, and index that appears in a spec must trace back to a verified source — repo, migration, or a Component spec it depends on.
- In **Patch** (`schemagen`, `codegen` for data-access code): only emit SQL whose objects are verified. Unverified objects route to `// SPEC-GAP-<N>:` and stop.
- In **Execute**: dry-run migrations only. Real applies against shared databases are excluded from the Execute allowlist.

## Output skeleton when SQL is in scope

`Verified schema facts` → `Unverified schema assumptions` → `Safe next step` (which mode handles which item).

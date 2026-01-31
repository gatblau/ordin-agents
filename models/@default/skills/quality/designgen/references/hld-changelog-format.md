# HLD changelog format (`99-changelog.md`)

`99-changelog.md` is the append-only audit trail of every HLD edit. Every edit, regardless of origin (direct edit, `/spec` HLD-impact-pass, applied RFC, applied RCA), appends one line. The file lives only in folder-form HLDs; single-file HLDs do not have a separate changelog (their git history is the audit trail).

## File header

```markdown
# <Feature> HLD — Changelog

Append-only. One line per edit, newest at the bottom. Format: `<date> — <origin>: <summary> → revision: <new-revision>`.
```

## Line format

```
<date> — <origin>: <summary> → revision: <new-revision>
```

- **`<date>`** — ISO date, `YYYY-MM-DD`. Use the date the edit was applied, not the date the originating work started.
- **`<origin>`** — one of:
  - `initial draft (designgen, mode=<mode>)` — the first write of the HLD.
  - `direct edit` — a human edit not driven by any skill.
  - `promoted from <phase-file>` — auto-amend by `/spec` HLD-impact-pass (e.g. `promoted from phase-3-component-payment-handler`).
  - `applied RFC <rfc-id>` — an RFC adoption that touched the HLD (e.g. `applied RFC 0042`).
  - `applied RCA <rca-id>` — an RCA that resulted in an HLD edit (e.g. `applied RCA 0017`).
- **`<summary>`** — one short sentence describing what changed. Examples: "added Component PaymentRouter", "ADR-007 signing key custody decision", "tenancy boundary moved to row-level", "added Glossary term `idempotency key`".
- **`<new-revision>`** — the HLD's new SemVer after the edit (the `revision:` value in the README preamble after the edit lands).

## Revision bump rules

(Repeated from `design-template.md` for convenience.)

- **Patch** — clarifications, typo fixes, prose expansion with no semantic change, single-row additions to Glossary / Assumptions.
- **Minor** — new ADR entries, new components, new tech-stack rows, new cross-cutting policies, new regulatory obligations, new principal sequences.
- **Major** — first promotion from *Draft* to *Approved*, or any change that invalidates an existing approved spec phase.

A single review block may carry multiple edits; the line written into the changelog is **one line per ratified edit**, with a single bump applied at the end of the block (i.e. four patch-level edits accumulated into one batch still produce four changelog lines and one final patch-revision bump).

## Examples

```
2026-01-12 — initial draft (designgen, mode=interview): bootstrapped HLD for payments-service → revision: 0.1.0
2026-01-13 — direct edit: corrected typo in Component Compiler responsibility → revision: 0.1.1
2026-01-14 — promoted from phase-3-component-registry: introduced Glossary term `RegistryIndex` → revision: 0.1.2
2026-01-15 — promoted from phase-4-cross-cutting-signing: ADR-007 ed25519 detached signature scheme → revision: 0.2.0
2026-01-15 — applied RFC 0011: tenancy boundary moved to row-level → revision: 0.3.0
2026-01-20 — direct edit: promoted from Draft to Approved → revision: 1.0.0
```

## What never goes in the changelog

- Edits to the changelog itself (it is append-only by hand).
- Spec-side edits (those live in `docs/spec/`'s own files and `phase-6-audit.md`).
- Code-side edits (those live in git history and PR descriptions).
- Conversations that did not result in an HLD edit. If a `/spec` HLD-impact-pass surfaced a candidate edit and the user rejected it, the line is **not** appended — the rejection is recorded in the spec phase as an Assumption with reduced confidence.

## How `/spec` writes to the changelog

When the HLD-impact-pass produces ratified edits, `specgen` appends one line per ratified edit at the end of the spec-phase review pass. The append is part of the same review block — the user approves both the spec output and the changelog appends together. See `@default/skills/quality/specgen/references/hld-impact-pass.md` §Output.

## How `sync-check` reads the changelog

`sync-check` does not enforce the changelog's content (humans audit it). It does enforce that every HLD revision bump in `README.md` has a corresponding line in `99-changelog.md` — a bump without a matching line is reported as **D-HLD-6 (changelog gap)**. See `@default/skills/sync/sync-check/references/drift-taxonomy.md`.

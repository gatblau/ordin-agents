# Classification rubric — the four signals

Canonical rubric for `triage`. Each signal is evaluated independently; any one turning positive forces Standard. A class proposal must be the most conservative class consistent with the signal readings.

## Signal 1 — File scope

**Question:** how many distinct components do the touched files (or, in the absence of a diff, the area named in the change description) belong to?

| Reading | Class implication |
|---|---|
| One component | Local-eligible |
| More than one component | Forces Standard |
| Cannot localise to a component | Forces Standard *and* escalate to clarifying question |

**Component boundary** is determined by the workspace's Component spec layout under `docs/spec/components/<area>.md`. Files map to a component if they fall under the path the Component spec declares as its source area. Where a component's source area is not declared, a Practice Pack convention applies; absent both, classify Standard.

## Signal 2 — Surface signal (`apidiff`)

**Question:** does the change alter any public surface — OpenAPI, gRPC, NATS subjects, or SQL public surfaces?

| Reading | Class implication |
|---|---|
| Zero changes on every surface | Local-eligible |
| Any non-zero on any surface | Forces Standard |
| `apidiff` cannot be run (no Practice Pack supplies the toolchain) | Forces Standard *and* note the unrun signal in the rationale |

The exact surfaces and the per-surface rules live in `@default/skills/analysis/apidiff/references/`. `triage` consumes the `apidiff` output rather than re-implementing the surface scan.

## Signal 3 — Schema signal

**Question:** does the change introduce any DDL change against any schema object?

| Reading | Class implication |
|---|---|
| No DDL changes in the diff | Local-eligible |
| Any CREATE / ALTER / DROP on any object | Forces Standard |
| Files under `schema/**` or `*.sql` modified, even with no detectable DDL change | Forces Standard (defensive) |

A schema-affecting change always belongs in the Standard lane because the Component spec's Data Model section needs full authoring, not an addendum.

## Signal 4 — Spec presence

**Question:** does an existing Component spec cover the affected area?

| Reading | Class implication |
|---|---|
| Spec exists at `docs/spec/components/<area>.md` (or equivalent) | Local-eligible |
| No Component spec exists for the area | Forces Standard |
| Spec exists but is in *Draft* status (Phase 6 audit not passed) | Forces Standard |

The Local lane appends a Change addendum to an existing approved Component spec. If there is no spec, or if the spec is not yet approved, there is nothing to addendum — full authoring is required, which is the Standard lane.

## Compound rules

- A change is classified **Local** when *all four* signals read Local-eligible *and* the diff does not match the Trivial-pattern set in `trivial-patterns.md`.
- A change is classified **Trivial** when *all four* signals read Local-eligible *and* every diff hunk matches a Trivial pattern.
- Any other reading is **Standard**.
- Ambiguity (signal cannot be read because tooling is unavailable, or the change description is too vague to localise) is **Standard**.

## HLD form (derived from class)

The class determines the shape of the HLD produced by `/design` (or amended by `/spec`'s HLD-impact-pass):

| Class | `hldForm` | HLD path |
|---|---|---|
| Standard | `folder` | `docs/design/<topic>/` with `README.md` + numbered child files + `99-changelog.md` per `@default/skills/quality/designgen/references/hld-folder-layout.md`. |
| Local | `single-file` | `docs/design/<topic>.md` with all sections inline. |
| Trivial | `single-file` | `docs/design/<topic>.md` with all sections inline. Often *no HLD is produced at all* — Trivial work usually targets an existing HLD with no edits, and produces only Scope attestations. |

The rule is straightforward: **Standard lane work touches enough surface that the HLD is easier to read split by topic; smaller-lane work does not justify the folder overhead.** Triage exposes `hldForm` so downstream skills (`designgen`, `specgen`, `sync-check`) do not need to re-derive the decision.

## Examples

- *"Add a retry budget to the payments client."* — File scope: one component (payments). Surface: zero (internal only). Schema: none. Spec presence: covered. Trivial pattern match: no (logic change). → **Local.**
- *"Bump `golang.org/x/net` to v0.55.0."* — File scope: `go.mod`/`go.sum` only, single dep. Surface: none. Schema: none. Spec presence: N/A (dep change does not touch a component). Trivial pattern match: in-range dep bump. → **Trivial.**
- *"Rename `OrderService.Place` to `OrderService.Submit` across the codebase."* — File scope: probably more than one component (caller files). Surface: gRPC method rename. Schema: none. Spec presence: covered. → **Standard** (file-scope and surface both fail).
- *"Fix typo in error message: `quanity` → `quantity`."* — File scope: one component. Surface: error string is part of the public surface if it is contractually documented; otherwise none. Schema: none. Spec presence: covered. → **Trivial** if the error string is internal; **Standard** if contractually documented.
- *"Add a new column to the `orders` table."* — Schema signal: DDL change. → **Standard.**

## What `triage` must never do

- Propose a class lower than the most pessimistic signal reading.
- Re-implement the `apidiff` surface scan or the schema-diff tool — always delegate.
- Decide that a missing signal can be safely assumed clear. Missing signals are always pessimistic.
- Override the user's escalation. If the user forces Standard, take Standard, even if signals are clear.

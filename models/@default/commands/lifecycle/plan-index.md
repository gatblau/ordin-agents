---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:lifecycle:plan-index"
  name: /plan-index
  version: 1.3.0
  owner: gatblau
  description: "Maintains a single derived roll-up of progress across all working plans."
description: Maintain docs/wip/plan/00-index.md — a single, auto-maintained, DERIVED roll-up of progress across every working plan, so overall status is visible in one place instead of being scattered across each plan's /apply status trail.
argument-hint: "[build | update <NN> | add <NN>] (default: build)"
---

# /plan-index — build & maintain the plan progress index

Maintains a single roll-up of progress across every working plan in `docs/wip/plan/`, so overall status is visible in one place instead of scattered across each plan's `/apply` status trail. The index is a **derived view** — each plan's own body remains the source of truth.

Parse the argument (all optional):
- **`build`** (default when empty) — rebuild the whole index by scanning every `docs/wip/plan/NN-*.md`.
- **`update <NN>`** — refresh only plan `NN`'s row and its Plan state entry (used by `/apply` after a phase, and by `/breakdown` for the parent plan).
- **`add <NN>`** — insert a row and a Plan state entry for a newly-created plan `NN` (used by `/breakdown` after writing a new plan file).

If the argument names an `<NN>` that has no `docs/wip/plan/NN-*.md`, stop and say so.

## Index location & identity

- **Path:** `docs/wip/plan/00-index.md` (sorts first; the `00-` ordinal is reserved for the index and is never a plan).
- Transient and gitignored, exactly like the plans it summarises. It is never committed and never treated as authoritative — if it disagrees with a plan body, the plan body wins and the index is re-derived.

## Active modes

**Observe → Plan.** Observe to read each plan's status trail; Plan to author the index file. The `identifier-verification` layer rule is active: a phase's status is recorded **only** from what the plan text states. A phase with no status marker is `❔ unknown` — never a guess. Do not invent commit hashes, follow-up ids, or lineage edges that the plan does not state.

The command writes exactly one file (`00-index.md`) and nothing else. It never edits plan bodies, source, or config. It never commits.

## Index format contract

The file has six sections, in order. Preserve this shape on every rebuild.

1. **Header** — a one-line `_Snapshot: <date> · …_` note stating it is derived, names `/plan-index` as the refresh command, and that plan bodies are authoritative.
2. **Status legend** — the glyph table below (verbatim).
3. **Lineage** — a fenced ASCII tree grouping plans into families, each child annotated with its `[source]` edge (parent plan / FU id, or the `[…root]` / standalone marker). Build edges from each plan's `**Source:**` / `scheduled-in:` fields only.
4. **Roll-up** — one row per plan:
   `| Plan | Title | Scope | Done | Phase strip | Open FUs | Committed |`

   The table carries no free-text column. Every cell is short and fixed-shape, so each row stays one line high and the table reads at a glance. Narrative about a plan belongs in Plan state (section 6), never in the table.

   - **Done** — `<fully-done>/<total>` phases (only `✅` counts as done; `🟡`/`⏳`/`⏸`/`↗`/`🔒`/`⬜`/`❔` do not).
   - **Phase strip** — one glyph per phase, in phase order, from the legend.
   - **Open FUs** — count of follow-up entries whose `status:` is `open` (or the plan's stated count).
   - **Committed** — a commit hash if the trail records one (`✅ <hash>`), `partial (<hash>)` if only some phases cite one, `⬜ working tree` if explicitly uncommitted, else `—`.
5. **⚠ Needs attention** — bulleted list of every P0, `operator-gated`, `blocking`, or `blocked` item pulled from the plans, each naming its plan + id.
6. **Plan state** — one entry per plan, in plan-ordinal order, matching the rows of the roll-up table one for one. Each entry is a bullet of the form:

   `- **NN** — <state note>`

   - The **state note** gives the headline blocker or completion note: what is done, what is outstanding, and what it waits on. Keep it to one to three sentences; move longer narrative back to the plan body.
   - Name phases and follow-ups by id (`P5`, `FU-012`) so the reader can match the note to the strip in the table.
   - Every plan in the table has an entry, even a finished one (`- **03** — Complete.`). A missing entry is a defect.

Optionally follow with a short **Family summary** paragraph per family.

### Status legend (verbatim)

| Glyph | Meaning |
|---|---|
| ✅ | done — applied, exit criteria met |
| 🟡 | partial — landed with a deferred sub-item |
| ⏳ | gate-pending — code-complete, a real gate/verification still outstanding |
| ⏸ | deferred — consciously not done (premise void, or moved to a follow-up) |
| ↗ | relocated — moved to another plan (arrow names it) |
| 🔒 | operator-gated — blocked on a human/shared-state action the agent cannot perform |
| ⬜ | not-started |
| ❔ | unknown — no status marker recorded in the plan trail |

## Extraction procedure (per plan, for `build`)

1. Read the plan file. Record: title (H1), total phase count (`### Phase`/`#### Phase` headings), `**Source:**` and any `scheduled-in:` edges, and the scope/repo if stated.
2. For each phase, classify its glyph from the nearest status evidence in the body or the `/apply` follow-up trail:
   - explicit `LANDED`/`DONE`/`complete` + exit criteria met → `✅`
   - landed but a listed sub-change deferred → `🟡`
   - code done, a real gate not run → `⏳`
   - consciously skipped / premise void → `⏸`
   - `MOVED`/`RELOCATED` to plan M → `↗M`
   - blocked on an operator/shared-state action → `🔒`
   - no work + no marker → `⬜`
   - no marker at all → `❔`
   For large plans, dispatch one read-only `Explore` agent per plan (or small group) in parallel and have each return the compact per-plan block; assemble the rows yourself. Do not fabricate — an agent that finds no marker returns `❔`.
3. Count `status: open` follow-ups; collect P0/operator/blocking items for the attention section.
4. Build lineage edges from Source/scheduled-in only.

For `update <NN>` / `add <NN>`, re-derive just that plan's row and Plan state entry (and, for `add`, its lineage edge + the parent's edge) and splice them in, leaving every other row and Plan state entry byte-for-byte unchanged.

## Invocation by other commands

- **`/breakdown`** calls `/plan-index add <NN>` after writing a new plan file (and creates `00-index.md` via `build` if it is absent), and `/plan-index update <parent-NN>` when the breakdown scheduled a parent's entry.
- **`/apply`** calls `/plan-index update <NN>` after persisting follow-ups, so the applied phase's new glyph, done/total, commit hash, and follow-up count are reflected.

## Output

Reply with: the index path, a one-line summary of what changed (rows added/updated), and the current headline (e.g. "9/15 plans complete or near-complete; 6 with open operator/P0 items"). Do not commit.

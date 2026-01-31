---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:sync:sync-spec"
  name: sync-spec
  description: "Fixes drift in the code-to-spec direction, updating the spec to match an accepted code change."
  version: 1.2.0
  owner: gatblau
description: Reconcile spec and code in the *code → spec* direction after a `sync-check` report has detected drift and the user has confirmed the spec is the side that should change. Updates Component specs, Cross-cutting specs, or the Spec preamble to match the current source of truth in code. Read both sides; write only to specs. Stops on any conflict where both sides have diverged from a common ancestor in disagreeing ways. Invoke explicitly — trigger only on imperative phrases like "run sync-spec", "reconcile spec to code", "update spec from code", or /sync-spec. Do NOT trigger on ambiguous prompts like "fix the drift" without a stated direction.
---

# sync-spec — code → spec reconciliation

`sync-spec` is the procedure invoked by the **`/sync-spec`** slash command — the resolver for drift in the *code → spec* direction. The command (in `@default/commands/sync/sync-spec.md`) is the user-facing surface; this skill is the canonical procedure behind it. The opposite direction (*spec → code*) is handled by `/sync-code`. For *intent-changing* drift, the right path is `/spec`, not this skill.

Resolve drift detected by `sync-check` by updating the spec to reflect what the code now does. The skill never picks the direction; the user does.

> **Guardrails:** writes specs/design only — never source (`src/**`, `internal/**`, `pkg/**`, `lib/**`, `schema/**`, `migrations/**`); the sync direction must be user-confirmed.

## Active modes

**Sync → Review.**

- **Sync** for the reconciliation itself: read both spec and code, propose patches to the spec only.
- **Review** for the final pass: rerun `sync-check` and confirm the targeted findings are resolved without introducing new ones.

The skill enters **Escalate** on any conflict it cannot resolve without inventing intent (see *Stop conditions*). It never enters **Patch** — code edits are out of scope.

## Inputs

- `sync-check-report`: path to a `sync-check` report from a recent run, or the report inline in conversation context. Required. The skill refuses to run without one.
- `direction`: must be `code-to-spec`. Any other value stops the skill and points the user at `/sync-code`.
- `scope`: optional. `all` (default) | `<component-name>` | `cross-cutting` | `preamble`. Limits which findings are addressed.

## What gets written

| Target | When | Source of truth |
|---|---|---|
| Component spec — Public Interface, Data Model, Error Table | A signature, field, route, status code, error code, or DDL row drifted from the code | Code |
| Component spec — Internal Logic | A step changed and the code is the accepted version | Code |
| Component spec — Gherkin Acceptance Criteria | An accepted edge case or new error path is now in the code but not the spec | Code |
| Cross-cutting spec | The cross-cutting policy itself changed (logging format, auth header, retry policy) and the code is correct | Code |
| Spec preamble — Assumptions or Glossary | An assumption is now contradicted by the code in an accepted way | Code |
| Component spec — **Approach**, **Purpose** | Almost never. These describe intent, not state. Drift here usually means INTENT-DRIFT and routes back to `designgen`, not Sync. | (escalate) |

The skill writes nothing to source files, schema files, or migrations. Those are `/sync-code` territory.

## Process

### Step 1 — Load the report

Read the `sync-check-report`. If absent, stop and tell the user to run `/sync-check` first. Confirm the report has at least one finding labelled **REALITY-DRIFT** or **CONTRACT-DRIFT** in the *spec is stale* direction. If every finding is INTENT-DRIFT, stop — that is `designgen` work, not Sync.

### Step 2 — Confirm direction with the user

State, in one sentence per finding to be addressed, what will change in which spec file and why. Stop and wait for the user to confirm. Do not proceed on implicit consent. If the user nominates a different finding or a different direction, restart from Step 1 with the new scope.

### Step 3 — Classify each finding

Load `references/conflict-taxonomy.md`. For every finding in scope, attach one of the four labels (INTENT-DRIFT, CONTRACT-DRIFT, REALITY-DRIFT, SCOPE-GAP) and the resolution path. Findings that resolve to "stop and escalate" per the taxonomy are removed from the work list and reported.

### Step 4 — Apply spec updates

For each finding remaining in the work list:

1. Read the affected spec file in full.
2. Read the code that is now the source of truth.
3. Edit the spec section that drifted, and only that section. Keep the rest of the spec untouched.
4. Where the code reveals a new error path, add a row to the Error Table; if it reveals a new edge case, add a Gherkin scenario. Do not invent rows the code does not justify.
5. Apply the authoring rules of `plan-mode` (no banned phrases, atomic & self-contained, errors first-class, active locale per `urn:ordin:default:rules:layer:output-language`).

### Step 5 — Rerun `sync-check`

Run `sync-check` over the same scope. Confirm the targeted findings now report as resolved. New findings introduced by the spec edits are a Step 4 defect — fix or revert.

### Step 6 — Report

Output: list of findings addressed (with label, spec file, summary of edit), list of findings escalated (with reason), `sync-check` rerun summary. The user reviews and commits the spec changes — sync-spec never commits.

## Stop conditions

The skill stops, surfaces an Escalate output, and writes nothing further when:

- The user has not confirmed `direction = code-to-spec`. Suggested next: `/sync-code` for the opposite direction, or restart with explicit confirmation.
- A finding is INTENT-DRIFT (the design itself changed). Suggested next: `designgen` to update the design, then `/spec` to derive new specs.
- A finding is CONTRACT-DRIFT *and the spec is correct* (code is the stale side). Suggested next: `/sync-code` for that finding.
- A finding is REALITY-DRIFT *and both sides have changed in disagreeing ways since the last common state* (true conflict). Suggested next: user adjudication; either revert one side or author a Cross-cutting spec change that reconciles both.
- A spec edit would require inventing an identifier not present in the code or in an Approved spec. Suggested next: route to *Gaps* and stop.
- A Component spec change would contradict an Approved Cross-cutting spec. Suggested next: change the Cross-cutting spec first; cross-cutting wins by default over component-level drift.

## What this skill does not do

- Pick the direction. The user nominates `code-to-spec` explicitly.
- Edit code, schema, or migrations.
- Run `codegen` or `testgen`. That sequence is `/sync-code`.
- Auto-apply patches. Every spec edit is proposed; the user reviews and writes the commit.
- Resolve INTENT-DRIFT. Intent changes flow back through `designgen` → `/spec`, not through Sync.

## References (load on demand)

- `references/conflict-taxonomy.md` — the four conflict labels with definitions, evidence, resolution path, and the stop-vs-proceed rule for each. Load at the start of Step 3.

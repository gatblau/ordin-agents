---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:sync:sync-code"
  name: sync-code
  description: "Fixes drift in the spec-to-code direction, regenerating the code the updated spec now needs."
  version: 1.0.0
  owner: gatblau
description: Push a spec change forward into code by chaining Sync → codegen → testgen → sync-check. Use after a Component, Cross-cutting, or Preamble spec has been updated and the affected code must follow. Stops on any conflict at any sub-stage. Invoke explicitly — trigger only on imperative phrases like "run sync-code", "propagate spec change to code", "push spec forward", or /sync-code. Do NOT trigger on ambiguous prompts like "update everything" without a stated direction.
---

# sync-code — spec → code reconciliation

`sync-code` is the procedure invoked by the **`/sync-code`** slash command — the resolver for drift in the *spec → code* direction. The command (in `@default/commands/sync/sync-code.md`) is the user-facing surface; this skill is the canonical procedure behind it. The opposite direction (*code → spec*) is handled by `/sync-spec`. For *intent-changing* drift, the right path is `/spec` first, then this skill.

> **Guardrails:** writes source and tests only — never specs (`docs/spec/**`) or design (`docs/design/**`); the sync direction must be user-confirmed before any patch.

Resolve drift detected by `sync-check` (or anticipated after a deliberate spec edit) by regenerating or amending source code to match the updated spec. The skill never picks the direction; the user does.

## Active modes

**Sync → Patch → Review.**

- **Sync** to identify which Playbook steps the spec change affects and to confirm the direction is `spec-to-code`.
- **Patch** to invoke `codegen` per affected Playbook step and produce updated source.
- **Review** to run `testgen`, run `/sync-check` again, and confirm the spec and code now agree.

The skill enters **Execute** transiently inside `codegen` and `testgen` (their verification gates) and **Escalate** on any stop condition. It never enters **Plan** — the spec is already authored; this skill consumes it.

## Direction is fixed

This skill operates strictly in the *spec → code* direction. The opposite direction (code → spec) is `/sync-spec`. If the user invokes `/sync-code` when the actual direction needed is code → spec (the spec is correct; the code is the accepted state), stop and point them at `/sync-spec`.

## Inputs

- `spec`: path to the updated spec file (e.g. `docs/spec/components/user-service.md`), or a component name that resolves to its declared `**File:**` path. Required.
- `scope`: optional. `components` (default — affected component specs only) | `cross-cutting` (a Cross-cutting spec changed; every component touching the concern is in scope) | `preamble` (an Assumption or Glossary entry changed; the whole spec set may be affected).

If the spec source is missing or ambiguous, ask the user once and stop. Do not pick the "most recently edited spec" on your own.

## Process

### Step 1 — Load the updated spec
- Read the spec file at the supplied path (or the path declared by the named component).
- Confirm the spec is in *Approved* state. If it is *Draft*, stop and tell the user to run the `/spec` Phase 6 self-audit and promote first — `/sync-code` does not consume Draft specs.
- If the spec has a non-empty *Gaps* section, stop. Gaps must be resolved before code can be regenerated.

### Step 2 — Identify affected Playbook steps
- Read the Generation Playbook (the Phase 5 spec).
- For `scope: components`: list the Playbook steps that build or import the changed component.
- For `scope: cross-cutting`: list every Playbook step whose component touches the cross-cutting concern (auth, logging, retry policy, etc.) named in the changed spec.
- For `scope: preamble`: identify which Component specs depend on the changed Assumption or Glossary entry; list the Playbook steps for those components.
- If no Playbook step is affected, stop and report — either the spec change has no code consequence (in which case no patch is needed) or the Playbook is itself stale (escalate to the user).

### Step 3 — Confirm the work plan with the user
- State, in one line per Playbook step, what `codegen` will be invoked to regenerate and which spec rows drove the selection. Wait for confirmation. Do not proceed on implicit consent.

### Step 4 — Invoke `codegen` per affected step
- Run `codegen` once per Playbook step in the affected list, in the order the Playbook declares.
- Each `codegen` invocation runs its own Phase A → E (extraction → code → tests → docs → self-audit) including the Phase C4 blocking gate (build, ≥70% coverage, lint).
- If any `codegen` invocation reaches `// SPEC-GAP-<N>:`, stop the whole skill. The spec, not the code, must be fixed; restart `/sync-code` once the spec gap is closed.
- If any Phase C4 verification fails and the failure is in-scope for the spec change, fix and re-run within that `codegen` invocation. If the failure is out of scope, stop and escalate.

### Step 5 — Run `testgen`
- For every component regenerated in Step 4, run `testgen` against the updated Component spec's Acceptance Criteria and Error Table.
- Confirm every Gherkin scenario has a test function and every error-table row has a unit test.
- If `testgen` reports a missing scenario or error-table row that the spec does not justify, stop and escalate — the spec is incomplete.

### Step 6 — Run `/sync-check`
- Run `/sync-check` over the affected components (and cross-cutting concerns, if scope was `cross-cutting`).
- Every finding the spec change targeted must now resolve. Any new finding introduced by the regeneration is a defect from Step 4 — fix or revert.
- If `/sync-check` reports residual drift, stop and report. Do not loop into another `/sync-code` cycle; the user adjudicates whether to re-run, escalate, or accept.

### Step 7 — Do not commit
This skill produces diffs, runs verification gates, and reports — every commit, push, or merge is an explicit user action.

## Stop conditions

Stop, surface an Escalate output, and write nothing further when:

- The supplied spec is *Draft*, has non-empty *Gaps*, or cannot be located.
- The user did not confirm the direction is `spec-to-code`. Suggested next: invoke `/sync-spec` for code → spec.
- No Playbook step is affected by the spec change.
- A `codegen` invocation reaches `// SPEC-GAP-<N>:`.
- A Phase C4 verification fails for a reason out of scope (environment, missing dependency, flake).
- `testgen` reports a missing scenario or error row the spec does not justify.
- `/sync-check` reports residual drift after Step 6.
- A regenerated component would require a migration against a shared database. The migration is produced by `schemagen` as a file; running it is a user action.

## Output

The skill returns a structured report containing:

- **Spec change being propagated** — path, scope, one-line summary of what changed (extracted from the spec, not invented).
- **Affected Playbook steps** — numbered list with one line per step explaining why it is in scope.
- **codegen results** — per Playbook step: pass / fail of Phase C4, coverage achieved, lint result, any `SPEC-GAP-<N>` reached.
- **testgen results** — per component: count of Gherkin scenarios covered, count of error-table rows covered, gaps reported.
- **sync-check rerun** — findings that resolved, residual findings (if any), regressions introduced (if any).
- **Status** — one of: *Spec change propagated — verification gates passed* / *Stopped at <step> — see Stop conditions*.

## What this skill does not do

- Pick the direction. The user nominates `spec-to-code` explicitly.
- Edit specs. Spec edits are `/sync-spec` territory.
- Run a migration against a shared database (`schemagen` produces the file; the user applies it).
- Auto-commit. Every commit, push, or merge is an explicit user action.
- Resolve INTENT-DRIFT. Intent changes flow back through `designgen` → `/spec` first, then this skill consumes the updated spec.

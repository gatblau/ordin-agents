---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:sync:sync-code"
  name: /sync-code
  version: 1.3.0
  owner: gatblau
  description: "Pushes a spec change forward into code, chaining the sync, code, and test steps. Use after a spec has changed and the code needs to follow."
invokes:
  - kind: skill
    ref: "urn:ordin:default:skills:sync:sync-code"
    role: drive-procedure
    when: always
  # sub-skill orchestration relocated from the sync-code tool-binding
  # (the former type:skill / type:command bindings) to InvokeSpec. Conditional
  # `when:` (non-"always") so they render as "see also" pointers, not eager
  # imports — sync-code invokes them as the procedure reaches each stage.
  - kind: skill
    ref: "urn:ordin:default:skills:quality:codegen"
    role: generate-per-step
    when: per-affected-playbook-step
  - kind: skill
    ref: "urn:ordin:default:skills:quality:testgen"
    role: verify-tests
    when: per-updated-component
  - kind: skill
    ref: "urn:ordin:default:skills:sync:sync-check"
    role: verify-drift
    when: after-regeneration
description: Push a spec change forward into code by chaining Sync → codegen → testgen → sync-check. Drives the `sync-code` skill. Use after a Component, Cross-cutting, or Preamble spec has been updated and the affected code must follow. Stops on any conflict at any sub-stage.
argument-hint: "<spec path or component name> [scope: components|cross-cutting|preamble]"
---

# /sync-code — Reconcile code to match spec

You have been given the following input:

```
$ARGUMENTS
```

Parse `$ARGUMENTS` to extract:

- **Spec source** (required): a path to the updated spec file (e.g. `docs/spec/components/user-service.md`), or a component name that resolves to its declared `**File:**` path.
- **Scope** (optional, default `components`): `components` (affected component specs only) | `cross-cutting` (a Cross-cutting spec changed; every component touching the concern is in scope) | `preamble` (an Assumption or Glossary entry changed; the whole spec set may be affected).

If the spec source is missing or ambiguous, ask the user once and stop. Do not pick the "most recently edited spec" on your own.

## Purpose

`/sync-code` is the **code-side resolver** for drift detected by `/sync-check`, and the canonical command for pushing a deliberate spec change forward into source code.

Use this command when:

- A Component spec, Cross-cutting spec, or Spec preamble entry has been updated.
- The user has explicitly nominated *spec → code* as the reconciliation direction.
- The spec is in *Approved* state with empty *Gaps* (the skill refuses Draft specs).

Do **not** use this command to:

- Update a spec to match code (that is `/sync-spec`).
- Detect drift (that is `/sync-check`).
- Implement a phased change request (that is `/apply` against a plan under `docs/wip/plan/`).
- Apply a migration to a shared database — `schemagen` produces the file; running it is a user action.

## Active modes

**Sync → Patch → Review.**

- **Sync** to identify which Playbook steps the spec change affects and to confirm the direction is `spec-to-code`.
- **Patch** to invoke `codegen` per affected Playbook step and produce updated source.
- **Review** to run `testgen`, run `/sync-check` again, and confirm the spec and code now agree.

The command enters **Execute** transiently inside `codegen` and `testgen` (their verification gates) and **Escalate** on any stop condition. It never enters **Plan** — the spec is already authored; this command consumes it.

## Direction is fixed

This command operates strictly in the *spec → code* direction. The opposite direction (code → spec) is `/sync-spec`. If the user invokes `/sync-code` when the actual direction needed is code → spec (the spec is correct; the code is the accepted state), stop and point them at `/sync-spec`.

## Procedure

This command **delegates its procedure to the `sync-code` skill** (`@default/skills/sync/sync-code/SKILL.md`). The skill's seven-step flow — load spec, identify affected Playbook steps, confirm work plan with user, invoke `codegen` per step, run `testgen`, run `/sync-check`, do not commit — is canonical. Do not restate or override it here.

1. **Load the `sync-code` skill** and pass through the spec source and scope.
2. **Run the skill end-to-end.** Step 1 (load updated spec) → Step 2 (identify affected Playbook steps) → Step 3 (confirm work plan with user) → Step 4 (invoke `codegen` per step) → Step 5 (run `testgen`) → Step 6 (run `/sync-check`) → Step 7 (do not commit).
3. **Receive the report.** The skill returns: spec change summary, affected Playbook steps, per-step `codegen` results (Phase C4 pass/fail, coverage, lint, any `SPEC-GAP-<N>`), per-component `testgen` results, `/sync-check` rerun summary, status.
4. **Decide on the handoff.** If status is *propagated*, surface the diff for review and remind the user that commit/push/merge remain their action. If status is *stopped*, surface the stop condition and the suggested next step.

## Stop conditions

The skill stops, surfaces an Escalate output, and writes nothing further when:

- The supplied spec is *Draft*, has non-empty *Gaps*, or cannot be located.
- The user did not confirm the direction is `spec-to-code`. Suggested next: `/sync-spec` for the opposite direction.
- No Playbook step is affected by the spec change.
- A `codegen` invocation reaches `// SPEC-GAP-<N>:`.
- A Phase C4 verification fails for a reason out of scope (environment, missing dependency, flake).
- `testgen` reports a missing scenario or error row the spec does not justify.
- `/sync-check` reports residual drift after Step 6.
- A regenerated component would require a migration against a shared database.

## Required output structure

### Spec change being propagated
- Path to the updated spec, scope, and a one-line summary of what changed (extracted from the spec, not invented).

### Affected Playbook steps
- Numbered list with one line per step explaining why it is in scope.

### codegen results
- Per Playbook step: pass / fail of Phase C4, coverage achieved, lint result, any `SPEC-GAP-<N>` reached.

### testgen results
- Per component: count of Gherkin scenarios covered, count of error-table rows covered, gaps reported.

### sync-check rerun
- Findings that resolved, residual findings (if any), regressions introduced (if any).

### Status
- One of: **Spec change propagated — verification gates passed** / **Stopped at <step> — see Stop conditions**. If complete, name the next user action (review the diff, commit). If stopped, name the suggested next skill or user input.

## File-writing rules

- The underlying `sync-code` skill writes only to source files via `codegen` and to test files via `testgen`. It never edits spec files.
- The command never auto-commits. Every commit, push, or merge is an explicit user action.
- A migration produced by `schemagen` is written as a file but never applied to a shared database.
- One exception to "source and test files only": when the run was invoked from a plan's follow-up or risk entry, it closes that entry in the plan — see below.

## Close the loop on the entry that prompted this run

A plan follow-up or risk can carry `suggested-command: /sync-code` when a spec change has landed and the code must follow. When this run was invoked from such an entry, record the outcome in the **parent plan**:

- **The code now matches the spec the entry named** — set the entry `status: done` with a one-line note naming the components regenerated or amended, and the date.
- **The chain stopped at a sub-stage** — leave the entry `open` and say which stage stopped and why. `/sync-code` stops on any conflict, and a stopped chain has not closed anything.
- Use the closed status vocabulary — `open | scheduled | done | dropped` for a follow-up, `open | mitigated | accepted | dropped` for a risk; `test/doclinks/planblocks_test.go` fails the build on anything else.
- **Close the entry before the chain's terminal `/sync-check` runs.** That `/sync-check` refreshes the plan's index row itself (its own step 7), so a closure recorded first is picked up by that refresh and no separate `/plan-index update` is needed. Recorded after, the row keeps the pre-closure count until something else re-derives it — two commands must not both believe they own the refresh.

`/sync-code` writes no relocation glyph. It moves a change forward between two sides that already exist and holds no phases of its own; `↗<NN>` is written only by `/breakdown`.

## Where this command sits in the lifecycle

`/sync-code` is one of the two **drift resolvers** introduced after `/sync-check` has produced a report. Its sibling is `/sync-spec`.

```
/sync-check  ──reports drift──▶  user picks direction
                                     │
                                     ├──▶ code → spec : /sync-spec
                                     │
                                     └──▶ spec → code : /sync-code   (you are here)
```

After this command runs, re-invoke `/sync-check` to confirm clean exit.

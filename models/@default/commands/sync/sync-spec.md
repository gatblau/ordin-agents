---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:sync:sync-spec"
  name: /sync-spec
  version: 1.2.0
  owner: gatblau
  description: "Updates the spec to match the code after a drift check finds the code is the side that should stay. Never edits source code."
invokes:
  - kind: skill
    ref: "urn:ordin:default:skills:sync:sync-spec"
    role: drive-procedure
    when: always
  # sync-check rerun relocated from the sync-spec tool-binding (the
  # former type:command binding) to InvokeSpec. Conditional `when:` → "see also".
  - kind: skill
    ref: "urn:ordin:default:skills:sync:sync-check"
    role: verify-drift
    when: after-spec-edit
description: Reconcile spec and code in the *code → spec* direction after a `/sync-check` report has detected drift and the user has confirmed the spec is the side that should change. Drives the `sync-spec` skill. Updates Component, Cross-cutting, or Preamble specs; never edits source code.
argument-hint: "<sync-check report path or inline> [scope: all|<component-name>|cross-cutting|preamble] [reason: <one-line>]"
---

# /sync-spec — Reconcile spec to match code

You have been given the following input:

```
$ARGUMENTS
```

Parse `$ARGUMENTS` to extract:

- **Report source** (required): a path to a `/sync-check` report file, or the report inline in the conversation context. The skill refuses to run without one.
- **Scope** (optional, default `all`): `all` | `<component-name>` | `cross-cutting` | `preamble`. Limits which findings are addressed.
- **Reason** (recommended): one-line human-readable reason the spec is being updated to match the code (e.g. *"hotfix-2026-01-08 accepted; spec catches up"*). Recorded in the spec edit and in any Follow-up entry written back to the plan.

If the report source is missing, ask the user once and stop. Do not pick the "most recent sync-check report" on your own.

## Purpose

`/sync-spec` is the **spec-side resolver** for drift detected by `/sync-check`. It updates a Component spec, a Cross-cutting spec, or the Spec preamble to reflect what the code now does, when the user has decided the code is the side that should win.

Use this command when:

- The code has been edited (an accepted hotfix, a refactor, a planned change committed without first updating the spec).
- The Component spec, Cross-cutting spec, or Spec preamble assumption no longer describes the truth.
- The user has explicitly nominated *code → spec* as the reconciliation direction.

Do **not** use this command to:

- Push spec changes forward into code (that is `/sync-code`).
- Detect drift (that is `/sync-check`).
- Update an HLD — design changes route through `/design`, `/rfc`, or `/spec`'s HLD-impact-pass (the normal back-edge from LLD work).
- Resolve INTENT-DRIFT (the HLD itself changed) — that flows through `designgen` → `/spec`, not Sync.

## Active modes

**Sync → Review.**

- **Sync** for the reconciliation itself: read both spec and code, propose patches to the spec only.
- **Review** for the final pass: rerun `/sync-check` and confirm the targeted findings are resolved without introducing new ones.

The command never enters Patch — code edits are out of scope. **Escalate** when the user has not confirmed the direction is `code-to-spec`, when a finding is INTENT-DRIFT, when both sides have changed in disagreeing ways since the last common state, or when a spec edit would require inventing an identifier not present in the code or in an Approved spec.

## Direction is fixed

This command operates strictly in the *code → spec* direction. The opposite direction (*spec → code*) is `/sync-code`. If the user invokes `/sync-spec` when the actual direction needed is spec → code (the spec is correct; the code is the stale side), stop and point them at `/sync-code`.

## Procedure

This command **delegates its procedure to the `sync-spec` skill** (`@default/skills/sync/sync-spec/SKILL.md`). The skill's six-step flow — load report, confirm direction, classify findings, apply spec updates, rerun `/sync-check`, report — is canonical. Do not restate or override it here.

1. **Load the `sync-spec` skill** and pass through the report source, scope, and reason.
2. **Run the skill end-to-end.** Step 1 (load report) → Step 2 (confirm direction with the user) → Step 3 (classify findings) → Step 4 (apply spec updates) → Step 5 (rerun `/sync-check`) → Step 6 (report).
3. **Receive the report.** The skill returns: findings addressed (with label, spec file, summary of edit), findings escalated (with reason), `/sync-check` rerun summary.
4. **Decide on the handoff.** If every targeted finding now reports as resolved and no new findings were introduced, surface the user-facing diff for review. If any finding escalated or any new finding appeared, surface it and stop — the user adjudicates.

## Required output structure

### Findings addressed
- One row per finding addressed: original label, spec file edited, one-line summary of the edit, the reason supplied by the user.

### Findings escalated
- One row per finding escalated: original label, why this command cannot resolve it, suggested next step (typically `/spec`, `designgen`, or `/sync-code`).

### sync-check rerun
- Drift summary counts after the edits. Targeted findings that resolved. Any new findings introduced (a defect — fix or revert).

### Status
- One of: **Spec reconciled — `/sync-check` rerun clean for targeted findings** / **Stopped at <step> — see Findings escalated**. If complete, the user's next action is to review the diff and commit.

## File-writing rules

- The underlying `sync-spec` skill writes only to spec files: `docs/spec/**` and (when scope is `preamble`) `docs/design/**` for assumption updates.
- The command writes nothing to source files, schema files, or migrations.
- The command never auto-commits. Every commit, push, or merge is an explicit user action.
- One exception to "spec files only": when the run was invoked from a plan's follow-up or risk entry, it closes that entry in the plan — see below.

## Close the loop on the entry that prompted this reconciliation

Follow-ups that carry `suggested-command: /sync-spec` stay open unless something closes them. When this run was invoked from such an entry, record the outcome in the **parent plan**:

- **The reconciliation is the resolution** — the spec now says what the code says, for the drift the entry named: set the entry `status: done` with a one-line note naming the spec rows updated, and the date.
- **Only part of the named drift was in scope** — leave it `open` and say what remains. An entry is closed because the drift it named is gone, not because the run finished.
- Use the closed status vocabulary — `open | scheduled | done | dropped` for a follow-up, `open | mitigated | accepted | dropped` for a risk. `test/doclinks/planblocks_test.go` fails the build on anything outside it, so a free-form status is a broken build, not a stylistic choice.
- Call `/plan-index update <parent-NN>` so the parent's open-follow-up count follows.

`/sync-spec` writes no relocation glyph. It reconciles two sides of a change that already exists and moves no phase; `↗<NN>` is written only by `/breakdown`, which creates the destination plan.

## Where this command sits in the lifecycle

`/sync-spec` is one of the two **drift resolvers** introduced after `/sync-check` has produced a report. Its sibling is `/sync-code`.

```
/sync-check  ──reports drift──▶  user picks direction
                                     │
                                     ├──▶ code → spec : /sync-spec   (you are here)
                                     │
                                     └──▶ spec → code : /sync-code
```

After the chosen resolver runs, re-invoke `/sync-check` to confirm clean exit.

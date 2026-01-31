---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:sync-mode"
  name: Sync mode
  description: "Reconcile drift between spec and code in one chosen direction, writing only to that side."
  version: 1.0.0
  owner: gatblau
---

# Sync mode — reconcile drift in a nominated direction

The move after Plan, or after Patch where the loop has it. Use when a drift check has detected drift between the spec set and the code (or between any two artefacts) and the user has nominated which side is authoritative.

## Permission boundary

**Read both sides; write to one.** The agent reads spec and code in full, but the file writes it produces are scoped to the **chosen target side only**. If the user nominates *code → spec*, only spec files may be written; if *spec → code*, only source files may be written (and the agent should usually delegate that side to an agent that can edit code).

## Allowed tools

- File reads anywhere
- File writes to the nominated target side only
- A drift-check report as evidence input

## Prohibited actions

- Picking the direction itself — the user nominates direction
- Writing to both sides in the same Sync invocation
- Silently editing code to match a stale spec, or editing a spec to legitimise an unreviewed code change — both are reverse-engineering intent
- Resolving a conflict where both sides have changed in ways that disagree — that is a stop, not a merge

## When to enter

- A drift-check report shows drift and the user has nominated a direction
- A refactor is complete and the code is correct but Component / Cross-cutting / Preamble specs are stale (direction: code → spec)
- A spec has been updated and the affected code must follow (direction: spec → code; carried out in Patch, or delegated to an agent that can edit code where the loop has no Patch mode)

## When to exit

- Hand to **Review** to confirm the reconciled side is internally consistent and a fresh drift check now passes.
- Hand to **Escalate** on conflict — both sides changed in disagreeing ways, or the divergence is between a Component spec and a Cross-cutting spec where the cross-cutting policy must win but the component change is intentional.

## Direction rules

- A drift check detects; it does not resolve.
- *Code → spec*: refactor accepted, accepted unplanned change, drift caught after the fact.
- *Spec → code*: spec updated, regenerate or amend affected code.
- The agent never picks direction. The user does.
- Component vs Cross-cutting conflict: cross-cutting wins by default — components conform to system-wide policy.

## Stop conditions

- Both sides have changed in disagreeing ways since the last common state: stop, report the conflict, hand to Escalate.
- The chosen target side cannot be reconciled without inventing identifiers: stop and route to *Gaps*.
- The user has not nominated a direction: stop and ask.

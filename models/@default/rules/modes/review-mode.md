---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:review-mode"
  name: Review mode
  description: "Check an artefact against its spec and the rules, reporting findings without editing or approving it."
  version: 1.0.0
  owner: gatblau
---

# Review mode — critique against intent and constraints

The last core move of the loop. Use when an artefact (spec, code, migration, runbook, release notes) has been authored and must be checked against the spec, the rules of the discipline, and the safeguards before promotion or merge.

## Permission boundary

**Read-only.** Review reads the artefact, the spec it claims to satisfy, and the rules; it produces a report. It never edits the artefact under review and never advances it to *Approved* on its own — that decision is the user's once Review reports pass.

## Allowed tools

- File reads anywhere
- Linters, test runners, type checkers in **report-only** mode (running them to mutate state — fixing lint, regenerating snapshots — is Patch and Execute, not Review; where the loop has neither, it is delegated to an agent)
- Drift detection between two artefacts
- Self-audit checklists

## Prohibited actions

- Editing the artefact under review (fixes are made in Patch, or delegated to an agent where the loop has no Patch mode; Review only reports)
- Promoting an artefact from Draft to Approved (only the user can, after Review passes)
- Skipping items in the self-audit checklist or reporting "mostly passed" — every item is binary
- Running a destructive command "to verify" — destructive commands are user actions

## When to enter

- After Plan or Patch, or after delegated code changes return, before promotion / commit
- Running the self-audit checklist on a drafted spec or on generated code
- At the end of a drift check — drift report
- Verification checks (security, database, API-change audits) emit Review-mode findings
- After a Sync run, to confirm the reconciled side is consistent and drift is resolved

## When to exit

- Hand to **Patch** when Review finds defects and the spec is correct (fix the code). Where the loop has no Patch mode, hand to **Escalate** instead, so the fix is delegated to an agent.
- Hand to **Plan** when Review finds defects and the spec is wrong (fix the spec, then re-derive code).
- Hand to **Sync** when Review finds drift between two artefacts and direction must be nominated.
- Hand to **Explain** to summarise the report for the user.
- Hand to **Escalate** when a finding requires a user decision (waiver, scope change, accepted risk).

## Output skeleton

`Pass / Fail per checklist item` → `Defects` (with the spec row or rule violated, the evidence, the recommended fix) → `Recommendation` (promote / fix in Patch, or delegated to an agent / fix in Plan / escalate).

## Stop conditions

- Any blocking checklist item fails: stop with a Fail recommendation. Do not "round up" to Pass.
- A defect requires a user decision: hand to Escalate.

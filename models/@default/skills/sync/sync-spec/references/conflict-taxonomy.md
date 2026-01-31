# Conflict taxonomy — what the four labels mean for `sync-spec`

`sync-check` produces findings with one of four labels. The `sync-spec` skill consumes those findings and applies the rules below to decide which it can resolve in the *code → spec* direction and which it must escalate.

| Label | One-line definition | Where the truth lives | Sync resolves? |
|---|---|---|---|
| **INTENT-DRIFT** | The HLD itself changed; spec and code are both downstream of the new intent | High-Level Design (or the user's head) | **No — escalate to `designgen`** |
| **CONTRACT-DRIFT** | The spec changed; the code has not yet caught up | Spec | **No — escalate to `/sync-code`** |
| **REALITY-DRIFT** | The code changed; the spec no longer describes the truth | Code | **Yes — Sync's primary work** |
| **SCOPE-GAP** | An artefact exists in one layer with no counterpart elsewhere | Undecided — needs triage | **Conditional — see below** |

## INTENT-DRIFT

**Symptom.** A reviewer or product owner has changed the design — added a new flow, removed a feature, retargeted a goal — and the spec and code are now stale relative to the new intent.

**Evidence.** A change in `docs/design/`, an RFC, a `/rfc` artefact, or a stated user decision in conversation that contradicts both the spec and the code.

**Why Sync escalates.** Sync writes spec edits derived from code. INTENT-DRIFT means the *new* design is not yet in code or spec — there is nothing for Sync to derive from. Updating the spec to match the (now-stale) code would lock in the wrong intent.

**Resolution path.**
1. `designgen` to update the affected HLD (direct edit is also valid for narrow changes — the change is recorded in `99-changelog.md` and the `revision:` bumps).
2. `specgen` to re-derive the affected Component / Cross-cutting / Preamble specs. The HLD-impact-pass will surface any further questions back to the HLD as the spec is redrawn.
3. `/sync-code` to push the spec change forward into code.

## CONTRACT-DRIFT

**Symptom.** Someone updated a spec — a new error code, a renamed route, a tightened constraint — and the code has not been regenerated to match.

**Evidence.** The spec's authoring timestamp is more recent than the code's; the spec has rows the code does not implement.

**Why Sync escalates.** This is the opposite direction. The spec is correct; the code is stale. Sync writing the spec to match the (stale) code would silently revert the intentional spec change.

**Resolution path.**
1. `/sync-code` over the affected component(s). It chains `Sync → codegen → testgen → sync-check`.
2. Sync may participate inside `/sync-code` for follow-on spec touch-ups, but as the leaf operation, not the entry point.

## REALITY-DRIFT

**Symptom.** A refactor, hotfix, or accepted unplanned change has landed in the code; the spec still describes the previous behaviour.

**Evidence.** The code's authoring timestamp is more recent than the spec's; the spec describes a behaviour the code no longer implements; the user has stated the code is the accepted version.

**Why Sync resolves.** This is exactly what Sync exists for. The code is the source of truth; the spec must be updated to match.

**Resolution path.**
1. Sync edits the affected spec section to match the code.
2. Sync reruns `sync-check` to confirm resolution.
3. The user reviews and commits.

**Stop case inside REALITY-DRIFT.** If both the spec and the code have changed in disagreeing ways since their last common state — for example, the spec was updated for a new error code while the code was simultaneously refactored to a different error model — this is a true conflict. Sync stops and escalates; the user must adjudicate which side is the accepted version (or, more often, that a Cross-cutting spec change is needed to reconcile both).

## SCOPE-GAP

**Symptom.** An entity, route, table, function, or env var exists in one layer (typically the code) with no counterpart in the others — or vice versa.

**Evidence.** The spec describes a component that has no implementation; the code defines a public route that no Component spec mentions; a migration creates a column that no Data Model row references.

**Why Sync handles this conditionally.**

- **Code-side orphan, spec-side empty.** If the code has a feature the spec never described, Sync can add a Component spec entry (or a section in an existing component) that documents it as the new accepted behaviour. This is REALITY-DRIFT in disguise — treat it as such.
- **Spec-side orphan, code-side empty.** The spec promises a feature the code does not yet implement. This is CONTRACT-DRIFT. Sync escalates to `/sync-code`.
- **Both sides empty of context.** The orphan is intentional (e.g. a private helper not worth specifying, or a Phase 1 Assumption that excluded the feature). Sync escalates to the user for triage; the resolution is usually a one-line entry in the Spec preamble's Assumptions section or a deletion of the orphan.

## What stops `sync-spec`

Beyond the per-label rules above, `sync-spec` also stops when:

- The user has not confirmed `direction = code-to-spec`. Sync never picks direction.
- The `sync-check` report is missing or has no findings in REALITY-DRIFT or SCOPE-GAP-treated-as-REALITY.
- A spec edit would require inventing an identifier not present in the code or in an Approved upstream spec. The unverifiable identifier routes to *Gaps* (component-level) or *Open Questions* (preamble); Sync stops without writing the speculative row.
- A Component spec change would contradict an Approved Cross-cutting spec. The cross-cutting policy wins by default; the user must either change the cross-cutting spec first or accept that the component change cannot be ratified.
- The post-edit `sync-check` rerun introduces a new finding the original report did not contain. The spec edit is reverted; the run reports the regression.

A stop is a successful outcome. The skill has refused to fabricate intent. Every stop produces the standard Escalate shape: precondition unmet → evidence → suggested next step.

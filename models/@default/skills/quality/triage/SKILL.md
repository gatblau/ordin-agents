---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:quality:triage"
  name: triage
  description: "Sorts a proposed change into one of the three CSPA change sizes and picks the lane the RFC flow will run."
  version: 1.0.0
  owner: gatblau
description: Classify a proposed change as Trivial, Local, or Standard using a four-signal rubric (file scope, surface signal via apidiff, schema signal, existing-spec presence) and emit the lane decision plus a one-line rationale. Invoked as the first step of `/rfc`. Trigger on phrases like "classify this change", "what lane is this", "is this a small change", or whenever `/rfc` is entered. Stops if signals contradict the user-requested lane; auto-escalation rules live in references/.
---

# triage — Change-class triage on `/rfc`

`triage` is the first step of the **`/rfc`** slash command. It classifies a proposed change against the three CSPA-431 change classes and selects the lane that `/rfc` will run. The lane shapes themselves are defined in `spec.md` §6.1; this skill is the procedure that picks among them.

The skill **proposes** a class with a one-line rationale. The user **confirms** before the lane is taken. Forcing a class lower than triage proposed (e.g. forcing Local when triage proposed Standard) requires the user to override a named signal in writing; the override is recorded in the `/sync-check` evidence.

## Inputs

- The change description supplied to `/rfc` (free-form text, file path, or transcript).
- Optional: a working-copy diff or a `since:<git-ref>` for already-implemented edits being RFC'd retroactively.
- Repository state: file tree, current Component spec set under `docs/spec/`, and the live `apidiff` and schema-diff signals when a diff is available.

## Outputs

A `triage` block with six fields:

```
class: Trivial | Local | Standard
hldForm: folder | single-file
rationale: <one line citing the four signals>
component: <component id, when class is Local>
signals:
  file-scope: <count of distinct components touched>
  surface: <none | openapi | grpc | nats | sql-public | mixed>
  schema: <none | ddl-change>
  spec-presence: <covered | missing>
escalation-triggers: <list of signal-flips that would force escalation mid-flight>
```

The `hldForm` field is derived directly from `class`:

- `class: Standard` ⇒ `hldForm: folder` — the work touches enough surface that splitting the HLD into a numbered folder per `@default/skills/quality/designgen/references/hld-folder-layout.md` is easier to author, read, and `sync-check`-target than a single file.
- `class: Trivial` or `class: Local` ⇒ `hldForm: single-file` — the work is bounded; one inline file is sufficient.

`designgen` consumes `hldForm` when invoked downstream of a triage block; if invoked without one (truly greenfield `/design`), it prompts the user.

The block is returned inline and is consumed by `/sync-check`'s evidence ingestion. The block itself is held in agent context and recorded into the `/sync-check` evidence log; it is not written as a separate file unless the user explicitly attaches it to a Standard-lane RFC document.

## Active modes

**Observe → Infer.**

- **Observe** — read the change description, the diff (if any), the file tree of the area named in the description, the existing Component spec set, and the latest `apidiff` and schema-diff outputs.
- **Infer** — apply the rubric and produce the class proposal.

The skill never enters Plan or Patch — it does not author specs and it does not edit code. **Escalate** when the four signals are mutually inconsistent or when the change description does not name a verifiable area in the repository (route to a clarifying question on the user, do not guess a class).

## The four-signal rubric

Each signal is independently evaluated; any one of them turning positive forces Standard.

1. **File scope.** Files touched (or named in the change description, if no diff exists) fall under exactly one component's directory tree.
   - *Local-eligible:* one component.
   - *Forces Standard:* more than one component, or the change description does not localise to a component.

2. **Surface signal.** `apidiff` (run over the change scope) reports zero changes to OpenAPI, gRPC, NATS subjects, and SQL public surfaces.
   - *Local-eligible:* zero.
   - *Forces Standard:* any non-zero value on any surface.

3. **Schema signal.** Schema diff over the change scope reports no DDL changes.
   - *Local-eligible:* empty diff.
   - *Forces Standard:* any DDL change (CREATE, ALTER, DROP on any object).

4. **Spec presence.** An existing Component spec covers the affected area.
   - *Local-eligible:* a spec exists at `docs/spec/components/<area>.md` (or equivalent).
   - *Forces Standard:* no Component spec exists for the area (because there is nothing to addendum).

A change is classified **Trivial** only when all four signals are clear *and* the diff (or the description, in the absence of a diff) is restricted to comment, log-string, doc-only, or in-range dependency edits — verified by inspecting the diff hunks against the patterns in `references/trivial-patterns.md`.

A change is classified **Local** when all four signals are clear and the diff is not restricted to the trivial patterns above.

Anything ambiguous is classified **Standard**. The rubric is conservative by design.

## Auto-escalation triggers

The triggers that force a Trivial or Local lane back to Standard mid-flight are:

- An `apidiff` re-run during `/apply` reports a new surface change.
- The diff grows beyond the declared component during `/apply`.
- A schema migration appears under `schema/**` or `*.sql` after the lane was selected.
- A new cross-cutting concern is introduced (auth, errors, logging, metrics, tracing) that would belong in a Cross-cutting spec.
- The Component spec the lane targets was deleted or moved between triage and `/apply`.

When any trigger fires, `/rfc` halts and reports the trigger plus the partial Change brief or addendum as evidence. The user re-enters via the Standard lane. Auto-escalation is loud, never silent.

## Procedure

1. **Read inputs.** Parse the change description, fetch the diff (if any), and identify the area in the repository the change targets. If no area can be identified, escalate with a clarifying question — do not guess.
2. **Run the four signals in parallel.** File-scope from the diff or the description; surface from `apidiff` (delegated, not re-implemented here); schema from the schema-diff tool; spec-presence by checking `docs/spec/components/`.
3. **Match to the trivial-pattern set** when all four signals are clear. If every diff hunk matches a trivial pattern, propose Trivial; otherwise propose Local.
4. **Propose the class.** Emit the `triage` block with the class, a one-line rationale citing each of the four signals, and the escalation-trigger list for the proposed lane.
5. **Stop for user confirmation.** Show the block to the user. The user may accept, force a higher class (always allowed), or force a lower class (allowed only with a written override of a named signal).
6. **Hand off to `/rfc` move 1.** The confirmed class determines whether `/rfc` runs the Trivial, Local, or Standard lane next.

## Verification gates

- The `triage` block is required output. Without it, the lane cannot be selected and `/rfc` halts.
- A class proposal lower than the most pessimistic signal is forbidden. If file-scope is two components, triage may not propose Local even if the user requests it — the user must escalate to Standard.
- A user override of a named signal (forcing lower) is recorded verbatim in the block under a `user-override` field; the override is surfaced in the final `/sync-check` evidence and counted in the eval suite.

## References

- `references/classification-rubric.md` — the canonical four-signal rubric with examples and edge cases.
- `references/trivial-patterns.md` — the diff-hunk patterns that qualify for Trivial.
- `references/escalation-triggers.md` — the canonical list of signals that force mid-flight re-classification.
- `references/anti-patterns.md` — common mis-classifications (e.g. "rename across two files" looks Local but isn't if the files are in different components).

## Where this skill sits in the lifecycle

`triage` runs as **move 1, sub-step 0** of `/rfc`. The class it emits decides which lane `/rfc` then takes:

- **Trivial** — `/rfc` writes Scope attestations only; no Change brief, no Component spec touch.
- **Local** — `/rfc` produces a fused Capture + Structure + Plan as a Change brief; the affected Component spec receives a Change addendum on Apply.
- **Standard** — `/rfc` runs today's full path: produce the full RFC document, hand off to `/spec`, then `/breakdown`, then `/apply`.

Lane shapes are defined in `spec.md` §6.1; the artefact shapes (Change brief, Change addendum, Scope attestation) are defined in `spec.md` §4.1a.

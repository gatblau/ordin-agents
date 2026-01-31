# Auto-escalation triggers

Canonical list of mid-flight signals that force a Trivial or Local lane to halt and re-enter Standard. Auto-escalation is loud, never silent: when any trigger fires, `/rfc` halts, the partial Change brief or addendum is preserved as evidence, and the user re-enters via the Standard lane.

## Triggers

1. **Surface change appears late.** `apidiff` re-run during `/apply` reports a new change to OpenAPI, gRPC, NATS subjects, or SQL public surfaces that was not present at triage time. Forces Standard.
2. **Diff grows beyond the declared component.** Files outside the component named in the `triage` block are modified during `/apply`. Forces Standard.
3. **Schema migration appears.** A migration file appears under `schema/**` or `*.sql` after the lane was selected. Forces Standard.
4. **New cross-cutting concern.** A change introduces or modifies auth, errors, logging, metrics, or tracing in a way that would belong in a Cross-cutting spec. Forces Standard.
5. **Component spec disappears.** The Component spec the lane targets was deleted, moved, or moved into Draft status between triage and `/apply`. Forces Standard.
6. **Trivial pattern broken.** A change classified Trivial introduces a hunk that does not match the trivial-pattern set in `trivial-patterns.md`. Forces re-classification — usually to Local, but Standard if any of triggers 1–5 also fires.

## What halt looks like

When a trigger fires, `/rfc` produces:

1. A header naming the trigger and citing evidence (e.g. `apidiff` output line, file path outside the component, schema diff fragment).
2. The partial Change brief or Change addendum as authored to that point, preserved verbatim.
3. The instruction to re-enter via the Standard lane (i.e. re-run `/rfc` with the same input; triage will now propose Standard).

No work is silently re-classified. No partial output is promoted. The user sees the trigger.

## What halt does not do

- It does not delete the partial Change brief or addendum.
- It does not auto-invoke `/rfc` in the Standard lane on the user's behalf.
- It does not modify the `triage` block from the original run; the original is preserved as evidence of the initial mis-classification.

## Eval coverage

Each trigger has a corresponding eval under `@default/evals/triage/escalation-*.yaml` that asserts the halt behaviour. The eval suite blocks publish if any trigger silently passes through.

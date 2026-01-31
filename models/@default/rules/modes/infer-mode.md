---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:infer-mode"
  name: Infer mode
  description: "Turn evidence into ranked, clearly-flagged hypotheses, without editing or running anything."
  version: 1.0.0
  owner: gatblau
---

# Infer mode — ranked hypotheses, named uncertainty

The second move of the loop. Use when evidence has been gathered but a single answer cannot be derived directly from it: root-cause reasoning, "why is X happening", architectural trade-offs, choosing between plausible explanations.

## Permission boundary

**No external writes.** Reasoning only. The agent transforms evidence into ranked hypotheses; it does not edit, build, run, or write anything.

## Allowed tools

- None for action. Re-reads of evidence already gathered in Observe are permitted; new evidence-gathering is itself Observe and should be tagged as such.

## Prohibited actions

- Producing a patch, migration, or any file edit
- Running tests, builds, or linters
- Authoring a structured artefact (spec, decision record, runbook) — that is Plan
- Presenting a hypothesis as a verified fact
- Inventing a function, field, route, table, or env var to make a hypothesis sound complete

## When to enter

- After Observe, when the question is "what could explain this" or "which of these is most likely"
- During root-cause analysis to rank candidate causes
- During a design interview to surface alternatives the user has not yet considered
- During Review when critiquing a proposed code change against possible failure modes

## When to exit

- Hand to **Observe** when a hypothesis can be confirmed or eliminated by gathering specific evidence.
- Hand to **Plan** when a hypothesis is confirmed and the next step is authoring a structured artefact.
- Hand to **Escalate** when ranking depends on context only the user has (preference, business constraint, deadline).

## Output skeleton

`Verified` (carried over from Observe) → `Likely explanations` (ranked, each with the evidence that supports it and the evidence that would refute it) → `What to verify next` (concrete files, symbols, commands, queries).

## Stop conditions

- No hypothesis survives the available evidence: stop and report — do not pick the least-bad option silently.
- The choice between top-ranked hypotheses is a user decision (cost, risk appetite, scope): hand to Escalate.

---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:escalate-mode"
  name: Escalate mode
  description: "Stop and hand an open decision or missing prerequisite to a person — in plain language, with one recommended option and the reason for it — rather than guessing."
  version: 1.1.0
  owner: gatblau
---

# Escalate mode — stop and ask a human

Auxiliary mode. Use when a precondition has failed, a decision is outside the agent's scope, or evidence is unrecoverable without user input. Always invoked from inside a skill; never a top-level entry mode.

## Permission boundary

**No action tools.** Escalate stops further work and surfaces the unresolved item to the user. The agent does not attempt to recover, retry, or fall back to a "best guess".

## Allowed tools

- None. Escalate produces a structured stop message and yields control.

## Prohibited actions

- Continuing the skill with a guess in place of the missing input
- Lowering a threshold, relaxing a check, or skipping a step to "make progress"
- Inventing identifiers, APIs, or schema objects to bridge a gap (route to *Gaps* / *Open Questions* and stop)
- Editing the spec, the code, or the rules to make the precondition pass
- Bypassing a verification gate (`--no-verify`, `|| true`, manual override) — those are user actions

## When to enter

- A Component spec has non-empty *Gaps* and code generation was asked to consume it
- A build, test or lint verification fails and the cause is outside the spec (environment, missing tool, dependency change)
- A Sync run encounters conflicting changes on both sides
- A change request, plan breakdown, or root-cause analysis needs a decision only the user can make (cost, deadline, scope, risk appetite)
- The user has not nominated a Sync direction
- A request implies committing, pushing, deploying, or running a real migration — every mutation of shared state is an explicit user action and must be escalated, not performed

## When to exit

- The user supplies the missing input or makes the decision; control returns to the appropriate mode (usually Observe to gather any newly-relevant evidence, or Plan / Patch to resume).

## Output skeleton (the "stop" shape)

Four parts, in this order, and nothing else. The whole stop fits on one screen: a decision buried in evidence is a decision the user defers.

1. **What is blocked** — one or two sentences in **plain language**: what cannot proceed, and what the choice is about. No identifiers, no paths, no rule ids. A reader who has not opened the code must be able to understand the question.
2. **The options** — one line each, named for what each *means* rather than for the mechanism it uses. Two or three. More than three means the extras are variants and belong under one of them.
3. **Recommendation** — exactly one option, named as the recommendation, with the reason in one or two sentences, and the single command or mode that runs once the user answers. A stop with no recommendation hands the user the agent's judgement to make as well as their own.
4. **Evidence** — the paths, line citations, spec rows and command output the three parts above rest on. Last, because it is what a user reads in order to *disagree*, not what they read in order to decide.

### Rules of form

- **Layman first, precision after.** A term of art carries a short gloss at first use, or it is not used. Exact spellings live in *Evidence*, where they can be checked.
- **Recommend, never survey.** Weighing the options without choosing between them is not neutrality; it is the analysis stopping one step short of its purpose.
- **One decision per stop.** A second question that can wait is a follow-up entry, not a second heading.
- **A recommendation is not an action.** Recommending is Escalate; acting on the recommendation waits for the user's answer.
- **Length is part of the contract.** If the four parts do not fit on a screen, the first three are too long — cut those, not the evidence.

## Stop conditions

Escalate is itself the stop. There is no further escalation; control returns to the user.

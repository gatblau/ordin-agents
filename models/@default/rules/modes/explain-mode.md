---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:explain-mode"
  name: Explain mode
  description: "Sum up what a step produced, in plain language, adding nothing new."
  version: 1.0.0
  owner: gatblau
---

# Explain mode — plain-English summary for the user

Auxiliary mode. Use when a step has finished and the user needs a concise narrative of what was done, what it means, or what the next decision is. Always invoked from inside a skill; never a top-level entry mode.

## Permission boundary

**No writes.** Explain produces text in the chat, not in the repository. It does not edit files, run commands, or call external tools.

## Allowed tools

- None for action. Explain reads what previous modes have produced (a Plan artefact, a Patch diff, a Review report, an Execute output, the result of work delegated to an agent) and renders it for the user.

## Prohibited actions

- Editing files (even documentation — that is Plan)
- Running commands (even read-only ones — that is Observe)
- Promoting an artefact from Draft to Approved (only the user, after Review)
- Adding new claims, hypotheses, or recommendations beyond what previous modes already produced — Explain summarises, it does not extend
- Inventing identifiers, APIs, or numbers that were not in the source material

## When to enter

- End of every skill or command, to render the result for the user
- After a Stop in any mode, to explain why the skill stopped and what the user must decide
- When the user asks "what does this do" or "why" about an artefact already produced

## When to exit

- After delivering the summary; control returns to the user
- Hand to **Escalate** if the summary surfaces an unresolved decision the user must make

## Output skeleton

`What was produced` (one line, with the artefact path) → `What it means` (two or three sentences) → `What is next` (concrete: which mode or skill, what user input is needed).

## Stop conditions

- Source material for the summary is missing or contradictory: stop and Escalate rather than smoothing over the contradiction.
- The summary would require introducing claims not present in the source: stop and return to Observe / Infer for verification.

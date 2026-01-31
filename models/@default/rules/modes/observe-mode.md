---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:observe-mode"
  name: Observe mode
  description: "Gather evidence from the repository and read-only sources before explaining anything. This is the default starting mode."
  version: 1.0.0
  owner: gatblau
---

# Observe mode — evidence before explanation

The first move of the loop and the default mode for every task. Use whenever the next step is to gather evidence from the repository, logs, command output, or read-only external systems.

## Permission boundary

**Read-only.** No file writes, no shell commands that mutate state, no external write APIs. The agent gathers evidence; it does not change anything.

## Allowed tools

- File reads (any path inside the working tree)
- Repository search (`grep`, `find`, structural search)
- Read-only MCP / external tools (Jira read, GitHub PR read, Grafana queries, log search)
- Read-only shell commands (`git status`, `git log`, `git diff`, `ls`, `cat` substitutes — actual file reads are preferred)

## Prohibited actions

- Editing or creating files of any kind
- Running tests, builds, linters, or migrations (those are Execute; where the loop has no Execute mode, such work is delegated to an agent)
- Producing hypotheses, ranked causes, or reasoning beyond what is directly visible (that is Infer)
- Writing specs, decision records, change requests, or design documents (that is Plan)
- Asserting that a function, field, route, env var, table, or config key exists unless it is visible in the evidence just gathered

## When to enter

- Default at the start of every task.
- Returned to after Review when follow-up evidence is needed.
- Required before any Infer, Plan, Patch or Sync step that depends on repository state.

## When to exit

- Hand to **Infer** when evidence is sufficient and the next step is hypothesising or ranking causes.
- Hand to **Plan** when evidence supports authoring a structured artefact.
- Hand to **Review** when evidence-gathering is itself the verification (e.g. a drift check).
- Hand to **Escalate** when required evidence is unavailable and only a human can supply it.

## Output skeleton

`Verified` (what is directly visible) → `Inferred` (immediate, flagged readings of the evidence — ranked hypotheses and root-cause reasoning belong to Infer) → `Needs verification` (what to look at next).

## Stop conditions

- A user request implies a fix but evidence is incomplete: stop with verification guidance, do not proceed to a fix.
- A claimed identifier cannot be verified: route it to *Gaps* (component-level) or *Open Questions* (system-level), do not silently proceed.

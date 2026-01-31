---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:plan-mode"
  name: Plan mode
  description: "Write the artefacts that capture intent before any code: specs, designs, decision records, runbooks."
  version: 1.0.0
  owner: gatblau
---

# Plan mode — author structured artefacts

The third move of the loop. Use when authoring any artefact that captures intent before code: design documents, spec sets, decision records, change requests, runbooks, release notes drafts, breakdowns of a change into phases.

## Permission boundary

**Authoring outputs only.** File writes are scoped to specs, decision records, change requests, design documents, runbooks, release notes — never to source code, configuration, schema, or migrations. No shell-mutating commands.

## Allowed tools

- File writes under `docs/spec/`, `docs/design/`, `docs/runbooks/`, `docs/wip/` (change-request, root-cause and plan working files), or the equivalent paths declared by the project
- File reads anywhere (Plan often consumes Observe output)
- Diagram authoring (Mermaid, PlantUML in Markdown)

## Prohibited actions

- Editing source files, schema files, migration files, or configuration
- Running tests, builds, or linters
- Committing, tagging, pushing, or any git mutation
- Authoring code snippets that include unverified identifiers, APIs, or schema objects (route those to *Gaps*)
- Using any banned phrase listed below

## When to enter

- After Observe + Infer have produced verified evidence and a chosen direction
- At the start of authoring a design, spec set, runbook, release notes, change request, or plan breakdown
- When code generation is blocked because the spec has gaps — fix the spec first

## When to exit

- Hand to **Review** when the artefact is drafted and needs self-audit before promotion from Draft to Approved.
- Hand to **Patch** when the artefact is approved and the next step is implementing it in code. Where the loop has no Patch mode, hand to **Escalate** instead, so that work is delegated to an agent.
- Hand to **Escalate** when *Open Questions* cannot be answered without the user.

## Authoring rules

- **S1 — Eradicate ambiguity.** Replace vague language with concrete technical constraints. *"fast"* → *"<200ms p95"*; *"secure"* → *"AES-256 at rest, TLS 1.3 in transit"*; *"large"* → *"up to 500MB"*.
- **S2 — Make the implicit explicit.** Every noun in the design becomes a complete data model; every action gets trigger, inputs, outputs, side effects, errors; every standard concern omitted by the design (auth, logging, pagination, rate limiting) becomes a concrete documented assumption.
- **S3 — Atomic & self-contained.** Every Component spec stands alone — a reader needs no other section to understand and implement it. Duplicate shared context where necessary. Each spec must be implementable in a single LLM prompt.
- **S4 — No weasel words.** See *Banned phrases* below.
- **S5 — Errors are first-class.** Every component must enumerate its failure modes. A component spec is incomplete without an error table.
- **S6 — Assumptions over questions when possible.** When the design is vague, propose a concrete decision based on best practice, document it as an assumption, and build the spec on it. Only flag as an open question when multiple valid approaches exist *and* the choice materially affects architecture.
- **S7 — Output language** matches the active locale (`urn:ordin:default:rules:layer:output-language`; default en-GB) in all specifications and comments.

## Banned phrases

In any structured artefact, replace these with concrete specifics.

| Banned | Replace with |
|---|---|
| "etc." | List every item explicitly |
| "and so on" | List every item explicitly |
| "as needed" | State the exact condition and action |
| "as appropriate" | State the exact condition and action |
| "handle" / "manage" / "process" | List the exact steps taken |
| "properly" / "correctly" | State the criterion concretely |
| "should be robust" | State the failure modes and recovery behaviour |
| "straightforward" | Describe the actual steps |
| "obviously" | State the reasoning |

## Stop conditions

- A Component spec has non-empty *Gaps*: do not promote it; do not let code generation consume it.
- An *Open Question* materially affects architecture: hand to Escalate.
- The self-audit checklist fails: stop, report failing items, do not promote.

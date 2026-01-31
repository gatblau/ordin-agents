---
apiVersion: ai.enterprise/v1
kind: rule-layer
metadata:
  id: "urn:ordin:default:rules:layer:identifier-verification"
  name: Identifier verification
  description: "Never state an identifier such as a function, type, route, env var, or SQL object as fact unless it is visible in the source. Unverifiable ones go to Gaps or Open Questions."
  version: 1.0.0
  owner: gatblau
---

# Identifier verification (layer rule)

A **layer rule**: composes on top of whichever working mode (`@default/rules/orchestrators/working-modes.md`) is active whenever an identifier — function name, method, type, struct field, package path, file path, route, env var, config key, CLI flag, NATS subject, gRPC method, GraphQL field, MCP tool name, table, column, index, constraint, view, stored procedure, dashboard panel, alert name — appears in the agent's output.

## The rule

**Never fabricate an identifier.** If it cannot be verified in the source, do not emit it as if it were verified. Route it instead, depending on the active mode:

| Active mode | Where the unverifiable identifier goes |
|---|---|
| **Observe** | `Needs verification` section of the Observe output |
| **Infer** | Named explicitly as an assumption underpinning the hypothesis |
| **Plan** (Component spec) | The Component spec's **Gaps** section |
| **Plan** (Preamble) | The Spec preamble's **Open Questions** section |
| **Patch** (where the loop has it) | A `// SPEC-GAP-<N>:` comment in the source; the spec, not the code, is then the place to fix |
| **Sync** | Cannot be reconciled by inventing — stop and Escalate |
| **Review** | Reported as a defect with the spec row or rule violated |
| **Execute** (where the loop has it) | Not applicable — Execute runs commands, not identifiers |
| **Explain** | The summary mentions the gap by ID, not by inventing a plausible name |
| **Escalate** | The unverifiable identifier is the precondition that was unmet |

## Verified means visible

An identifier is **verified** when it is directly visible in:

- The repository (file content read in this session)
- The current command output or tool result
- A Component spec / Cross-cutting spec / Preamble already promoted to *Approved*

It is **not** verified by:

- Plausibility ("the codebase probably names it `User.Email`")
- Convention ("Go projects typically have a `cmd/` directory")
- Pattern completion from sibling identifiers ("if `GetUser` exists, `UpdateUser` probably does")
- Memory of a similar codebase
- The user's prior statement, unless that statement quoted the identifier verbatim from source

## Specific prohibitions

- Do not invent helpers, wrappers, or adapter functions to make a patch feel complete (no gold plating).
- Do not propose a rename, even an obvious one, without verifying every call site.
- Do not assert that an env var, config key, or feature flag exists unless it is in the repo or in an Approved Cross-cutting Configuration spec.
- Do not invent a route, status code, error string, or message subject — they are part of the public contract and must come from the spec or the existing source.
- Do not invent a SQL object.

## Stop conditions

- A request implies inventing an identifier to make progress: stop, route to *Gaps* / *Open Questions* per the table above, hand to Escalate.
- A spec under Review contains an identifier with no traceable source: report as a defect; do not promote.

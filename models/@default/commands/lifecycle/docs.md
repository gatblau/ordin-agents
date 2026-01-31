---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:lifecycle:docs"
  name: /docs
  version: 1.0.0
  owner: gatblau
  description: "Writes a documentation site that teaches how this project's system works."
description: >
  Authors a concept-ladder teaching documentation site for the target project, by driving the
  docsgen skill under the Document capability. Trigger on "/docs", "document this project",
  "write a docs site", "teach a newcomer this codebase". Do not trigger to edit a single
  hand-written page, to generate API reference from a schema alone, or when no documentation
  practice pack is installed — the run stops and asks which site generator to target.
argument-hint: "[path to the project] [depth: minimal|standard|full]"
---

# /docs — write a teaching documentation site

`/docs` is the typed entry point to the **Document capability**. It resolves its arguments, drives the `docsgen` skill (`urn:ordin:default:skills:documentation:docsgen`), and renders the run report. It holds no procedure of its own: the method — deriving the concept ladder, drafting each rung, tracing every claim, running the anti-AI-prose pass — lives in `docsgen`, and this command restates none of it.

## Arguments

| Argument | Type | Default | Values |
|---|---|---|---|
| `target` | path | the invocation directory | The target project root. Its design and specification are read when present. |
| `depth` | enum | `standard` | `minimal`, `standard`, `full` |
| `audience` | enum | `newcomer` | `newcomer`, `operator` |

Invocation forms:

```
/docs
/docs ./services/payments
/docs ./services/payments depth: full
/docs depth: minimal audience: operator
```

## Active modes

**Observe → Infer → Plan → Explain**, with **Escalate** on any stop. These are the Document capability's five operating modes; the command adds no tool reach of its own and runs under the capability's policy and the workspace safety floor. It never enters Patch (it writes no source) and never enters Execute (it never runs the pack's build command).

## Procedure

This command delegates its method to `docsgen`. It does not reproduce the skill's steps.

1. **Parse arguments.** An unrecognised `depth` or `audience` value stops with the accepted values listed (`DOCS_BAD_ARGUMENT`).
2. **Resolve `target`.** Default to the invocation directory. A path that does not resolve to a directory stops with the path quoted (`DOCS_TARGET_NOT_FOUND`).
3. **Drive `docsgen`.** Enter Observe and load `docsgen`, passing `target`, `depth` and `audience`.
4. **Relay stops verbatim.** Any stop `docsgen` reports — including `DOC_NO_PACK` when no documentation pack is installed — is relayed to the operator unchanged, with no fallback attempted.
5. **Render the run report.** Enter Explain and render `docsgen`'s run report: the ladder, the conflicts with both citations, the intent-only claims, and any paragraph that failed the anti-AI-prose pass.
6. **Print the handoff line.** Name the pack's `buildCommand` for the operator to run. The command does not run it.

## Error table

| Condition | Effect | Code | Observable result |
|---|---|---|---|
| `depth` or `audience` carries an unrecognised value | Stop before loading the skill | `DOCS_BAD_ARGUMENT` | The accepted values are listed |
| `target` does not resolve to a directory | Stop before loading the skill | `DOCS_TARGET_NOT_FOUND` | The path tried is quoted |
| `docsgen` stops for any reason | Relayed verbatim, no fallback | the skill's own code | The skill's stop text, unchanged |

## Required output structure

- **Run report** — the ladder (each rung's title and `enables` sentence), the conflicts found (each with both citations), the intent-only claims, and any paragraph that failed the anti-AI-prose pass.
- **Handoff line** — the pack's `buildCommand`, verbatim, for the operator to run.

## Example — no documentation pack installed

`/docs` in a project with no documentation pack installed relays `docsgen`'s stop:

```
Stopped: no documentation practice pack is installed.

docsgen needs a pack of class `documentation` to know where the site lives,
how navigation is declared, and which fence renders a diagram. There is no
generator-neutral answer to those, so no default is assumed.

Install one, or tell me which site generator to target:
  - mkdocs-material  (documentation-mkdocs-material)

No file has been written.
```

## Handoff

After `/docs` writes the site, run the pack's `buildCommand` (named on the handoff line) to verify the emitted fences, callouts and navigation render under the target generator. The command never runs it for you — building the site is the operator's action.

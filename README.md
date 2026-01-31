# ordin-agents

The agents that ship inside Ordin. Ordin bundles this repository at a pinned commit, so the agents
are there without being installed.

## Agents

| Agent | Identifier | Status |
|---|---|---|
| Ordin, the coordinator | `urn:ordin:default:workspaces:coordinator` | Draft 0.1.0 |
| The document agent: summarises, compares, drafts and humanises documents | `urn:ordin:default:workspaces:document-agent` | Draft 0.1.0 |
| Software engineer (CSPA-431): design, spec, plan and apply, with drift checks between design, spec and code | `urn:ordin:default:workspaces:cspa-431` | 1.0.0 |
| The agent maker | `urn:ordin:default:workspaces:advisor` | Not included; comes with Ordin's `authoring` switch |

```
models/@default/
  workspaces/coordinator/   workspace-profile.yaml, system-role.md
  workspaces/document-agent/ workspace-profile.yaml, system-role.md
  workspaces/cspa-431/      workspace-profile.yaml, system-role.md
  skills/documents/         summarise, compare, draft, humanise (with its scanner, scan.py)
  skills/                   analysis, documentation, quality, release, schema, sync: the CSPA-431 skills
  commands/                 the CSPA-431 slash commands: intent, lifecycle, sync
  capabilities/             the CSPA-431 capabilities
  practice-packs/           stack, testing, architecture, database, library, documentation
  context-resources/        the CSPA glossary and the agent-anatomy vocabulary
  rules/                    working-modes orchestrator, layer rules, the nine operating modes, control loops: plan-centric, cspa
  overlays/                 language: en-GB, en-US, fr, es; style: plain-language, concise, exec-brief,
                            regulatory-precise, teaching; source-workflow: five branching strategies
  vocabulary/               category, audience-role, loop-strategy, rule-subvariant, pack-class
  evals/                    the evaluations the publish gate names
tools/ordin-harness/        checks that run Ordin's own code against this repository
```

## Rules for changing this repository

- An identifier is `urn:ordin:default:<kind-dir>:...`. No other prefix is read.
- A reference must name a part in this repository. Ordin's bundled catalogue reads nothing else.
- A vocabulary term must be in `models/@default/vocabulary/`. `rule-subvariant.yaml` must stay:
  without it Ordin refuses the layer rules and the orchestrator.

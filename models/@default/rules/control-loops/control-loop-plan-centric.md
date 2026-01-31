---
apiVersion: ai.enterprise/v1
kind: control-loop
metadata:
  id: "urn:ordin:default:rules:control-loops:plan-centric"
  name: Plan-centric control loop
  description: "A plan-first control loop over the working modes, for work that starts from an approved plan."
  version: 1.0.0
  owner: gatblau
# A document-only control loop: drops Patch and Execute, because the
# roles that use it (architect, product manager) author documents, not source
# code and never run a build. Composes the seven operating-mode primitives
# by id. `modes` must be a subset of the referencing workspace's
# allowedOperatingModes.
#
# `tool-iterative`: the agent iterates until it asks for no further tool.
#
# There is no `transitions` and no `entry`: the within-iteration graph is derived
# from the modes' own exit conditions and the start node is the referencing
# workspace's `defaultMode`. Both are refused at ingest.
strategy: tool-iterative
trigger: human-pulled
modes:
  # core loop (no patch)
  - "urn:ordin:default:rules:modes:observe-mode"
  - "urn:ordin:default:rules:modes:infer-mode"
  - "urn:ordin:default:rules:modes:plan-mode"
  - "urn:ordin:default:rules:modes:sync-mode"
  - "urn:ordin:default:rules:modes:review-mode"
  # auxiliary (no execute)
  - "urn:ordin:default:rules:modes:explain-mode"
  - "urn:ordin:default:rules:modes:escalate-mode"
---

# Plan-centric control loop — the seven-mode document loop

The control loop for a role whose deliverables are **documents, not source code**, such as
the architect and product-manager workspaces. It has no **Patch** (edit source) and no
**Execute** (run a build) mode, which makes it structurally impossible for the role to touch
code or run a toolchain; such work is delegated to an agent.

> **Loop ≠ lifecycle.** This is the *agent's* per-step loop. Each consuming role keeps its own
> per-change lifecycle / command surface, which this artefact does not define.

## Selection matrix

| Active mode | Permission | Typical tools | When to use |
|---|---|---|---|
| **Observe** | Read-only | File reads, repo grep, MCP read tools | Gathering evidence |
| **Infer** | No external writes | Reasoning only | Forming hypotheses, ranking causes, naming uncertainty |
| **Plan** | Authoring outputs only | File writes scoped to design / decision / analysis docs | Producing a structured artefact — the dominant mode |
| **Sync** | Read both sides; write to one | File writes to the chosen target only | Reconciling a document against implemented reality |
| **Review** | Read-only | File reads, report-only checks | Critique against intent, norms, safeguards (assurance) |
| **Explain** | No writes | None | End-of-step summary for the user |
| **Escalate** | No action tools | None | Stop and ask a human |

## Sequence and selection rules

- **Default is Observe.** Every task starts at the referencing workspace's `defaultMode`, which for these roles is Observe.
- **Exactly one mode is active at a time.** State the active mode in the response if it is not Observe.
- **Auxiliary modes are never top-level.** Explain and Escalate appear inside skills.
- **Mode tags are enforceable, not decorative.** The agent may not call a tool the active mode does not allow. Patch and Execute are *not in this loop* — a step that would need them is a stop, routed to Escalate.
- **No skipping in the loop.** Observe → Infer → Plan → Sync → Review. A step may be empty, but the order of the moves that *do* run is fixed.

## Legal moves

The legal moves within one iteration are **derived, not authored here**: for each
mode this loop composes, its successors are that mode's own *When to exit* list
intersected with this loop's `modes`. Having no Patch or Execute mode therefore
means no edge leads into them, without this file naming a single edge.

Note what derivation does to one edge this artefact used to assert. It listed
`plan → sync`, and `rules/modes/plan-mode.md` (*When to exit*) sanctions only
Review and Escalate — so under derivation the edge simply does not exist.
Restoring it means arguing for it in `plan-mode`, which is where it belongs.

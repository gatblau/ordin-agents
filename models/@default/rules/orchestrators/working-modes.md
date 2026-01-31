---
apiVersion: ai.enterprise/v1
kind: rule-orchestrator
metadata:
  id: "urn:ordin:default:rules:orchestrators:working-modes"
  name: Working modes orchestrator
  description: "Loads the working modes, so the agent always has its full set of modes to hand."
  version: 1.0.0
  owner: gatblau
# No `imports:` block: behavioural-artefact eager loading — operating modes AND
# layer rules — is owned by the plan-derived bootstrap, which @-imports exactly
# the workspace's resolved modes (= allowedOperatingModes) + layer rules + this
# orchestrator into the agent's context. The mode set is never hand-listed here:
# a fixed list would break roles that load a mode subset (e.g. the seven-mode
# document roles, which carry no patch or execute mode).
---

# Working modes — orchestration

Nine modes govern every step of every skill or command. Six are **core** (the loop's moves); three are **auxiliary** (used inside skills, never as top-level entry). An agent loads only the modes its `allowedOperatingModes` names: a document agent carries no Patch or Execute mode, and delegates editing source code and running builds to an agent that does. The workspace loader pulls each allowed mode rule into context whenever this orchestrator is active.

> **Loop topology lives in the control-loop artefact.** The *control-loop topology* (the move sequence, selection matrix, and transition graph) is owned by a **`control-loop`** artefact under `rules/control-loops/` (`control-loops:plan-centric`, the seven-mode document loop; `control-loops:cspa`, the full nine-mode loop). **This orchestrator is a pure import manifest** — it indexes the mode and layer-rule primitives below; it does not carry the selection matrix or transition graph. A workspace selects its loop through `controlLoop:`; `allowedOperatingModes` stays the closed-set authority, and which modes a role loads is governed by it, not by this manifest.

## Core modes

- `observe-mode`
- `infer-mode`
- `plan-mode`
- `patch-mode`
- `sync-mode`
- `review-mode`

## Auxiliary modes

- `execute-mode`
- `explain-mode`
- `escalate-mode`

## Layer rules (compose on top of any mode)

- `layer/identifier-verification`
- `layer/output-language`
- `layer/output-style`
- `layer/sql-safety`
- `layer/spec-anchors`
- `layer/branching-strategy`

Layer rules are not modes; they apply on top of whichever mode is active whenever the work touches their subject. New layer rules belong alongside the existing ones under the `layer/` sibling directory.

## Loop topology

The selection matrix (per-mode permission and tools), the move sequence, and the transition graph are defined by the **control-loop artefact** the active workspace selects via `controlLoop:` — `control-loops:plan-centric` or `control-loops:cspa`. See `rules/control-loops/`. This manifest deliberately holds no topology so that the loop is its own first-class, swappable artefact.

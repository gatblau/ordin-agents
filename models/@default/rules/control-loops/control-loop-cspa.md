---
apiVersion: ai.enterprise/v1
kind: control-loop
metadata:
  id: "urn:ordin:default:rules:control-loops:cspa"
  name: CSPA control loop
  description: "The CSPA control loop: a named path over the nine working modes, starting at Observe."
  version: 1.0.0
  owner: gatblau
# The control loop declares HOW the agent decides what to do next: the strategy it
# runs and the operating modes it may occupy. It composes modes by id; it does not
# redefine them. `modes` must be a subset of, or equal to, the referencing
# workspace's allowedOperatingModes.
#
# `tool-iterative`: the agent iterates until it asks for no further
# tool — its own output is what terminates the step. The nine-mode set below and
# the seven-mode set in control-loop-plan-centric.md are the SAME strategy at two
# permission subsets; the axis is demonstrated by control-loops:autonomic
# (`goal-evaluated`) and control-loops:reactive (`reactive`), not by this pair.
#
# There is no `transitions` and no `entry`: the within-iteration graph is derived
# as { m -> (m.exits & loop.modes) } from the modes' own exit conditions, and the
# start node is the referencing workspace's `defaultMode`. Both are
# refused at ingest as retired fields.
strategy: tool-iterative
trigger: human-pulled          # a person drives each step; cf. control-loops:autonomic for unattended runs
modes:
  # core loop
  - "urn:ordin:default:rules:modes:observe-mode"
  - "urn:ordin:default:rules:modes:infer-mode"
  - "urn:ordin:default:rules:modes:plan-mode"
  - "urn:ordin:default:rules:modes:patch-mode"
  - "urn:ordin:default:rules:modes:sync-mode"
  - "urn:ordin:default:rules:modes:review-mode"
  # auxiliary
  - "urn:ordin:default:rules:modes:execute-mode"
  - "urn:ordin:default:rules:modes:explain-mode"
  - "urn:ordin:default:rules:modes:escalate-mode"
---

# CSPA control loop — the nine-mode deliberative loop

The full deliberative control loop for a role that authors **and implements** change: the
software-engineer workspace (`cspa-431`). It composes all nine operating modes — six core,
three auxiliary — under a single strategy. The modes themselves are the shared primitives
(`rules/modes/*`); this artefact declares which of them the role may occupy and how its
iterations chain.

> **Loop ≠ lifecycle.** This is the *agent's* per-step loop (which mode is active at each
> step). It is distinct from the engineer's per-change *lifecycle* (the four moves · three
> doors · one exit — `/design /rfc /rca → /spec → /breakdown → /apply → /sync-check`), which
> is the user's command surface, not a control loop.

## Selection matrix

| Active mode | Permission | Typical tools | When to use |
|---|---|---|---|
| **Observe** | Read-only | File reads, repo grep, MCP read tools | Gathering evidence |
| **Infer** | No external writes | Reasoning only | Forming hypotheses, ranking causes, naming uncertainty |
| **Plan** | Authoring outputs only | File writes scoped to specs / ADRs / design docs | Producing a structured artefact |
| **Patch** | Propose code changes | File writes scoped to source; never commit / push / merge | Implementing a confirmed plan |
| **Sync** | Read both sides; write to one | File writes to the chosen target only | Reconciling drift in a nominated direction |
| **Review** | Read-only | File reads, lints, tests in report-only mode | Critique against spec, norms, safeguards |
| **Execute** | Restricted writes against allowlisted tools | Sandboxed `build` / `test` / `lint` / dry-run | Behavioural validation, only inside a skill |
| **Explain** | No writes | None | End-of-step summary for the user |
| **Escalate** | No action tools | None | Stop and ask a human |

## Sequence and selection rules

- **Default is Observe.** Every task starts at the referencing workspace's `defaultMode`, which for this role is Observe.
- **Exactly one mode is active at a time.** State the active mode in the response if it is not Observe. A mode change is a deliberate transition — the previous mode's output is the next mode's input.
- **Auxiliary modes are never top-level.** Execute, Explain, Escalate appear inside skills.
- **Mode tags are enforceable, not decorative.** A mode change permits new tools and forbids others. The agent may not call a tool the active mode does not allow.
- **No skipping in the loop.** Observe → Infer → Plan → Patch → Sync → Review. A step may be empty (e.g. a refactor with no spec change skips Plan), but the order of the moves that *do* run is fixed.

## Legal moves

The legal moves within one iteration are **derived, not authored here**: for each
mode this loop composes, its successors are that mode's own *When to exit* list
intersected with this loop's `modes`. Read `rules/modes/<mode>.md` for the
authority on where a mode may hand off to; a table in this file would be a second
copy of it, and a second copy drifts.

How iterations chain is the strategy's business, not the graph's: under
`tool-iterative` the step ends when the agent asks for no further tool.

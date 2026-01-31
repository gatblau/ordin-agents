# Reference architecture — service template

A language-neutral skeleton for a saga / orchestration service. It names
**roles**, not files or types — the concrete layout, language, and workflow
coordinator are the stack pack's (`file-layout.md`) and the Workspace Profile's.

## Components

```
saga service
├── coordinator   # owns the saga definition: ordered steps, compensations, failure policy
├── step          # executes one local step on command; replies succeeded | failed
├── compensation  # undoes a completed step; idempotent, retried until acknowledged
└── saga-state    # the durable record: saga_id, status, current step, per-step outcome
```

## Responsibilities

| Role | Owns | References |
|---|---|---|
| **coordinator** | The ordered steps and their compensations; advancing on a successful reply and driving compensations on failure; persisting saga state on every transition. (Absent in a choreographed saga — the step events carry the order.) | `../patterns/orchestrated.md`, `../patterns/choreographed.md`, `../patterns/saga-state.md` |
| **step** | A single local transaction, invoked by command on the `saga_id`; idempotent on `saga_id` + step; bounded by timeout and retry budget; replies succeeded or failed. | `../steps/contract.md` |
| **compensation** | Semantically undoing a completed step; idempotent and retried until acknowledged. | `../patterns/compensation.md` |
| **saga-state** | The durable record of steps taken and their outcomes; the source of truth for resume / compensate on restart. | `../patterns/saga-state.md` |

## What the template deliberately omits

- **Concrete types, packages, file names** — the stack pack's `file-layout.md`.
- **The workflow / saga coordinator and its client** — "a workflow / saga
  coordinator abstraction" (`approvedLibraries`), supplied by the stack pack.
- **The logging / metrics client** — the stack pack owns the *how* of the signals
  in `../observability/required-signals.md`.

A skill instantiating this template fills each role using the active stack pack's
idiom; this pack supplies only the role decomposition and the per-role rules.

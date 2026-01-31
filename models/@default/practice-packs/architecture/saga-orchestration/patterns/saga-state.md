# Pattern — Saga-state persistence

**Required.** `when:` a saga spans more than one message.

## Problem

A saga is long-running: it can outlive a single request, a process restart, or a
coordinator failover. If the record of which steps have run and how they ended
lives only in process memory, a restart loses every in-flight saga — the system
is left partially applied, unable to complete or compensate.

## Solution

Persist the **saga state** durably: the `saga_id`, the saga type, the current
step, the outcome of each completed step, and whether the saga is running,
completed, or compensating. On startup or failover, the coordinator loads
in-flight sagas from this store and resumes them — driving the next step, or
compensating if the saga had failed.

## Shape (language-neutral)

```
saga_state:
  saga_id        # stable correlation id (steps/contract.md)
  saga_name      # saga type
  status         # running | completed | compensating | compensated
  current_step   # the step the saga is on
  steps[]        # per step: name, status (pending|done|compensated), outcome
  updated_at
```

## Rules

- **State is written in the same transaction as the step effect** where the step
  is local to the coordinator, so the record never disagrees with reality. For a
  remote step, the state is updated on the step's reply.
- **The store is the source of truth for recovery**, not an in-memory cache. The
  `orchestrator-without-persisted-state` anti-pattern keeps it only in memory.
- **Transitions are append-only / monotonic** where possible — a step moves
  `pending → done` or `done → compensated`, so replaying recovery is idempotent.
- **A choreographed saga** persists the same state at each participant (or in a
  shared saga-log) so the distributed saga can still be reconstructed without a
  central coordinator (`choreographed.md`).
- The number of `sagas_in_flight` and saga durations are surfaced as signals
  (`../observability/required-signals.md`).

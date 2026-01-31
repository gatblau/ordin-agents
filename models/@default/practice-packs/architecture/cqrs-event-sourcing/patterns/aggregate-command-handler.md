# Pattern — Aggregate command handler

**Required.** `when:` a command mutates an aggregate.

## Problem

A command expresses intent ("open this account", "cancel this order"). It must be
validated against the aggregate's *current* state, decided deterministically, and
recorded as events — without ever editing prior events and without two concurrent
commands corrupting each other.

## Solution

Route every write through the aggregate that owns the invariant. The aggregate is
reconstructed from its event stream, decides, and emits new events; nothing else
writes to the store.

1. **Load.** Read the aggregate's event stream (`<aggregate>-<id>`,
   `../events/stream-naming.md`) and fold it into current state, noting the
   `currentVersion`. A snapshot may shortcut the fold (`snapshotting.md`).
2. **Decide.** Apply the command to the loaded state. Validate invariants; on
   violation, reject the command — no events are produced.
3. **Append.** Append the new event(s) to the stream asserting
   `expectedVersion == currentVersion` (optimistic concurrency,
   `event-store.md`). On version conflict, reload and retry the decision against
   fresh state.
4. **Return.** Acknowledge the command. The handler returns **no query data** —
   reads come from projections (`query-the-write-side` is prohibited).

## Shape (language-neutral)

```
handle(command):
    history          = store.read(stream = aggregate-id)
    state, version   = fold(history)
    new_events       = aggregate.decide(state, command)   # [] means reject/no-op
    store.append(stream = aggregate-id,
                 events = new_events,
                 expectedVersion = version)               # conflict -> reload+retry
    return ack                                            # never returns read data
```

## Rules

- One aggregate instance is the consistency boundary for one command. A command
  that must atomically change two aggregates is a modelling smell — split it or
  use a process that emits follow-up commands.
- `decide` is a pure function of `(state, command)`: same inputs, same events. No
  I/O, no clock reads outside the event payload.
- The handler emits events; **projection** updates happen later, asynchronously,
  on the read side.

## What this pack does not specify

The **store driver, serialisation, and transaction mechanics** are stack-pack
concerns — referred to here only as "an event-store client abstraction" (manifest
`approvedLibraries`).

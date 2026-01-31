# Projection-consumer good practice

Policy for the read side consuming the event stream, expressed against an
**abstract** store/stream client ("the event store"). No product, library, or
protocol is named — the concrete client is the stack pack's. These are the
settings and behaviours a projection consumer must honour whatever the underlying
store.

## Consumer pattern

- **Durable, checkpointed stream.** The projection owns a durable position into the
  event stream so it survives restarts; it pulls events from its last checkpoint
  at its own pace, which gives natural backpressure (`maxInFlight: bounded`).
- **One checkpoint per projection.** Each projection tracks its own
  `(projection-id, stream-position)` independently, so projections lag and rebuild
  without affecting each other.

## Checkpoint and acknowledgement

- **Checkpoint after the projection commit.** Advance the checkpoint **atomically
  with** the projection write for the same event — in one transaction. Checkpointing
  before the write skips an event on a crash; checkpointing after double-applies it.
- On a processing failure, **do not advance the checkpoint** — the event is
  re-read on the next pass, applied idempotently into the projection.

## Replay from zero (projection rebuild)

The defining read-side capability: a projection can be rebuilt by replaying the
whole stream from the start.

| Setting | Policy |
|---|---|
| `startPosition` | Configurable — `from-zero` for a rebuild, `last-checkpoint` for normal resume. |
| `replayPolicy` | `replay-from-zero-on-rebuild` — a rebuild seeks position 0 and consumes the entire history into a fresh model (`../patterns/projection-rebuild.md`). |
| `checkpointGranularity` | Per-projection stream position, committed with each applied event. |
| `redeliveryBackoff` | Exponential — back off between retries so a transient store/dependency outage is not hammered. |

```
rebuild:  seek(0); for e in stream: apply(model, e); commit(checkpoint=e.position)
resume:   seek(checkpoint); for e in stream: apply(model, e); commit(checkpoint=e.position)
```

## Rules

- `maxInFlight` is **bounded**; "unbounded in-flight" is a defect, not a default.
- A rebuild from zero must reproduce the same model as the live projection — this
  holds only if `apply` is idempotent and upcasting is pure
  (`../events/upcasting.md`).
- The **how** of seeking, committing checkpoints, and wiring the client
  (API, config keys) is the stack pack's; this file states the **what**.

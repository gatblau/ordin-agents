# Pattern — Projection rebuild

**Recommended.** `when:` a read model's shape changes or it is corrupted and must
be regenerated from the event stream.

## Problem

A read model's shape needs to change (a new field, a different grouping), or a
projection has drifted because of a bug. Because a projection is **derived**, it
must be possible to discard it and reconstruct it deterministically from the event
store — without touching the write side.

## Solution

Treat the projection as a pure function of the event stream up to a checkpoint, so
a rebuild is "replay from zero into a fresh model".

1. **Build the new model alongside the old.** Create the new projection table/store
   empty, with its checkpoint at position zero (`startPosition: from-zero`,
   `../broker/projection-consumer.md`).
2. **Replay from zero.** Consume the event stream from the start, applying each
   event to the new model, advancing the checkpoint atomically with each write.
3. **Catch up to live.** When the rebuild reaches the current tail, keep consuming
   new events until lag is within tolerance (`projection_lag`,
   `../observability/required-signals.md`).
4. **Cut over.** Atomically switch reads to the new model and drop the old one. No
   write-side change occurs at any step.

## Shape (language-neutral)

```
rebuild(projection):
    new = empty_model()
    checkpoint = 0
    for event in store.stream(from = 0):       # replay from zero
        apply(new, event)
        checkpoint = event.position            # committed with the write
    when lag(new) <= tolerance:
        swap_reads_to(new); drop(old)
```

## Rules

- A rebuild is **idempotent**: replaying the same events into a fresh model yields
  the same result every time. If it does not, the projection has hidden state
  (a clock, a random value, external I/O) — remove it.
- The event store is never read for *current values* during a rebuild's cutover;
  the model is authoritative for reads, the store for facts
  (`read-model-treated-as-authoritative` is forbidden).
- Old and new projections coexist during a rebuild; readers see a consistent one
  at all times.

## What this pack does not specify

The **projection storage, batching, and cutover mechanics** (blue/green table
swap, view rename) are stack-pack concerns.

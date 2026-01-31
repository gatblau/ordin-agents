# Pattern — Snapshotting

**Recommended.** `when:` an aggregate's event count makes replaying from zero on
every load too slow.

## Problem

Reconstructing an aggregate folds its entire event stream
(`aggregate-command-handler.md`). For a long-lived aggregate with thousands of
events, replaying from zero on every command becomes the dominant cost of a write.

## Solution

Periodically persist a **snapshot** — the folded aggregate state at a known
version — as an *optimisation*, never as the source of truth. Loads start from the
latest snapshot and replay only the events after it.

1. **Write a snapshot** every N events (or on a size/time threshold): store the
   folded `state` together with the `version` it represents.
2. **Load via snapshot:** read the latest snapshot, then read the event stream
   *from `snapshot.version + 1`* and fold those onto the snapshot state.
3. **Snapshots are disposable.** Deleting every snapshot must change only
   performance, never correctness — a load with no snapshot falls back to a full
   replay from zero.

## Shape (language-neutral)

```
load(aggregate-id):
    snap = snapshots.latest(aggregate-id)        # may be absent
    state, version = snap ? (snap.state, snap.version) : (empty, 0)
    for event in store.read(stream=aggregate-id, fromVersion=version+1):
        apply(state, event); version = event.position
    return state, version
```

## Rules

- A snapshot is **derived state**, subject to the same rule as a projection: it
  carries no authority and can always be regenerated from the events. The event
  store remains the single source of truth.
- A snapshot records the **version** it was taken at, so the post-snapshot replay
  starts at exactly the right position. An off-by-one here corrupts the load.
- Snapshots never replace events. The append-only stream is untouched
  (`mutate-a-stored-event` stays prohibited); snapshotting only changes how state
  is *reconstructed*, not what is *stored*.

## What this pack does not specify

The **snapshot cadence, serialisation, and storage location** are stack-pack
concerns.

# Pattern — Append-only event store with optimistic concurrency

**Required.** `when:` state changes are persisted as events (`event-store-append-only`)
and `when:` concurrent commands target one aggregate
(`optimistic-concurrency-by-version`).

## Problem

State must be persisted durably and read back to reconstruct an aggregate, while
guaranteeing that (a) no historical event is ever altered, and (b) two concurrent
commands cannot both extend the same aggregate from the same starting point.

## Solution

Persist state as an **ordered, append-only** sequence of events per aggregate
stream, and gate every append on the version it expected to extend.

### Append-only

- Events are written to the tail of a stream (`<aggregate>-<id>`,
  `../events/stream-naming.md`) and assigned a monotonically increasing position.
- The store supports exactly two write-side operations: **read** a stream from a
  position, and **append** to its tail. There is no update and no delete
  (`mutate-a-stored-event` is prohibited). A correction is a new event.

### Optimistic concurrency by version

- Each aggregate stream has a current **version** = the position of its last event.
- An append carries `expectedVersion`. The store commits only if the stream's
  current version still equals `expectedVersion`; otherwise it rejects with a
  version-conflict error.
- The command handler treats a conflict as "someone else won": reload the stream,
  re-decide against fresh state, append again
  (`aggregate-command-handler.md`).

## Shape (language-neutral)

```
read(stream, fromVersion=0)  -> [events...], currentVersion
append(stream, events, expectedVersion):
    if store.currentVersion(stream) != expectedVersion:
        raise VersionConflict          # caller reloads and retries
    persist(events at currentVersion+1 ..)   # atomic, ordered
```

## Rules

- `append` is **atomic** over the whole batch: either all the command's events
  land at consecutive positions, or none do.
- Versions are per-aggregate-stream, not global. Two different aggregates advance
  independently.
- Reads are by stream and position so any consumer can resume from a checkpoint
  (`../broker/projection-consumer.md`) or replay from zero
  (`projection-rebuild.md`).

## What this pack does not specify

The **storage engine, batching, serialisation format, and index strategy** are
stack-pack concerns — "an event-store client abstraction" (manifest
`approvedLibraries`).

# Pattern — Windowing

**Required.** `when:` an unbounded stream is aggregated.

## Problem

An aggregation (count, sum, join, distinct) over an **unbounded** stream has no
natural end. Holding all state to compute "the total so far" grows without bound
and exhausts memory — the `unbounded-state-without-eviction` prohibition. The
aggregation needs a finite slice of the stream to operate over.

## Solution

Bound the aggregation to a **window**: a finite span of the stream, defined in
the stage's declared time domain (event-time by default). State for a window is
released once the window closes and emits, so total state is proportional to the
number of *open* windows, not to the length of the stream.

Window kinds (language-neutral):

| Window | Shape | Use when |
|---|---|---|
| **Tumbling** | Fixed size, non-overlapping. | Periodic aggregates ("count per minute"). |
| **Sliding** | Fixed size, overlapping by a step. | Rolling aggregates ("count over the last 5 min, every 1 min"). |
| **Session** | Closes after a gap of inactivity. | Per-entity bursts ("a user session"). |

## Shape (language-neutral)

```
source ── records (event-time t) ──► window-assign ──► aggregate ──► emit on close
                                          │
                                   state per OPEN window only
```

## Rules

- A window declares its **time domain** (event-time vs processing-time) and, for
  event-time, defers its close decision to a watermark (`watermarking.md`,
  `../time/watermark-semantics.md`).
- Every stateful window has an **eviction trigger** — close-and-emit, or an
  explicit TTL for session state. State with no eviction trigger is the
  `PIPE_UNBOUNDED_STATE` defect.
- Window state lives in the stage's **checkpointed** state (`checkpointing.md`),
  so an open window survives a restart.

## What this pack does not specify

The **state backend, serialisation, and timer mechanics** are stack-pack
concerns — provided by "a stream-processing runtime abstraction" (manifest
`approvedLibraries`).

# Pattern — Watermarking

**Recommended.** `when:` event-time aggregation must decide when a window is
complete despite out-of-order arrivals.

## Problem

Records carry an **event-time** (when the fact happened) but arrive in a
different order and after a delay (network, batching, retries). An event-time
window — "all events in 10:00–10:01" — cannot close on processing-time, because a
10:00:30 event might arrive at 10:02. Without a completeness signal the
aggregation either emits early and misses late records, or waits forever. That is
the `aggregation-without-watermark` anti-pattern (`PIPE_NO_WATERMARK`).

## Solution

Emit a **watermark**: a monotonically advancing assertion that "no event with an
event-time earlier than W will still arrive". When the watermark passes a
window's end, the window is complete and may emit. A bounded **allowed-lateness**
admits stragglers slightly past the watermark; anything later follows the stage's
declared on-late policy (drop, side-output, or correction).

## Shape (language-neutral)

```
records (event-time, out of order) ──► watermark generator ──► W advances
                                                                  │
window [t0,t1) emits when  W ≥ t1 + allowedLateness ◄─────────────┘
late record (event-time < W − lateness) ──► on-late policy
```

## Rules

- Every event-time aggregation has a **watermark strategy** and a declared
  **allowed lateness**; both live in `../time/watermark-semantics.md`.
- The **on-late policy** (drop / side-output / correct) is explicit, never
  implicit silent loss.
- A watermark is **monotonic** — it never moves backwards; a stale source that
  stops advancing the watermark stalls window emission (a monitored condition).

## What this pack does not specify

The **watermark-generation API and timer firing** are stack-pack concerns —
provided by "a stream-processing runtime abstraction" (manifest
`approvedLibraries`).

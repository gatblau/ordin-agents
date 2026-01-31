# Pattern — Backpressure

**Required.** `when:` a downstream stage is slower than its source.

## Problem

Stages run at different speeds. When a transform or sink is slower than the
source feeding it, the records pile up *somewhere*. Two naive responses both lose
the system:

- **Unbounded buffering** between stages — memory grows until the process is
  killed.
- **Dropping records** under load — silent data loss, invisible until a
  reconciliation downstream fails.

## Solution

Make demand flow **upstream**: a stage pulls from its source only as fast as it
can hand work to the *next* stage. The slowest stage sets the rate of the whole
pipeline; the source reads at exactly the rate downstream can absorb. No stage
buffers without bound, and no record is shed.

This is the architectural reason the source is a **durable pull** consumer
(`../broker/stream-consumer-good-practice.md`): pulling at the consumer's pace
*is* backpressure. A push source must be paired with a bounded, demand-aware
buffer that signals the source to slow.

## Shape (language-neutral)

```
source ◄── demand ── transform ◄── demand ── sink
   │  bounded in-flight    │  bounded in-flight  │
   └── pull at downstream-set rate ─────────────►
```

## Rules

- Every inter-stage buffer is **bounded**; `maxInFlight`
  (`../broker/stream-consumer-good-practice.md`) caps records in flight per
  stage. "Unbounded queue" is a defect, not a default.
- Backpressure **throttles the source**, never drops records. A pipeline that
  must shed load does so by an explicit, documented policy at the source
  boundary, not silently mid-pipeline.
- A persistently lagging stage surfaces as rising `stage_lag`
  (`../observability/required-signals.md`) — the signal to scale that stage out,
  not to widen the buffer.

## What this pack does not specify

The **demand-signalling mechanism and buffer implementation** are stack-pack
concerns — provided by "a stream-processing runtime abstraction" (manifest
`approvedLibraries`).

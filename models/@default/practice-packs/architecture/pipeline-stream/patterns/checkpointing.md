# Pattern — Checkpointing

**Required.** `when:` the pipeline must resume after failure.

## Problem

A stream-processing stage holds **state** (open windows, running aggregates,
dedup keys) and a **position** (the source offset it has consumed up to). If the
stage crashes and restarts, it must resume *exactly* where it left off. Two
failures must be impossible:

- Resuming from the start of an unbounded stream — reprocesses everything,
  multiplies side effects, may never catch up.
- Restoring state that disagrees with the committed offset — replays a gap or a
  duplicate at the boundary.

## Solution

Periodically take a **checkpoint**: a consistent snapshot of *both* the stage's
state and the source offset that produced it, committed atomically. On restart
the stage restores the snapshot and resumes reading from the committed offset.
Because state and offset are committed **together**, the two can never diverge.

1. The runtime quiesces the stage at a checkpoint barrier (no record straddles
   the boundary).
2. It snapshots state and records the source offset reached.
3. It commits both atomically (`commit-with-checkpoint`,
   `../broker/stream-consumer-good-practice.md`).
4. On restart, restore state, seek the source to the committed offset, resume.

## Shape (language-neutral)

```
                ┌── snapshot state ──┐
records ──► stage ─┤                    ├─ commit atomically ─► checkpoint store
                └── record offset ───┘
restart: restore(state, offset) ──► seek(source, offset) ──► resume
```

## Rules

- State snapshot and offset commit are **atomic**; never commit one without the
  other.
- Checkpoint **interval** trades recovery time (records to replay) against
  overhead — bounded, never "checkpoint every record" nor "never".
- `checkpoint_age_seconds` (`../observability/required-signals.md`) is monitored;
  a stalled checkpointer is an outage even while records still flow.
- Exactly-once delivery, when chosen (ADR `delivery-guarantee`), is the
  checkpoint barrier plus a transactional sink commit on the same boundary.

## What this pack does not specify

The **checkpoint store, snapshot format, and barrier mechanics** are stack-pack
concerns — provided by "a stream-processing runtime abstraction" (manifest
`approvedLibraries`).

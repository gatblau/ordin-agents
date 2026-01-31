# Stream source/sink consumer — good practice

Policy for consuming a stream source and committing to a sink, expressed against
an **abstract** client ("the stream runtime"). No product, library, or protocol
is named — the concrete client is the stack pack's. These are the settings and
behaviours a stage must honour whatever the underlying stream.

## Consumer pattern

- **Durable, partitioned pull.** The stage owns a durable position per partition
  so it survives restarts, and it pulls at its own pace rather than being pushed
  faster than it can checkpoint. Pulling at the consumer's pace **is**
  backpressure (`../patterns/backpressure.md`).
- **Partition = unit of parallelism and ordering.** Records within a partition
  are processed in offset order; horizontal scaling assigns partitions across
  workers.

## Offset and acknowledgement

- **Commit the offset with the checkpoint.** The source offset is committed as
  part of the atomic checkpoint, never independently
  (`commit-with-checkpoint`, `../patterns/checkpointing.md`).
- **Ack after checkpoint.** A record is acknowledged only once its effect *and*
  its offset are durably checkpointed (`ack-after-checkpoint`). Acking on receipt
  can drop records on a crash; never auto-ack.

## Replay and flow control

| Setting | Policy |
|---|---|
| `maxInFlight` | Bounded — the most uncheckpointed records a stage holds at once. Caps memory and bounds replay after a crash. |
| `replaySemantics` | Replay from the **last committed offset** on restart; records since the last checkpoint are reprocessed (made safe by an idempotent sink or exactly-once commit). |
| `offsetCommitPolicy` | `commit-with-checkpoint` — offset and state advance together, never apart. |
| `backpressureStrategy` | `pull-rate-from-downstream-demand` — the source reads only as fast as downstream can absorb. |

## Rules

- Every setting above has a **bounded** value; "unbounded in-flight" or
  "commit-every-record without a checkpoint" are defects, not defaults.
- Replay re-emits records — the sink **must** tolerate it
  (`../patterns/idempotent-sink.md`).
- The **how** of wiring these settings (client API, config keys) is the stack
  pack's; this file states the **what**.

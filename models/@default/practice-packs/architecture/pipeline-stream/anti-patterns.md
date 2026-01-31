# Pipeline / stream-processing — anti-patterns

The architectural failure modes this pack forbids. Loaded eagerly. Each maps to
an `antiPatterns` entry in the manifest; a skill that activates on a `pipeline/`
or `stream/` artefact should flag these.

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| **Unbounded state without eviction** | A stateful stage over an unbounded stream that never evicts grows its keyspace forever — memory exhausts and the stage crashes, losing progress. Detection: `PIPE_UNBOUNDED_STATE`. | Bound the state with a window or an explicit eviction policy (`patterns/windowing.md`); never hold an ever-growing per-key map. |
| **Aggregation without a watermark** | An aggregation over an unbounded, possibly out-of-order stream with no watermark can never decide a window is complete. It either emits early (missing late records) or never emits at all. Detection: `PIPE_NO_WATERMARK`. | Drive window completion from watermarks (`patterns/watermarking.md`, `time/watermark-semantics.md`); declare a lateness allowance and an on-late policy. |
| **Side effect without idempotency** | At-least-once delivery and checkpoint replay re-emit records. A sink that performs a non-idempotent side effect (insert, charge, send) double-applies it after any restart. | Make the sink idempotent on a stable record key (`patterns/idempotent-sink.md`), or commit the pipeline exactly-once via checkpoints. |
| **Dropping records under load** | "Shedding" records when a downstream stage is slow silently loses data and is invisible until reconciliation fails. | Apply backpressure (`patterns/backpressure.md`): pull from the source at the rate downstream can absorb, so the slow stage throttles the fast one. |
| **Resuming from the stream start after a crash** | Replaying an unbounded stream from offset zero on every restart reprocesses everything, multiplies side effects and may never catch up. | Checkpoint offset and state together and resume from the last committed checkpoint (`patterns/checkpointing.md`). |

## Smell list (review prompts)

- A stateful operator keyed by an unbounded identifier (user id, session id) with
  no window or TTL.
- A `window` or `groupBy` over event-time with no watermark and no allowed
  lateness.
- A sink `write()` / `insert()` with no upsert, no dedup key, and no
  exactly-once commit.
- An in-memory queue between stages with an unbounded capacity and no demand
  signal back to the source.
- A pipeline that reads "from the beginning" on start with no checkpoint restore.

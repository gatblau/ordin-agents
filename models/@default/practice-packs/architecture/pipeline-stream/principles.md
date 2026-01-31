# Pipeline / stream-processing — principles

The defining stance of this reference architecture. Loaded eagerly; the pattern,
time-semantics and consumer-practice bodies are loaded lazily when their file
globs match.

## The shape

Data flows through a **pipeline** of stages: a **source** reads records (bounded
or unbounded), one or more **transform** stages reshape, filter, enrich or
aggregate them, and a **sink** writes the result out. Each stage is a small,
independent unit with a declared input schema and output schema; records move
downstream, demand pulls upstream. The pipeline does not assume the stream ever
ends.

## Non-negotiables

1. **Every stage declares its time semantics.** A stage states whether it keys on
   **event-time** (when the record happened) or **processing-time** (when it was
   seen). Event-time with watermarks is the default; processing-time is the
   exception and must be justified (`patterns/watermarking.md`,
   `time/watermark-semantics.md`).
2. **Unbounded state is bounded.** A stateful stage over an unbounded stream
   bounds its state with a **window** or an **eviction policy** — never an
   ever-growing map. The `unbounded-state-without-eviction` prohibition forbids
   the alternative (`patterns/windowing.md`).
3. **Progress is checkpointed.** A stage commits its source offset and its state
   snapshot together. On restart it resumes from the last committed checkpoint,
   never from the start of an unbounded stream (`patterns/checkpointing.md`).
4. **Backpressure flows upstream, records are never dropped.** When a downstream
   stage is slower than its source, demand throttles the source rather than
   buffering without bound or shedding records (`patterns/backpressure.md`).
5. **Sinks are idempotent or the pipeline is exactly-once.** At-least-once
   delivery and checkpoint replay re-emit records; a sink either deduplicates
   (`patterns/idempotent-sink.md`) or the pipeline commits exactly-once via
   checkpoints (ADR `delivery-guarantee`).

## What this pack does not decide

- The **language, framework, stream engine, or client library** — those are the
  stack pack's, referred to here only as "the stream runtime".
- **How** signals are emitted (logging library, metric client, field mechanics) —
  this pack names *what* must be emitted (`observability/required-signals.md`);
  the stack pack owns the *how*.
- The **language pairing** — declared by the Workspace Profile, never here.

# Reference architecture — service template

A language-neutral skeleton for a stream-processing pipeline. It names **roles**,
not files or types — the concrete layout, language, and stream runtime are the
stack pack's (`file-layout.md`) and the Workspace Profile's.

## Components

```
pipeline/
├── source         # durable partitioned pull from the stream; declares input schema + event-time
├── transform/     # stateless (map/filter/enrich) and stateful (window/aggregate/join) stages
├── window         # window assignment + watermark-driven completeness for stateful stages
├── checkpoint     # atomic snapshot of stage state + source offset; restore on restart
└── sink           # idempotent write, or exactly-once commit on the checkpoint barrier
```

## Responsibilities

| Role | Owns | References |
|---|---|---|
| **source** | Durable partitioned pull at downstream-set rate; offset committed with the checkpoint; declares the input record schema and event-time. | `../broker/stream-consumer-good-practice.md`, `../time/watermark-semantics.md` |
| **transform** | Per-record reshape (stateless) or bounded stateful aggregation; declares its output schema; holds no unbounded state. | `../patterns/windowing.md`, `../time/watermark-semantics.md` |
| **window** | Window assignment, watermark generation, allowed-lateness and on-late policy; emit on close. | `../patterns/windowing.md`, `../patterns/watermarking.md` |
| **checkpoint** | Atomic snapshot of state + offset; restore + seek on restart; bounded checkpoint interval. | `../patterns/checkpointing.md` |
| **sink** | Idempotent write on a stable key, or exactly-once commit on the checkpoint barrier. | `../patterns/idempotent-sink.md` |

## What the template deliberately omits

- **Concrete types, packages, file names** — the stack pack's `file-layout.md`.
- **The stream runtime, state backend, and sink client** — "a stream-processing
  runtime abstraction" (`approvedLibraries`), supplied by the stack pack.
- **The logging / metrics client** — the stack pack owns the *how* of the signals
  in `../observability/required-signals.md`.

A skill instantiating this template fills each role using the active stack pack's
idiom; this pack supplies only the role decomposition and the per-role rules.

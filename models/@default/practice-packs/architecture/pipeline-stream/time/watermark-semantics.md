# Interface conventions — time and watermark semantics

The shape contracts every stage honours, expressed abstractly — not a wire
schema. This is the body of the manifest's `interfaceConventions`. It binds three
things: the stage I/O schema contract, the time domain and its watermark
semantics, and the checkpoint/offset-commit contract.

## Stage I/O schema contract

- Every stage declares an **input record schema** and an **output record
  schema**. A record is the unit that flows; a stage's output schema is its only
  contract with the next stage.
- A downstream stage's input schema **must accept** its upstream's output schema.
  Schema evolution is forward-only at a stage boundary: a new optional field is
  additive; a removed or retyped field is a breaking stage-boundary change.
- A record carries its **event-time** and a **stable key** (used for windowing,
  partitioning, and sink idempotency).

## Time domain and watermarks

- The **default time domain is event-time**: a window is keyed on when the record
  happened, taken from the record, not from when the stage observed it
  (ADR `event-time-over-processing-time`).
- **Processing-time** is allowed **by exception only** and must be justified; it
  is correct only where event-time is unavailable or irrelevant (e.g. a pure
  rate-limit).
- An event-time aggregation declares a **watermark strategy** and an **allowed
  lateness** (`../patterns/watermarking.md`). The watermark advances
  monotonically and asserts completeness up to its value.
- The **on-late policy** — drop, side-output, or correct — is explicit. Silent
  loss of late records is forbidden.

## Checkpoint / offset-commit contract

- A stage commits its **source offset** and its **state snapshot** as one atomic
  checkpoint (`../patterns/checkpointing.md`).
- On restart, a stage **restores state and seeks the source to the committed
  offset**; it never resumes from the start of an unbounded stream.
- **Replay** is from the last committed offset
  (`../broker/stream-consumer-good-practice.md`); replayed records are made safe
  by an idempotent sink or exactly-once commit
  (`../patterns/idempotent-sink.md`).

## What this pack does not specify

The **concrete schema format, timestamp encoding, and offset representation** are
stack-pack concerns; this file states the contract, not the wire format.

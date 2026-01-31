# Pattern — Dead-letter and replay

**Recommended.** `when:` a message exceeds its redelivery budget and must be
parked for later replay.

## Problem

A poison message — malformed, or one a consumer cannot yet process — is
redelivered forever under at-least-once semantics. It blocks the partition behind
it (with ordered delivery) and burns the consumer in a tight retry loop.

## Solution

Bound redelivery, then **park** the message in a dead-letter destination instead
of retrying indefinitely; replay it deliberately once the cause is fixed.

1. Set a redelivery budget (`maxDeliver`) on the consumer
   (`../broker/consumer-good-practice.md`). Each failed processing increments the
   delivery count.
2. When the count exceeds the budget, route the message to a **dead-letter
   destination** (DLQ) with the failure reason and the original headers attached,
   and acknowledge it off the main stream so the partition advances.
3. Surface DLQ depth as a signal (`dlq_depth`, `../observability/required-signals.md`).
   A rising DLQ is an alert, not a silent sink.
4. **Replay** is an explicit operation: after the defect is fixed, re-publish the
   parked messages to the original stream. Because consumers are idempotent
   (`idempotency.md`), replaying a message that *did* partially succeed is safe.

## Rules

- The DLQ retains enough context to diagnose and replay: original topic,
  original id, headers, delivery count, and the last error.
- Replay re-enters the normal stream; it does not bypass idempotency or
  validation.
- A DLQ is **not** a place messages are forgotten — an unbounded, unmonitored DLQ
  is the `in-memory-event-cache` anti-pattern wearing a different hat.

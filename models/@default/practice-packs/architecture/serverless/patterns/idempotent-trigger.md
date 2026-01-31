# Pattern — Idempotent trigger

**Required.** `when:` an event source may deliver more than once.

## Problem

An event source maps events to function invocations with at-least-once semantics:
on a retry, a redelivery, or a re-drive from a dead-letter destination, the same
logical event triggers the function again. A handler that applies its effect
unconditionally double-applies it — a second charge, a second shipment, a second
downstream write.

## Solution

Give every event a stable **idempotency key** and make the function's effect a
function of that key, so a re-triggered invocation is a no-op.

1. The event source stamps each event with a stable `id` in its envelope
   (`../triggers/binding.md`). The id is identical on every redelivery of the same
   logical event.
2. Before applying the effect, the handler checks a **processed-keys store** (a
   unique constraint on the event id, or an upsert keyed on it) in the external
   state store.
3. If the key is already present, return ack and stop — the work is done. If not,
   apply the effect **and** record the key in the *same* write as the effect, then
   ack.

## Shape (language-neutral)

```
handler(event):
  BEGIN
    if store.seen(event.id): COMMIT; return ack      # already done
    apply side effect
    store.record_processed(event.id)                 # same txn as the effect
  COMMIT
  return ack                                         # ack AFTER commit
```

## Rules

- The idempotency key is the **event id**, not a payload hash and not a delivery
  sequence number. Two deliveries of one event share an id; two distinct events
  never do.
- Record the key in the **same transaction** as the side effect. Recording it
  separately reopens the double-apply window.
- **Acknowledge after the effect is committed** (`../triggers/binding.md`), never
  before — an ack before commit can drop an event on a crash and skip the work.
- Idempotency is the function-per-trigger counterpart of statelessness: because the
  handler reads its state externally (`stateless-handler.md`), a redelivery
  re-reads the same state and the processed-keys check makes the re-apply harmless.

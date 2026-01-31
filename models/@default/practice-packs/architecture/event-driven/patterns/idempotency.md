# Pattern — Idempotent consumer

**Required.** `when:` a consumer processes an at-least-once stream.

## Problem

The broker guarantees at-least-once delivery, so a consumer *will* see the same
event more than once — after a redelivery, a rebalance, or a poller replay. A
consumer that applies a side effect unconditionally double-applies it: a second
charge, a second shipment, a second email.

## Solution

Give every event a stable **idempotency key** and make the consumer's effect a
function of that key, so re-processing is a no-op.

1. The producer stamps each event with a stable `id` (in the envelope —
   `../events/topic-naming.md`). The id is the same on every redelivery of the
   same logical event.
2. Before applying the effect, the consumer checks a **processed-keys store**
   (e.g. a unique constraint on `processed_event_id`, or an upsert keyed on it).
3. If the key is already present, acknowledge and stop — the work is already
   done. If not, apply the effect **and** record the key in the *same*
   transaction as the effect, then acknowledge.

## Shape (language-neutral)

```
on event e:
  BEGIN
    if exists processed(e.id): COMMIT; ack; return    # already done
    apply side effect
    INSERT INTO processed (id) VALUES (e.id)            # same txn as the effect
  COMMIT
  ack                                                  # ack AFTER commit
```

## Rules

- The idempotency key is the **event id**, not a payload hash and not the offset.
  Two distinct deliveries of one event share an id; two distinct events never do.
- Record the key in the **same transaction** as the side effect. Recording it
  separately reopens the double-apply window.
- **Acknowledge after commit** (`../broker/consumer-good-practice.md`), never
  before — an ack before commit can drop an event on a crash.
- Idempotency and the outbox are complementary: the outbox makes *publishing*
  exactly-effectively-once; idempotency makes *consuming* exactly-effectively-once.

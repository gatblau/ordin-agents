# Observability — required signals (the *what*)

The signals a system built with this pack **must** emit. This is the *what* slice
of the `observabilityConventions` seam; the *how* — logging library, metric
client, field-naming mechanics — is the stack pack's. A skill consuming this pack
checks that these signals exist, not how they are wired.

> The concrete signal set below is authored as proposed and is flagged for
> platform / observability-team ratification at governance approval (Phase 1
> OQ-3). Treat it as a baseline an overlay may strengthen.

## Required counters

| Counter | Meaning | Why it is required |
|---|---|---|
| `event_published_total` | Events published, by topic. | Detects a producer that has gone silent. |
| `event_consumed_total` | Events consumed, by topic and consumer group. | With the published count, exposes a drift between produce and consume rates. |
| `consumer_lag` | Unconsumed messages behind a consumer group. | The primary health signal for an async consumer; rising lag means it cannot keep up. |
| `dlq_depth` | Messages parked in the dead-letter destination. | A rising DLQ is an alert (`../patterns/dead-letter-replay.md`), never a silent sink. |

## Required span attributes

Set on the span that produces or consumes a message:

- `messaging.system` — the broker class (set by the stack pack's client).
- `messaging.destination` — the topic the message was published to or consumed
  from.

## Required log fields

Every log line emitted while handling an event carries:

- `trace_id` — correlates the log with the distributed trace (envelope
  `traceparent`, `../events/topic-naming.md`).
- `tenant_id` — the tenant the event belongs to (envelope `tenant`).
- `event_id` — the event's stable id (the idempotency key).

## Rules

- These are **minimums**. An overlay or the stack pack may add more; none may be
  dropped.
- The counters must be labelled so produce/consume/lag/DLQ are attributable to a
  topic and consumer group, not just global totals.
- Field **values** come from the event envelope; field **emission mechanics** are
  the stack pack's.

# Event interface — topic naming and envelope

The shape contract for events. This is an abstract contract (naming + required
envelope fields), **not** a wire schema and **not** a serialisation format —
those are the stack pack's and the platform's concern.

## Topic naming

```
<bounded-context>.<aggregate>.<event-type>.v<schema-version>
```

- **bounded-context** — the owning domain (`orders`, `billing`).
- **aggregate** — the entity the event is about (`order`, `invoice`).
- **event-type** — the fact, past tense (`placed`, `cancelled`, `paid`).
- **v\<schema-version>** — the major schema version (`v1`, `v2`). A breaking
  change increments it (`../events/schema-evolution.md`).

Example: `orders.order.placed.v1`.

### Naming rules

- Name the **fact and its owner**, never the consumer. `orders.order.placed.v1`,
  not `order-events-for-billing` (the `topic-name-encoding-a-consumer`
  anti-pattern).
- Event types are **past tense** — they record something that has happened, not
  a command to do something.
- The bounded-context and aggregate are owned by the producer's domain; a
  consumer never renames them.

## Envelope (required fields)

Every event carries an envelope with at least these fields. The envelope is a
*shape* contract — field presence and meaning — not a byte layout.

| Field | Meaning |
|---|---|
| `id` | Stable, globally unique event id. The idempotency key (`../patterns/idempotency.md`). Identical across redeliveries. |
| `type` | The fully-qualified event type, matching the topic's `<event-type>.v<n>`. |
| `occurredAt` | When the fact happened (producer clock), not when it was published. |
| `traceparent` | W3C trace context for distributed tracing (`../observability/required-signals.md`). |
| `tenant` | The tenant the event belongs to, for isolation and routing. |

The payload (the event's data) sits beside the envelope; its fields are the
event-type's own contract and evolve under `../events/schema-evolution.md`.

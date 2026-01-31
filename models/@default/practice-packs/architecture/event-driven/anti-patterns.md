# Event-driven services — anti-patterns

The architectural failure modes this pack forbids. Loaded eagerly. Each maps to
an `antiPatterns` entry in the manifest; a skill that activates on a messaging or
events artefact should flag these.

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| **Synchronous call from an event handler** | Reintroduces synchronous coupling into an async consumer — the handler now fails when the called service is slow or down, defeating the decoupling the architecture exists for. | Publish a follow-up event, or offload to a separate request/response boundary that owns the synchronous concern. |
| **Publish inside a DB transaction without an outbox** | The publish and the commit are not atomic. A crash after commit but before publish loses the event; a crash after publish but before commit emits an event for a state change that rolled back. | Use the outbox (`patterns/outbox.md`): record the event in the same transaction, publish from the outbox afterwards. |
| **Consumer without an idempotency key** | At-least-once delivery *will* redeliver. A non-idempotent consumer double-applies side effects (double charge, double email). | Make the consumer idempotent on an idempotency key (`patterns/idempotency.md`). |
| **Topic name encoding a consumer** | Naming a topic after who reads it (`orders-for-billing`) couples the producer to the consumer topology; adding a second consumer forces a producer change. | Name topics after the fact and its owner (`patterns/.../topic-naming.md`): `<bounded-context>.<aggregate>.<event-type>.v<n>`. |
| **In-memory event cache as the source of truth** | Buffering events in process memory loses them on restart and cannot be replayed. | Keep durability in the broker and the outbox; treat process memory as a cache only. |

## Smell list (review prompts)

- A consumer handler that opens an outbound HTTP/RPC call.
- A `publish()` call inside the same code block as a DB `commit()` with no outbox.
- An event type named in the imperative ("ChargeCard") rather than the past tense
  ("PaymentRequested" / "CardCharged").
- A consumer with no de-duplication store or unique constraint on an event id.

# Pattern — In-process domain events

**Recommended.** `when:` a module reacts to another module's state change without
a synchronous call.

## Problem

Sometimes a module should react to something that happened in another module
("when an order is placed, billing prepares an invoice"), but a direct facade
call would couple the producer to the reactor — the producer would have to know
billing exists and call it.

## Solution

The producer publishes an **in-process domain event**; interested modules
subscribe. The producer knows nothing about its subscribers. This is the
in-process analogue of the event-driven pattern — but with no broker, no
network, and no at-least-once redelivery.

1. The producing module raises a domain event through the **in-process
   mediator / event-bus abstraction** (`approvedLibraries`), naming it
   `<module>.<entity>.<event>` (`../modules/boundary-rules.md`).
2. Subscribing modules register a handler. Handlers run **in the same process**,
   within the producer's transaction boundary (or a clearly-defined immediately-
   after hook) — delivery is in-process and exactly-once, so **no idempotency key
   and no outbox are needed**.
3. The event carries a small, stable payload — a boundary DTO, not an internal
   entity.

## Shape (language-neutral)

```
module orders:   publish orders.order.placed(OrderPlaced{ id, total })
module billing:  on orders.order.placed -> prepare invoice    # in-process handler
```

## Rules

- Delivery is **in-process and synchronous-to-the-transaction**: there is no
  broker and no redelivery. Do not bolt on outbox/idempotency — that is the
  `distributed-pattern-where-in-process-suffices` anti-pattern.
- The event payload is a boundary DTO; it never carries an internal entity.
- If a reaction genuinely needs to survive a process crash or cross a network,
  the boundary is no longer in-process — model it with the event-driven
  architecture pack instead, deliberately.

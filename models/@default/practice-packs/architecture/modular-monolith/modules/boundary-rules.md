# Module boundary rules

The cross-module interface conventions. Abstract shape contracts — not a wire
format and not a language API.

## Cross-module calls

- A module is reachable **only** through its published facade
  (`../patterns/module-facade.md`). No other module imports anything under a
  module's `internal/`.
- Facade methods accept and return **boundary DTOs**, never internal entities.
- A facade call is a direct in-process call: no retry, timeout, or circuit
  breaker (those belong to the request/response architecture).

## In-process events

- An in-process domain event is named `<module>.<entity>.<event>` — for example
  `orders.order.placed`.
- The module name is the **producer's**; a subscriber never renames it.
- Event payloads are boundary DTOs (`../patterns/in-process-events.md`).

## Table ownership

- There is **one** database. Each table is owned by exactly one module
  (`ownership-map.md`).
- Only the owning module writes its tables. Another module that needs the data
  reads it through the owner's facade, or keeps its own table and reconciles via
  an in-process event.
- A foreign key may cross module tables for referential integrity, but the
  **write path** never does — only the owner mutates.

## When a boundary is wrong

- A facade returning another module's internal entity → the model is leaking;
  introduce a boundary DTO and, on the consumer side, an anti-corruption layer
  (`../patterns/anti-corruption-layer.md`).
- A table written by two modules → split ownership or move the write behind one
  module's facade.
- A need for crash-durable or networked delivery → this is no longer an
  in-process boundary; use the event-driven architecture pack deliberately.

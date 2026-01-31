# Event interface — schema evolution via upcasting

How a stored event's payload is allowed to change over time. Because events are
**immutable** and live forever in the store, history written under an old schema
must stay readable under the new one. The mechanism is **upcasting on read** — old
events are transformed in flight, never rewritten in place.

## The constraint: stored events are never edited

A stored event is a historical fact (`../patterns/event-store.md`). When a schema
changes you do **not** migrate the events table. The bytes written years ago stay
exactly as written; editing them is the `mutate-a-stored-event` anti-pattern and
would make every projection's rebuild non-reproducible.

## Backward-compatible changes (same event version)

An old event remains readable by a new consumer with no upcaster needed when:

- A new **optional** field is added with a default applied when absent.
- A field's accepted range is **widened** where consumers already tolerate it.

Consumers **ignore unknown fields** so a producer can add optional data without a
coordinated rebuild.

## Breaking changes — upcasting on read

A renamed field, a changed type, or a newly-required field is a **new event
version** (`AccountOpened.v2`). Old `v1` events stay in the store unchanged.

1. The aggregate and projections emit/expect the **latest** version.
2. A pure **upcaster** transforms a `v1` event into the `v2` shape on read —
   supplying defaults for new fields, mapping renamed ones, deriving a changed
   type. It performs no I/O.
3. Every reader (the aggregate fold, each projection, a rebuild) applies the
   upcaster chain before its logic sees the event, so core logic only ever handles
   the latest shape.
4. Upcasters are **chained and cumulative**: `v1 → v2 → v3`. A reader on `v3`
   composes all upcasters; nothing is ever lost because nothing is rewritten.

## Shape (language-neutral)

```
read(event):
    while event.version < LATEST:
        event = upcaster[event.type, event.version](event)   # pure, in flight
    return event            # logic only sees LATEST
```

## Rules

- Upcasting happens **on read, in memory**; the store is never rewritten. A
  rebuild from zero (`../patterns/projection-rebuild.md`) applies the same
  upcasters and therefore reproduces the same model.
- An upcaster is a **pure function** of one event: same input, same output, no
  clock, no lookups.
- The **serialisation format and a schema registry** (how bytes are encoded, where
  schemas live) are stack-pack / platform concerns, not specified here.

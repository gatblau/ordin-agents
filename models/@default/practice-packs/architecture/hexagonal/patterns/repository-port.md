# Pattern — Repository port

**Required.** `when:` the core needs persistence.

## Problem

The domain core needs to load and store aggregates, but it must not depend on a
database, a driver, or an ORM. If the core calls a concrete data-access object, the
dependency arrow points outward — the core now depends on infrastructure, cannot be
tested without it, and changes whenever the storage technology changes.

## Solution

The core defines a **repository port**: an interface, owned by the core, expressed
purely in domain terms. It speaks of aggregates and domain identifiers, never of
tables, rows, queries, or connections. A **driven adapter** in the infrastructure
layer implements that port using the concrete storage technology.

1. The core declares the port — the capability it requires (load, save, find by a
   domain criterion) in terms of domain entities and domain errors.
2. A driven persistence adapter implements the port, translating domain entities to
   the storage shape and back (`../boundary/dto-mapping.md`) and translating storage
   failures to domain errors (`../boundary/error-translation.md`).
3. The wiring layer binds the concrete adapter to the port at the composition root
   (`../patterns/dependency-inversion.md`).

## Shape (language-neutral)

```
core/
  defines  RepositoryPort  { load(id) -> Entity ; save(Entity) ; findBy(criterion) -> [Entity] }
  uses     RepositoryPort   (depends on the interface only)

adapters/persistence/
  implements RepositoryPort  (maps Entity <-> stored shape; maps store error -> domain error)
```

## Rules

- The port is defined in the **core**, not in the adapter. The core owns the
  interface; the adapter owns the implementation.
- The port signature names only **domain types** — no connection, transaction
  handle, query string, or driver type crosses it.
- A storage failure surfaces to the core as a **domain error**, translated at the
  adapter; the core never catches a driver-specific exception.

## What this pack does not specify

The **driver, query mechanics, connection pooling, and migration tooling** are
stack-pack concerns. This pack names only the port shape and the inward dependency;
the concrete persistence library is the stack pack's.

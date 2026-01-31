# Modular monolith — principles

The defining stance of this reference architecture. Loaded eagerly; the pattern
and module-rule bodies are loaded lazily when their file globs match.

## The shape

One deployable, one process, one database — structured internally as **N modules**
with hard boundaries. Each module owns its data and its logic, exposes a small
**published facade**, and keeps everything else internal. Modules collaborate
in-process: a direct facade call, or an in-process domain event. There is **no
network boundary between modules**, and therefore no broker, no remote call, and
no distributed transaction.

This is the broker-free counterpart to event-driven services. The two validate
both ends of the disjoint-seam model: the same stack pack composes with either.

## Non-negotiables

1. **Facade-only cross-module calls.** A module reaches another module *only*
   through its published facade (`patterns/module-facade.md`). Importing another
   module's internals is the `cross-module-internal-import` prohibition.
2. **Single-owner tables.** There is one database; each table is owned by exactly
   one module and only its owner writes it (`modules/ownership-map.md`).
3. **In-process over distributed.** A change spanning modules uses an in-process
   transaction or an in-process domain event (`patterns/in-process-events.md`),
   never outbox/saga/idempotency-key — those exist to bridge a network boundary
   this architecture does not have.
4. **Translate at the boundary.** When two modules have divergent models, the
   consumer wraps the producer in an anti-corruption layer
   (`patterns/anti-corruption-layer.md`) rather than leaking one model into the
   other.
5. **Keep the boundary observable.** Cross-module traffic is measured
   (`observability/required-signals.md`) so creeping coupling is visible before
   it hardens.

## Why the boundary matters

The modular monolith earns the simplicity of a single deployable only while the
module boundaries hold. Once modules reach into each other's internals or share
tables, it becomes a distributed monolith with none of the benefits — the worst
of both. The facade and single-owner rules are what keep a future extraction
(one module → one service) a local change rather than a rewrite.

## What this pack does not decide

- The **language, framework, or build tooling** — the stack pack's.
- **How** signals are emitted — this pack names *what*; the stack pack owns *how*.
- The **language pairing** — the Workspace Profile's, never here.

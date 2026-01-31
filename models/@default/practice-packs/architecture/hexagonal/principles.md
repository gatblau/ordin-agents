# Hexagonal / ports-and-adapters — principles

The defining stance of this reference architecture. Loaded eagerly; the pattern
and boundary bodies are loaded lazily when their file globs match.

## The shape

A service is organised as a **domain core** surrounded by **adapters**, connected
through **ports**. The core holds the business rules and depends on nothing outside
itself. A **port** is an interface the core *owns*: it states a capability the core
requires (persistence, notification) or offers (a use case the outside may invoke).
An **adapter** sits at the edge and depends on a port — a *driving* adapter calls a
port the core offers; a *driven* adapter implements a port the core requires.

## Non-negotiables

1. **The dependency rule points inward.** Every dependency arrow points toward the
   core. The core depends on its own ports and on nothing else. Adapters depend on
   ports; ports depend on the core. Nothing the core touches depends on an adapter.
2. **The core is pure.** No framework type, transport type, ORM entity, or
   infrastructure concern appears inside the domain core. If it cannot be unit
   tested with no external system running, it does not belong in the core.
3. **Ports are owned by the core, not by the adapter.** The interface is defined
   where it is *needed* (the core), not where it is *implemented* (the adapter).
   An adapter implements a port; it never dictates one.
4. **Translation happens at the edge.** External DTOs become domain entities, and
   external errors become domain errors, at the adapter boundary
   (`boundary/dto-mapping.md`, `boundary/error-translation.md`). The core never
   sees a transport shape.
5. **Instrumentation lives at adapters.** Observability signals are emitted where
   the core meets the outside — at the adapters — never inside the domain core
   (`observability/required-signals.md`). The core stays uninstrumented.

## What this pack does not decide

- The **language, framework, wiring container, or driver** — those are the stack
  pack's, referred to here only as "a dependency-wiring abstraction".
- **How** signals are emitted (logging library, metric client, field mechanics) —
  this pack names *what* must be emitted; the stack pack owns the *how*.
- The **language pairing** — declared by the Workspace Profile, never here.

# Pattern — Dependency inversion at the boundary

**Required.** `when:` any boundary crosses into an external system.
Also backs the **recommended** `adapter-per-external-system`: `when:` the core
integrates with more than one external system.

## Problem

The core needs work done by external systems — storage, notification, another
service — but it must not depend on them. Naively, the high-level core would call
the low-level infrastructure, pointing the dependency arrow outward and dragging
every external concern into the core.

## Solution

Invert the dependency. The core depends on an **abstraction it owns** (a port); the
external system is reached only through a **driven adapter** that implements that
port. Concrete adapters are bound to ports at the **composition root** by a
dependency-wiring abstraction, so the core never names a concrete type.

1. For each external system the core needs, the core defines a **driven port** in
   domain terms (`repository-port.md` is the persistence case of this rule).
2. A **driven adapter** implements the port against the concrete external system,
   translating shapes (`../boundary/dto-mapping.md`) and errors
   (`../boundary/error-translation.md`) at the edge.
3. The **composition root** — the only place that knows concrete types — wires each
   adapter to its port using the dependency-wiring abstraction, then hands the wired
   ports to the core.

## Adapter per external system (recommended)

When the core integrates with more than one external system, give **each** its own
driven adapter behind its own port. Do not let one adapter span two systems: a
single adapter that talks to both a database and a queue couples them and hides two
failure domains behind one boundary.

## Shape (language-neutral)

```
core defines    NotificationPort, RepositoryPort        # abstractions the core owns
adapters        EmailAdapter implements NotificationPort
                StoreAdapter implements RepositoryPort
composition     wire(EmailAdapter -> NotificationPort)   # dependency-wiring abstraction
root            wire(StoreAdapter -> RepositoryPort)
                start(core, wired ports)
```

## Rules

- The core depends on the **port**, never on the adapter or the external system.
- Concrete wiring happens **only** at the composition root; no domain or use-case
  code references a concrete adapter type.
- One driven port and one adapter **per external system**; do not merge two systems
  behind one boundary.

## What this pack does not specify

The **wiring container/injector, lifecycle, and configuration mechanics** are
stack-pack concerns — referred to here only as "a dependency-wiring abstraction"
(manifest `approvedLibraries`).

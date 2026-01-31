# Modular monolith — anti-patterns

The architectural failure modes this pack forbids. Loaded eagerly. Each maps to
an `antiPatterns` entry in the manifest; a skill activating on a module-boundary
artefact should flag these.

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| **Import another module's internals** | Reaching past the facade into another module's internal types couples the two modules and erases the boundary; a change to the internal breaks a distant module. This is how a modular monolith rots into a distributed monolith. | Call the published facade only (`patterns/module-facade.md`). If the facade lacks what you need, extend the facade — do not bypass it. |
| **Shared mutable table across modules** | Two modules writing one table destroys single-owner ownership: neither can reason about the table's invariants, and a schema change must coordinate both. | Give the table one owner (`modules/ownership-map.md`); the other module reads through the owner's facade or keeps its own table. |
| **Distributed pattern where in-process suffices** | Adding an outbox, saga, or idempotency-key between in-process modules pays the full cost of distributed coordination with no network boundary to justify it. | Use one in-process transaction across the modules, or an in-process domain event (`patterns/in-process-events.md`). |

## Smell list (review prompts)

- An import path crossing from one module into another module's `internal/`.
- A table written by handlers in more than one module.
- An outbox table, saga coordinator, or message-broker client appearing inside a
  single-deployable codebase with no remote consumers.
- A facade method that returns another module's internal entity type rather than a
  boundary DTO (the model is leaking — apply an anti-corruption layer).

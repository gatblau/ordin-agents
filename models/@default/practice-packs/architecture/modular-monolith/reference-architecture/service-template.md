# Reference architecture — service template

A language-neutral skeleton for one module in a modular monolith. It names
**roles**, not files or types — the concrete layout and language are the stack
pack's (`file-layout.md`) and the Workspace Profile's.

## Module skeleton

```
module <name>
├── facade        # the published surface: the ONLY cross-module entry point
├── internal      # entities, logic, persistence — private to this module
└── events        # in-process domain events this module publishes / subscribes to
```

## Responsibilities

| Role | Owns | References |
|---|---|---|
| **facade** | The narrow published interface and boundary DTOs; the place cross-module observability is recorded. Accepts/returns DTOs, never internal entities. | `../patterns/module-facade.md` |
| **internal** | Entities, domain logic, and the module's owned tables. Never imported by another module. | `../modules/ownership-map.md` |
| **events** | In-process domain events named `<module>.<entity>.<event>`, published via the in-process event bus; subscriptions to other modules' events. | `../patterns/in-process-events.md`, `../modules/boundary-rules.md` |

## What the template deliberately omits

- **Concrete types, packages, file names** — the stack pack's `file-layout.md`.
- **The in-process mediator / event-bus implementation** — referred to abstractly
  in `approvedLibraries`; the concrete library is the stack pack's.
- **The logging / metrics client** — the stack pack owns the *how* of the signals
  in `../observability/required-signals.md`.

## What it must NOT contain

- A message-broker client (blocked in `approvedLibraries` — there is no network
  boundary between modules).
- An outbox table, saga coordinator, or idempotency-key store — distributed
  machinery with nothing to bridge (`../anti-patterns.md`).

A skill instantiating this template fills each role using the active stack pack's
idiom; this pack supplies only the role decomposition and the boundary rules.

# Reference architecture — service template

A language-neutral skeleton for a hexagonal service. It names **roles**, not files or
types — the concrete layout, language, and wiring container are the stack pack's
(`file-layout.md`) and the Workspace Profile's.

## Components

```
hexagonal service
├── domain         # entities + business rules; depends on nothing outside itself
├── ports          # interfaces the core owns: inbound (use cases) + driven (capabilities)
├── adapters       # driving (translate triggers -> inbound ports) + driven (implement driven ports)
└── composition    # the wiring root: binds concrete adapters to ports, then starts the core
```

## Responsibilities

| Role | Owns | References |
|---|---|---|
| **domain** | Entities and business rules. Imports no adapter and no framework type; pure and unit-testable in isolation. | `../principles.md` |
| **ports** | The inbound and driven interfaces the core defines. Inbound ports name use cases; driven ports name capabilities the core requires. | `../patterns/use-case.md`, `../patterns/repository-port.md` |
| **adapters** | Driving adapters translate external triggers to inbound-port calls; driven adapters implement driven ports against external systems, translating DTOs and errors at the edge. Adapters stay thin — no business logic. | `../boundary/dto-mapping.md`, `../boundary/error-translation.md`, `../patterns/dependency-inversion.md` |
| **composition** | The only place that knows concrete types: binds each adapter to its port via the dependency-wiring abstraction and starts the core. | `../patterns/dependency-inversion.md` |

## What the template deliberately omits

- **Concrete types, packages, file names** — the stack pack's `file-layout.md`.
- **The dependency-wiring container and its config** — "a dependency-wiring
  abstraction" (`approvedLibraries`), supplied by the stack pack.
- **The logging / metrics client** — the stack pack owns the *how* of the signals in
  `../observability/required-signals.md`; this pack requires only that they are emitted
  at the adapters.

A skill instantiating this template fills each role using the active stack pack's
idiom; this pack supplies only the role decomposition and the inward dependency rule.

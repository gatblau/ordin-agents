# Hexagonal / ports-and-adapters — anti-patterns

The architectural failure modes this pack forbids. Loaded eagerly. Each maps to an
`antiPatterns` entry in the manifest; a skill that activates on a ports, adapters,
or domain artefact should flag these.

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| **Domain imports an adapter** | Reverses the dependency rule. The core now depends on a concrete adapter (and through it on a transport, driver, or framework), so it can no longer be tested or reasoned about in isolation, and a change to infrastructure forces a change to the core. | Define a port the core owns; let the adapter implement it. The core depends only on the port (`patterns/repository-port.md`, `patterns/dependency-inversion.md`). |
| **Framework type leaks into the core** | A transport request, an ORM entity, or a framework annotation inside the domain couples the business rules to infrastructure. The core stops being pure and drags the framework into every test. | Translate at the adapter boundary (`boundary/dto-mapping.md`): map the framework/DTO type to a domain entity on the way in and back on the way out. |
| **Business logic in an adapter** | Domain rules placed in a driving or driven adapter cannot be exercised without the external system, and the same rule drifts across adapters. The core no longer holds the single source of behaviour. | Keep the adapter thin: it only translates and delegates. The rule belongs in the core behind a port (`patterns/use-case.md`). |
| **Port defined by the adapter** | When the adapter owns the interface, the core depends on the adapter's shape and the dependency arrow points outward. The "port" is then just the adapter's API. | Define the port where the capability is *needed* — in the core — and have the adapter implement it. |
| **Instrumentation inside the core** | Emitting metrics, spans, or transport-aware logs from the domain core pulls observability concerns into pure business code and couples it to the signal mechanics. | Emit signals at the adapter boundary only (`observability/required-signals.md`); pass correlation values inward as plain domain values if the core needs them. |

## Smell list (review prompts)

- An `import` in a domain file that names an adapter, a driver, a transport, or a
  framework.
- A domain entity carrying a field whose type comes from a serialization or ORM
  layer.
- A conditional that expresses a business rule sitting inside an HTTP, queue, or
  database adapter.
- An interface that the core depends on but that is declared in the adapter's
  module rather than the core's.
- A metric increment or span start inside a use case or entity in the core.

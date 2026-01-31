# Reference architecture — service template

A language-neutral skeleton for a synchronous request/response service. It names
**roles**, not files or types — the concrete layout, language, and service client are
the stack pack's (`file-layout.md`) and the Workspace Profile's.

## Components

```
request/response service
├── handlers      # accept a request, serve it from the owned datastore, return a versioned response
├── clients       # resilient wrappers around calls to other services (timeout/retry/breaker/bulkhead)
├── api           # versioning policy, error envelope, pagination, status-code map
└── store         # the service's OWN datastore — never shared with another service
```

## Responsibilities

| Role | Owns | References |
|---|---|---|
| **handlers** | Serving inbound requests on a versioned route; validation; mapping outcomes to the status-code map; idempotent writes. Authn/authz at this boundary. | `../api/versioning.md`, `../api/error-envelope.md`, `../patterns/idempotent-write.md` |
| **clients** | Every cross-service call, wrapped with a timeout, a retry budget, a circuit breaker, and a bulkhead. No call leaves the service except through here. | `../patterns/resilience.md` |
| **api** | The versioning policy, the one error envelope, the pagination contract, and the status-code map — the service's external shape contract. | `../api/versioning.md`, `../api/error-envelope.md`, `../api/pagination.md` |
| **store** | The service's own datastore; reached only by this service. Cross-service data comes via `clients`, never by sharing this store. | `topology.md` (`one-service-one-datastore`) |

## What the template deliberately omits

- **Concrete types, packages, file names** — the stack pack's `file-layout.md`.
- **The service client and its config** — "a resilient service-client abstraction"
  (`approvedLibraries`), supplied by the stack pack.
- **The logging / metrics client** — the stack pack owns the *how* of the signals in
  `../observability/required-signals.md`.

A skill instantiating this template fills each role using the active stack pack's
idiom; this pack supplies only the role decomposition and the per-role rules.

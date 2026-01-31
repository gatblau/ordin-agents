# Request/Response microservices — anti-patterns

The architectural failure modes this pack forbids. Loaded eagerly. Each maps to an
`antiPatterns` (or prohibited `designPatterns`) entry in the manifest; a skill that
activates on an API or handler artefact should flag these.

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| **Chatty cross-service calls** | Fanning one inbound request into many fine-grained downstream calls multiplies latency (each adds a round trip) and failure surface (each adds a thing that can be slow or down). | Coarsen the contract so one call returns what the caller needs, or co-locate the data behind the service that owns it. |
| **Synchronous call chain without a timeout** | An unbounded chain (A→B→C→D) lets one slow downstream stall every caller above it, exhausting their connection and thread budgets — a coupling cascade. | Put a timeout, a retry budget, and a circuit breaker on every hop (`patterns/resilience.md`); keep chains shallow. |
| **Shared database across services** | Two services writing one schema couple their releases, hide the cross-service contract inside the database, and make one service's migration another's outage. | Give each service its own datastore (`one-service-one-datastore`); reach other data only through the owning service's API. |
| **Retryable write that is not idempotent** | A timeout makes the caller retry. A non-idempotent write double-applies the effect (double order, double charge) because the first attempt may have succeeded server-side. | Make write endpoints idempotent on an idempotency key (`patterns/idempotent-write.md`). |

## Smell list (review prompts)

- A handler that issues a downstream call with no timeout, retry budget, or circuit
  breaker.
- One inbound request that triggers a loop of per-item downstream calls (an N+1
  across services).
- A service reading or writing a table owned by another service, or a connection
  string shared between two services.
- A `POST`/`PUT` write endpoint with no idempotency key and no de-duplication, sitting
  behind a client that retries on timeout.
- A call chain three or more services deep with no aggregate timeout budget.

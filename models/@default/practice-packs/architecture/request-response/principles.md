# Request/Response microservices — principles

The defining stance of this reference architecture. Loaded eagerly; the pattern
and API-convention bodies are loaded lazily when their file globs match.

## The shape

Services answer **requests** synchronously: a caller sends a request and blocks
until it gets a response, because it needs that answer to proceed. Requests enter
the mesh through an edge / API gateway and fan out to the services that own the
data. A service that needs data owned by another service **calls that service** —
it never reaches into the other service's database.

## Non-negotiables

1. **Client-side resilience on every cross-service call.** Every call to another
   service carries a **timeout**, a **retry budget**, and a **circuit breaker**
   (see `patterns/resilience.md`). A call missing any of the three is a
   resilience-omission defect (`RR_NO_TIMEOUT`).
2. **One service, one datastore.** No two services share a database
   (`shared-database-across-services` is prohibited, `RR_SHARED_DB`). Cross-service
   data is obtained by calling the owning service.
3. **Write endpoints are idempotent.** A write that may be retried is idempotent on
   an idempotency key (see `patterns/idempotent-write.md`), so a retried request
   has the same effect as a single request.
4. **Bound the call chain.** A synchronous call chain without timeouts lets one slow
   downstream stall every caller above it (`synchronous-call-chain-without-timeout`
   is prohibited). Keep chains shallow and every hop bounded.
5. **Stable API contracts.** The API is versioned, errors share one envelope, lists
   paginate, and status codes follow a fixed map
   (`api/versioning.md`, `api/error-envelope.md`, `api/pagination.md`).

## What this pack does not decide

- The **language, framework, or service-client library** — those are the stack
  pack's, referred to here only as "a resilient service-client abstraction".
- **How** signals are emitted (logging library, field mechanics) — this pack names
  *what* must be emitted (`observability/required-signals.md`); the stack pack owns
  the *how*.
- The **language pairing** — declared by the Workspace Profile, never here.

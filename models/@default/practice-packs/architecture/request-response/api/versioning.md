# API interface — versioning and status-code map

The shape contract for the synchronous API surface. This is an abstract contract
(versioning policy, status-code semantics), **not** a wire schema and **not** a
serialisation format — those are the stack pack's and the platform's concern.

## Versioning

```
/v<major>/<resource>
```

- The **major** version lives in the path (`/v1/orders`, `/v2/orders`).
- A **breaking change** — removing or renaming a field, changing a type, tightening
  validation, changing status-code semantics — increments the major and serves the
  old major in parallel until consumers migrate.
- An **additive change** — a new optional field, a new endpoint, a new enum value the
  client may ignore — does **not** change the major. Clients tolerate unknown fields.
- Two majors run side by side during a migration window; the old major is retired
  only after consumers have moved.

## Status-code map

A fixed mapping from outcome to HTTP status, so every service in the mesh answers the
same way and callers' resilience logic (`../patterns/resilience.md`) can react
consistently.

| Outcome | Status |
|---|---|
| Validation failure (malformed or invalid request) | `400` |
| Unauthenticated (no or invalid credentials) | `401` |
| Forbidden (authenticated but not permitted) | `403` |
| Not found | `404` |
| Conflict (idempotency-key clash, version conflict) | `409` |
| Upstream dependency unavailable / breaker open | `503` |
| Upstream call timed out | `504` |

## Rules

- `5xx` from an upstream maps to `503`/`504` at the caller's edge, never leaks the
  upstream's internal error body to the external client (`../api/error-envelope.md`).
- A retry-safe failure (`503`, `504`) is the signal the resilience layer retries on,
  within its budget; a `4xx` is not retried.
- Auth/authz is enforced at the handler boundary (`401`/`403`); the pack names the
  *contract*, the stack pack names the mechanism.

## What this pack does not specify

The **framework, router, and (de)serialisation** are stack-pack concerns. This pack
names the versioning policy and the status-code semantics, not their implementation.

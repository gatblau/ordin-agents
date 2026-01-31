# Observability — required signals (the *what*)

The signals a system built with this pack **must** emit. This is the *what* slice of
the `observabilityConventions` seam; the *how* — logging library, metric client,
field-naming mechanics — is the stack pack's. A skill consuming this pack checks that
these signals exist, not how they are wired.

> The concrete signal set below is authored as proposed and is flagged for
> platform / observability-team ratification at governance approval (Phase 1 OQ-3).
> Treat it as a baseline an overlay may strengthen.

## Required counters

| Counter | Labels | Meaning | Why it is required |
|---|---|---|---|
| `request_total` | `route`, `status` | Inbound requests served, by route and result status. | The primary health and error-rate signal for a service's own surface. |
| `upstream_call_total` | `upstream`, `status` | Cross-service calls made, by upstream and result. | Exposes which downstream a service depends on and where calls fail or time out (`../patterns/resilience.md`). |
| `circuit_breaker_state` | `upstream` | The breaker state per upstream (closed / open / half-open). | Shows resilience engaging — an open breaker is a downstream in trouble, surfaced before it cascades (`../patterns/resilience.md`). |

## Required span attributes

Set on the span that serves or makes a request:

- `http.route` — the route template (e.g. `/v1/orders/{id}`), not the raw URL, so
  cardinality stays bounded.
- `peer.service` — the upstream service a cross-service span is calling.

## Required log fields

Every log line emitted while handling a request carries:

- `trace_id` — correlates the log with the distributed trace (`../api/error-envelope.md`
  `traceId`).
- `tenant_id` — the tenant the request belongs to.
- `route` — the route template being served.

## Rules

- These are **minimums**. An overlay or the stack pack may add more; none may be
  dropped.
- Counters are labelled so request rate, error rate, upstream health, and breaker
  state are attributable to a route and an upstream, not just global totals.
- `http.route` and `route` use the **route template**, never the raw path, to bound
  metric and span cardinality.
- Field **emission mechanics** are the stack pack's; this pack names only the required
  signals and their labels.

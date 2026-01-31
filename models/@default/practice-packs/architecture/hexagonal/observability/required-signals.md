# Observability — required signals (the *what*)

The signals a system built with this pack **must** emit. This is the *what* slice of
the `observabilityConventions` seam; the *how* — logging library, metric client,
field-naming mechanics — is the stack pack's. A skill consuming this pack checks that
these signals exist, not how they are wired.

> The concrete signal set below is authored as proposed and is flagged for platform /
> observability-team ratification at governance approval (Phase 1 OQ-3). Treat it as a
> baseline an overlay may strengthen.

## Where signals are emitted

**At the adapters, never in the core.** Every signal in this file is emitted at an
adapter boundary — where the core meets an external system. The domain core stays
uninstrumented so it remains pure (`../principles.md`); a counter, span, or
transport-aware log inside a use case or entity is a core-purity violation.

## Required counters

| Counter | Meaning | Why it is required |
|---|---|---|
| `adapter_call_total{adapter,direction}` | Calls crossing an adapter, labelled by adapter and direction (inbound for driving, outbound for driven). | Exposes the traffic and failure profile of every boundary the core has, without instrumenting the core itself. |

## Required span attributes

Set on the span that crosses an adapter boundary:

- `adapter.name` — the adapter the call crossed (the driving or driven adapter).
- `port.name` — the port the adapter implements or invokes, so a span ties the
  concrete adapter back to the abstract capability the core required.

## Required log fields

Every log line emitted at an adapter carries:

- `trace_id` — correlates the log with the distributed trace; passed inward as a plain
  domain value if the core needs it, never as a transport type.
- `tenant_id` — the tenant the call belongs to.

## Rules

- These are **minimums**. An overlay or the stack pack may add more; none may be
  dropped.
- All emission happens at **adapters**; the core carries no instrumentation. Correlation
  values the core needs are passed inward as plain domain values.
- Counters must be labelled by `adapter` and `direction` so a boundary's traffic is
  attributable, not just a global total.
- Field **values** come from the adapter's context; field **emission mechanics** are the
  stack pack's.

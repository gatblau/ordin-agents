# Boundary — error translation at the adapter

The shape contract for translating external failures into domain errors at the
adapter edge. Abstract — it names a rule, not an error code catalogue.

## The rule

The core **raises and handles only domain errors.** Every adapter translates the
failures of its external system — a driver exception, a transport status, a timeout,
a serialization fault — into a **domain error** at the boundary, *before* the failure
reaches the core. The core never catches a driver-specific or transport-specific
error type.

## Why

- The core stays pure: it does not depend on any external system's error taxonomy and
  is unaffected when the underlying technology's errors change.
- Failure handling is uniform: a use case reasons about a small set of domain errors
  (not found, conflict, unavailable, invalid), not about a sprawl of vendor codes.
- The boundary is the single place that decides what an external failure *means* in
  domain terms, so meaning is not re-derived inconsistently inside the core.

## Direction

| Direction | Adapter kind | Translation |
|---|---|---|
| **Inbound failure** | Driven adapter | external failure (driver/transport/timeout) → domain error, raised to the core. |
| **Outbound failure** | Driving adapter | domain error → external failure representation (status, fault payload) on the way back out. |

## Rules

- Translation lives in the **adapter**, never in the core. The core defines the domain
  error set; the adapter maps to and from it.
- The core **never** catches or types against an external error — no driver exception,
  no transport status, no serialization fault crosses the boundary untranslated.
- The mapping is **total**: every external failure class maps to a domain error or to
  a deliberate "unexpected" domain error; none leaks through as an external type.
- A driving adapter performs the **inverse** translation — mapping the domain error
  back to the transport's failure representation — so the external contract is honoured
  without the core knowing the transport.

## What this pack does not specify

The **error types, status-code map, and exception mechanics of the concrete
technology** are stack-pack concerns. This pack names only the translate-at-the-edge
rule and the core-sees-only-domain-errors invariant.

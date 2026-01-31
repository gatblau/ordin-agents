# Observability — required signals (the *what*)

The signals a system built with this pack **must** emit. This is the *what* slice
of the `observabilityConventions` seam; the *how* — logging library, metric
client, field-naming mechanics — is the stack pack's. The two counters here exist
specifically to make **creeping coupling** visible before it hardens.

> The concrete signal set below is authored as proposed and is flagged for
> platform / observability-team ratification at governance approval (Phase 1
> OQ-3). Treat it as a baseline an overlay may strengthen.

## Required counters

| Counter | Meaning | Why it is required |
|---|---|---|
| `module_request_total` | Requests handled, labelled by `module`. | Shows each module's load and which modules are hot. |
| `cross_module_call_total` | Cross-module facade calls, labelled by `from` and `to` module. | The coupling signal: a rising `{from,to}` edge that should be rare reveals two modules drifting into tight coupling — the early warning that the monolith is becoming distributed-in-disguise. |

## Required span attributes

- `module.name` — the module handling the current unit of work, set on its span,
  so a trace shows the path a request takes across module boundaries.

## Required log fields

Every log line carries:

- `trace_id` — correlates the log with the distributed trace.
- `tenant_id` — the tenant the work belongs to.
- `module` — the module emitting the line, so logs are attributable per module.

## Rules

- These are **minimums**; an overlay or the stack pack may add more, none may be
  dropped.
- `cross_module_call_total` must be labelled by both `from` and `to`, or it cannot
  expose a specific coupling edge.
- Field **values** identify the module; field **emission mechanics** are the stack
  pack's.

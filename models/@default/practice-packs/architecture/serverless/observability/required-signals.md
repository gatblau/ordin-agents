# Observability — required signals (the *what*)

The signals a system built with this pack **must** emit. This is the *what* slice
of the `observabilityConventions` seam; the *how* — logging library, metric
client, field-naming mechanics — is the stack pack's. A skill consuming this pack
checks that these signals exist, not how they are wired.

> The concrete signal set below is authored as proposed and is flagged for
> platform / observability-team ratification at governance approval (Phase 1
> OQ-3). Treat it as a baseline an overlay may strengthen.

## Required counters

| Counter | Meaning | Why it is required |
|---|---|---|
| `invocations_total` | Function invocations, labelled by `function` and `status`. | The base health signal for a function-per-trigger system; status splits success from failure per function. |
| `cold_start_total` | Cold starts, labelled by `function`. | The distinguishing serverless signal; a rising cold-start rate threatens the cold-start budget (`../principles.md`). |
| `throttle_total` | Invocations throttled by the platform, labelled by `function`. | A throttle means demand exceeded the function's concurrency budget — events are delayed or dead-lettered. |
| `errors_total` | Handler errors, labelled by `function`. | With `invocations_total`, exposes the error rate that drives retry and dead-letter behaviour (`../triggers/binding.md`). |

## Required span attributes

Set on the span that handles an invocation:

- `function.name` — the function the invocation ran (`<bounded-context>.<capability>.<trigger-type>`).
- `trigger.source` — the event source that triggered the invocation.

## Required log fields

Every log line emitted while handling an invocation carries:

- `trace_id` — correlates the log with the distributed trace across functions
  (envelope `traceparent`, `../triggers/binding.md`). This is what stitches a
  chain of trigger-driven functions into one trace.
- `tenant_id` — the tenant the event belongs to (envelope `tenant`).
- `function` — the function name, so logs are attributable per function.

## Rules

- These are **minimums**. An overlay or the stack pack may add more; none may be
  dropped.
- Counters must be **labelled by function** so cold-start, throttle and error rates
  are attributable to a single function, not just global totals.
- Because functions chain via trigger sources rather than synchronous calls,
  `trace_id` propagated through the envelope is the **only** correlation across
  functions — emitting it on every line is non-negotiable.
- Field **values** come from the event envelope; field **emission mechanics** are
  the stack pack's.

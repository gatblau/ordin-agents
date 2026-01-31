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
| `saga_started_total` | Sagas started, by saga name. | The base rate against which completion and compensation are read. |
| `saga_completed_total` | Sagas that ran every step to success, by saga name. | With the started count, exposes the success rate. |
| `saga_compensated_total` | Sagas that failed a step and compensated, by saga name. | A rising compensation rate is the primary failure signal for a saga. |

## Required gauge

| Gauge | Meaning | Why it is required |
|---|---|---|
| `sagas_in_flight` | Sagas currently running (not yet completed or compensated). | A growing in-flight count means sagas are starting faster than they finish — often a stuck step (`saga-step-without-timeout`). |

## Required histogram

| Histogram | Meaning | Why it is required |
|---|---|---|
| `saga_duration_seconds` | End-to-end saga duration, started to completed or compensated. | Detects sagas that complete but slowly, before they show as stuck in-flight. |

## Required span attributes

Set on the span that drives or executes a saga step:

- `saga.name` — the saga type.
- `saga.step` — the step the span covers.

## Required log fields

Every log line emitted while driving or executing a saga carries:

- `trace_id` — correlates the log with the distributed trace.
- `tenant_id` — the tenant the saga belongs to.
- `saga_id` — the saga instance's stable correlation id (`../steps/contract.md`).

## Rules

- These are **minimums**. An overlay or the stack pack may add more; none may be
  dropped.
- Counters and the in-flight gauge must be labelled by `saga.name` so the rates
  are attributable per saga type, not just global totals.
- Field **values** come from the saga state and envelope; field **emission
  mechanics** are the stack pack's.

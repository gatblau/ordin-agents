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
| `records_in_total{stage}` | Records read by a stage, labelled by stage. | The input rate of every stage; a stage at zero in is a stalled source. |
| `records_out_total{stage}` | Records emitted by a stage, labelled by stage. | With `records_in_total`, exposes per-stage selectivity and a stage that silently drops records. |
| `stage_lag` | Records (or event-time) a stage is behind its source. | The primary health signal for a stream stage; rising lag means it cannot keep up and should scale out (`../patterns/backpressure.md`). |
| `checkpoint_age_seconds` | Time since the stage's last committed checkpoint. | A stalled checkpointer is an outage even while records flow — recovery would replay everything since the last checkpoint (`../patterns/checkpointing.md`). |

## Required span attributes

Set on the span that processes a record in a stage:

- `stage.name` — the stage the record is flowing through, so a trace shows the
  per-stage path.

## Required log fields

Every log line emitted while processing a record carries:

- `trace_id` — correlates the log with the distributed trace.
- `tenant_id` — the tenant the record belongs to.
- `stage` — the stage emitting the line (matches the `stage.name` span
  attribute).

## Rules

- These are **minimums**. An overlay or the stack pack may add more; none may be
  dropped.
- `records_in_total` and `records_out_total` must be **labelled by stage** so
  per-stage rates and selectivity are attributable, not just pipeline totals.
- `stage_lag` and `checkpoint_age_seconds` are the two signals an on-call alert is
  built from; both must exist before a pipeline is considered production-ready.
- Field **values** come from the record and stage context; field **emission
  mechanics** are the stack pack's.

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
| `events_appended_total` | Events appended to the store, by aggregate type. | The write-side throughput signal; a sudden drop means commands are failing or blocked. |
| `projection_lag` | Events behind the stream tail, per projection. | The primary read-side health signal; rising lag means a projection cannot keep up and reads are increasingly stale. |
| `projection_rebuild_seconds` | Wall-clock duration of a projection rebuild from zero. | Bounds the recovery window — how long a read model is unavailable or stale after a shape change or corruption. |

## Required span attributes

Set on the span that handles a command or applies an event:

- `aggregate.type` — the aggregate type the span operates on (`account`, `order`).
- `aggregate.version` — the aggregate version observed or written, so a
  version-conflict retry (`../patterns/event-store.md`) is visible in the trace.

## Required log fields

Every log line emitted while handling a command or projecting an event carries:

- `trace_id` — correlates the log with the distributed trace.
- `tenant_id` — the tenant the aggregate belongs to.
- `aggregate_id` — the aggregate instance the work concerns (the stream id,
  `../events/stream-naming.md`).

## Rules

- These are **minimums**. An overlay or the stack pack may add more; none may be
  dropped.
- `projection_lag` must be labelled per projection so a single slow read model is
  attributable, not hidden in a global average.
- Field **values** come from the command/event context; field **emission
  mechanics** are the stack pack's.

# CQRS + event-sourcing — anti-patterns

The architectural failure modes this pack forbids. Loaded eagerly. Each maps to an
`antiPatterns` entry in the manifest; a skill that activates on an aggregate,
projection or events artefact should flag these.

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| **Query the write side** | Serving reads by replaying aggregates or scanning the event store couples query load to the write side, ignores the read model the architecture exists to build, and scales badly as the stream grows. | Read only through a projection (`patterns/projection-rebuild.md`). The write side is command-only and exposes no query path. |
| **Mutate a stored event** | Editing or deleting a stored event rewrites history. Every projection derived from that stream is now non-reproducible, and a rebuild produces a different result than the live model. | Append a new compensating event. The store is append-only (`patterns/event-store.md`); corrections are facts too. |
| **Read model treated as authoritative** | A projection is a derived, eventually-consistent view. Trusting it as the source of truth lets stale data, or a half-finished rebuild, override the event store. | Treat the event store as the single source of truth; the projection is a disposable cache that can always be regenerated. |
| **Missing concurrency version check** | Appending events without asserting the expected aggregate version lets two concurrent commands both succeed against the same starting state, silently overwriting each other's intent. | Append with optimistic concurrency by version (`patterns/event-store.md`): assert `expectedVersion`, reject on mismatch, retry against fresh state. |

## Smell list (review prompts)

- A query handler that loads an aggregate or opens the event store directly.
- An `UPDATE` or `DELETE` against the events table, or any code path that edits a
  previously-stored event.
- Application logic that writes back into a projection table as if it were the
  primary record.
- An `append` call with no `expectedVersion` argument, or one that ignores the
  store's version-conflict error.
- An event type named in the imperative ("OpenAccount") rather than the past tense
  ("AccountOpened").

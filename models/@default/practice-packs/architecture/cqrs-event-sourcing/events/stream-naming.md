# Event interface — stream naming and the projection checkpoint

How event streams are identified and how a projection records its position. These
are abstract shape contracts; the serialisation and storage are the stack pack's.

## Stream naming

Each aggregate instance owns exactly one event stream, named:

```
<aggregate>-<id>
```

- `<aggregate>` — the aggregate type, lower-case (`account`, `order`).
- `<id>` — the aggregate instance's stable identifier.

Examples: `account-7f3a`, `order-90021`. A stream holds every event for one
instance, in append order; its current **version** is the position of its last
event (`../patterns/event-store.md`).

The stream is named after the **aggregate that owns the invariant**, never after a
consumer. Naming a stream for who reads it couples the write side to the read
topology, the same coupling the command/query split exists to remove.

## Command and query naming (the split, restated)

- **Commands** target the write side: `<Aggregate><Imperative>` — `AccountOpen`,
  `OrderCancel`. A command is handled by an aggregate command handler and returns
  an acknowledgement, never query data.
- **Queries** target the read side: `<ReadModel><Question>` — `AccountBalanceGet`,
  `OrderSummaryList`. A query is served by a projection and never touches the write
  side (`query-the-write-side` is prohibited).

## Projection checkpoint contract

A projection records how far it has consumed so it can resume after a restart and
be rebuilt deterministically:

```
checkpoint = (projection-id, stream-position)
```

- The checkpoint is committed **atomically with the projection write** for the
  same event — never before (would skip on crash) and never after (would
  double-apply). See `../broker/projection-consumer.md`.
- `stream-position` is the position in the consumed stream, so a rebuild can start
  the checkpoint at zero and replay the whole history
  (`../patterns/projection-rebuild.md`).

## Rules

- One aggregate instance ⇒ one stream. Cross-aggregate views are built by a
  projection consuming many streams, never by widening a stream.
- The stream name and the aggregate id move together; renaming an aggregate type
  is a new stream namespace, not an in-place rename of stored events.
- The **encoding of the stream id and the checkpoint storage** are stack-pack /
  platform concerns, not specified here.

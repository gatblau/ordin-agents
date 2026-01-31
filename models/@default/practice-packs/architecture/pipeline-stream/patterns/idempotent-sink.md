# Pattern — Idempotent sink

**Recommended.** `when:` an at-least-once pipeline writes to an external sink that
may see the same record twice.

## Problem

An at-least-once pipeline (the default delivery guarantee unless exactly-once is
chosen) re-emits records after any restart: checkpoint replay re-reads from the
last committed offset, so records between the last checkpoint and the crash are
reprocessed. If the sink's write is a non-idempotent side effect — an `INSERT`, a
charge, a notification — the record is double-applied. That is the
`side-effect-without-idempotency` anti-pattern.

## Solution

Make the sink **idempotent on a stable record key**: writing the same record
twice has the same observable effect as writing it once. The record carries a
deterministic key (derived from source offset + content, not from wall-clock or a
generated id), and the sink deduplicates on it.

Strategies (language-neutral):

| Strategy | How |
|---|---|
| **Upsert** | Write keyed by the record key; a repeat overwrites rather than duplicates. |
| **Dedup store** | Record processed keys; skip a key already seen (bounded by a window — see `windowing.md`). |
| **Conditional commit** | Write only if the sink's committed offset is below this record's offset; advance atomically. |

The alternative is **exactly-once** via a transactional sink commit on the
checkpoint barrier (`checkpointing.md`, ADR `delivery-guarantee`) — choose one.

## Shape (language-neutral)

```
record(key) ──► sink: if key already applied → skip
                       else apply + record key (atomically)
```

## Rules

- The dedup **key is stable and deterministic** — same record, same key across
  restarts. A key derived from processing-time or a fresh random id does not
  dedup.
- The dedup store is **bounded** (a window or TTL); an unbounded dedup set is the
  `unbounded-state-without-eviction` defect.
- Apply-and-record-key is **atomic**; recording the key without applying (or vice
  versa) reopens the double-apply window.

## What this pack does not specify

The **sink driver, upsert mechanics, and transaction API** are stack-pack
concerns — provided by the concrete sink client behind the stream runtime.

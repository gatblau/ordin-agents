# Pattern — Transactional outbox

**Required.** `when:` a service publishes events tied to database state changes.

## Problem

A handler changes state *and* must publish an event about that change. Writing to
the database and publishing to the broker are two separate systems with no shared
transaction. Any ordering of the two leaves a failure window:

- Commit, then crash before publish → state changed, no event. Consumers never
  hear about it.
- Publish, then crash before commit → event emitted for a change that rolled
  back. Consumers act on a lie.

## Solution

Make the event part of the same database transaction as the state change, then
publish it asynchronously.

1. In the business transaction, write the domain change **and** insert a row into
   an `outbox` table describing the event (id, type, aggregate, payload,
   occurred-at, headers). One commit covers both.
2. A separate **outbox poller** reads unpublished outbox rows in order, publishes
   each to the broker, and marks it published (or deletes it) once the broker
   acknowledges.
3. The poller is itself at-least-once: a crash after publish but before marking
   the row republishes on restart. That is safe because every consumer is
   idempotent (`../patterns/idempotency.md`).

## Shape (language-neutral)

```
BEGIN
  apply domain change
  INSERT INTO outbox (id, type, aggregate_id, payload, occurred_at, headers)
COMMIT
-- later, in the poller:
for row in outbox where not published, ordered by occurred_at:
    publish(row)            # the platform broker client
    mark row published
```

## Rules

- The outbox insert and the state change share **one** transaction. If they can
  be in different transactions, this pattern is not in use.
- Publish order follows `occurred_at` per aggregate so a consumer sees an
  aggregate's events in causal order.
- Never publish directly from the handler "as well, to be fast" — that
  reintroduces the dual-write the outbox removes.

## What this pack does not specify

The outbox **table mechanics, driver, and poller scheduling** are stack-pack
concerns — referred to here only as "an outbox helper" (manifest
`approvedLibraries`).

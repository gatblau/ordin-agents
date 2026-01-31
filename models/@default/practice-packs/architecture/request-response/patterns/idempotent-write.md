# Pattern — Idempotent write endpoint

**Required.** `when:` a write endpoint may be retried.

## Problem

A synchronous caller cannot tell a *lost request* from a *lost response*. When a
write call times out, the write may already have succeeded server-side; the caller's
resilience layer (`./resilience.md`) then **retries** it. Without protection, the
second attempt applies the effect again — a second order, a second charge, a second
debit. At-least-once delivery on the client side meets exactly-once expectation on
the server side only if the endpoint is idempotent.

## Solution

Make each retryable write idempotent on an **idempotency key** supplied by the
caller and stable across retries of the same logical operation.

1. The caller generates an idempotency key for the operation and sends it on every
   attempt (a header or a field), unchanged across retries.
2. The service records the key with the operation's result in the **same transaction**
   as the state change. A unique constraint on the key makes a duplicate write fail
   to insert rather than re-apply.
3. On a retry the service sees the key already recorded and returns the **stored
   result** instead of re-executing — same status, same response body.

## Shape (language-neutral)

```
on write(request, idempotency_key):
  BEGIN
    if exists(processed where key = idempotency_key):
        return stored_response(idempotency_key)        # replay, no re-apply
    apply state change
    INSERT INTO processed (key, response) VALUES (idempotency_key, response)
  COMMIT
  return response
```

## Rules

- The processed-key insert and the state change share **one** transaction. If the
  effect can commit without the key, a crash between them re-applies on retry.
- The key is the **caller's**, stable across retries; the service does not invent it
  per attempt.
- Pure reads (`GET`) are naturally idempotent and need no key. This pattern targets
  state-changing writes that the resilience layer may retry.

## What this pack does not specify

The **key store mechanics, header name, and transaction driver** are stack-pack
concerns. This pack names the contract — a stable caller key, a single-transaction
record, a replayed result — not the implementation.

# Pattern — Stateless handler

**Required.** `when:` a function processes a trigger.

## Problem

A function may run on a fresh instance for any invocation: the platform scales to
zero and back, and concurrent invocations land on different instances. Any state a
handler keeps in memory, in a module-level variable, or on local disk is therefore
unreliable — it survives some invocations (a warm container) and vanishes on
others (a cold start), and two concurrent instances see different copies. A
handler that depends on that state produces non-deterministic results.

## Solution

Make every invocation **self-contained**: the handler reads the state it needs
from an external store at the start, applies one effect, persists the result to
the store, and returns. Nothing the handler needs to outlive the invocation is
kept in process memory.

1. On entry, the handler reads the current state for the trigger's subject from the
   **external store** (the source of truth), keyed by an identifier in the event
   payload.
2. It computes the effect from that state plus the event payload alone — no
   reliance on a previous invocation's residue.
3. It writes the new state back to the external store before returning.

## Shape (language-neutral)

```
handler(event):
  state = store.read(event.subject)          # external store, every invocation
  result = apply(state, event)               # pure function of state + event
  store.write(event.subject, result)         # persist before returning
  return ack
```

## Rules

- **In-memory data is a per-invocation cache, never the source of truth.** A
  connection pool or a read-through cache may live module-level for reuse on a warm
  container, but correctness must not depend on it being present.
- **No durable writes to local disk.** Local disk is ephemeral and not shared
  across instances; durable output goes to the external store.
- The store read/write should be the handler's **only** cross-invocation
  dependency. Pair this with `idempotent-trigger.md` so a redelivered event
  re-reads the same state and re-applies the same effect harmlessly.
- Statelessness is what makes a function **horizontally scalable** with no
  coordination: any instance can serve any invocation.

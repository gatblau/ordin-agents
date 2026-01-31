# Serverless / function-per-trigger — principles

The defining stance of this reference architecture. Loaded eagerly; the pattern,
trigger-binding and observability bodies are loaded lazily when their file globs
match.

## The shape

A unit of work is a **function** bound one-to-one to an **event trigger**. The
trigger source maps an incoming event to a single function invocation; the
function reads what it needs from an external store, applies one effect, and
returns. There is no long-lived process holding state between requests: each
invocation starts from nothing and may run on a freshly provisioned instance.

## Non-negotiables

1. **Stateless by default.** A function holds no state between invocations. All
   durable state lives in an external store (see `patterns/stateless-handler.md`);
   warm-container memory and local disk are caches that may vanish, never the
   source of truth.
2. **One function, one trigger, one responsibility.** A function binds to exactly
   one trigger type and does one thing. Branching on the trigger type or fanning
   out to unrelated effects is the `single-responsibility-function` smell.
3. **Idempotent triggers.** An event source may deliver the same trigger more than
   once. Every function is idempotent on an idempotency key (see
   `patterns/idempotent-trigger.md`); a redelivery has the same effect as a single
   delivery.
4. **Short execution within a cold-start budget.** A function returns promptly.
   Long-running work inside the handler (`long-running-work-in-handler`) is
   forbidden; offload it to a queue or a step. The pack asserts a **cold-start
   budget** as a runtime NFR for systems built with it: cold start plus execution
   stays within the target stated by the consuming team's profile.
5. **State is externalised, not chained.** Functions communicate by writing to a
   store or publishing to a trigger source, never by calling each other
   synchronously (`synchronous-function-chaining`).

## What this pack does not decide

- The **language, framework, function runtime, or platform** — those are the stack
  pack's, referred to here only as "the function runtime" and "the trigger source".
- The **numeric cold-start budget** — the pack asserts that a budget exists and is
  measured; the target value is the consuming team's, stated in their profile.
- **How** signals are emitted (logging library, metric client, field mechanics) —
  this pack names *what* must be emitted (`observability/required-signals.md`); the
  stack pack owns the *how*.
- The **language pairing** — declared by the Workspace Profile, never here.

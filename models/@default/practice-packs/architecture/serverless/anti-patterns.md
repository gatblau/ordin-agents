# Serverless / function-per-trigger — anti-patterns

The architectural failure modes this pack forbids. Loaded eagerly. Each maps to
an `antiPatterns` entry in the manifest; a skill that activates on a function or
handler artefact should flag these.

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| **Shared mutable state between invocations** | The function relies on warm-container memory (a module-level cache, a connection counter, an accumulating buffer) surviving from one invocation to the next. The next invocation may be a cold start on a fresh instance, so the state is silently lost or, worse, two concurrent instances diverge. | Externalise state (`patterns/stateless-handler.md`): read it from and write it to an external store on every invocation. Treat in-memory state as a per-invocation cache only. |
| **Long-running work in a handler** | Blocking work inside the handler — a slow loop, a synchronous wait on a downstream, a batch job — exceeds the cold-start and execution budget. The platform may throttle or terminate the function mid-flight, leaving the effect half-applied. | Offload the work: enqueue it to a trigger source and let a separate function pick it up, or break it into a step. Return promptly with the work scheduled, not done inline. |
| **Synchronous function chaining** | Function A calls function B synchronously and waits for its result. Their availability and latency are now coupled, both pay a cold start on the critical path, and a failure in B fails A. The function-per-trigger decoupling is defeated. | Chain via a trigger source: A writes its result or publishes an event; B is triggered by that event (`triggers/binding.md`). The handoff is asynchronous and idempotent. |

## Smell list (review prompts)

- A module-level or static variable mutated inside the handler and read on a later
  invocation.
- A handler that opens a long synchronous loop or blocks on a downstream call
  before returning.
- One function's handler invoking another function's endpoint and awaiting it.
- A single function that switches on the trigger type and performs several
  unrelated effects (a `single-responsibility-function` violation).
- Durable data written to local disk or a warm-container file rather than an
  external store.

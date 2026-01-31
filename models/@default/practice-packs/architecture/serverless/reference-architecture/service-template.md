# Reference architecture — service template

The language-neutral skeleton for a function-per-trigger service. A skill that
scaffolds a new function follows this layout; the concrete file extensions,
runtime entry point and build wiring are the **stack pack's**, not this pack's.

## Layout

```
functions/
  <bounded-context>.<capability>.<trigger-type>/
    handler           # the entry point bound to one trigger
    binding           # trigger-source binding declaration (one trigger)
    state             # external-store read/write adapter (no in-memory state)
README                # which trigger, which store, the cold-start budget
```

- **One directory per function.** The directory name is the function name
  (`<bounded-context>.<capability>.<trigger-type>`, `../triggers/binding.md`); the
  directory holds exactly one handler.
- **No shared mutable module** across function directories. Shared *pure* helpers
  may be factored out, but nothing that carries state between invocations.

## Handler skeleton (language-neutral)

```
handler(event):                                   # event = typed envelope
  assert event.id, event.tenant                   # envelope contract
  if store.seen(event.id): return ack             # idempotency on event id
  BEGIN
    state  = store.read(event.subject)            # state externalised, per invocation
    result = apply(state, event)                  # pure function of state + event
    store.write(event.subject, result)
    store.record_processed(event.id)              # same txn as the effect
  COMMIT
  return ack                                       # ack AFTER commit
```

## What the template fixes vs defers

| Fixed by this pack (architecture) | Deferred to the stack pack |
|---|---|
| One directory per function, one trigger per handler | File extensions, runtime entry-point signature |
| Stateless handler reading/writing an external store | The concrete store client and runtime SDK |
| Idempotency on the event id, ack after commit | The build, package and deploy commands |
| Required envelope fields and function naming | The wire encoding of the envelope |
| The cold-start budget exists and is measured | The numeric budget target (the team's profile) |

## Rules

- Every scaffolded function ships its **trigger binding** (one trigger) and its
  **external-state adapter** — never an in-memory store.
- The README states the **trigger**, the **external store**, and the **cold-start
  budget** the function is held to (`../principles.md`).
- No long-running loop or synchronous downstream call in the handler
  (`../anti-patterns.md`); offload via a follow-up event.

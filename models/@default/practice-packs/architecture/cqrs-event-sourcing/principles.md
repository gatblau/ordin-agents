# CQRS + event-sourcing — principles

The defining stance of this reference architecture. Loaded eagerly; the pattern
and projection-consumer bodies are loaded lazily when their file globs match.

## The shape

The system is split into two sides. The **write side** accepts commands, loads an
aggregate, decides what happened, and appends **immutable events** to an
append-only event store. The **read side** is built from **projections** that
consume that event stream and maintain disposable query models the application
reads from. A command never returns query data; a query never touches the write
side.

## Non-negotiables

1. **Events are immutable facts.** A stored event names something that has already
   happened, in the past tense. It is never edited or deleted in place. A mistake
   is corrected by appending a new compensating event, not by rewriting history
   (`mutate-a-stored-event` is prohibited).
2. **The store is append-only.** State is persisted as an ordered sequence of
   events per aggregate (`patterns/event-store.md`). Current state is a fold of
   that sequence, never an in-place row update.
3. **Optimistic concurrency by version.** Every append asserts the aggregate
   version it expected to extend. A version mismatch means a concurrent command
   won the race; the loser retries against fresh state
   (`missing-concurrency-version-check` is forbidden).
4. **Read models are disposable.** A projection carries no authority. It can be
   dropped and rebuilt from zero off the event stream
   (`patterns/projection-rebuild.md`); treating it as the source of truth is the
   `read-model-treated-as-authoritative` anti-pattern.
5. **The two sides are eventually consistent.** A projection lags the store by its
   processing latency. Clients tolerate that lag; the write side never blocks on a
   projection catching up.

## What this pack does not decide

- The **language, framework, event-store product, or client library** — those are
  the stack pack's, referred to here only as "the event store" / "an event-store
  client abstraction".
- **How** signals are emitted (logging library, metric client) — this pack names
  *what* must be emitted (`observability/required-signals.md`); the stack pack
  owns the *how*.
- The **language pairing** — declared by the Workspace Profile, never here.

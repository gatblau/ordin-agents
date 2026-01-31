# Event-driven services — principles

The defining stance of this reference architecture. Loaded eagerly; the pattern
and broker-practice bodies are loaded lazily when their file globs match.

## The shape

Services communicate by publishing and consuming **events** over a message
broker, not by calling each other synchronously. A producer records a fact ("an
order was placed"); any number of consumers react to it independently. The
producer does not know who consumes, and a consumer's failure does not fail the
producer.

## Non-negotiables

1. **Asynchronous by default.** Inter-service communication is via events. A
   synchronous call is the exception and must be justified against the
   `synchronous-rpc-in-handler` prohibition.
2. **At-least-once delivery.** The broker may redeliver. Every consumer is
   idempotent on an idempotency key (see `patterns/idempotency.md`); processing
   the same event twice has the same effect as processing it once.
3. **Publish atomically with state.** A service that publishes events tied to a
   database change uses the outbox pattern (see `patterns/outbox.md`) so the
   commit and the publish cannot diverge under a crash.
4. **Events are facts, not commands.** An event names something that has already
   happened, in the past tense. It carries the data a consumer needs without
   prescribing what the consumer must do.
5. **Durability lives in the broker, not in process memory.** The
   `in-memory-event-cache` anti-pattern loses events on restart.

## What this pack does not decide

- The **language, framework, broker product, or client library** — those are the
  stack pack's, referred to here only as "the platform broker client".
- **How** signals are emitted (logging library, field mechanics) — this pack
  names *what* must be emitted (`observability/required-signals.md`); the stack
  pack owns the *how*.
- The **language pairing** — declared by the Workspace Profile, never here.

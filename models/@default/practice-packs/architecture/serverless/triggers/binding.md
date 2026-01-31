# Trigger binding & event-source contract

The shape contracts for binding a trigger to a function and for the event-source
mapping. Abstract — "the trigger source" is the platform's event source, named no
product. This is the *what* of the `interfaceConventions.triggers` and
`brokerClientPractice` seams; the concrete runtime wiring is the stack pack's.

## One function, one trigger

A function binds to **exactly one** trigger type. The trigger source maps an
incoming event to a single handler invocation; the handler signature receives the
event envelope and returns an ack/nack. A function never multiplexes several
trigger types behind one entry point — that is the `single-responsibility-function`
smell.

## Event-source payload (envelope)

Every event delivered to a handler is a typed envelope carrying:

| Field | Meaning |
|---|---|
| `id` | Stable event id — the idempotency key (`../patterns/idempotent-trigger.md`). Identical on every redelivery. |
| `source` | The trigger source that emitted the event. |
| `occurredAt` | When the originating fact happened (not when it was delivered). |
| `traceparent` | Distributed-trace context for correlation (`../observability/required-signals.md`). |
| `tenant` | The tenant the event belongs to. |

The payload body is carried alongside the envelope and is typed per function.

## Function naming

Functions are named `<bounded-context>.<capability>.<trigger-type>` — after the
fact they react to, never after a downstream consumer. The name is stable across
redeliveries and identifies the single responsibility the function owns.

## Event-source mapping (ack / retry / dead-letter)

Against an **abstract** event source:

- **Ack after the effect is committed** (`ack-after-effect-committed`). An ack
  before the external write commits can drop an event on a crash.
- **Bounded retry with exponential backoff** on a nack or an unhandled error. The
  source redelivers with increasing delay up to a bounded `maxDeliver`.
- **Dead-letter on budget exhaustion.** When `maxDeliver` is exceeded the event is
  parked in a dead-letter destination for deliberate replay, never silently
  dropped. A rising dead-letter depth is an alert.

## Rules

- The binding is **one-to-one**: adding a second trigger type means adding a second
  function, not branching inside the handler.
- Redelivery is expected (at-least-once); the handler must be idempotent on `id`
  (`../patterns/idempotent-trigger.md`).
- The envelope **fields** are this pack's contract; the wire encoding and the
  concrete source client are the stack pack's.

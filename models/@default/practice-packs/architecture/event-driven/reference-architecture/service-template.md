# Reference architecture — service template

A language-neutral skeleton for an event-driven service. It names **roles**, not
files or types — the concrete layout, language, and broker client are the stack
pack's (`file-layout.md`) and the Workspace Profile's.

## Components

```
event-driven service
├── handler        # accepts a command, applies a state change, writes the outbox (one txn)
├── publisher      # the outbox poller: reads unpublished outbox rows, publishes in order
├── consumer       # durable-pull subscriber: idempotent effect, ack-after-commit
└── events         # event-type definitions: topic names + envelope + payload shape
```

## Responsibilities

| Role | Owns | References |
|---|---|---|
| **handler** | The state change and the outbox insert, atomically. Emits no event directly. | `../patterns/outbox.md` |
| **publisher** (outbox poller) | Reading the outbox in per-aggregate order and publishing to the broker; marking rows published after ack. | `../patterns/outbox.md` |
| **consumer** | Idempotent processing on the event id; ack after commit; respect `maxInFlight` / `maxDeliver`; dead-letter on budget exceed. | `../patterns/idempotency.md`, `../broker/consumer-good-practice.md`, `../patterns/dead-letter-replay.md` |
| **events** | Topic naming, the required envelope, and backward-compatible payload evolution. | `../events/topic-naming.md`, `../events/schema-evolution.md` |

## What the template deliberately omits

- **Concrete types, packages, file names** — the stack pack's `file-layout.md`.
- **The broker client and its config** — "the platform broker client"
  (`approvedLibraries`), supplied by the stack pack.
- **The logging / metrics client** — the stack pack owns the *how* of the signals
  in `../observability/required-signals.md`.

A skill instantiating this template fills each role using the active stack pack's
idiom; this pack supplies only the role decomposition and the per-role rules.

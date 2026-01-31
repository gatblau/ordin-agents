# Broker-client good practice

Policy for consuming from the broker, expressed against an **abstract** client
("the platform broker client"). No product, library, or protocol is named — the
concrete client is the stack pack's. These are the settings and behaviours a
consumer must honour whatever the underlying broker.

## Consumer pattern

- **Durable pull.** The consumer owns a durable subscription so its position
  survives restarts; it pulls at its own pace rather than being pushed faster
  than it can commit. This gives natural backpressure.
- **One durable group per logical consumer.** Horizontal scaling adds workers to
  the same group (`competing-consumers`); a second logical consumer of the same
  stream uses its own group so the two read independently.

## Acknowledgement

- **Ack after commit.** Acknowledge a message only once its effect is durably
  committed (`../patterns/idempotency.md`). Acking before commit can drop a
  message on a crash; never auto-ack on receipt.
- On processing failure, **do not ack** — let the message be redelivered, up to
  the redelivery budget.

## Redelivery and flow control

| Setting | Policy |
|---|---|
| `maxInFlight` | Bounded — the most unacknowledged messages a worker holds at once. Caps memory and bounds redelivery storms. |
| `maxDeliver` | Bounded — the redelivery budget. On exceed, route to the dead-letter destination (`../patterns/dead-letter-replay.md`). |
| `redeliveryBackoff` | Exponential — back off between redeliveries so a transient dependency outage is not hammered. |
| `deadLetterThreshold` | When delivery count exceeds `maxDeliver`, dead-letter the message rather than retry forever. |

## Rules

- Every setting above has a **bounded** value; "unbounded in-flight" or "infinite
  retries" are defects, not defaults.
- Backpressure comes from durable pull + bounded `maxInFlight`, not from dropping
  messages.
- The **how** of wiring these settings (client API, config keys) is the stack
  pack's; this file states the **what**.

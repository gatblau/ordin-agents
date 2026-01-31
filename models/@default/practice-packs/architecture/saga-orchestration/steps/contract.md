# Step and compensation contract

The abstract shape contracts for a saga step, its reply, and its compensation,
plus the step-messaging policy against an **abstract** broker / coordinator
client. No product, library, or workflow engine is named — the concrete client
is the stack pack's. This file backs the `interfaceConventions`,
`brokerClientPractice`, and the `per-step-timeout-and-retry` pattern.

## Step contract

- A step is invoked by a **command**: `<saga-name>.<step>.command`.
- A step answers with a **reply**: `<saga-name>.<step>.reply` carrying a result of
  `{ succeeded | failed }` and, on failure, a reason.
- Every message — command, reply, compensation — carries the **`saga_id`** so the
  coordinator (or the next participant, in a choreographed saga) correlates it to
  one saga instance.

## Compensation contract

- A completed step is undone by `<saga-name>.<step>.compensate`.
- A compensation is **idempotent** and is **retried until acknowledged**: at
  least-once delivery means it may arrive more than once, and re-running it on the
  same `saga_id` and step has the same effect as running it once.

## Correlation-id propagation

- `saga_id` is the correlation id; it is generated once at saga start and stamped
  on every command, reply, and compensation for that saga instance.
- `trace_id` and `tenant_id` propagate alongside it for observability
  (`../observability/required-signals.md`); they do not replace `saga_id`.

## Step-messaging policy (abstract client)

`per-step-timeout-and-retry` — every step that calls an external participant is
bounded:

| Setting | Policy |
|---|---|
| `stepMessaging` | command / reply on the `saga_id`. |
| `ackPolicy` | Ack after commit — acknowledge a step or compensation only once its effect and the saga-state update are durably committed (`../patterns/saga-state.md`). |
| `maxInFlight` | Bounded — the most unacknowledged step messages held at once. |
| `maxDeliver` | Bounded — the per-step retry budget; on exceed the step is failed and the saga compensates (`../patterns/compensation.md`). |
| `redeliveryBackoff` | Exponential — back off between retries so a transient participant outage is not hammered. |
| `stepIdempotency` | Required on `saga_id` + step — re-delivery of a step command does not double-apply its effect. |
| `compensationDelivery` | At-least-once, idempotent — a compensation is retried until acknowledged and is safe to re-run. |

## Rules

- A step with **no bounded timeout** is the `saga-step-without-timeout`
  anti-pattern; the saga must never hang on a participant.
- The **how** of wiring these settings (client API, config keys) is the stack
  pack's; this file states the **what**.

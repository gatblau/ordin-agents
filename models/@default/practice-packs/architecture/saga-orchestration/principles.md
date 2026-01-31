# Saga / orchestration — principles

The defining stance of this reference architecture. Loaded eagerly; the pattern,
step-contract and observability bodies are loaded lazily when their file globs
match.

## The shape

A **saga** is a long-running distributed transaction split into a sequence of
**local steps**, each owned by one service. There is no shared transaction
across services. Instead, every forward step defines a **compensating action**
that undoes its effect, so a failure part-way through is rolled back by running
the compensations for the steps that already succeeded — never by a distributed
two-phase commit or cross-service lock.

Two coordination shapes carry the same semantics:

- **Orchestrated** — a central coordinator drives the steps and, on failure,
  drives the compensations (`patterns/orchestrated.md`).
- **Choreographed** — each step reacts to the previous step's event and emits
  its own; there is no central coordinator (`patterns/choreographed.md`).

## Non-negotiables

1. **Every forward step has a compensating action.** A step with side effects
   that cannot be undone is a defect (`patterns/compensation.md`); the
   `distributed-transaction-without-compensation` prohibition forbids relying on
   a distributed transaction in its place.
2. **Saga state is persisted.** The steps taken and their outcomes are written
   durably (`patterns/saga-state.md`) so a coordinator restart resumes or
   compensates an in-flight saga rather than losing it.
3. **Every step is bounded.** A step that calls an external participant has a
   timeout and a retry budget (`steps/contract.md`); on exhaustion the saga
   compensates, it does not hang.
4. **Steps and compensations are idempotent.** Step commands and compensations
   are delivered at least once; re-running one on the same `saga_id` and step has
   the same effect as running it once.
5. **No shared mutable state across steps.** Each step owns its own data and
   communicates only through the step / compensation contract
   (`steps/contract.md`); the `shared-mutable-state-across-saga-steps`
   anti-pattern couples steps and makes compensation non-deterministic.

## What this pack does not decide

- The **language, framework, broker product, or workflow engine** — those are the
  stack pack's, referred to here only as "the workflow / saga coordinator".
- **How** signals are emitted (logging library, metric client) — this pack names
  *what* must be emitted (`observability/required-signals.md`); the stack pack
  owns the *how*.
- The **language pairing** — declared by the Workspace Profile, never here.

> This pack reuses messaging *vocabulary* with the Event-Driven pack
> (at-least-once delivery, idempotency, ack-after-commit) but is **standalone**:
> it imports nothing from that pack and may be installed without it.

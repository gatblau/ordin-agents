# Saga / orchestration — anti-patterns

The architectural failure modes this pack forbids. Loaded eagerly. Each maps to
an `antiPatterns` entry in the manifest; a skill that activates on a saga or
workflow artefact should flag these.

| Anti-pattern | Why it is wrong | Do instead |
|---|---|---|
| **Distributed transaction without compensation** | A multi-service write coordinated by a distributed two-phase commit or cross-service locks blocks resources across services and still cannot roll back a step that another service already committed. A failed step has no defined undo. | Model the work as a saga where each forward step has a compensating action (`patterns/compensation.md`); roll back by compensation, never by a distributed transaction. |
| **Saga step without a timeout** | A step that calls an external participant with no bounded timeout hangs the whole saga on a slow or dead participant. In-flight sagas pile up and never complete or compensate. | Give every step a bounded timeout and retry budget (`steps/contract.md`); on exhaustion, fail the step so the saga compensates. |
| **Orchestrator without persisted state** | A coordinator that holds the steps-taken and their outcomes only in process memory loses every in-flight saga on restart — it can neither resume nor compensate them, leaving the system in a partially-applied state forever. | Persist saga state durably (`patterns/saga-state.md`); on restart, load in-flight sagas and resume or compensate them. |
| **Shared mutable state across saga steps** | Steps that read and write one shared mutable record are coupled: the order they run in changes the result, and compensation cannot deterministically restore an earlier value. | Each step owns its own data; steps communicate only through the step / compensation contract (`steps/contract.md`). |

## Smell list (review prompts)

- A step that performs an irreversible side effect (a real-world dispatch, an
  external charge with no refund path) with no compensating action defined.
- A coordinator whose saga state lives only in an in-memory map or a local cache.
- A step call to an external participant with no timeout and no maxDeliver bound.
- A compensation that is not idempotent — re-running it double-undoes or errors.
- Two steps mutating the same row, where the second depends on the first's write.

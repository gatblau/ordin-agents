# Testing Honeycomb — levels

Cited by `urn:ordin:default:skills:quality:testgen`. Defines what each band covers and where it runs. The active **stack** Practice Pack supplies the concrete test runner, container library, and contract-test tooling; this file is language-neutral.

| Band | Covers | Counterpart | Weight |
|---|---|---|---|
| Unit | Complex algorithms: pure logic with real branching | None (in-process) | Few |
| Integration (collaboration) | Each service-to-service collaboration — every outbound dependency | Real (containerised) or contract-stubbed | The body — primary |
| End-to-end | A few cross-service journeys | Real system / staged environment | Few |

## Unit (few)

- Reserved for **complex algorithms** — calculations, parsing, state machines — not wiring or glue.
- Table-driven where ≥3 cases exercise the same path (`scenarioStyle: xunit`).
- Glue between services is covered by the collaboration band, not unit-tested with mocks.

## Integration — collaboration (the primary band)

- One per **outbound collaboration**: every other service, database, message bus, or external API this service calls.
- Backed by a **real, containerised counterpart** where possible (the library pack names the container library); otherwise a **contract-stubbed counterpart** honouring the same wire contract (stub contract source recorded in the test).
- Cover the success interaction and the failure interactions (counterpart errors, times out, is unavailable).
- This is the heaviest band — the system's risk lives between services, so most confidence is bought here.
- Where the project publishes or consumes a versioned contract, a **contract test** (consumer/provider) belongs in this band.

## End-to-end (minimal)

- A few cross-service journeys that only the wired system can prove.
- Slow and flaky across services; keep the count low and do not use e2e to compensate for a weak collaboration band.

## Mapping to the workspace gates

- The stack pack's **unit** command feeds the coverage number (secondary in the honeycomb).
- The stack pack's **integration** command satisfies the integration-suite gate — the collaboration band is the bulk of it.
- e2e, where present, runs in the cross-cutting validation step, not the per-phase unit gate.

# Test Pyramid — levels

Cited by `urn:ordin:default:skills:quality:testgen`. Defines what each level covers and where it runs. The active **stack** Practice Pack supplies the concrete runner, file naming, and container tooling; this file is language-neutral.

| Level | Covers | Dependency | Speed | Proportion |
|---|---|---|---|---|
| Unit | Pure logic: validation, transformation, calculation, state machines, error mapping | None (in-process) | Milliseconds | Many (the base) |
| Integration | One boundary-crossing function against a real, containerised dependency | Real (containerised) | Seconds | Some |
| End-to-end | A whole user journey across the deployed system | Real system / environment | Tens of seconds+ | Few (the cap) |

## Unit

- One unit test file per implementation file, in the stack pack's idiom (co-located or mirrored — the stack pack decides).
- **Table-driven** where ≥3 cases exercise the same path (`scenarioStyle: xunit`).
- Cover every error-table row of the component spec and every Gherkin scenario at the cheapest level that reaches it.
- No process boundary crossed; no real database, broker, or network.

## Integration

- One per **boundary-crossing function** (the boundary rule in `strategy.md`): one happy-path + one error-path, minimum.
- Real, containerised dependency (the library pack names the container library); never a mock for a containerisable service.
- Brought up and torn down per test binary/module (the library pack's container lifecycle idiom); do not share a global container across unrelated suites.
- **Not** counted toward the unit-coverage threshold; required by the framework gate on its own.

## End-to-end

- Few — reserve for the critical user journeys that only a fully-wired system can prove.
- Slow and the most brittle; do not push detail here that a unit or integration test can catch.
- Where a full environment cannot be stood up, a **stub** of the unavailable edge service honours the same wire contract (the stub's contract source is recorded in the test).

## Mapping to the workspace gates

- The stack pack's **unit** command feeds the ≥70% coverage gate.
- The stack pack's **integration** command satisfies the integration-suite gate (independent of coverage).
- e2e, where present, runs in the cross-cutting validation step, not the per-phase unit gate.

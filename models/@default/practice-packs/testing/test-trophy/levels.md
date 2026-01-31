# Test Trophy — levels

Cited by `urn:ordin:default:skills:quality:testgen`. Defines what each band covers and where it runs. The active **stack** Practice Pack supplies the concrete type-checker, linter, test runner, and container tooling; this file is language-neutral.

| Band | Covers | Tooling (the stack pack's) | Weight |
|---|---|---|---|
| Static | Type errors, lint violations, unsafe constructs, formatting | The stack pack's type-check + lint commands | The floor — always clean |
| Unit | Complex pure logic only: algorithms, calculations, state machines | The stack pack's unit runner | Some — selective |
| Integration | Each boundary-crossing function against a real, containerised dependency | The stack pack's test runner + the library pack's container library | The body — primary |
| End-to-end | A few critical whole-system journeys | The stack pack's e2e harness / a stub edge | Few |

## Static (the floor)

- The active stack pack's **type-check** and **lint** run first and must exit clean before any test runs.
- This band is not optional and is not substituted by tests; it is the cheapest defect catch.
- Formatting is part of the floor where the stack pack enforces it.

## Unit (selective)

- Reserved for **complex pure logic** — not glue, not wiring, not thin pass-throughs.
- Table-driven where ≥3 cases exercise the same path (`scenarioStyle: xunit`).
- If a unit test needs a real dependency, it is an integration test and moves to that band.

## Integration (the primary band)

- One per **boundary-crossing function**: at least one happy-path and one error-path test, backed by a **real, containerised** dependency (the library pack names the container library).
- This is the heaviest band — most of the suite's behavioural confidence lives here.
- Never a mock for a containerisable service.

## End-to-end (minimal)

- A few critical user journeys that only a fully-wired system can prove.
- Where a full environment cannot be stood up, a **stub** of the unavailable edge service honours the same wire contract (the stub's contract source is recorded in the test).

## Mapping to the workspace gates

- The stack pack's **type-check + lint** is the static floor — required, and clean before tests.
- The stack pack's **integration** command satisfies the integration-suite gate (the primary band here).
- The stack pack's **unit** command feeds the coverage number (secondary in the trophy).

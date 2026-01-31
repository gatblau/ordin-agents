# Test Pyramid — strategy

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase C. This file describes the *shape* a test suite takes; the active **stack** Practice Pack supplies *how* each level is written (runner, file naming, container tooling). This pack names no language or tool.

## The shape

A pyramid: a broad base of fast unit tests, a narrower band of integration tests, and a small cap of end-to-end tests.

```
        /\        e2e        — few; whole-system, slowest, most brittle
       /  \
      /----\      integration — some; one per boundary-crossing function, real dependency
     /      \
    /--------\    unit         — many; fast, isolated, the bulk of the suite
```

Indicative proportion (a guide, not a hard gate): roughly **70% unit / 20% integration / 10% e2e** by test count. The point is the *ordering* of investment, not the exact numbers — push detail down to the cheapest level that can catch the defect.

## Where coverage is enforced

- The workspace's **≥70% coverage threshold applies to the unit run** (computed by the active stack pack's coverage command — this pack names no tool; the stack pack's `build-commands` supplies the concrete one).
- Integration and e2e tests are **required by the framework gate independently** of the coverage number; they prove behaviour across boundaries, not lines covered.
- Coverage is a floor, not a target: 100% line coverage of trivial code is not the goal; covering each behaviour and error path is.

## The boundary rule

Every **boundary-crossing function** — one that talks to a database, message bus, blob store, external API, or hardware peripheral — gets at least:

- one **happy-path** integration test, and
- one **error-path** integration test (the dependency returns an error, times out, or is unavailable),

each backed by a **real, containerised** dependency (the active library pack names the container library; do not mock a service that can be containerised). How the container is brought up is the library pack's idiom; *that* it must be real is this strategy's rule.

## What stays at the unit level

Pure logic — validation, transformation, calculation, state machines — is unit-tested with table-driven cases (`scenarioStyle: xunit`). A unit test does not cross a process boundary; if it needs a real database, it is an integration test and moves down a band.

## Forbidden

- Inverting the pyramid (more e2e than unit) — see `anti-patterns.md`.
- Substituting a mock for a containerisable dependency in the integration band.
- Treating unit coverage as the *only* gate; the integration band is required on its own.

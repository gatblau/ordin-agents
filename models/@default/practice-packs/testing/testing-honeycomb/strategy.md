# Testing Honeycomb — strategy

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase C. This file describes the *shape* a test suite takes for a **service-oriented** system; the active **stack** Practice Pack supplies *how* each band is realised (the test runner, container library, contract-test tooling). This pack names no language or tool.

## The shape

A honeycomb: a small unit band, a **wide integration body centred on service-to-service collaboration**, and a small e2e cap.

```
       _____        e2e          — few; cross-service journeys
      /     \
     /       \      integration   — the body; every service collaboration
     \       /
      \_____/       unit           — few; complex algorithms only
```

It is the shape for systems whose risk lives **between services**, not inside a single unit. A microservice is mostly orchestration and I/O across collaborators; isolated unit tests (with mocks) miss exactly the integration risk that matters, and broad end-to-end suites across many services are slow and flaky. So the investment concentrates on the **collaboration** band.

## The collaboration boundary rule

For each **service-to-service collaboration** — every outbound dependency this service calls (another service, a database, a message bus, an external API) — write an integration test that exercises the real interaction:

- backed by a **real, containerised counterpart** where it can be containerised (the active library pack names the container library), or
- backed by a **contract-stubbed counterpart** honouring the same wire contract where it cannot be containerised (a third-party SaaS, a proprietary appliance). The stub's contract source is recorded in the test.

Never a mock for a counterpart that can be containerised. Cover the success interaction and the meaningful failure interactions (the counterpart errors, times out, or is unavailable).

## What stays at the unit level

Only **complex algorithms** — pure logic with real branching — get isolated unit tests (`scenarioStyle: xunit`). Wiring and glue between services are covered by the collaboration band, not unit-tested with mocks.

## End-to-end, minimal

A few cross-service journeys only. Broad e2e suites are slow and flaky across services; do not grow them to compensate for a weak collaboration band — strengthen the collaboration band instead.

## Forbidden

- Broad, slow, flaky end-to-end suites standing in for collaboration tests — see `anti-patterns.md`.
- Mocking a containerisable counterpart in the collaboration band.
- Naming a concrete test runner (the stack pack's idiom) or container library / contract tool (the library pack's idiom) here — this strategy pack names no tool.

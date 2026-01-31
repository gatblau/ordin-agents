# Test Trophy — strategy

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase C. This file describes the *shape* a test suite takes; the active **stack** Practice Pack supplies *how* each band is realised (the type-checker, linter, test runner, container tooling). This pack names no language or tool.

## The shape

A trophy: a wide static-analysis base, a slim unit band, a heavy integration body, and a small e2e cap.

```
        /\        e2e         — few; whole-system
       /==\
      /    \      integration  — the body; the primary confidence layer
     /      \
      \    /      unit          — some; complex pure logic only
       \  /
    ==========    static        — the floor; types + lint, always clean
```

The contrast with the pyramid is deliberate: the **integration band is the primary confidence layer**, not a thin tier above a large unit base. Many systems are mostly glue and I/O; testing that glue in isolation (with mocks) adds little confidence, so the investment moves to integration against real dependencies.

## The static floor

Static analysis — the active stack pack's **type-check and lint** — is the **non-negotiable floor**. It runs first and must be clean before tests run. It is the cheapest place to catch a whole class of defects (type errors, unused/unsafe constructs), so it carries weight a unit test would otherwise spend.

## Where confidence comes from

- **Integration (primary):** each boundary-crossing function tested against a **real, containerised** dependency (the active library pack names the container library). This is where the bulk of the test investment goes. No mocking a containerisable service.
- **Unit (selective):** only complex **pure logic** — algorithms, calculations, state machines — gets isolated unit tests. Glue and wiring are covered by the integration band, not unit-tested with mocks.
- **e2e (minimal):** a few critical journeys only.

## Coverage

- A line-coverage number is computed by the active stack pack's coverage command, but in the trophy it is a **secondary** signal — the integration band's behavioural coverage matters more than the unit line count.
- The static floor and the integration suite are each required by the framework gate on their own.

## Forbidden

- Skipping or relaxing the static floor — see `anti-patterns.md`.
- Over-investing in isolated unit tests of glue instead of integration tests of behaviour.
- Substituting a mock for a containerisable dependency in the integration band.

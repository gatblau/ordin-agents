# BDD / Specification-by-Example — strategy

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase C. This file describes the *shape* a test suite takes when scenarios are the unit of truth. *How* the scenarios are bound and run splits across two packs: the active **library** pack supplies the step runner and the container tooling; the active **stack** pack supplies where step files live and the language test mechanics. This pack names no language or tool.

## Scenarios are the executable specification

The unit of truth is a `Given/When/Then` scenario in a `.feature` file, written **outside-in** (from the observable behaviour a user or caller cares about) and **business-readable** (a domain expert can read it without seeing code). The scenarios *are* the specification; the implementation makes them pass.

- A `Feature` groups scenarios for one behaviour cluster.
- A `Scenario` is one concrete example: a `Given` context, a `When` action, a `Then` outcome (plus `And`/`But`).
- Steps describe **what** happens, never **how** (no UI selectors, no API endpoints encoded in the step text, no implementation nouns).

## The boundary rule

Every **boundary behaviour** — a behaviour that crosses into a database, message bus, blob store, external API, or peripheral — gets at least one scenario, backed by a **real, containerised** dependency (the active library pack names the container library and the step runner; *that* the dependency is real is this strategy's rule). Do not back a scenario with a mock of a service that can be containerised.

Cover both the success behaviour and the meaningful failure behaviours (invalid input rejected, dependency unavailable) as separate scenarios.

## Relationship to test levels

BDD is a *style*, orthogonal to the pyramid/trophy proportion (`shape: scenario-driven`). Scenarios are realised predominantly at the **integration** level (a scenario backed by a real dependency is an integration test); pure-logic helpers beneath them may still be unit-tested in the stack pack's idiom. Line coverage is secondary to **scenario coverage of behaviours**.

## How a scenario is run

The `.feature` is language-neutral. The **active library pack** supplies the binding that executes it — a step-definition runner declared in that pack's `approvedLibraries` / `container-setup.md` (e.g. the Gherkin runner). This pack names none of them; the same `features/orders.feature` composes with every stack + library pack unchanged. See `features/orders.feature` for the worked example.

## Forbidden

- Imperative steps coupled to a UI or wire detail — see `anti-patterns.md`.
- Backing a scenario with a mock of a containerisable dependency.
- Naming a concrete step runner or container library here — that is the library pack's idiom.

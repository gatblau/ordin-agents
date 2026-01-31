# Test Trophy — anti-patterns

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase E. Strategic anti-patterns — failures of *shape*, not of language idiom (those are the stack pack's). Each is reported with a citation; do not flag without evidence.

| id | What it is | Why it bites |
|---|---|---|
| `over-investing-in-isolated-unit-tests-of-glue` | Unit tests (often mock-heavy) for wiring, pass-throughs, and glue that have no complex logic | Inflates the suite and the coverage number without confidence; in the trophy, confidence in glue comes from integration against real dependencies, not from mocked unit tests. |
| `skipping-the-static-floor` | Letting type-check or lint warnings through, or treating them as optional | The static floor is the cheapest defect catch and the non-negotiable base of the trophy; tests do not substitute for a clean type-check and lint. |
| `mocking-a-containerisable-dependency` | A mock standing in for a service that has a real, containerisable implementation, in the integration band | The integration band is the primary confidence layer; a mock there proves nothing about production. |
| `thin-integration-band` | Treating integration as a thin tier above a large unit base (a pyramid in trophy's clothing) | Defeats the trophy's premise — for glue-and-I/O systems, the integration band must be the heaviest, not an afterthought. |
| `e2e-creep` | Growing the e2e cap to compensate for a weak integration band | Slow, flaky, expensive; fix the integration band rather than pile on e2e. |

## How testgen uses this

- Flag mock-heavy unit tests of glue/wiring as `over-investing-in-isolated-unit-tests-of-glue`.
- Flag a suppressed type-check/lint finding as `skipping-the-static-floor`.
- Flag an integration band smaller than the unit band (for a glue/I-O-heavy component) as `thin-integration-band`.

These are *shape* findings. Language-level test smells are the stack pack's `antiPatterns`, not this pack's.

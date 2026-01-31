# Test Pyramid — anti-patterns

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase E. Strategic anti-patterns — failures of *shape*, not of language idiom (those are the stack pack's). Each is reported with a citation; do not flag without evidence.

| id | What it is | Why it bites |
|---|---|---|
| `inverted-ice-cream-cone` | More end-to-end than unit tests — a wide, slow e2e layer on a thin unit base | Slow, flaky, expensive feedback; a failure points at "something, somewhere" rather than a precise unit. Invert it: push detail to the cheapest level that catches the defect. |
| `mocking-a-containerisable-dependency` | A mock or stub standing in for a service that has a real, containerisable implementation, in the integration band | Mocks encode assumptions that drift from production behaviour; the integration band exists precisely to test against the real thing. Reserve mocks for the unit level. |
| `asserting-on-implementation-detail` | Tests that assert on private internals, call order, or structure rather than observable behaviour | Break on every refactor even when behaviour is unchanged; raise the cost of change without raising confidence. Assert on inputs/outputs and side effects. |
| `coverage-as-a-target` | Chasing a coverage percentage by testing trivial getters/glue | Inflates the number without adding confidence; coverage is a floor that flags untested behaviour, not a score to maximise. |
| `boundary-without-error-path` | An integration test for the happy path only, with no error-path test for the dependency failing | The error path is where boundary bugs live (timeouts, partial failures, retries); the boundary rule requires both. |

## How testgen uses this

- Flag a suite whose e2e count exceeds its unit count as `inverted-ice-cream-cone`.
- Flag a mock of a dependency the active library pack's container tool can containerise as `mocking-a-containerisable-dependency`.
- Flag a boundary-crossing function with a happy-path integration test but no error-path one as `boundary-without-error-path`.

These are *shape* findings. Language-level test smells (e.g. a shared mutable fixture) are the stack pack's `antiPatterns`, not this pack's.

# Testing Honeycomb — anti-patterns

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase E. Strategic anti-patterns — failures of *shape*, not of language idiom (those are the stack pack's). Each is reported with a citation; do not flag without evidence.

| id | What it is | Why it bites |
|---|---|---|
| `broad-slow-flaky-e2e-suites` | A large end-to-end suite across many services standing in for collaboration tests | Slow, flaky, and hard to diagnose — a failure points at the whole mesh, not the broken collaboration. In the honeycomb, confidence comes from per-collaboration integration tests. |
| `mocking-a-containerisable-dependency` | A mock standing in for a counterpart that has a real, containerisable implementation | Proves nothing about the real interaction; use a real or contract-stubbed counterpart in the collaboration band. |
| `unit-testing-glue-instead-of-collaboration` | Unit-testing the wiring/orchestration between services with mocked collaborators | Misses the integration risk that is the whole point of a service; test the collaboration against a real or contract-stubbed counterpart. |
| `untested-collaboration` | An outbound dependency (service, queue, external API) with no integration test for the collaboration | The honeycomb's premise is that every collaboration is exercised; an untested one is where the production incident hides. |
| `contract-drift-uncaught` | A consumed or published interface with no contract test, left to drift | Cross-service contracts break silently; a contract test in the collaboration band catches the drift before deploy. |

## How testgen uses this

- Flag a large e2e suite with few collaboration integration tests as `broad-slow-flaky-e2e-suites`.
- Flag an outbound dependency with no collaboration integration test as `untested-collaboration`.
- Flag a mock of a containerisable counterpart as `mocking-a-containerisable-dependency`.

These are *shape* findings. Language-level test smells are the stack pack's `antiPatterns`, not this pack's.

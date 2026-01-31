# BDD — anti-patterns

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase E. Strategic anti-patterns — failures of *scenario shape*, not of language idiom (those are the stack pack's). Each is reported with a citation; do not flag without evidence.

| id | What it is | Why it bites |
|---|---|---|
| `imperative-steps-coupled-to-ui` | Steps that drive UI selectors or wire detail (`When I click "#submit"`, `When I POST /orders`) | Describes HOW, not WHAT; breaks on any UI/endpoint change and stops being a readable specification. Push the mechanics into the step definition; keep the scenario declarative. |
| `mocking-a-containerisable-dependency` | A scenario backed by a mock or stub of a service that has a real, containerisable implementation | Proves nothing about production behaviour; the boundary rule requires a real dependency. |
| `assertions-on-implementation-detail` | `Then` steps asserting internal state, table contents, or call order rather than observable outcome | Couples the spec to structure; breaks on refactor and is unreadable to a domain expert. Assert on what a caller/user can observe. |
| `scenario-soup` | One scenario with many `When`/`Then` pairs testing several behaviours | Hard to read, hard to diagnose on failure; split into one scenario per behaviour. |
| `incidental-detail-in-steps` | Steps cluttered with data irrelevant to the behaviour under test | Obscures the example; include only the data the behaviour depends on, push the rest to `Background` or fixtures. |

## How testgen uses this

- Flag a step naming a UI selector or HTTP verb/path as `imperative-steps-coupled-to-ui`.
- Flag a scenario backed by a mock of a dependency the active library pack's container tool can containerise as `mocking-a-containerisable-dependency`.
- Flag a scenario with multiple `When` actions as `scenario-soup`.

These are *scenario-shape* findings. Language-level binding smells (e.g. a brittle step regex) are the stack pack's `antiPatterns`, not this pack's.

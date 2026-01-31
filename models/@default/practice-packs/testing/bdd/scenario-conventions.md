# BDD — scenario-authoring conventions

Cited by `urn:ordin:default:skills:quality:testgen`. Language-neutral rules for writing `.feature` scenarios. The active **stack** Practice Pack supplies the runner that binds the steps; these conventions govern the scenario text, not the binding.

## Structure

- **One `Feature` per behaviour cluster.** The `Feature:` line names the capability and a short value statement.
- **One `Scenario` per concrete example.** Prefer several specific scenarios over one scenario with many branches.
- **`Background`** holds the `Given` steps common to every scenario in the feature; do not repeat them.
- **`Scenario Outline` + `Examples`** for the same behaviour across a table of inputs; keep the outline readable.

## Step style

- `Given` sets up state (a running service, seeded data) — the context, in the past/present tense.
- `When` is the single action under test — one `When` per scenario where possible.
- `Then` asserts an observable outcome — what a caller or user can see, not an internal field.
- Write steps in the **domain's language**, declaratively: *"When a client places a valid order"*, not *"When I POST /orders with body {…}"*. The wire detail lives in the step definition (the library pack's runner idiom), not the scenario.
- Reuse step phrasings so the step-definition surface stays small and stable.

## Outside-in

Author the scenario first, from the behaviour the caller cares about; let it drive the interface and the implementation. The scenario is the specification — it exists before the code that satisfies it.

## Boundary coverage

For each boundary behaviour, write at least:

- a **success** scenario (the happy path), and
- one or more **failure** scenarios (invalid input rejected; the dependency unavailable or returning an error),

each backed by a **real** dependency (no mocking a containerisable service).

## Forbidden in scenario text

- UI selectors, element ids, or page mechanics (`When I click the "#submit" button`).
- Wire/transport detail (HTTP verbs, paths, status codes, JSON bodies) — those belong in the step definition.
- Implementation nouns (table names, class names, queue names).
- A concrete runner or tool name — the scenario is runner-agnostic; the library pack binds it.

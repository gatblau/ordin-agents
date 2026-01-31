# Phase C — Test Generation & Verification

Every file in Phase B that contains logic gets a corresponding test file. Test files live in the same package by default; switch to an external test package only if the spec specifies black-box testing. The exact file naming and packaging convention come from the active Practice Pack's `file-layout.md`.

## C1 — Unit tests

- One `Test<Function>_<Scenario>` (or the language's idiomatic equivalent) per Gherkin scenario in the spec's Acceptance Criteria.
- One `Test<Function>_Error_<Condition>` per row in the spec's Error Table.
- Table-driven tests whenever ≥3 cases exercise the same code path. The exact form (struct slices, parameterised tests, theory tests, …) is the language's idiom.
- Mock external dependencies using interfaces defined in Phase B (repository, clients, publishers). Hand-written test doubles in the location the Practice Pack's `file-layout.md` specifies for shared test helpers, not generated mocks, unless the project already uses a mocking library.
- Validation tests: every field constraint declared in the spec's Data Model gets at least one positive and one negative case.

## C2 — Integration tests

For components that cross a process boundary (database, message bus, blob store, external API, peripheral), produce integration tests using the test-container or stub tooling supplied by the active Practice Pack's `container-setup.md`, following the build constraint or test-tag form and the file-naming convention in its `integration-testing.md`. The container library lives in `container-setup.md` (the active library pack's); the language test mechanics live in `integration-testing.md` (the active stack pack's).

The skill produces at minimum one happy-path and one error-path integration test per such component, **fully implemented** — not stubs, not skipped.

Where a real dependency cannot be containerised (proprietary appliance, third-party SaaS, hardware peripheral), materialise a stub service that honours the same wire contract and record the contract source in a comment on the stub. The stub pattern is workspace-level discipline; the language idiom for stubs is the Practice Pack's concern.

## C3 — Test helpers

If (and only if) the component needs shared fixtures, factories, or mock builders, put them in the location the Practice Pack's `file-layout.md` specifies for shared test helpers. Do not create helpers speculatively. Single-use helpers stay inline.

## C4 — Blocking verification

After generating all code and tests, run the verification commands supplied by the active Practice Pack's `build-commands.md`. Code generation is **not complete** until every command passes.

The sequence is, in this order, with the exact commands from the Practice Pack:

1. **Compile / build** — must succeed with no errors.
2. **Unit tests with coverage** — must pass; coverage must meet the project's coverage minimum (the Practice Pack's `build-commands.md` declares the threshold; the workspace default is 70%).
3. **Lint** — must pass with no errors.

The integration tests are run separately as the integration-suite framework gate (per `@default/commands/lifecycle/apply.md` step 7), not inside Phase C4.

If any step fails:
1. Identify the root cause (not the symptom).
2. Fix the implementation or test in Phase B/C.
3. Re-run the entire verification sequence.
4. Do not deliver the response with any step failing. Do not weaken or skip the criteria. Do not bypass pre-commit or CI hooks.

## What Phase C is not

- Not benchmark tests unless the spec defines a performance-critical path with explicit latency targets.
- Not fuzz tests unless the spec requires them.
- Not end-to-end tests that cross multiple components — those are owned by the integration suite orchestrated elsewhere.
- Not security scanning — that is the security-scan framework gate, not Phase C.

---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:quality:testgen"
  name: testgen
  description: "Writes unit and integration tests for code that has no spec, working out the intended behaviour from the code."
  version: 2.0.0
  owner: gatblau
description: Retrofit unit and integration tests for existing source code that lacks coverage. Reverse-engineers behaviour from the code (no spec required), identifies uncovered branches and error paths, and generates table-driven tests with hand-written test doubles. Stack-neutral — names no language; the active Practice Pack supplies the toolchain (test runner, coverage commands, file naming, build constraints, test-container library). Trigger on phrases like "generate tests for <file>", "retrofit tests", "testgen <package>", "improve coverage of X", or when the user asks to add tests to existing code without a spec. Do NOT trigger on greenfield "generate code + tests from a spec" (that is codegen).
---

# testgen — Test retrofit for existing code

Produce unit and integration tests for code that was written without a spec. Different from `codegen`: there is no spec — behaviour is reverse-engineered from the code itself and any existing tests, then tested against current behaviour (not against a desired contract).

This skill is **stack-neutral**. The toolchain (test runner, coverage commands, file naming, build constraints, test-container library) comes from the active Practice Pack's `build-commands.md`, `file-layout.md`, `integration-testing.md` (the language test mechanics) and `container-setup.md` (the test-container library / stub idiom itself). If no Practice Pack is installed, the skill stops and asks the user — do not guess.

## Arguments

- `target` (required): a file, package path, or directory to cover. Form is the language's idiomatic path (e.g. a module path in Go, a file glob in TypeScript, a package in Java).
- `coverage-goal`: default supplied by the active Practice Pack (workspace fallback: 70%). Minimum acceptable line coverage for the target.
- `mode`: `generate` (default) | `audit-only` (produce coverage gap report; do not write tests).

## Active modes

**Observe → Patch → Review**, with **Execute** inside the test-run verification.

- **Observe** for Phases 1–4: probe toolchain, baseline coverage, extract behaviour from the code as-written. Pure file reads; no test execution yet.
- **Patch** for Phases 5–6: write test files. Test sources are emitted alongside the code under test (location per the Practice Pack's `file-layout.md`), never rewriting the code under test.
- **Execute** for the test-run verification at the end of Phase 6 — sandboxed run of the test command supplied by the Practice Pack's `build-commands.md`.
- **Review** for Phase 7: coverage report against the `coverage-goal` argument, list of skipped tests with reasons.

The skill never edits the code under test. When a generated test fails because current behaviour looks wrong, testgen marks the test skipped (in the language's idiomatic skip form, e.g. `t.Skip` in Go, `it.skip` in JS, `pytest.skip` in Python) with a reason and routes to `/rca`. **Escalate** when toolchain probing fails (no test runner available), when no Practice Pack supplies a toolchain for the target language, or when the coverage goal cannot be met without inventing behaviour the code does not exhibit.

## Hard rule

**Testgen tests current behaviour, not desired behaviour.** If the code has a bug, the test will encode the bug. Testgen surfaces the coverage gap; it does not decide whether the code is correct. Fixing bugs is a separate `/rca` → `/breakdown` → `/apply` cycle.

State this explicitly in the final summary. Users must understand what they are signing off on.

## Process

### Phase 1 — Toolchain probe
Read the active Practice Pack's `build-commands.md` for the test command, coverage command, and any per-language version probe. Verify the runner is available. Load `references/language-toolchain.md` for stack-neutral guidance on detecting which test runner the project actually uses (in case the Practice Pack permits multiple).

If no Practice Pack supplies a toolchain for the target's language, stop and tell the user.

### Phase 2 — Coverage baseline
Run the project's existing test suite against the target and capture current coverage. The exact command comes from the Practice Pack's `build-commands.md`.

Record per-function coverage. This is the "before" number — every generated test must move it toward `coverage-goal`.

### Phase 3 — Behaviour extraction
Load `references/coverage-probes.md`. For each function in the target:

1. Extract the signature and exported / unexported status.
2. Identify every branch (conditional, switch, early return, error-return path).
3. Identify every external call (persistence, HTTP, message bus, filesystem, current-time, random). These are mocking boundaries.
4. Identify every validation or precondition check.
5. Record the set of observable outcomes (return values + side effects).

The output of this phase is a per-function behaviour table. Do not guess — read the code. If a function's behaviour cannot be determined by reading (e.g. depends on reflection, runtime configuration, or generated code), flag it and skip test generation for that function.

### Phase 4 — Gap identification
Cross-reference Phase 3's branches against Phase 2's coverage. Every uncovered branch is a gap. Every untested error path is a gap. Rank gaps:

- **Critical** — untested error path on a public function; untested branch that writes to persistence / publishes a message / mutates external state.
- **Important** — untested branch on a public function that only reads.
- **Minor** — untested branch on an unexported helper.

Generate tests in that order.

### Phase 5 — Test generation
Load `references/test-patterns.md`. For each gap, generate a test using the language's idiomatic pattern:

- Table-driven tests when ≥3 cases share a path.
- Hand-written test doubles for interfaces (do not invent new mocking frameworks the project does not use).
- **Integration tests are the primary exit-gate shape** for any function that crosses a process boundary (persistence, message bus, blob store, external API, peripheral). Bring the integrating service up as a black box using the test-container or stub tooling supplied by the active Practice Pack's `container-setup.md`, following the build constraints and file/package layout in its `integration-testing.md`. Use the same image and version the project already uses; do not invent a version. Where the technology cannot be containerised, materialise a **stub service** that honours the same wire contract and record where the contract came from (spec section, vendor doc, captured trace). Unit tests are still allowed for pure logic, but they do not substitute for the integration test on a boundary-crossing function.
- One happy path + every error-path case at minimum.

Respect the project's test conventions: same package (white-box) unless existing tests in the target use the language's external test convention (black-box). Match existing naming patterns; the Practice Pack's `file-layout.md` declares the project's convention for test file naming.

Do not modify the source code under test. Do not add new dependencies unless the user explicitly approves.

### Phase 6 — Verification
Run the generated tests and re-measure coverage using the Practice Pack's commands.

If coverage has not reached `coverage-goal`, either:
- Add more tests for the remaining critical / important gaps, or
- Stop and report the remaining gaps honestly — do not pad with trivial tests to hit a number.

Every generated test must pass on current code. If a test fails because the current behaviour looks wrong, do not "fix" the code — report the failure as a suspected bug, leave the test marked skipped (in the language's idiom) with a one-line reason, and tell the user to run `/rca`.

### Phase 7 — Summary
Report:
- Baseline coverage → post-generation coverage.
- Files added (test files, test data, helpers).
- Critical gaps closed, remaining open.
- Any tests skipped due to suspected bugs — list each with the function name and the unexpected behaviour observed.
- Explicit reminder: "These tests encode current behaviour. If any encoded behaviour is incorrect, fix the code and update the test — do not read the test as specification."

## Output files

The exact file naming is supplied by the Practice Pack's `file-layout.md`. Examples of what the Practice Pack might specify:

- *(Go pack)* `<package>/<file>_test.go` for unit tests; `<package>/<file>_integration_test.go` with `//go:build integration` for integration tests; `<package>/testutil_test.go` for shared fixtures.
- *(TypeScript pack)* `__tests__/<file>.test.ts` for unit tests; `__tests__/<file>.integration.test.ts` for integration tests.
- *(Python pack)* `tests/test_<module>.py`, `tests/integration/test_<module>.py`, `tests/conftest.py`.

The skill never produces source files outside the test layout. The skill never adds dependencies.

## References (load on demand)

- `references/language-toolchain.md` — stack-neutral guidance on detecting which test runner / coverage tool the project actually uses, when the Practice Pack permits multiple. Load at Phase 1.
- `references/coverage-probes.md` — how to identify branches, calls, and outcomes per language. Load at Phase 3.
- `references/test-patterns.md` — table-driven, mocking, integration, fixture patterns (stack-neutral with examples). Load at Phase 5.

## Practice Pack references (load on demand from the active pack)

- `build-commands.md` — exact test, coverage, integration-test commands.
- `file-layout.md` — test file naming and packaging convention.
- `integration-testing.md` — build constraints, file/package layout (language test mechanics).
- `container-setup.md` — test-container or stub tooling (the active library pack's).

## What testgen does not do

- Does not fix bugs in the code under test.
- Does not refactor the code under test.
- Does not generate tests for dead code — flag it for deletion instead.
- Does not add behavioural assertions that are not verifiable from the current code.
- Does not produce documentation.

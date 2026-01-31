# Integration testing (Go)

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` Phase C. This file names the Go-specific integration-testing **mechanics** — the file/package layout and build constraints. Two adjacent decisions live elsewhere (RFC-09 / RD-2):

- The **container tool** (which test-container library, the bring-up idiom) is the active **library** pack's `container-setup.md` — e.g. `urn:ordin:default:practice-packs:library:go:testcontainers`. This pack names no container library.
- The **strategy** (which functions need integration tests, how many, and the no-mocking-a-containerisable-dependency rule) is the active **testing-strategy** Practice Pack's `boundaryRule`.

With no testing pack installed, the skill falls back to the workspace's baseline integration gate.

## File and package layout

- Integration tests live in `<file>_integration_test.go` next to the unit tests.
- The first non-comment line is the build constraint:
  ```go
  //go:build integration
  ```
- Tests live in the same package as the implementation by default; switch to the external `_test` package only if the spec specifies black-box testing.

## Container setup and stub services

The container bring-up/teardown idiom and the stub-service fallback (when a dependency cannot be containerised) are the active **library** pack's `container-setup.md` — they depend on the chosen container tool, which this stack pack does not name. The Go mechanics in this file (build constraint, file naming, same-package placement) compose with whatever container tool that pack supplies.

## Coverage mechanics

- **How many** integration tests, and on which boundary-crossing functions, comes from the active testing-strategy Practice Pack's `boundaryRule` — not from this file. This pack supplies only the Go mechanics for writing them.
- Integration tests do **not** count toward the 70% unit coverage threshold; that threshold is computed from the unit test run only.
- Integration tests are required by the framework gate independently of unit coverage. Unit-test results alone do not satisfy the integration suite gate (per `@default/commands/lifecycle/apply.md` step 7 and `@default/commands/sync/sync-check.md` clean-exit criterion).

## Forbidden

- Sharing containers across test binaries via global state. Each test sets up and tears down its own containers, even if it is slower.
- Inventing image versions. Use what the project pins; if no pin exists, stop and ask the user.
- Skipping the integration suite with `-short` or a custom flag and treating the unit run as the gate. The gate is non-overridable.

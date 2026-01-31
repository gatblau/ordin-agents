# File layout (Go)

Cited by `urn:ordin:default:skills:quality:codegen` Phase A6 and Phase B sub-order. The workspace skill produces a generic per-component file plan; this file makes the plan concrete for a Go project.

## Module-level layout

- `cmd/<binary>/main.go` — process entry points. One subdirectory per binary the module produces.
- `internal/` — implementation. Default for any code not designed for external import.
- `pkg/` — code explicitly designed to be imported by external, third-party projects. Reserve this; do not use it as a default.
- `internal/domain/<component>/` — one directory per spec component (per `urn:ordin:default:skills:quality:specgen` Phase 2B Component Inventory).

`R13` (minimise public surface) translates here as: default to unexported names; default to `internal/`; promote to `pkg/` only when the spec explicitly names the component as a library surface.

## Per-component file set

For each spec component, produce these files in this sub-order during Phase B:

| Sub-phase | File | Contents |
|---|---|---|
| B1 | `errors.go` | Typed error definitions and error code constants used elsewhere in the package |
| B2 | `model.go` | Data models (structs) and validation methods |
| B3 | `repository.go` | Data access (queries, transactions). Omit if the component is pure logic. |
| B4 | `service.go` | Business logic orchestration |
| B5 | `handler.go` (or `consumer.go` / `cli.go`) | HTTP handler / message-bus consumer / CLI entrypoint |
| B6 | `wire.go` | Constructors (`NewService`, `NewHandler`, ...) |
| B7 | Migrations | If the component owns DDL, paired `up.sql` + `down.sql` under the project's migrations directory |

Skip sub-phases that do not apply to a given component (e.g. an in-memory cache has no `repository.go`).

## Tests

Match the implementation file set:

- `<file>_test.go` for unit tests, in the same package by default.
- `<file>_integration_test.go` for integration tests, with `//go:build integration` at the top.
- `testutil_test.go` only when shared fixtures or factories are needed.

## File header

Every generated file begins with a marker comment so a reviewer can map a generated file to its target path at a glance:

```
// File: internal/domain/<component>/<file>.go
```

Then the package declaration. Then the file body.

## Forbidden

- `internal/...` exported from `pkg/...`. The convention exists to be enforced.
- One giant `main.go` containing handlers, services, and migrations. Use the per-component file set above even for small services.
- Speculative `testutil_test.go`. Add it when the second test file needs shared fixtures, not before.

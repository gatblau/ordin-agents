# Build / lint / test / coverage commands (Go)

Cited by `urn:ordin:default:skills:quality:codegen` Phase C4, by the `/apply` framework gate, and by the `/sync-check` framework gate. The workspace itself names no toolchain; this file does.

## Build

```
go build ./<package>/...
```

A clean exit (`exit 0`) is required for the gate to pass. Vet errors do **not** fail the build by default — they are caught by the lint command below.

## Lint

```
golangci-lint run ./<package>/...
```

A clean exit (`exit 0`) is required for the gate to pass. The linter configuration is the project's `.golangci.yml`; this pack does not mandate a configuration. If no `.golangci.yml` is present, run with the project's CI-equivalent flags or stop and ask the user — do not silently apply defaults.

## Unit tests

```
go test ./<package>/... -v -count=1 -cover -coverprofile=coverage.out
```

Minimum coverage: **70%** total over the changed packages. Coverage is computed from `coverage.out`. The 70% threshold is the workspace default; a Practice-Pack consumer may raise it but not lower it.

## Integration tests

```
go test ./<package>/... -tags=integration -v -count=1
```

Integration tests carry the `integration` build tag and live in `*_integration_test.go` files. They are **not** part of the default unit-test run; they are run separately as the integration-suite gate (see `integration-testing.md`).

## Documentation generation (optional)

```
go doc ./<package>/...
```

Used to verify GoDoc completeness during Phase E self-audit; not part of any gate. Failures here do not block; missing GoDoc on exported symbols is caught by the audit checklist.

## Notes

- Always pin to `-count=1` on unit and integration runs to defeat the test result cache. Cached results do not satisfy a gate.
- The change scope passed to `/apply` and `/sync-check` is the package set affected by the phase. Run the commands above scoped to those packages, not the whole module, unless the project conventions say otherwise.
- Deprecated runners (`gotestsum` etc.) are project preferences — if the project uses one, prefer it; this pack does not require it.

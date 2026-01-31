# Echo router conventions (Go HTTP library)

Cited by `urn:ordin:default:skills:quality:codegen` (Phase B handler generation) and `urn:ordin:default:skills:quality:testgen`. This file carries the router-specific shape of an HTTP handler. The Go language mechanics it sits on — file layout, GoDoc rules, build commands — are the active **stack** pack's, not this file's.

## Blessed router

**`github.com/labstack/echo/v4`** is the blessed HTTP router. The concrete version is pinned by the consuming project's `go.mod`; do not invent or upgrade a version inside generated code.

## Handler signature

Every HTTP handler is an `echo.HandlerFunc`:

```go
func (h *Handler) CreateOrder(c echo.Context) error {
    // 1. bind + validate the request at the boundary
    // 2. call the use case with c.Request().Context()
    // 3. return c.JSON(status, body) or a typed *echo.HTTPError
}
```

- Propagate `c.Request().Context()` into every downstream call — never `context.Background()` in a handler.
- Return errors as `*echo.HTTPError` with the status code and error string the spec's Public Interface section names character-for-character; do not leak internal error text to the client.
- Register routes on an `*echo.Group` per bounded context; the method + path must match the spec's `@Router` annotation exactly.

## Swag annotation flavour

Every Echo handler carries Swag annotations matching the spec's API contract character-for-character (the annotation **mechanics** — required tags, GoDoc placement — remain the active stack pack's `annotation-conventions.md`; this file fixes only that the annotations sit on an Echo handler):

- `@Router` — exact method + path matching the spec's Public Interface section, as registered on the Echo group.
- Request/response models reference the Phase 2C shared types, not inline structs.

## Where this pack stops

This pack owns the router choice and its handler/annotation shape. It does **not** own: the Go file layout, the build/lint/test commands, the integration-test container tooling (that is the active `library/go/testcontainers` pack), or the test strategy (the active `testing` pack). Swapping this pack for a different router pack changes the handler shape only.

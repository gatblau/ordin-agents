# Testcontainers setup (Go integration-test tooling)

Cited by `urn:ordin:default:skills:quality:testgen` and `urn:ordin:default:skills:quality:codegen` (Phase C). This file carries the container bring-up idiom for the **testcontainers-go** tool. It does not carry the test strategy (the active testing pack's `boundaryRule`) nor the Go test mechanics (the active stack pack's `//go:build integration` constraint and file naming).

## Blessed tool

**`github.com/testcontainers/testcontainers-go`** is the blessed integration-test container library. The concrete version is pinned by the consuming project's `go.mod`; do not invent a version. Use the engine-specific module (e.g. `.../modules/postgres`) where one exists.

## Container bring-up

Bring up each integrating service as a real black box:

```go
//go:build integration

package <component>

import (
    "context"
    "testing"

    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

// startPostgres returns a started container plus a teardown.
// 1. Uses the SAME image and version the project uses elsewhere — read it from
//    the project's docker-compose, Helm chart, or other pinned source. Do not
//    invent a version.
// 2. Waits on a real readiness signal (log line, port open) via wait.For…
// 3. Returns a teardown the caller defers.
func startPostgres(t *testing.T) (string, func()) {
    // ...
}
```

- Defer teardown in the caller; never leak a container between tests.
- Wait on a genuine readiness signal, not a fixed sleep.

## Where a real service cannot be containerised

If the dependency genuinely cannot be containerised (proprietary appliance, third-party SaaS, hardware peripheral, licensed image you cannot ship), materialise a **stub service** that honours the same wire contract — same protocol, same surface, deterministic responses — and record the stub's contract source in a comment on the stub type.

## Where this pack stops

This pack owns the container tool and its bring-up idiom. It does **not** own: how many integration tests or on which boundaries (the active `testing` pack's `boundaryRule`), the Go build constraint and file naming (the active stack pack's `integration-testing.md` mechanics), or the unit-coverage threshold. Swapping this pack for a different tool pack (e.g. dockertest) changes the bring-up idiom only.

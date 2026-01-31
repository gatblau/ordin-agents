# Observability conventions (Go)

Cited by `urn:ordin:default:skills:release:runbookgen` extraction signals. The workspace's runbookgen produces a generic operational runbook; this file lists the Go-specific signals to extract from a service.

## Signals to extract

### Lifecycle

- **Startup** — `main.go` initialisation order, dependency wiring, fail-fast behaviour on missing config.
- **Shutdown** — signal handlers (`syscall.SIGTERM`, `syscall.SIGINT`), graceful shutdown timeouts, context cancellation chains.
- **Health endpoints** — typically `/healthz` (liveness) and `/readyz` (readiness). Read the actual route registration; do not assume.

### Resource lifecycle

- **Goroutines** — long-running goroutines started in `main` or in service constructors. Each carries a `context.Context` and exits when the context is cancelled. Goroutines started without a cancellation path are reported as a leak risk in the runbook's Risks section.
- **Connection pools** — DB pool size (pgx, database/sql), HTTP client pool, NATS connection options (max reconnects, reconnect wait). Exhaustion behaviour is operationally relevant.
- **Timeouts** — every external call (HTTP client, DB query, message-bus publish) has a deadline derived from the spec's latency targets. Calls without a deadline are flagged.

### Concurrency hazards

- Unbounded retry loops without exponential backoff.
- Goroutine leaks on cancelled contexts.
- Missing timeouts on HTTP clients.
- Cascading failures when a dependency is down (no circuit breaker, no bulkhead).
- Channel sends without a select on `ctx.Done()`.

These are reported in the runbook's *Patterns that commonly bite operators* section. Only include patterns that can be cited in code; do not pad the section.

## What to read

| Signal | Where to find it |
|---|---|
| Signal handlers | `main.go`, look for `signal.Notify` |
| Connection pools | Constructors of `pgxpool.Pool`, `*sql.DB`, `*nats.Conn`, `*http.Client` |
| Timeouts | `context.WithTimeout`, `context.WithDeadline`, transport configs |
| Health endpoints | Router registration in `main.go` or `wire.go` |
| Goroutine starts | `go func()` in `main.go` and service constructors |
| Retry loops | Functions that implement retry; presence of `time.Sleep` inside a loop is a smell |

## Forbidden

- Inventing endpoints. If the runbook says `GET /healthz` returns 200, that route must exist in the code.
- Inferring goroutine count or pool size from documentation; read the constructor.
- Reporting concurrency hazards as findings without a code citation. The runbook's claims are evidence-tagged the same way design and spec documents are.

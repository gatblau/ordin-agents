# Pattern — Client-side resilience

**Required.** `when:` a service calls another service.

## Problem

In a synchronous mesh, a caller's fate is tied to its downstreams. If a downstream
is slow, the caller's request threads block on it; if enough do, the caller runs out
of connections or threads and starts failing requests it could otherwise serve. One
slow service becomes a mesh-wide outage — a coupling cascade. Naive retries make it
worse by multiplying load on the struggling downstream.

## Solution

Every cross-service call carries **all four** controls. The first three are
non-negotiable; the fourth isolates blast radius.

1. **Timeout.** No call waits forever. Each call has a deadline derived from the
   inbound request's remaining budget, so a deep chain cannot exceed the caller's own
   timeout. A call that exceeds its deadline fails fast as a timeout, not a hang.
2. **Retry budget.** Retries are bounded — a small maximum count *and* a ceiling on
   the fraction of traffic that may be retries — with exponential backoff and jitter.
   Retry only idempotent operations (`./idempotent-write.md`). A budget prevents a
   retry storm from amplifying a downstream's overload.
3. **Circuit breaker.** Per upstream, track recent failures. When they cross a
   threshold the breaker **opens** and calls fail immediately without hitting the
   upstream, giving it room to recover; after a cool-down the breaker goes
   **half-open** and lets a probe through before **closing** again. The breaker's
   state is exported (`../observability/required-signals.md`: `circuit_breaker_state{upstream}`).
4. **Bulkhead.** Cap the concurrency or connection pool *per upstream* so one slow
   upstream cannot consume the caller's entire budget and starve calls to healthy
   upstreams (`bulkhead-isolation`, recommended).

## Shape (language-neutral)

```
result = client.call(upstream, request,
                     timeout    = deadline_from(inbound_budget),
                     retry      = bounded(max_attempts, max_retry_fraction, backoff=exp_jitter),
                     breaker    = per_upstream(failure_threshold, cooldown),
                     bulkhead   = per_upstream(max_concurrency))
```

## Rules

- A cross-service call with no timeout, no retry budget, or no circuit breaker is a
  resilience-omission defect (`RR_NO_TIMEOUT`); the `synchronous-call-chain-without-timeout`
  pattern is prohibited.
- Per-hop timeouts are derived from the inbound request's remaining budget so the
  whole chain stays inside the caller's deadline.
- Retry only idempotent calls; a non-idempotent retry double-applies the effect.

## What this pack does not specify

The **concrete client, breaker implementation, and pool mechanics** are stack-pack
concerns — referred to here only as "a resilient service-client abstraction"
(manifest `approvedLibraries`).

# Pattern — Module facade

**Required.** `when:` a module is consumed by another module.

## Problem

If any module can call any other module's internals, every module depends on
every other module's implementation detail. The boundary that makes a monolith
*modular* — and a future module-to-service extraction local — disappears.

## Solution

Each module exposes exactly one **published facade**: a narrow, stable surface
that is the *only* entry point other modules may use. Everything else is internal
and invisible across the boundary.

1. A module is split into a **published** part (the facade interface + boundary
   DTOs) and an **internal** part (entities, persistence, logic). Only the
   published part is importable by other modules.
2. Cross-module calls go through a facade method. The facade accepts and returns
   **boundary DTOs**, never the module's internal entities — so the internal
   model can change without breaking callers.
3. The facade is the contract: it is versioned in spirit (changes are reviewed as
   a boundary change), and it is where cross-module observability is recorded
   (`../observability/required-signals.md`).

## Shape (language-neutral)

```
module orders:
  published/
    facade   : PlaceOrder(cmd) -> OrderSummary    # boundary DTOs only
  internal/
    entity   : Order, LineItem                    # never crosses the boundary
    store    : orders tables (owned)              # only orders writes them
```

## Rules

- The facade is the **only** cross-module entry point. No other module imports
  anything under `internal/`.
- Facade signatures use boundary DTOs, not internal entities — returning an
  internal entity leaks the model (apply `anti-corruption-layer.md` if you are
  the consumer).
- Keep the facade narrow: expose the behaviours other modules need, not the
  module's whole surface.
- A facade call is a direct in-process call. It is not a remote call and needs no
  retry/timeout/circuit-breaker — those belong to the request/response
  architecture, not here.

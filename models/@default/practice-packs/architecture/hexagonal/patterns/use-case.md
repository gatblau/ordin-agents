# Pattern — Use-case application service

**Required.** `when:` a driving adapter invokes domain behaviour.

## Problem

A driving adapter (an HTTP handler, a CLI command, a message consumer) must trigger
domain behaviour. If the adapter reaches directly into entities and orchestrates the
work itself, business logic leaks into the adapter: it cannot be tested without the
transport, and the same flow is re-implemented for every driving adapter.

## Solution

The core offers a **use-case port** — an application service that names one unit of
domain behaviour as an inbound capability. A driving adapter translates its input to
the use case's domain request, invokes the use case, and translates the result back.
The use case orchestrates entities and driven ports; the adapter stays thin.

1. The core defines an inbound port per use case: a single operation taking a domain
   request and returning a domain result or raising a domain error.
2. The use-case implementation orchestrates the domain — loading aggregates through
   driven ports (`repository-port.md`), applying rules, and saving results.
3. Each driving adapter maps its transport input to the domain request and the domain
   result back to its transport output (`../boundary/dto-mapping.md`).

## Shape (language-neutral)

```
core/
  defines  PlaceOrderUseCase  { execute(PlaceOrderRequest) -> OrderResult }   # inbound port
  implements PlaceOrderUseCase using RepositoryPort + domain rules

adapters/http/    -> translates request body  -> PlaceOrderRequest  -> execute(...)
adapters/cli/     -> translates arguments      -> PlaceOrderRequest  -> execute(...)
```

## Rules

- One use case is **one inbound port** with **one operation** expressed in domain
  terms; it carries no transport type in or out.
- All orchestration of entities and driven ports lives in the use case, **not** in
  the driving adapter. The adapter only translates and delegates.
- A use case depends only on **ports** (driven and its own inbound port) and domain
  types — never on a concrete adapter.

## What this pack does not specify

The **transport, routing, serialization, and dependency container** are stack-pack
concerns. This pack names only the inbound-port shape and the thin-adapter rule.

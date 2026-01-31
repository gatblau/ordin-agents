# Pattern — Anti-corruption layer

**Required.** `when:` two modules have divergent models and one must consume the
other.

## Problem

Module A needs data from module B, but B's model does not match A's. If A adopts
B's types directly, B's model leaks into A: A now breaks whenever B's internal
shape changes, and A's domain language is polluted by B's concepts.

## Solution

The **consumer** places a thin translation layer at its own boundary that maps
the producer's facade DTOs into the consumer's own model. The producer is never
asked to change; the consumer owns the translation.

1. The consumer calls the producer's published facade (`module-facade.md`) and
   receives the producer's boundary DTOs.
2. An **anti-corruption layer (ACL)** inside the consumer maps those DTOs into the
   consumer's own domain types, dropping fields it does not need and renaming to
   its own ubiquitous language.
3. The consumer's core logic sees only its own model. When the producer's facade
   evolves, only the ACL changes.

## Shape (language-neutral)

```
module billing (consumer):
  acl/
    fromOrders : orders.OrderSummary -> billing.Billable   # translation lives here
  internal/
    logic       : operates on billing.Billable only         # never sees orders types
```

## Rules

- The ACL belongs to the **consumer**, at the consumer's boundary. The producer
  does not bend its model to suit a consumer.
- The consumer's core never references the producer's types directly — only the
  ACL does.
- An ACL maps *facade DTOs*, not the producer's internals. If you find yourself
  needing the producer's internals to translate, the facade is too thin — extend
  the facade, do not bypass it.

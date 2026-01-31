# Boundary — DTO ↔ domain-entity mapping

The shape contract for translating external data structures to and from domain
entities at the adapter edge. Abstract — it names a rule, not a wire schema or a
serialization format.

## The rule

A **domain entity never carries a transport type.** Every adapter — driving or
driven — translates the external **DTO** (the request body, the stored row, the
message payload) into a **domain entity** on the way *in*, and translates the domain
entity back into a DTO on the way *out*. The translation lives at the adapter, on the
outside of the boundary; the core only ever sees domain entities.

## Why

- The core stays pure: it depends on no serialization, ORM, or transport type, so it
  is testable with no external system and is unaffected by a wire-format change.
- The external contract can evolve independently of the domain model: a new DTO field
  or a renamed wire attribute is absorbed in the mapper, not in the core.
- One place owns the translation, so a malformed external shape is rejected at the
  edge, never deep in a use case.

## Direction

| Direction | Adapter kind | Translation |
|---|---|---|
| **Inbound** | Driving adapter | external DTO → domain request/entity; reject or default missing/invalid fields *before* the core is called. |
| **Outbound** | Driven adapter | domain entity → external DTO (stored shape, request payload) at the moment of the external call. |
| **Result** | Driving adapter | domain result → external DTO (response body) on the way back out. |

## Rules

- The **mapper lives in the adapter layer**, never in the core. The core defines the
  domain entity; the adapter owns the DTO and the mapping.
- A domain entity exposes **no** field whose type is a transport, ORM, or framework
  type. If such a field is needed at the edge, it lives in the DTO only.
- Validation that a DTO can become a valid domain entity happens **at the boundary**,
  before the core runs; the core may then assume well-formed domain inputs.
- Mapping is **total and explicit** — every DTO field maps to a domain concept or is
  deliberately dropped; no field silently crosses untranslated.

## What this pack does not specify

The **serialization library, schema/IDL, and field codecs** are stack-pack concerns.
This pack names only the translate-at-the-edge rule and the no-transport-type-in-core
invariant.

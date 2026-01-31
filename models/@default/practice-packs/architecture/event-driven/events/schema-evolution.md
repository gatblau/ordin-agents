# Event interface — schema evolution

How an event's payload is allowed to change over time. The governing rule is
**backward-compatible-only** within a major schema version; a breaking change is
a new major version on a new topic.

## Backward-compatible changes (same major version)

Allowed within `v<n>` — an old consumer keeps working against a new producer:

- **Add an optional field** with a sensible default when absent.
- **Add a new event type** on its own topic.
- **Widen** a field's accepted range where consumers already tolerate it.

A consumer must **ignore unknown fields** rather than reject them, so a producer
can add optional fields without coordinating a fleet-wide upgrade.

## Breaking changes (new major version)

These require a new `v<n+1>` topic — never an in-place edit of `v<n>`:

- Removing or renaming a field.
- Changing a field's type or semantics.
- Making a previously-optional field required.

### Migration via upcasting

**Recommended** (`event-version-upcasting`) `when:` an event schema evolves and
old-version events remain in the stream.

1. Publish the new event on `…​.v<n+1>`. Keep `…​.v<n>` flowing until consumers
   have migrated.
2. A consumer that needs to read history defines an **upcaster**: a pure function
   that transforms a `v<n>` event into the `v<n+1>` shape (supplying defaults for
   new fields, mapping renamed ones).
3. The consumer applies the upcaster on read, so its core logic sees only the
   latest shape. Old events are never rewritten in place.
4. Retire `v<n>` only once no producer emits it and no replay window still
   references it.

## Rules

- The major version in the topic name (`../events/topic-naming.md`) and the
  envelope `type` move together. A `v2` topic never carries `v1`-shaped payloads.
- Schema evolution is a **producer** decision the consumer must tolerate;
  consumers never demand a producer break compatibility.
- The **serialisation format and registry** (how bytes are encoded and where
  schemas are stored) are stack-pack / platform concerns, not specified here.

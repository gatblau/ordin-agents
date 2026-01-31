# API interface — pagination

The shape contract for list endpoints. Every endpoint that returns a collection
paginates the **same way**, so callers iterate uniformly and a large result set can
never return unbounded. This is an abstract *shape* contract — parameter and field
presence and meaning — not a wire schema.

## Cursor pagination

The mesh standardises on **cursor** pagination (an opaque continuation token), not
offset pagination, because cursors are stable under concurrent inserts and do not
degrade on deep pages.

### Request parameters

| Parameter | Meaning |
|---|---|
| `cursor` | Opaque continuation token from a previous response's `nextCursor`. Absent on the first page. |
| `limit` | Maximum number of items to return in this page. The service applies a hard ceiling; a request above it is clamped, not honoured. |

### Response fields

| Field | Meaning |
|---|---|
| `items` | The page of results — at most `limit` entries. |
| `nextCursor` | The cursor for the next page, or absent/null when this is the last page. |

## Rules

- **Always bounded.** A list endpoint never returns the whole collection; the absence
  of `limit` applies the default page size, not "all". This is what keeps one request
  from fanning into an unbounded response (`../anti-patterns.md`, chatty calls).
- **Opaque cursor.** The `cursor` is an opaque token; clients pass it back unchanged
  and never construct or parse it.
- **Stable ordering.** Pagination is over a deterministic sort key so a cursor names a
  stable position across requests.

## What this pack does not specify

The **cursor encoding, default and maximum page sizes, and storage-level keyset query**
are stack-pack concerns. This pack names the parameter and field contract, not the
mechanism that produces the cursor.

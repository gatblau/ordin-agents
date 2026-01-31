# API interface — error envelope

The shape contract for error responses. Every service in the mesh returns errors in
**one** envelope, so callers parse failures uniformly and an external client never
sees a service's internal error shape. This is an abstract *shape* contract — field
presence and meaning — not a byte layout or serialisation format.

## Envelope (required fields)

Every non-2xx response carries an error envelope with at least these fields.

| Field | Meaning |
|---|---|
| `code` | A stable, machine-readable error code (e.g. `validation_failed`, `not_found`, `upstream_timeout`). Callers branch on this, not on the message string. |
| `message` | A human-readable description, safe to surface. It carries no secrets, stack traces, SQL, or internal identifiers (`../anti-patterns.md`). |
| `traceId` | The distributed-trace id for the failed request, so an operator can find the trace from the error a client reports (`../observability/required-signals.md`). |

An optional `details` array may carry field-level validation errors (`{ field, code }`),
but the three fields above are always present.

## Mapping to status codes

The envelope rides on top of the status-code map (`../api/versioning.md`). The `code`
is finer-grained than the HTTP status: a single `400` may carry
`code: validation_failed` or `code: malformed_body`.

## Rules

- **No internal-state leakage.** The `message` never contains a stack trace, a SQL
  fragment, an upstream's raw error, or a secret. An upstream `5xx` is translated to
  this service's own `503`/`504` envelope, not forwarded verbatim.
- **`code` is stable.** It is part of the API contract; renaming a code is a breaking
  change (`../api/versioning.md`) and increments the major.
- **`traceId` is always present**, even on a `5xx`, so a client error report is
  traceable.

## What this pack does not specify

The **serialisation format, framework error middleware, and code registry storage**
are stack-pack concerns. This pack names the envelope's required fields and their
meaning, not the mechanism that emits them.

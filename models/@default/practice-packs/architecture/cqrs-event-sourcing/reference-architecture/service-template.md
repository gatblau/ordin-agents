# Reference architecture — service template

A language-neutral skeleton for a CQRS + event-sourced service. It names
**directories and responsibilities**, never a language, framework, or store
product. A stack pack maps these directories onto its file layout; the skill
globs in `skillActivations` (`**/aggregates/**`, `**/projections/**`,
`**/events/**`) are keyed to this shape.

## Directory shape

```
<service>/
  aggregates/        # write side — one folder per aggregate type
    <aggregate>/
      commands        # command definitions  (<Aggregate><Imperative>)
      aggregate       # decide(state, command) -> events  (pure)
      apply           # apply(state, event)   -> state     (the fold)
  events/            # the event types this service appends, plus upcasters
    <event>.vN
    upcasters         # pure vN -> vN+1 transforms (events/upcasting.md)
  projections/       # read side — one folder per read model
    <read-model>/
      project         # apply(model, event)   -> model
      checkpoint      # (projection-id, stream-position) store
      queries         # query definitions     (<ReadModel><Question>)
  ports/
    event-store       # the abstract event-store client (approvedLibraries)
```

## Responsibilities

- **`aggregates/`** — the write side. Each aggregate folds its stream, decides on a
  command, and emits events (`../patterns/aggregate-command-handler.md`). It never
  serves a query.
- **`events/`** — the immutable event vocabulary and the upcasters that keep old
  versions readable (`../events/upcasting.md`). Nothing here is ever rewritten in
  place.
- **`projections/`** — the read side. Each projection consumes the stream from a
  checkpoint (`../broker/projection-consumer.md`), maintains a disposable query
  model, and is rebuildable from zero (`../patterns/projection-rebuild.md`).
- **`ports/event-store`** — the seam to "an event-store client abstraction". The
  concrete driver, serialisation, and checkpoint storage are the stack pack's.

## Rules

- The write side (`aggregates/`, `events/`) and the read side (`projections/`)
  share **only** the event stream. A projection never imports an aggregate's state
  type, and an aggregate never reads a projection.
- `decide`, `apply`, `project`, and the upcasters are **pure** functions of their
  inputs — this is what makes a projection rebuild and an aggregate reload
  deterministic.
- Directory names are **conventions** this pack relies on for skill activation; a
  stack pack may translate them, but the write/read separation must survive the
  translation.

# ladder — deriving, ordering and cutting the concept ladder

The ladder is the spine of the site. Each rung teaches one idea and relies only on ideas taught on lower rungs, so a reader who starts at rung 1 and reads in order never meets a term they have not been taught. This reference covers how `docsgen` derives the concept list (step 4), orders it (step 6) and cuts it into rungs.

## Deriving the concept list (step 4)

A concept is one of the **system's own ideas** — a noun the system reasons about, or an action it performs on one. Draw candidates from three sources, and record the evidence for each (the traceability record in `evidence.md`):

- **Source** — the names the code gives things: exported types, the entities behind the data model, the verbs on the public surface (routes, commands, message subjects). A recurring noun in the code is a strong concept signal.
- **Design** — the problem the system solves and the vocabulary the design uses for it. The design usually states the first rung's idea outright: what the system is for.
- **Specification** — the contracts and the domain terms the specification defines. A glossary term is a ready-made concept with a ready-made definition.

Prefer the system's own word for an idea over a generic one. If the code, design and specification each name the same idea differently, choose the word the reader will meet most often in the system itself, and note the synonyms in the concept's first definition.

Discard a candidate that is an implementation incidental rather than an idea the reader needs — a helper, a serialisation detail, a framework class the system merely uses. The test is whether a newcomer must understand it to understand the system, not whether it appears often in the code.

## Ordering the list (step 6)

Place a concept **after every concept its definition depends on**. Concept B depends on concept A when B cannot be defined without using A. The result is a dependency order: rung 1 depends on nothing, and each later rung depends only on earlier ones.

Two heuristics shape a good order:

- **Problem before parts.** The first rung states the problem the system solves, in the reader's terms, before any component is named. A reader who knows what the system is for can place everything that follows.
- **Vocabulary before behaviour before structure.** Teach what the system's core nouns mean, then what happens to them, then how the parts fit together. A structural diagram lands only once the reader knows the things it connects.

## Breaking a cycle

Two concepts are **mutually dependent** when each is used in the other's definition. Break a two-concept cycle by introducing **both on one rung**, named as a pair and defined together — the reader meets them at once rather than being sent forward.

A cycle spanning **three or more** concepts is not a teaching problem to smooth over; it signals the concepts were cut in the wrong place. Stop with `DOC_LADDER_CYCLE` and name the members, so the operator can recut them rather than accept a rung that teaches four interlocking ideas at once.

## Cutting into rungs and depth

Each concept, or each mutually-dependent pair, becomes one rung. The `depth` argument sets how many rungs the walkthrough tier adds:

- `minimal` — the problem, the core concepts, and one end-to-end walkthrough.
- `standard` — the above plus how the parts compose.
- `full` — the above plus one walkthrough per principal journey the design names.

When the rung count exceeds the pack's `sizeThreshold`, present the ladder to the operator and wait (step 7). The operator sees the whole ladder — every rung's title and its `enables` sentence — before a single page is drafted, and may cut, merge or reorder it. A declined ladder ends the run with no file written.

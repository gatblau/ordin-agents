# HLD folder layout (Standard lane)

Canonical layout for an HLD produced in folder form. Numbered prefixes fix reading order and give `sync-check`, `designgen`, and `specgen` stable filenames to target. Each child file carries the HLD's current `revision:` and the Mode banner.

```
docs/design/<topic>/
├── README.md                # Mode banner · revision: · one-paragraph orientation · index of children
├── 00-overview.md           # Summary · Motivation · Goals · Non-goals · Glossary
├── 01-context.md            # System context diagram (mermaid) · External actors · Neighbouring systems
├── 02-architecture.md       # System architecture (mermaid) · Component responsibilities
├── 03-sequences.md          # Principal sequence diagrams (mermaid) · Trigger · Result · Error posture
├── 04-domain.md             # Domain Model · Data Lifecycle
├── 05-tech-stack.md         # Tech Stack table · one-line rationale per row
├── 06-regulatory.md         # Regulatory and Compliance Context · "N/A — non-regulated" if applicable
├── 07-cross-cutting.md      # Cross-cutting Concerns table (15 rows) · Non-functional Requirements
├── 08-interfaces.md         # External interfaces — names and shapes only, no wire schemas
├── 09-decisions.md          # Architectural Decisions (ADR entries) — append-only
├── 10-risks.md              # Risks · Alternatives considered · Dependencies · Rollout and Rollback
└── 99-changelog.md          # Append-only HLD changelog (see hld-changelog-format.md)
```

## Per-child responsibilities

| File | Owns | Bubbles up from `/spec` when |
|---|---|---|
| `README.md` | Mode banner, current `revision:`, `Last updated:`, one-paragraph orientation, indexed link list to children with a one-line "what's in it" per child. | Never edited directly by `/spec` — `revision:` and `Last updated:` are bumped by the HLD-impact-pass after any child edit. |
| `00-overview.md` | Summary, Motivation, Goals, Non-goals, Glossary. | `/spec` introduces a glossary term not present here (D-HLD-1). Goals / Non-goals are *not* auto-amended; a goal change is escalated, not silently routed. |
| `01-context.md` | System context diagram, external actors, neighbouring systems. | `/spec` discovers a new external system or actor not currently in the context diagram. |
| `02-architecture.md` | System architecture diagram, component responsibilities. | `/spec` discovers a component boundary moves, splits, merges, or a new component appears. |
| `03-sequences.md` | Principal sequences (mermaid). | `/spec` discovers a new principal sequence or a material change to an existing one (e.g. a new fan-out, a new external call, a new failure mode). |
| `04-domain.md` | Domain Model, Data Lifecycle. | `/spec` introduces a domain entity not present, or names a lifecycle state not in the model. |
| `05-tech-stack.md` | Tech Stack table. | `/spec` introduces a new tech-stack member (a library swap is recorded as an ADR in `09-decisions.md`, not a silent row change). |
| `06-regulatory.md` | Regulatory and Compliance Context table. | `/spec` surfaces a regulatory obligation discovered during specification. |
| `07-cross-cutting.md` | Cross-cutting Concerns table, Non-functional Requirements. | `/spec` introduces a new cross-cutting policy that applies across all components (e.g. a new tenancy boundary, a new retry policy, a new signing scheme). |
| `08-interfaces.md` | External interfaces — names and shapes only. | `/spec` introduces a new externally-visible interface (route, NATS subject, CLI command). Wire-level detail stays in `/spec`. |
| `09-decisions.md` | Architectural Decisions (ADR entries). Append-only. | `/spec` discovers an ADR-shaped trade-off being made inside a component spec — promoted here with Decision / Context / Consequences / Alternatives. |
| `10-risks.md` | Risks, Alternatives considered, Dependencies, Rollout and Rollback. | `/spec` surfaces a new risk (a discovered failure mode, a dependency the design overlooked). |
| `99-changelog.md` | Append-only HLD changelog. | Every edit to any child file appends one line here, per `hld-changelog-format.md`. |

## README.md skeleton

```markdown
# <Feature / Problem Name> — High-Level Design

> **Mode:** {interview | draft | code-evidence}
> **Generated from:** <source>
> **Revision:** <semver>
> **Last updated:** <ISO date>

## Orientation

<One paragraph. What this design covers, who it is for, what the next move is.>

## Contents

- [00 — Overview](./00-overview.md) — Summary, Motivation, Goals, Non-goals, Glossary.
- [01 — Context](./01-context.md) — System context diagram, external actors, neighbouring systems.
- [02 — Architecture](./02-architecture.md) — System architecture diagram, component responsibilities.
- [03 — Sequences](./03-sequences.md) — Principal sequence diagrams.
- [04 — Domain](./04-domain.md) — Domain Model, Data Lifecycle.
- [05 — Tech stack](./05-tech-stack.md) — Tech choices and rationale.
- [06 — Regulatory](./06-regulatory.md) — Compliance obligations and how the design addresses them.
- [07 — Cross-cutting](./07-cross-cutting.md) — Cross-cutting Concerns table, NFRs.
- [08 — Interfaces](./08-interfaces.md) — External interfaces (names and shapes only).
- [09 — Decisions](./09-decisions.md) — Architectural Decision Records (ADRs).
- [10 — Risks](./10-risks.md) — Risks, Alternatives, Dependencies, Rollout/Rollback.
- [99 — Changelog](./99-changelog.md) — HLD revision history.
```

## Folder-vs-single-file decision

The decision comes from `triage`:

- **Standard lane** ⇒ folder form. The change touches enough surface that splitting by topic helps readability and `sync-check` targeting.
- **Trivial / Local lane** ⇒ single-file form. The work is bounded to one component and one or two concerns; the overhead of twelve files is not justified.

`designgen` infers `hld-form` from the `triage` block in context. When the user invokes `/design` without a prior `triage` (i.e. truly greenfield work), `designgen` prompts: "Is this work bounded to a single component / concern (single-file) or spans multiple components / concerns (folder)?" The user's answer fixes the shape.

## When to migrate a single-file HLD to folder form

When the HLD grows past ~800 lines, or when more than three child-file sections (architecture, sequences, ADRs, regulatory) have grown past ~150 lines each. Migration is a manual rewrite — `designgen` does not auto-split. Until migration, the single file remains canonical; `/spec`'s HLD-impact-pass continues to amend it inline.

# High-Level Design (HLD) template

The HLD owns *what we are building, why, and how the parts fit together at a system level*. Wire-level detail — exact field types, error code strings, JSON schemas, retry counts, Gherkin scenarios — belongs in `/spec` (LLD), not here.

Every section is mandatory. Write "N/A — <reason>" for sections that genuinely do not apply. Use the active locale throughout (see `urn:ordin:default:rules:layer:output-language`).

## Two output shapes

The HLD is produced in one of two shapes, decided by `triage` (see `@default/skills/quality/triage/references/classification-rubric.md` §Compound rules):

- **Folder form** (Standard lane) — one folder `docs/design/<topic>/` with a `README.md` index and numbered child files. Canonical layout in `hld-folder-layout.md`. Each child file carries a `revision:` header that matches the HLD's current revision.
- **Single-file form** (Trivial / Local lane) — one file `docs/design/<topic>.md` with all sections inline.

Both shapes carry the same content. The section list below is canonical; in folder form it is distributed across child files per `hld-folder-layout.md`.

## Mandatory preamble (every HLD)

```markdown
> **Mode:** {interview | draft | code-evidence}
> **Generated from:** <problem statement | inline context | code paths> <if code-evidence: list the scanned paths>
> **Revision:** <semver>  <!-- bumps on every edit; initial draft is 0.1.0 -->
> **Last updated:** <ISO date>
```

The Mode banner declares how the HLD was generated. The `revision:` header is bumped on every edit (direct or spec-driven), and the `Last updated:` date tracks the most recent change.

## Section list (canonical order)

```markdown
# <Feature / Problem Name>

> <preamble: Mode, Generated from, Revision, Last updated>

## Summary
<Two to four sentences. What this design covers and why it exists. Non-goals noted briefly.>

## Motivation
<The current state, the pain or gap, and why doing nothing is not acceptable. Concrete — name users, systems, or incidents where possible.>

## Goals
- <Observable outcome 1>
- <Observable outcome 2>

## Non-goals
- <What this explicitly does not address, and why (brief).>

## Glossary
| Term | Definition | Example |
|---|---|---|
| <Domain noun> | <Definition> | <Concrete example value> |

## System Context
<A mermaid context diagram (C4-style level 1, or equivalent) showing the system as a single box surrounded by external actors and neighbouring systems. Label every external interaction with protocol + auth.>

### External actors and neighbouring systems
- **<Actor / system name>** — <one-line role>. **Interaction:** <protocol + auth + direction>.

## System Architecture
<A mermaid component diagram showing the system's internal structure — components, their responsibilities, and the principal interactions between them. Names and interactions only; no wire detail. If the system is one component, say so and skip the inter-component arrows.>

### Component responsibilities
- **<ComponentName>** — <one-paragraph responsibility>. Owns: <data / interfaces>. Depends on: <other components>.

## Principal Sequences
<One mermaid sequence diagram per major flow. At minimum the golden path. Logical, not wire-level — show the *order of operations and decision points*, not exact payloads.>

### Sequence: <name>
```mermaid
sequenceDiagram
  ...
```
- **Trigger:** <who/what starts this sequence>
- **Result:** <observable outcome>
- **Error posture:** <what happens on the principal failure modes — retry, fail fast, alert, escalate>

## Domain Model
<For each entity: its purpose, key fields (without committing to data types yet — that is specgen's job), relationships to other entities, and lifecycle (created, updated, deleted, archived, etc.).>

## Data Lifecycle
<Where data originates, where it is stored, how long it is retained, who can read or modify it. Note any compliance, privacy, or multi-tenancy constraint.>

## Tech Stack
<One row per layer. Choose committed defaults; record alternatives the user rejected as one-line rationale.>

| Layer | Choice | Rationale (one line) |
|---|---|---|
| Language | | |
| Framework / runtime | | |
| Datastore | | |
| Message broker / queue | | |
| Deployment substrate | | |
| Observability (logs / metrics / traces) | | |
| Signing / crypto | | |
| Build / test toolchain | | |

## Regulatory and Compliance Context
<Standards, jurisdictions, and obligations the design must satisfy. Write "N/A — non-regulated" if it truly does not apply.>

| Obligation | Source | How the design addresses it |
|---|---|---|

## Cross-cutting Concerns
<For each concern: state one of "applies — <brief policy>", "does not apply — <why>", or "project default — see <reference>". All must be stated explicitly; do not omit.>

| Concern | Stance |
|---|---|
| Authentication | |
| Authorisation | |
| Logging | |
| Metrics | |
| Tracing | |
| Rate limiting | |
| Pagination | |
| Input validation | |
| Error handling / envelope | |
| Configuration | |
| Health checks | |
| Migrations | |
| Graceful shutdown | |
| CORS | |
| Multi-tenancy | |

## Non-functional Requirements
- **Performance targets:** <latency, throughput, memory>
- **Scale:** <expected load, growth curve>
- **Availability:** <SLO, failure modes tolerated>
- **Security posture:** <authn, authz, secret handling, threat model summary>

## Interfaces (external)
<APIs, NATS subjects, CLI commands, file formats this feature exposes to the outside world. **Names and shapes only — no JSON schemas, no error envelopes, no field types. Those belong in `/spec`.** Mark each as "new" or "extends existing".>

## Architectural Decisions
<ADR-shaped entries. Append-only — once recorded, decisions are amended via new entries, not by overwriting.>

### ADR-NNN: <title>
- **Decision.** <One sentence stating the committed choice.>
- **Context.** <What forced the decision — constraint, deadline, prior incident, regulatory driver.>
- **Consequences.** <What follows from the decision, both intended and accepted trade-offs.>
- **Alternatives considered.** <At least one, with a one-line reason it was rejected.>

## Assumptions
<Every reasonable default chosen during interview. One row per assumption.>

| ID | Area | Assumption | Rationale |
|---|---|---|---|

## Open Questions
<Items the HLD has not committed on. Mark each blocking / non-blocking. **Non-blocking is the default for HLD** — `/spec` will surface and resolve LLD-driven architectural questions via the HLD-impact-pass. A question is *blocking* only when specification cannot start without the answer.>

The `Plain-English` column is the layman-language phrasing the `/design` command surfaces first to developers reading the handoff — short sentence, no jargon, no unexpanded acronyms, no internal codenames, ending in a one-sentence trade-off.

| ID | Question | Plain-English | Options | Impact | Blocking? |
|---|---|---|---|---|---|

## Requirements
<Conditional section: present only when the active mode is `code-evidence` (see *Mode-driven sections* below).>

### Must preserve
| ID | Behaviour | Witness | Evidence |
|---|---|---|---|

### Observed but not required
| ID | Behaviour | Evidence |
|---|---|---|

### Drop candidates
| ID | Behaviour | Reason for dropping | Evidence (origin) |
|---|---|---|---|

### Gaps
| ID | Suspected behaviour | What is missing |
|---|---|---|

## Risks
<Things that could derail the feature during build or after deployment. Each risk gets one line: what it is, and what we will do about it.>

## Alternatives considered
<System-level alternatives — entire approaches rejected, not per-decision alternatives (those live in Architectural Decisions). At least one, with a one-line reason it was rejected. If genuinely none considered, state "None considered — <why>".>

## Dependencies
<Other features, teams, services, or infrastructure this design relies on.>

## Rollout and Rollback
<How the feature ships (dark launch, flag, full release) and how it is reverted if it goes wrong. For schema changes specifically, describe rollback semantics.>
```

## Rules for applying this template

- Write for a future reader who joins the team in six months. No in-jokes, no "as we discussed", no dangling references.
- Keep the Glossary, Domain Model, System Architecture, Principal Sequences, Tech Stack, and Architectural Decisions sections sharp — these are what `specgen` will lift directly and what the `sync-check` HLD↔spec rules police.
- Do not invent technical constraints the user did not state. Defaults go in Assumptions or in Architectural Decisions (with explicit rationale), not hidden in prose.
- Cross-cutting Concerns must have all rows present. An empty row is a bug — it means the interview missed something.
- **The HLD↔LLD line is sharp.** Wire-level detail belongs in `/spec`. If a section is tempted to include a JSON schema, an error code string, a retry count, or a Gherkin scenario, stop — that content goes in the LLD.
- **The HLD is a living document.** `/spec`'s HLD-impact-pass will amend it as LLD work reveals architectural questions. Every amendment bumps `revision:`, updates `Last updated:`, and (in folder form) appends a line to `99-changelog.md`.

## Mode-driven sections

Two parts of the template change shape with the active mode of the underlying skill.

### Mode banner (always present)

The banner at the top of the document declares the active mode and the input from which the design was generated.

| Mode | Banner reads | Generated-from |
|---|---|---|
| `interview` | `Mode: interview` | `problem statement` |
| `draft` | `Mode: draft` | `inline context` |
| `code-evidence` | `Mode: code-evidence` | `code paths` plus the list of scanned repo-relative paths |

### Requirements section (code-evidence only)

The *Requirements* section is present **only** when the active mode is `code-evidence`. It is omitted entirely in `interview` and `draft` modes — those produce forward-looking HLDs whose requirements live in product documents authored separately.

In `code-evidence` mode the four subsections are mandatory in the order shown (*Must preserve*, *Observed but not required*, *Drop candidates*, *Gaps*). Empty subsections write `_(none in initial draft)_` rather than being omitted; an empty section is informative.

The classification rules and evidence-tagging conventions for entries in this section live in `code-evidence-intake.md`. Do not duplicate them here.

### Revision header (always present)

The `revision:` SemVer header is part of the preamble in both shapes. It bumps:

- **Patch** (`0.1.0 → 0.1.1`) for clarifications, typo fixes, expanded prose with no semantic change, single-row additions to Glossary or Assumptions driven by `/spec`.
- **Minor** (`0.1.0 → 0.2.0`) for new ADR entries, new components in System Architecture, new tech-stack rows, new cross-cutting policy changes.
- **Major** (`0.1.0 → 1.0.0`) for first promotion from *Draft* to *Approved*, or for any change that invalidates an existing approved spec phase.

In folder form, every child file shares the HLD's current `revision:` — children are not versioned independently.

# Bubble-up rule — what goes to the HLD, what stays in the LLD

The HLD↔LLD boundary is the central discipline of the living-architecture model. This reference is the canonical, long-form statement of the rule that `hld-impact-pass.md` operates on.

## The one-line rule

**If the answer changes how the system is *shaped* or *governed*, it goes to the HLD. If it only changes how a known component *does its job*, it stays in the spec.**

## The table

| Finding shape during LLD work | Lives in HLD | HLD child file (folder form) |
|---|---|---|
| A component boundary moves, splits, merges, or a new component appears | **HLD** | `02-architecture.md` |
| A new external actor or neighbouring system enters scope | **HLD** | `01-context.md` |
| A new principal sequence or a material change to an existing one (new fan-out, new external call, new failure-mode path) | **HLD** | `03-sequences.md` |
| A new ADR-shaped trade-off (Decision · Context · Consequences · Alternatives) | **HLD** | `09-decisions.md` |
| A new tech-stack member, or a swap of an existing one (e.g. swapping the broker, the datastore, the signing scheme) | **HLD** | `05-tech-stack.md` (plus a new ADR in `09-decisions.md` capturing the *why*) |
| A new cross-cutting policy that applies across all components (e.g. a tenancy boundary move, a retry policy across all services, a uniform signing scheme) | **HLD** | `07-cross-cutting.md` |
| A new regulatory obligation discovered during specification | **HLD** | `06-regulatory.md` |
| A new domain entity or a glossary term not previously named | **HLD** | `00-overview.md` (glossary) / `04-domain.md` (entity) |
| A new externally-visible interface (HTTP route, NATS subject, CLI command, file format) — name and shape only | **HLD** | `08-interfaces.md` |
| A new system-level risk (a discovered failure mode, a dependency the design overlooked) | **HLD** | `10-risks.md` |
| | | |
| Exact field type for a Public Interface parameter or return | **Spec** (Phase 3 component body) | — |
| Exact JSON shape for an externally-visible payload | **Spec** (Phase 3 component body) | — |
| Error code string, error envelope, error-table row | **Spec** (Phase 3 component error table) | — |
| Retry count, backoff numbers, timeout duration, jitter range | **Spec** (Phase 3 component Internal Logic or Phase 4 cross-cutting) | — |
| Index choice, query plan, specific DDL, constraint shape | **Spec** (Phase 3 Data Model) | — |
| Gherkin scenario for an in-scope behaviour | **Spec** (Phase 3 Acceptance Criteria) | — |
| Component-internal helper, private interface, private state shape | **Spec** (Phase 3 Internal Logic) | — |
| Logging fields, metric names, specific OTel span names | **Spec** (Phase 4 cross-cutting) — unless the change introduces a new observability *policy*, then **HLD** `07-cross-cutting.md` |
| Specific env-var name, default value, scope | **Spec** (Phase 2D Configuration) — unless a new configuration *strategy* is introduced, then **HLD** `07-cross-cutting.md` |

## Edge cases and how to decide

### "It's both an ADR and a wire-level change"

When an architectural decision determines wire-level detail (e.g. "we use ed25519 signatures" determines the byte format of the lockfile's signature field), record **both**:

- The ADR in HLD `09-decisions.md` — Decision: use ed25519 with detached signatures; Context: ...; Consequences: ...; Alternatives: ...
- The wire shape in the relevant Phase 3 component spec — exact field name, exact encoding, exact validation rule.

The HLD entry captures *the choice and the why*; the spec entry captures *the bytes and the how*.

### "The component already exists in `02-architecture.md` but its responsibility is widening"

If the widening is **substantive** (the component now owns a new noun, a new flow, a new external integration), the responsibility row in `02-architecture.md` is amended — HLD finding.

If the widening is **internal** (the component is now doing more work behind the same public interface), it stays in the spec — LLD finding.

### "A new glossary term that the HLD's prose silently assumed"

Bubble it up to HLD `00-overview.md`. The HLD's silence is the bug; the spec did not invent the term, it surfaced one that should have been there. `sync-check` D-HLD-1 enforces this.

### "Cross-cutting middleware that exists in code (code-evidence mode) but is not in the HLD"

If the middleware corresponds to a cross-cutting *policy* (auth, logging, rate limiting, retry, tenancy), the policy belongs in HLD `07-cross-cutting.md`. The middleware's specific names, configuration, and code path live in the Phase 4 cross-cutting spec.

### "A new external dependency surfaces during specification"

If the dependency is a **neighbouring system** or **external actor** — HLD `01-context.md` and `10-risks.md` (dependency listing).

If the dependency is a **library** — HLD `05-tech-stack.md` (one-line row) plus a new ADR in `09-decisions.md` if the choice has rejected alternatives worth recording. If the library is a transitive dependency picked by a directly-named one, do not record it.

### "An NFR target tightens"

If the NFR change reframes the system (latency SLO drops from 1s to 50ms, throughput target 10×s) — HLD `07-cross-cutting.md` NFR section. Capture as an ADR if the change forced an architectural choice (caching layer, sharding decision).

If the NFR change is component-local and the system-level target is unchanged — stay in the spec.

## Anti-bubble-up patterns

Do not bubble up:

- **Implementation details masquerading as architecture.** "Use a `sync.Map` instead of `map[string]int` with a mutex" is not an ADR. It is an internal-logic decision; stays in the spec.
- **Test-only choices.** Test container library, mock framework, fixture format — these belong in the Phase 4 testing cross-cutting spec, not the HLD.
- **Code style.** Naming conventions, error-message phrasing, comment style, import grouping — these belong in the workspace's project-conventions file, not the HLD.
- **Single-component refactors.** A clean-up of a component's internal package layout is not an HLD change unless the component's *boundary* moves.
- **One-off opt-ins.** A feature flag for one customer, a temporary debug endpoint, a one-shot migration script — these do not warrant ADRs; record as Phase 1 Assumptions with `confidence: low` or as scoped exceptions in the relevant component spec.

## How the rule is enforced

- **`specgen` Phase 3.5** runs the HLD-impact-pass after every Phase 3 / Phase 4 / Preamble draft and produces the candidate edits per this table. See `hld-impact-pass.md`.
- **`sync-check`** enforces the rule after the fact:
  - **D-HLD-1** — spec introduces a glossary term not in HLD glossary.
  - **D-HLD-2** — spec body contains an ADR-shaped paragraph not in HLD `09-decisions.md`.
  - **D-HLD-3** — an HLD revision declaring it `affects:` this spec set is newer than the set's `derivedFromHld:` pin (on a multi-set HLD carrying no `affects:`, reported *unadjudicated*).
  - **D-HLD-4** — HLD names a component for which no Phase 3 spec exists *and* the Generation Playbook said one should.
  - **D-HLD-5** — sibling-file inconsistency inside a folder HLD.
  - **D-HLD-6** — HLD revision bump without a matching `99-changelog.md` line (folder form only).

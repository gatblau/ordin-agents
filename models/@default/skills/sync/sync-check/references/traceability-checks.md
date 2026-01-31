# Traceability checks (`scope: traceability`)

The cross-role **no-orphan traceability gate** (§13-Q8): a **read-only** check that traverses the requirement→test chain across a project's full artefact set and reports orphans at each link. Unlike the per-component `design-spec` / `spec-code` checks, this one spans what *different roles* produced — no single role's view sees the whole chain, so it runs above the component level.

Load this reference at the start of Step 3 when `scope` includes `traceability`. The check is **static** — it never executes tests (consistent with "sync-check does not execute the code under test"); "ends in a passing test" is verified structurally (a test exists and cites the requirement), not by running it.

## The traceability chain

```
FR → HLD-goal → AC → test
```

- **FR** — a functional requirement (the PM-owned FR register). **Graceful degradation:** when no FR register is installed, the `FR → HLD-goal` link is reported `unverifiable — FR register not installed`, **never a false orphan** (mirrors the NFR register-template convention). The FR head is activated when the FR register lands (plan-16 FU-001).
- **HLD-goal** — an entry in the HLD `## Goals` section (`docs/design/<topic>/00-overview.md`, or the single-file HLD).
- **AC** — an acceptance criterion in a Component spec or RFC (Phase-3 Acceptance / a Gherkin scenario).
- **test** — a test file/case in the source tree.

## Link mechanism — explicit id reference

A downstream artefact **traces to** an upstream one by citing its **id** — not by name or semantic similarity (`sync-check` never infers equivalence; `VAL_ERR ≠ ValidationError`). An AC cites the HLD-goal id it satisfies; a test cites the AC id it verifies (in its name, a comment, or a structured tag). A link with no cited id is **not** silently inferred — it is reported (see Orphan kinds).

The citation convention is `urn:ordin:default:rules:layer:spec-anchors` — the `<comment-leader> spec: <set>/<document>#<assertion-id>` directive, one anchor per line, verified against the document before it is written. That rule is what makes this check actionable rather than noisy: without a fixed form, every comment mentioning an id looks like a candidate link and none of them resolves. `spec-code-checks.md` aspect S11 applies the same mechanism to the `AC → code` link.

## Orphan kinds (bidirectional)

Evaluated at each link `upstream → downstream`:

| Label | Definition |
|---|---|
| `ORPHAN-FORWARD` | An upstream requirement (HLD-goal, AC) with no downstream artefact citing it — a requirement that ends in no test. |
| `ORPHAN-REVERSE` | A downstream artefact (test, AC) that cites no upstream id — a test that verifies no stated requirement. |
| `TRACE-DANGLING` | A downstream artefact citing an upstream id that does not exist. |

`ORPHAN-REVERSE` (no upstream id cited) is reported distinctly from `TRACE-DANGLING` (an id cited but unknown), so the fix is unambiguous.

## Procedure (Step 3, `scope: traceability`)

1. **Enumerate the artefact set.** There are two ways the roles' outputs are laid out, and the check reads whichever applies:

   - **A multi-role journey.** The process is a **Journey** (`journeys/<slug>.yaml`), which lists its crossings as `seams` — each seam an **OutputContract** id. The **members** are the workspaces taking part: find them through the **HandoffOverlays** that `produces`/`consumes` those seams, each bound to exactly one workspace by its `appliesTo.profile`. The artefacts crossing between members are the seams themselves. A Journey is not installable and pulls no workspace in, so it is an *index* of the chain, not the chain — read it to learn who the members are, then read each member's own design/spec/code.
   - **A single project repo.** Every role's output already lives in one tree; there is no journey to consult. Collect directly: HLD goals (`## Goals`), ACs (Phase-3 Acceptance / Gherkin), and tests.

   The chain is the same either way. The layout only decides where to look for each link.
2. **Build the chain.** For each link, resolve downstream→upstream by cited id.
3. **Detect orphans** per the table above, at each link, in both directions.
4. **FR head:** if no FR register is installed, mark the `FR → HLD-goal` link `unverifiable — FR register not installed`; do **not** emit `ORPHAN-FORWARD` for HLD-goals on the FR side (graceful degradation).

## Report

Add a **Traceability** summary-count block and a findings section grouped by link (and, for a journey, by member workspace) to the Step-5 report — see `report-template.md` §Traceability. Every finding carries its label, the link, the artefact id, and the member it belongs to. Like the rest of `sync-check`, this check is **report-only**; it proposes no patches (orphans are closed by authoring the missing test/AC/goal, or by removing the orphan, which is a human decision).

## What this check does not do

- Execute or run tests (static traceability only).
- Infer a link by name or semantic similarity (explicit id citation only).
- Emit FR-side orphans when the FR register is absent (graceful degradation).
- Cover NFRs — NFRs `refine` FRs and are the `cross-cutting-nfr` skill's concern.

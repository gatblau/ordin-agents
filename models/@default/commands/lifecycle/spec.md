---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:lifecycle:spec"
  name: /spec
  version: 1.2.0
  owner: gatblau
  description: "Turns a design, RFC, or root-cause outcome into the six-part low-level spec set, and routes any design-shaped findings back to the design. Saves the spec files."
invokes:
  - kind: skill
    ref: "urn:ordin:default:skills:quality:specgen"
    role: drive-procedure
    when: always
description: Structure intent into a Low-Level Design (LLD) spec set (analysis · architecture · component specs · cross-cutting · Generation Playbook · self-audit) by driving the `specgen` skill. Consumes a High-Level Design (HLD) at `docs/design/<topic>/` (folder form) or `docs/design/<topic>.md` (single-file form), an RFC / intent-changing RCA outcome (change / incident), or an as-built design produced by `/design code-evidence` (brownfield — the spec is generated against existing code, with each assertion classified Required / Observed / Not implemented / Gap). Each phase ends with an HLD-impact-pass that routes HLD-shaped findings back to the HLD as auto-drafted edits, reviewed by the user in the same combined diff as the spec output (the four CSPA moves do not change). Produces input suitable for `/breakdown`. Writes `docs/spec/phase-*.md`.
argument-hint: "<topic | HLD path | docs/design/> [phase: 1-2|3-6|all] [code-paths: <comma-separated paths>] [witness-sources: <comma-separated paths>]"
---

# /spec — Structure Intent into an LLD Spec Set

You have been given the following input:

```
$ARGUMENTS
```

Parse `$ARGUMENTS` to extract:

- **Input** (required): either a **topic shorthand** (the kebab-case topic name the HLD was authored under — e.g. `nats-key-rotation` resolves to `docs/design/nats-key-rotation/` if the folder exists, otherwise `docs/design/nats-key-rotation.md`), a path to an HLD (e.g. `docs/design/<topic>.md` or `docs/design/<topic>/`), an RFC document (e.g. `docs/wip/rfc/<NN>-<slug>.md`), an intent-changing RCA outcome (inline, or `docs/wip/rca/<NN>-<slug>.md`), or the directory `docs/design/` (default for a full greenfield spec set).
- **Phase** (optional): if a single positional argument matches `1-2 | 3-6 | all`, it is treated as the phase. `phase: <value>` is also accepted. Short form examples: `/spec nats-key-rotation 1-2` and `/spec nats-key-rotation phase: 1-2` are equivalent.
- **Phase** (optional, default `all`): `1-2` runs the analysis and architecture phases and stops for human review; `3-6` runs the per-component specs, cross-cutting specs, Playbook and self-audit; `all` runs the full sequence end-to-end.
- **Code paths** (optional, code-evidence mode only): one or more repo-relative directories or files. Required when the input design carries a `Mode: code-evidence` banner; should match the paths that were scanned to produce that design.
- **Witness sources** (optional, code-evidence mode only): explicit list of test files, contract files (OpenAPI, `.proto`, NATS subject schemas), or vendor docs the skill should treat as witness sources beyond what is auto-discovered in `code-paths`.

If `$ARGUMENTS` is empty, ask the user for the input path. Stop until they reply. If the input design carries a `Mode: code-evidence` banner and `code-paths` are not supplied, ask the user for the same code paths that were scanned to produce the design.

## Purpose

`/spec` is **move 2 (Structure intent)** of the four-move CSPA loop. It transforms captured intent — an HLD, an RFC, or an intent-changing RCA outcome — into the **LLD spec set** that downstream moves consume:

1. Analysis (Assumptions Register, Open Questions, Glossary) — Phase 1
2. System architecture (Context, Inventory, Shared types, Env vars) — Phase 2
3. Component specs — Phase 3
4. Cross-cutting specs — Phase 4
5. Generation Playbook — Phase 5
6. Self-Audit — Phase 6 (blocking gate)

The Self-Audit (Phase 6) is the blocking gate that promotes the spec set from *Draft* to *Approved*. `/breakdown` will refuse to consume a spec set whose Phase 6 audit has not passed.

## HLD-impact-pass — combined review per phase

Each Phase 3 (Component), Phase 4 (Cross-cutting), and Preamble draft is followed by an **HLD-impact-pass** that scans the draft for HLD-shaped findings (new components, new ADRs, new glossary terms, new tech-stack members, new cross-cutting policies, new regulatory obligations, new external actors, new principal sequences). Findings are auto-drafted as edits to the corresponding HLD child file, and the user reviews **one combined diff** (spec output + HLD delta + changelog line + revision bump) per phase. Approve all, reject any to demote to a spec-local Assumption, or edit individual entries before approval.

This back-edge is plumbing: the four CSPA moves remain `design · spec · breakdown · apply`; there is no new ceremony for the user. The bubble-up rule (`@default/skills/quality/specgen/references/bubble-up-rule.md`) and the procedure (`@default/skills/quality/specgen/references/hld-impact-pass.md`) are the canonical references.

Every Phase 3 / Phase 4 / Preamble spec carries a `derivedFromHld: <revision>` preamble pinning it to the HLD revision it was authored against. `sync-check` enforces that every HLD revision declaring it `affects:` this set has been absorbed (D-HLD-3) and that the HLD↔spec invariants hold (D-HLD-1 glossary, D-HLD-2 hidden ADR, D-HLD-4 orphan component, D-HLD-5 sibling inconsistency, D-HLD-6 changelog gap).

## When to use which branch

`/spec` operates in **three branches**, distinguished by whether a spec set already exists, whether the input is a forward-looking design, and whether the spec is being authored against existing code.

### Branch A — New spec set (greenfield)

Input: a HLD at `docs/design/<topic>.md` (or the whole `docs/design/` directory). The design's Mode banner reads `interview` or `draft`.

Triggered by `/design` upstream. Runs the full Phase 1–6 sequence in greenfield mode. Produces the complete Spec set under `docs/spec/`.

### Branch B — Update existing spec(s) (change request or intent-changing incident)

Input: an RFC at `docs/wip/rfc/<NN>-<slug>.md` (from `/rfc`), or an RCA outcome (from `/rca`, inline or at `docs/wip/rca/<NN>-<slug>.md`) classified as intent-changing.

Re-runs Phases 3–6 scoped to the affected component(s) — the per-component specs and the Self-Audit. Phases 1–2 are touched only if the change introduces new components, new shared types, or new cross-cutting concerns.

This is the CSPA rule **"fix the prompt first"** in action: when intent changes, the spec must be updated *before* code is patched.

### Branch C — Code-evidence (brownfield)

Input: an as-built HLD at `docs/design/<topic>.md` whose Mode banner reads `code-evidence`, plus the same `code-paths` that were scanned to produce it.

Triggered by `/design` code-evidence upstream. Runs the full Phase 1–6 sequence in `code-evidence` mode. The skill ingests the as-built design's Requirements section (*Must preserve*, *Observed but not required*, *Drop candidates*, *Gaps*) and walks the supplied `code-paths` to classify every spec assertion as one of:

- **`[Required]`** — present in code AND has a witness (test, contract, user confirmation, regulatory obligation).
- **`[Observed]`** — present in code, no witness; safe default.
- **`[Not implemented]`** — required by the design's *Must preserve* but no matching code (the rewrite remediation set).
- **`[Gap]`** — suspected but unverifiable; blocks promotion to *Approved*.

The full classification rules and the mapping to `sync-check`'s drift labels live in `@default/skills/quality/specgen/references/code-evidence-classification.md`. The cross-check itself reuses the aspect-by-aspect comparison logic in `@default/skills/sync/sync-check/references/spec-code-checks.md` — Branch C does not duplicate that logic; it applies it at spec-authoring time.

Use this branch when retrofitting a spec onto a brownfield codebase, or when scoping a rewrite from an existing system that has no spec.

### Skip condition — REALITY-DRIFT bug fix

`/spec` is **skippable** for one specific case: a verified, high-confidence RCA top hypothesis whose remediation is a *pure REALITY-DRIFT bug fix* — the existing component spec already states the desired behaviour and the code has drifted from it. In that case the spec is already correct; only the code needs to change. Proceed directly to `/breakdown` with the RCA as input.

If you are unsure whether the RCA qualifies for the skip, run `/sync-check` first. If the report shows zero INTENT-DRIFT and zero CONTRACT-DRIFT for the affected components, the skip is safe.

## Active modes

**Observe → Infer → Plan**, with **Review** for Phase 6, and the `identifier-verification` layer rule active throughout. The `sql-safety` layer rule activates whenever a spec touches `schema/**` or `*.sql`.

- **Observe** for Design-document or RFC intake (Phase 1A) and any source-code reads when components describe existing behaviour.
- **Infer** for the architecture pass (Phase 2) and the Assumptions Register (Phase 1A): rule S6 — *assumptions over questions when possible* — applies.
- **Plan** for Phases 1B–5. The Spec set is authored under `docs/spec/`, never under source.
- **Review** for Phase 6 — the Self-Audit checklist that promotes the spec set from *Draft* to *Approved*. Phase 6 is a **hard gate**.

The command never enters Patch — spec files are documents, not source. **Escalate** when an Open Question materially affects architecture and cannot be resolved by an assumption, or when Phase 6 audit fails on a non-fixable item.

## Procedure

This command **delegates its procedure to the `specgen` skill** (`@default/skills/quality/specgen/SKILL.md`). The skill's six-phase flow is canonical. Do not restate or override it here.

1. **Identify the branch.** Inspect the input file's structure (or its Mode banner if a HLD) and decide:
   - Design with `Mode: interview` or `Mode: draft` → Branch A (greenfield).
   - RFC or intent-changing RCA → Branch B (update).
   - Design with `Mode: code-evidence` → Branch C (code-evidence). Require `code-paths`; if absent, ask the user for them.
   - Ambiguous → ask the user before proceeding.
2. **Confirm the REALITY-DRIFT skip does not apply.** If the input is an RCA whose hypothesis is a pure code-drift bug fix, redirect the user to `/breakdown` and stop.
3. **Load the `specgen` skill** and pass through the input path, the `phase` argument, and (in Branch C) `code-paths` plus optional `witness-sources`.
4. **Run the skill in the chosen branch.**
   - *Branch A:* Phase 1 → 2 → 3 → 4 → 5 → 6, end-to-end, in greenfield mode.
   - *Branch B:* Phase 3 (scoped to affected components) → 4 (only if cross-cutting concerns changed) → 5 (Playbook update for new components only) → 6 (audit re-run).
   - *Branch C:* Phase 1 → 2 → 3 → 4 → 5 → 6 in code-evidence mode. Phase 1 ingests the as-built design's Requirements section. Phase 3/4 apply per-assertion classification tags using `code-evidence-classification.md` plus the cross-check logic in `sync-check/references/spec-code-checks.md`. Phase 5 splits the Playbook into a remediation phase (the `[Not implemented]` set) and a continuity phase. Phase 6 additionally verifies every assertion carries a tag and every `[Required]` carries a witness.
5. **Receive the file paths and the audit result.** The skill writes the relevant `docs/spec/phase-*.md` files and returns the paths plus the Phase 6 audit verdict (passed / failed with item list). In Branch C, also returns the per-component classification summaries.
6. **Decide on the handoff.** If Phase 6 audit failed or any Open Question is blocking, surface the failures and stop — do not invoke `/breakdown`. In Branch C, also stop if any `[Gap]` remains unresolved (the per-assertion equivalent of a non-empty *Gaps* section). Otherwise, suggest the next move (see *Handoff to /breakdown* below).

The Spec set shape — analysis, architecture, components, cross-cutting, Playbook, audit — is defined by `@default/skills/quality/specgen/references/`. This command file does not duplicate it. If the shape changes, it changes once, in the skill's references.

## Required output structure

The authored artefacts are the `docs/spec/phase-*.md` files. The reply this command returns to the user contains:

### Files written or updated
- List of paths under `docs/spec/`.

### Branch
- `new spec set (greenfield)`, `update existing specs (change / incident)`, or `code-evidence (brownfield)`, and which components were affected.

### Phase 6 audit verdict
- `passed` or `failed: <item list>`.

### Counts
- Number of components in scope.
- Number of Open Questions remaining (split blocking / non-blocking).
- Number of assumptions added.
- In Branch C, also: per-component classification totals (`Required: N | Observed: N | Not implemented: N | Gap: N`) and the workspace-wide totals.

### Handoff to /breakdown
- One-line suggested invocation.
  - Greenfield, full set: `/breakdown <topic>` (short form; resolves to the topic's `docs/spec/phase-5-playbook.md`).
  - Targeted update: `/breakdown docs/spec/components/<ComponentName>.md` (or the RFC path if the change scope is bounded by the RFC).
- If Phase 6 audit failed or any Open Question is **blocking**, state that the user should resolve those first and **do not** print the handoff line.

## File-writing rules

- The underlying `specgen` skill writes to `docs/spec/phase-*.md` (Branch A) or to the affected component file under `docs/spec/components/<ComponentName>.md` (Branch B).
- This command writes no other file, with one exception: when the run was invoked from a plan's follow-up or risk entry, it closes that entry in the plan — see below.
- The command never overwrites existing spec content silently; the skill's branch logic decides whether to extend or replace and surfaces conflicts to the user.

## Close the loop on the entry that prompted this spec change

Plan follow-ups and risks routinely carry `suggested-command: /spec …`. When this run was invoked from such an entry, record the outcome in the **parent plan**, or the roll-up goes on counting resolved work as open:

- **The spec amendment is itself the resolution** — the common case, and the one the corpus already shows: set the entry `status: done` with a one-line note naming what the spec now says, and the date.
- **The spec change only sets the work up** — the `/spec … then /breakdown` case: set `status: scheduled` with `scheduled-in:` pointing at the spec set or RFC that now carries it. It becomes `done` when the plan implementing it lands.
- Either way, call `/plan-index update <parent-NN>` so the parent's open-follow-up count and *Needs attention* bullets follow. If `00-index.md` does not exist yet, `/plan-index build` creates it first.

`/spec` writes no relocation glyph. It holds no phases and moves none: the spec set it produces becomes a plan's `Source spec set:` edge only when `/breakdown` writes that plan, and marking a relocated phase `↗<NN>` stays `/breakdown`'s job alone.

## Where this command sits in the lifecycle

`/spec` is **move 2 (Structure intent)** of the four-move CSPA loop. It is the move that every door passes through, except for the documented REALITY-DRIFT skip:

```
greenfield (interview/draft):  /design               → /spec (Branch A) → /breakdown → /apply → /sync-check
greenfield (code-evidence):    /design code-evidence → /spec (Branch C) → /breakdown → /apply → /sync-check
change:                        /rfc                  → /spec (Branch B) → /breakdown → /apply → /sync-check
incident (intent-changing):    /rca                  → /spec (Branch B) → /breakdown → /apply → /sync-check
incident (REALITY-DRIFT skip): /rca                                     → /breakdown → /apply → /sync-check
```

The CSPA rule **"no spec, no Patch"** is enforced downstream: `/breakdown` and `/apply` refuse to consume work without a Phase 6-approved spec set (or, in the documented skip case, an RCA that has been classified as a pure REALITY-DRIFT bug fix). In Branch C, additionally, `/apply` refuses any spec containing one or more unresolved `[Gap]` assertions.

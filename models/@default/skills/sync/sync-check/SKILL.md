---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:sync:sync-check"
  name: sync-check
  description: "Finds drift between design, spec, and code and labels each finding. The exit check for every change."
  version: 1.3.0
  owner: gatblau
description: Detect and classify drift between High-Level Design (docs/design/), Low-Level Design specifications (docs/spec/) and source code in any language. Polices the four canonical drift labels (INTENT-DRIFT, CONTRACT-DRIFT, REALITY-DRIFT, SCOPE-GAP) and the HLD↔spec subfamily (D-HLD-1 glossary gap, D-HLD-2 hidden ADR, D-HLD-3 stale derivedFromHld, D-HLD-4 orphan HLD component, D-HLD-5 sibling inconsistency, D-HLD-6 changelog gap). Read-only report by default; proposes reconciliation patches only in fix mode with explicit user approval. Invoke explicitly — trigger only on imperative phrases like "run sync-check", "check drift", "verify specs match code", "reconcile design spec code", or /sync-check. Do NOT trigger on passive questions like "is the spec up to date".
---

# sync-check — Design ↔ Spec ↔ Code drift detection

`sync-check` is the procedure invoked by the **`/sync-check`** slash command — the **exit gate** of every CSPA path. The command (in `@default/commands/sync/sync-check.md`) is the user-facing surface; this skill is the canonical procedure behind it. The CSPA invariant *no exit without sync* is enforced here: a change is not complete until `/sync-check` exits clean.

> **Guardrails:** read-only — never writes files, and never auto-resolves drift (proposes patches only, in fix mode, with explicit user approval).

Detect where the three artefact layers disagree, classify each finding so the right resolution path is obvious, and propose (never auto-apply) the minimum patch that closes the gap. Code inspection only — never executes the code under test.


## Active modes

**Observe → Review.**

- **Observe** for evidence gathering across design, spec, and code: tier-tagged extraction (T1 filesystem / T2 regex / T3 tree-sitter / T4 native AST). Low-tier findings are flagged "regex-confidence — verify manually" — the verified-vs-inferred discipline is preserved through the tier tag.
- **Review** for the diff-and-classify pass and the consolidated drift report. One of four labels per finding (INTENT / CONTRACT / REALITY / SCOPE-GAP), with a likely-source hint that the human adjudicates.

The skill never enters Patch — even `mode: fix` only **proposes** patches and stops for explicit user approval; the patches themselves are written by `/sync-spec` (code → spec) or `/sync-code` (spec → code). sync-check detects; it does not resolve. **Escalate** is implicit in every finding — every drift item points the user at the resolving command.

## Layers

| Layer | Location | Source of |
|---|---|---|
| HLD | `docs/design/<topic>/` (folder form: `README.md` + numbered child files + `99-changelog.md`) or `docs/design/<topic>.md` (single-file form) | Human intent · architecture · ADRs · tech stack · regulatory context |
| LLD | `docs/spec/phase-*.md` (+ optional `docs/spec/components/*.md`) | Machine-consumable contract |
| Code | Repository source tree + `migrations/*.sql` | Implementation |

HLD ↔ Code is never compared directly. The LLD is the only reconciliation layer — if it is missing, the skill stops and says so. Additionally, the LLD's `derivedFromHld:` preamble pins each spec phase to a specific HLD revision; `sync-check` enforces that pins stay current.

## Arguments

- `scope`: `all` (default) | `design-spec` | `spec-code` | `traceability` | `<component-name>`
  - `traceability` runs the cross-role no-orphan gate (§13-Q8) — the requirement→test chain `HLD-goal → AC → test` (`FR → HLD-goal` when an FR register is installed). See `references/traceability-checks.md`. It reads the whole chain across what *different roles* produced, from either a multi-role **Journey**'s member workspaces or a single repo holding every role's output. `all` does not imply it: it needs an artefact set no single component's view provides.
- `mode`: `report` (default, read-only) | `fix` (proposes patches; still writes nothing until approved)
- `since`: optional git ref. When set, only files changed since that ref are inspected. Use for fast incremental checks on large repos.

## Drift taxonomy (always use these four labels + HLD↔spec subfamily)

Load `references/drift-taxonomy.md` at the start of every run for full definitions and resolution playbooks. Headline:

| Label | Meaning | Owner |
|---|---|---|
| INTENT-DRIFT | HLD changed; spec/code stale | Human (may create open questions) |
| CONTRACT-DRIFT | Spec changed; code stale | `/codegen` re-run for affected component |
| REALITY-DRIFT | Code changed; spec no longer describes truth | Human decides: revert code **or** update spec |
| SCOPE-GAP | Artefact exists in one layer with no counterpart elsewhere | Human triage |

REALITY-DRIFT must never be auto-fixed by regenerating code — regeneration would destroy the hotfix. The skill surfaces two alternative diffs (code revert vs spec edit) and stops.

### HLD↔spec drift subfamily (`D-HLD-*`)

The HLD↔spec subfamily polices the living-architecture model: the HLD is amended by `/spec`'s HLD-impact-pass, and `sync-check` enforces that the back-edge does not silently rot either document.

| Label | Meaning | Owner |
|---|---|---|
| **D-HLD-1** | Spec introduces a glossary term not in HLD glossary | Spec → run HLD-impact-pass, promote term |
| **D-HLD-2** | Spec body contains an ADR-shaped paragraph not in HLD `09-decisions.md` | Spec → run HLD-impact-pass, promote ADR |
| **D-HLD-3** | An HLD revision that declares it `affects:` this spec set is newer than the set's `derivedFromHld:` pin | Spec → re-run `/spec` for the affected phase |
| **D-HLD-4** | HLD names a component for which no Phase 3 spec exists *and* the Generation Playbook said one should | LLD → run `/spec` Phase 3 for the missing component |
| **D-HLD-5** | Sibling-file inconsistency inside a folder HLD (a component named in `02-architecture.md` not referenced in `06-regulatory.md` where regulation says it should be; a glossary term used in `04-domain.md` absent from `00-overview.md`; an ADR in `09-decisions.md` referring to a component not in `02-architecture.md`) | HLD → direct edit to align siblings |
| **D-HLD-6** | HLD revision bump in `README.md` without a matching line in `99-changelog.md` (folder form only) | HLD → append the missing changelog line |

The `D-HLD-*` family stops the run from marking a phase clean — every `D-HLD-*` finding is a blocker. Resolution is via re-running the affected `/spec` phase (the HLD-impact-pass will produce the missing edits) or by a direct HLD edit (for D-HLD-5 and D-HLD-6).

## Process

### Step 1 — Toolchain probe
Load `references/extraction-tiers.md`. Run `which tree-sitter`, `which go`, `which tsc`, `which python3`, `which cargo` (fail-soft). Record which tiers are available. Report header must state this. Every finding is tagged with the tier that produced it.

If the project ships a **reference gate** — the repository-local check described in `urn:ordin:default:rules:layer:spec-anchors` §Mechanical enforcement, named by the active stack pack's `build-commands.md` — run it here. It resolves every document link, every source path cited by the descriptive layers, and every `spec:` anchor, exactly and cheaply. Its output is evidence for aspects S11 and S12: findings it reports are already verified, so the run spends its own effort on what it cannot compute (assertion coverage, semantic comparison). If it exits non-zero, state that in the report header — when the paths the other aspects resolve through are themselves broken, every downstream finding is less reliable.

### Step 2 — Inventory
- HLD files: `Glob docs/design/**/*.md`. Detect HLD shape per topic — folder form is a directory under `docs/design/` containing `README.md` (record current `revision:`); single-file form is a single `.md` under `docs/design/`. For folder-form HLDs, also locate `99-changelog.md`.
- Spec components: read `docs/spec/phase-2-architecture.md` → Component Inventory table. For each component, read its Phase 3 spec (declared `**File:**` path used in Step 3). Also read Phase 4 cross-cutting specs. Record every spec's `derivedFromHld:` preamble value.
- Source files: `Glob` with the default allowlist (see `references/extraction-tiers.md` for full list). Excludes: `vendor/`, `node_modules/`, `target/`, `dist/`, `build/`, `.git/`, `docs/`, generated directories. Overridable via `.sync-check.yml` or a `## sync-check` block in the workspace's project-conventions file.

If `docs/spec/` is missing or empty: stop. Tell the user to run `/spec` first.

### Step 3 — Extract contracts
Load `references/design-spec-checks.md` and `references/spec-code-checks.md`. When `scope` includes `traceability`, also load `references/traceability-checks.md` and run the requirement→test traversal over the artefact set — a Journey's member workspaces, or the whole project when every role's output lives in one repo.

For each spec component, apply the highest-tier extractor available against the file path declared in the spec's `**File:**` field. If the declared file does not exist, emit a `SCOPE-GAP` finding and continue with name-based fallback matching.

Extraction is confidence-tagged (T1 filesystem / T2 regex / T3 tree-sitter / T4 native AST). Low-tier findings are marked "regex-confidence — verify manually" in the report.

### Step 4 — Diff & classify
For each (spec aspect, code aspect) pair:
- If equal, no finding.
- If different, classify via the taxonomy. Use `git log -1 --format=%ct` on each artefact as a tiebreaker for CONTRACT vs REALITY: most-recently-modified layer is the **likely** drift source. This is a hint, not a verdict — the report states "likely source: <layer>" and lets the human adjudicate.

### Step 5 — Report (always produced)
Load `references/report-template.md`. Output: header (toolchain probe results, scope, timestamp, git HEAD), summary counts per label, then a findings table grouped by component. One row per finding with: component · aspect · expected · actual · label · tier · likely source · suggested action.

Write the report to stdout in the response. Do not write any file unless the user explicitly asks for a saved report.

### Step 6 — Propose patches (`mode: fix` only)
For each finding:
- **CONTRACT-DRIFT** → propose `/codegen step: "<N>: <ComponentName>"` with a one-line justification of what will change.
- **INTENT-DRIFT** → propose `/spec phase: 3-6` scoped to affected components, then `/codegen` for each.
- **REALITY-DRIFT** → present **two** alternative diffs, clearly labelled: (a) revert code to match spec via `/sync-code`, (b) edit spec to match code via `/sync-spec`. Do not default to one. Do not write either until the user picks one.
- **SCOPE-GAP** → no automated patch. Print the orphan and the three possible resolutions: add the missing counterpart in the other two layers, delete the orphan, or mark it as intentional in Phase 1 Assumptions.

Wait for explicit user approval before any write.

## What this skill does not do

- Execute the code (no `go run`, no `npm start`, no container boot, no test runs).
- Infer semantic equivalence (`VAL_ERR` ≠ `ValidationError` — both are flagged; the human decides).
- Self-schedule (no cron, no hook, no watcher — every run is user-initiated).
- Regenerate artefacts directly. Only points at the existing `/spec` or `/codegen` skill invocation that would close the gap.
- Compare design directly to code. Design ↔ Spec and Spec ↔ Code are the only axes.

## References (load on demand)

- `references/drift-taxonomy.md` — four labels, definitions, resolution playbooks. Load at start of run.
- `references/extraction-tiers.md` — T1–T4 probing, file-extension allowlist, exclude rules, per-language tree-sitter grammar names. Load at start of Step 1.
- `references/design-spec-checks.md` — design↔spec aspect checks (glossary, assumptions, noun/action/cross-cutting coverage). Load at start of Step 3 if scope includes `design-spec`.
- `references/spec-code-checks.md` — spec↔code aspect checks (routes, signatures, JSON tags, env vars, error codes, metric names, DDL, middleware references, spec anchors, reference integrity). Load at start of Step 3 if scope includes `spec-code`.
- `references/traceability-checks.md` — the cross-role no-orphan gate (§13-Q8): the `HLD-goal → AC → test` chain, bidirectional orphan kinds (`ORPHAN-FORWARD`/`ORPHAN-REVERSE`/`TRACE-DANGLING`), and the `FR → HLD-goal` graceful-degradation rule. Load at start of Step 3 if scope includes `traceability`.
- `references/report-template.md` — findings table format, header fields, summary counts. Load at start of Step 5.

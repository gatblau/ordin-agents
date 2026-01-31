---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:sync:sync-check"
  name: /sync-check
  version: 1.5.0
  owner: gatblau
  description: "Finds and labels drift between the design, the spec, and the code. Read-only report. This is the exit check every change must pass before it is done."
invokes:
  - kind: skill
    ref: "urn:ordin:default:skills:sync:sync-check"
    role: drive-procedure
    when: always
description: Detect and classify drift between High-Level Design (docs/design/), Low-Level Design specifications (docs/spec/) and source code. Polices the four canonical labels (INTENT-DRIFT, CONTRACT-DRIFT, REALITY-DRIFT, SCOPE-GAP) and the HLD↔spec subfamily (D-HLD-1 glossary gap, D-HLD-2 hidden ADR, D-HLD-3 unabsorbed HLD revision, D-HLD-4 orphan HLD component, D-HLD-5 sibling inconsistency, D-HLD-6 changelog gap). Read-only report by default. Drives the `sync-check` skill. The exit gate of every CSPA path — must be clean before a change is considered complete.
argument-hint: "[scope: all|design-spec|spec-code|<component>] [mode: report|fix] [since: <git-ref>]"
---

# /sync-check — Verify HLD ↔ LLD ↔ Code alignment

You have been given the following input:

```
$ARGUMENTS
```

Parse `$ARGUMENTS` to extract:

- **Scope** (optional, default `all`): `all` (Design ↔ Spec ↔ Code), `design-spec` (Design ↔ Spec only), `spec-code` (Spec ↔ Code only), or a component name to limit the scope.
- **Mode** (optional, default `report`): `report` (read-only) or `fix` (proposes patches but writes nothing without explicit approval).
- **Since** (optional): a git ref. When set, only files changed since that ref are inspected. Use for fast incremental checks on large repos.

If `$ARGUMENTS` is empty, run with the defaults.

## Purpose

`/sync-check` is the **exit gate of every CSPA path**. It verifies that the three artefact layers — HLD, LLD, Code — agree, and classifies any disagreement so the right resolution is obvious. Every successful traversal of the four-move loop ends with a clean `/sync-check` run; an unclean run blocks the change from being considered complete.

The check covers two families of findings:

- **Classic drift** — `INTENT-DRIFT`, `CONTRACT-DRIFT`, `REALITY-DRIFT`, `SCOPE-GAP` (full definitions in `@default/skills/sync/sync-check/references/drift-taxonomy.md`).
- **HLD ↔ spec subfamily** (`D-HLD-*`) — polices the living-architecture model. The HLD is auto-amended by `/spec`'s HLD-impact-pass; `sync-check` enforces that the back-edge does not silently rot either document. Six labels: D-HLD-1 (glossary gap), D-HLD-2 (hidden ADR), D-HLD-3 (unabsorbed HLD revision), D-HLD-4 (orphan HLD component), D-HLD-5 (sibling inconsistency in folder-form HLDs), D-HLD-6 (HLD revision bump without a changelog line).

This command is also useful **mid-flow** — for example, after `/spec` updates component specs but before `/breakdown` decomposes them — to confirm the previous step left things in a defensible state.

Do **not** use this command to:

- Author or update a spec (that is `/spec`).
- Apply a code patch (that is `/apply`).
- Reconcile spec to match code in-place (that is `/sync-spec`, surfaced as a remediation suggestion by this command).
- Push a spec change forward into code (that is `/sync-code`).

## Active modes

**Observe → Review.**

- **Observe** for evidence gathering across Design, Spec and Code. Tier-tagged extraction (T1 filesystem / T2 regex / T3 tree-sitter / T4 native AST). Low-tier findings are flagged *"regex-confidence — verify manually"*.
- **Review** for the diff-and-classify pass and the consolidated drift report.

The command never enters Patch — even `mode: fix` only **proposes** patches and stops for explicit user approval. The actual writes are performed by `/spec` (intent updates), `/apply` (code patches), `/sync-spec` (in-place reconciliation toward spec) or `/sync-code` (in-place reconciliation toward code). `/sync-check` detects; it does not resolve.

**Escalate** when:

- the spec set is missing or empty (the underlying skill stops and tells the user to run `/spec` first),
- a REALITY-DRIFT finding cannot be resolved by either of the two presented diffs,
- Design ↔ Code is queried without a Spec layer in between (the skill never compares those two directly).

## Drift taxonomy (four labels)

Every finding carries exactly one of these four labels. Definitions and resolution playbooks are in `@default/skills/sync/sync-check/references/drift-taxonomy.md`.

| Label | Meaning | Likely owner | Resolution |
|---|---|---|---|
| **INTENT-DRIFT** | Design changed; Spec and/or Code are stale | Human (may create Open Questions) | `/spec` (re-run scoped to affected components), then `/apply` |
| **CONTRACT-DRIFT** | Spec changed; Code is stale | Engineer | `/sync-code` (or re-run `/apply` for the affected component) |
| **REALITY-DRIFT** | Code changed; Spec no longer describes the truth | Human decides direction | Two alternative diffs presented: revert code (use `/sync-code` after spec is corrected) or update the spec (use `/sync-spec`). User picks. |
| **SCOPE-GAP** | Artefact exists in one layer with no counterpart elsewhere | Human triage | No automated patch. Either add the missing counterpart (run `/spec` and/or `/apply`), delete the orphan, or mark it intentional in the Spec preamble's Assumptions Register. |

REALITY-DRIFT is **never** auto-fixed by re-running `/apply` — regeneration would destroy a hotfix. The skill surfaces both alternative diffs and stops for the user's decision.

## Procedure

This command **delegates its procedure to the `sync-check` skill** (`@default/skills/sync/sync-check/SKILL.md`). The skill's six-step flow — toolchain probe, inventory, contract extraction, diff and classify, report, optional patch proposal — is canonical. Do not restate or override it here.

1. **Load the `sync-check` skill** and pass through the `scope`, `mode`, and `since` arguments.
2. **Run the skill end-to-end.** Step 1 (toolchain probe) → Step 2 (inventory) → Step 3 (extract contracts) → Step 4 (diff and classify) → Step 5 (report) → Step 6 (proposed patches, only in `mode: fix`).
3. **Receive the report.** The skill returns a header (toolchain probe results, scope, timestamp, git HEAD), summary counts per label, and a findings table.
4. **Apply the clean-exit criterion.** A run is **clean** only if **all** of the following hold:
   - all four drift summary counts are zero, **or** every finding has been explicitly accepted by the user with a written reason recorded in the report (and persisted as a Follow-up per step 6 if a plan is associated);
   - the project's **build command exits zero** in the current commit (Practice-Pack-supplied; ask the user if no Practice Pack is active and no project-conventions file declares one);
   - the project's **lint command exits zero** in the current commit (same Practice-Pack lookup);
   - the plan's **integration test suite has passed in the current commit** (black-box, with integrating services brought up via test containers or materialised stubs as the plan specified). Unit-test results alone do **not** satisfy this gate;
   - the **security scan is clean**. Run `secscan` with `mode: gate` over the change scope (or the full repo if no plan is associated). Zero findings at or above the project's configured severity floor (default `medium`), or every finding explicitly accepted by the user with a written reason recorded in the report.

   Otherwise the run is **dirty** and the change is not yet complete. If any of the four supplementary gates (build, lint, integration suite, security scan) has not been run, treat the run as dirty and tell the user to run it before re-invoking `/sync-check`. The five clean-exit conditions (drift-zero plus the four framework gates) are non-overridable; a Practice Pack may add stricter conditions but may not weaken or remove any of them.
4a. **Class-aware evidence ingestion.** When the change carries a `triage` block (set by `/rfc`), accept evidence by class. The adaptive lane introduces no new persistent artefact types — the Change brief and Scope attestations are evidence held in agent context and recorded as entries in this evidence log; only the Change addendum is persisted, and it lives on the existing Component spec.

   - **Trivial** — Scope attestations on every non-Component-spec artefact type, accepted as evidence-log entries (not separate files), framework gates green, drift count zero. No Component spec touch.
   - **Local** — Change addendum appended to the affected Component spec with `surface impact: none`, Scope attestations on every other artefact type accepted as evidence-log entries, framework gates green, drift count zero. The Change brief is not required to be persisted; if the user supplies one (e.g. from `.scratch/`), accept it as supporting evidence. If `surface impact` reads anything other than `none`, return **dirty** and instruct the user to re-enter via the Standard lane.
   - **Standard** — full §4 artefact set updated as required, framework gates green, drift count zero. Today's behaviour, unchanged.

   Framework gates (build, lint, integration suite, security scan) run uniformly across all three classes — only the artefact set varies. A run is **dirty** if the artefact set required for the declared class is incomplete, even if drift counts are zero.

5. **Surface remediation per finding.** For each row, the report names the resolution command per the taxonomy table above. Do not invoke any of those commands automatically — `/sync-check` is read-only by design; the user invokes the resolution explicitly.
6. **Persist deferred findings back to the plan.** If `/sync-check` was invoked in the context of a known plan file (the user named one, or exactly one plan file is in scope under `docs/wip/plan/` and the user accepts the association on prompt), then for every finding the user marks **accepted** or **deferred**, append a structured entry to that plan's **Follow-ups** section using the `/breakdown` schema (`id`, `title`, `why`, `source: sync-check`, `severity` scored against `/breakdown`'s rubric, `suggested-command` set to the per-label resolution command, `status: open`). A finding that scores `critical` or `high` is promoted the same way `/apply` promotes one — a phase appended to the plan's `## Phases` section, and the entry moved to `status: scheduled` with `scheduled-in:` naming that phase — because a drift finding the user accepted is deferred work, and deferred work that never reaches the phase strip is deferred work the roll-up cannot show. Each appended entry is re-invokable later — either directly via its `suggested-command` or by rolling it into a follow-up plan with `/breakdown FU-### from <plan-path>`. If no plan is associated, include the would-be entries inline in the report so the user can paste them. Write these entries `status: open`: a finding is never recorded as `status: scheduled`, because only `/breakdown` schedules work into another plan and only with a `scheduled-in:` path beside it.
7. **Refresh the plan index.** Whenever the run touched an associated plan file, call `/plan-index update <NN>` (where `<NN>` is that plan's ordinal) so `docs/wip/plan/00-index.md` follows. Two cases matter and both are easy to miss: appending deferred findings in step 6 changes the plan's open-follow-up count and can add a *Needs attention* item, and a **clean** exit is what makes the change CSPA-complete, which is a State the roll-up reports. Left out, the index keeps publishing a follow-up count the plan body has already moved past. If `00-index.md` does not exist yet, `/plan-index build` creates it first. The index is a **derived roll-up**, never the source of truth — transient, and not committed unless the user explicitly asks.

   `/sync-check` never writes a relocation glyph. It is read-only over the plans and moves no phase: where a finding shows the work landed under a different plan, record it as a follow-up naming that plan and leave `/breakdown` to mark the parent's phase `↗<NN>` when the entry is scheduled. Keeping one writer for `↗<NN>` is what stops two commands disagreeing about where a phase went.

The drift taxonomy and the report format are defined by `@default/skills/sync/sync-check/references/`. This command file does not duplicate them.

## Required output structure

### Header
- Toolchain probe results (T1–T4 availability).
- Scope, timestamp, git HEAD.
- Run mode (`report` or `fix`).

### Summary counts
- INTENT-DRIFT: N
- CONTRACT-DRIFT: N
- REALITY-DRIFT: N
- SCOPE-GAP: N

### Findings table
- One row per finding: `component · aspect · expected · actual · label · tier · likely source · suggested action`.

### Framework-gate status
- **Build:** `<command>` — pass/fail (Practice-Pack source).
- **Lint:** `<command>` — pass/fail (Practice-Pack source).
- **Integration tests:** the integration-test command(s) the plan defined, with pass/fail and a short failure excerpt if any. For each integrating service: how it was brought up (test container image+version, or stub service + contract source). If neither was specified by a Practice Pack and the user had not yet chosen, surface the gap and stop — do not pick on the user's behalf.
- **Security scan:** `secscan` over `<scope>` at severity floor `<floor>` — pass/fail (count of findings at or above floor).

### Verdict
- **clean** — drift counts all zero (or every drift finding accepted with a written reason and persisted as a Follow-up where a plan is associated) **and** all four framework gates are green (build, lint, integration suite, secscan; with secscan findings either zero or all accepted with a written reason). The change may close.
- **dirty** — one or more drift findings unresolved, or any of the four framework gates has not passed (or has not been run). Surface the resolution commands per finding and per failed gate. The change is **not** complete.

### Accepted findings (only present if any are accepted)
- For each accepted finding (drift or secscan): the finding row, the user's written reason for accepting it, and the timestamp.

## File-writing rules

- `/sync-check` writes nothing by default. The report is returned in the response.
- If the user explicitly asks for a saved report, write to `sync-check-<timestamp>.md` at the repo root.
- In `mode: fix`, no patch is written. The underlying skill only **proposes** patches. The user invokes `/spec`, `/apply`, `/sync-spec`, or `/sync-code` explicitly to apply any of them.

## Where this command sits in the lifecycle

`/sync-check` is the **exit gate** of the four-move CSPA loop. Every door's path ends here:

```
greenfield:  /design → /spec → /breakdown → /apply → /sync-check   (clean → done)
change:      /rfc    → /spec → /breakdown → /apply → /sync-check   (clean → done)
incident:    /rca   [→ /spec] → /breakdown → /apply → /sync-check  (clean → done)
```

A change is not complete until `/sync-check` exits clean. This is the CSPA invariant ***no exit without sync***.

---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:lifecycle:apply"
  name: /apply
  version: 1.4.0
  owner: gatblau
  description: "Applies a single phase of a plan and stops at that phase's exit checks."
description: Apply a single phase of a plan (or an in-context plan/RCA) using Patch → Review. Stops at that phase's exit criteria.
argument-hint: "[topic | plan path] <phase number> (e.g. /apply nats-key-rotation 2, /apply docs/wip/plan/03-nats-key-rotation.md 2, or just \"2\" to use an in-context plan/RCA)"
---

# /apply — Execute One Plan Phase

You have been given the following input:

```
$ARGUMENTS
```

Parse `$ARGUMENTS` to extract:
- **Plan source:** either a **topic shorthand** (kebab-case — `nats-key-rotation` resolves to the highest-numbered `docs/wip/plan/NN-nats-key-rotation.md`) or a path to a plan file. Plans normally live under `docs/wip/plan/<NN>-<slug>.md` (e.g. `docs/wip/plan/03-nats-key-rotation.md`), but any path the user supplies is acceptable. **Optional** — if omitted, fall back to the most recent plan or RCA produced in the current conversation context (see "In-context fallback" below).
- **Phase number:** the phase to implement (integer). Required.

### In-context fallback

If no plan path or issue id is supplied:

1. Scan the current conversation for the most recent artefact that looks like either:
   - a **plan** (phased structure with explicit phases, exit criteria, and open assumptions — e.g. produced by `/plan` or similar), or
   - an **RCA** (root-cause analysis with ranked hypotheses — e.g. produced by `/rca`).
2. If exactly one such artefact exists, use it as the plan source. State clearly in the output which artefact you selected and that it came from conversation context (not a file).
3. If the selected artefact is an **RCA** rather than a phased plan, it has no numbered phases. In that case:
   - Treat the top-ranked hypothesis's **What to verify next** / remediation as a single implicit "Phase 1".
   - Only proceed if the user supplied phase number is `1`. Otherwise stop and ask the user to either supply a real plan file or confirm they want Phase 1 of the RCA-derived fix.
   - Require that the top hypothesis is labelled **high confidence** in the RCA. If it is medium/low, stop and tell the user to verify the hypothesis first (per the Infer-mode discipline) before patching.
4. If zero or multiple candidate artefacts are present in context, stop and ask the user to disambiguate — do not guess.

If the phase number is missing or ambiguous, ask the user once and stop. Do not guess the phase. Do not pick the "next" phase on your own.

### Adaptive-lane duties (Trivial / Local — plan source is an `/rfc` Change brief)

When the plan source is a **Change brief held in conversation context** from `/rfc`'s Trivial or Local lane (see the `/rfc` command and the `triage` skill), this command carries the lane's persistence duties:

- **Local lane.** After applying the patch (step 6), append the five-field **Change addendum** — *what · why · gaps · tests touched · surface impact* — in place to the existing Component spec that covers the area, summarising the brief's reasoning into the *why* field. *Surface impact* must read `none`; any other value is a lane-invariant violation — halt loudly and instruct re-entry via the Standard lane (auto-escalation is never silent). Record a one-line **Scope attestation** for every other artefact type in the `/sync-check` evidence record.
- **Trivial lane.** Patch only — no spec touch. Record Scope attestations for every non-Component-spec artefact type in the `/sync-check` evidence record.
- **Eval breadth scales with the lane** (Trivial: smoke plus directly-touched checks; Local: component-scoped set; Standard: full suite). The four mandatory framework gates in step 7 are **not** scaled — they run in full on every lane.

If mid-phase any triage signal turns positive (an unforeseen surface change, the diff growing beyond the declared component, a schema touch), stop, preserve the partial brief/addendum as evidence, and instruct the user to re-enter via the Standard lane.

## Active modes

**Patch → Review**, with the `sql-safety` layer rule activating whenever the phase touches `schema/**` or `*.sql` and the `identifier-verification` layer rule active throughout.

- **Patch** for steps 6 (apply the patch). Code edits scoped to source files.
- **Review** for step 7 (run the phase's exit criteria) and the post-execution report.
- **Plan**, on the Local lane only, for the single bounded spec write: appending the Change addendum to the affected Component spec.

The command enters **Execute** transiently to run the exit-criteria commands and **Escalate** when any precondition has drifted, when an exit-criterion fails out of scope, or when the patch would require a commit (commits are explicit user actions).

When it escalates, it emits Escalate mode's stop shape (`urn:ordin:default:rules:modes:escalate-mode`) and nothing else: what is blocked in plain language, the two or three options, **one recommendation with its reason**, and the evidence last. A stop that surveys the options without choosing between them is an incomplete stop.

This command applies **exactly one phase**. Do not start the next phase, even if it looks trivial. The user will re-invoke `/apply` for subsequent phases.

## Procedure

1. **Load the plan.** If a plan path was supplied, read the plan file; if it does not exist, stop and tell the user. If no plan source was supplied, use the in-context fallback above and treat the selected conversation artefact as the plan.
2. **Locate the phase.** Find the section for the requested phase number. If it does not exist, list the available phases and stop. For an RCA-derived fallback, the only valid phase is `1` (the remediation for the top hypothesis).
3. **Re-verify preconditions.** For every file, symbol, signature, route, config key, env var, schema object, or external interface the phase says it will change, confirm it currently exists in the repo with Read/Grep. Note any drift from what the plan claimed. If a precondition drift resembles a CONTRACT-DRIFT finding (spec says X, code says Y, and the plan aligns with the spec), proceed with the patch as planned. If it resembles REALITY-DRIFT (code was recently changed and the plan would revert that change), stop and surface it — the plan may be stale.
4. **Check open assumptions.** Re-read the plan's **Open assumptions** section. If any assumption marked **blocking** (or any assumption this phase depends on) is still unverified, stop and surface it — do not patch.
5. **Respect prior phases.** If earlier phases were prerequisites and their changes are not present in the repo, stop and tell the user which earlier phase appears unimplemented.
6. **Apply the smallest viable patch.** Make only the edits this phase requires. Match existing project conventions. No opportunistic refactors, renames, or "while I'm here" cleanups. No new helpers/abstractions unless the plan calls for them and they are verified.
7. **Run the exit criteria.** Execute the exact commands listed under the phase's **Exit criteria**, **plus the four mandatory framework gates** below. Exit criteria are **integration-test-shaped, not unit-test-shaped**: they exercise the change end-to-end through real interfaces (HTTP, message bus, DB) with integrating services brought up as black boxes. Unit tests may still run as part of the build, but they do not satisfy the exit gate on their own.

   **Mandatory framework gates** (run on every `/apply` phase, in addition to the plan's named exit criteria):

   1. **Build green.** The project's build command exits zero. The build command is supplied by the active Practice Pack's project-conventions; if the workspace is running with no Practice Pack and no project-conventions file declares a build command, **stop and ask the user** rather than guess.
   2. **Lint green.** The project's lint command exits zero. Same Practice-Pack lookup rule as build.
   3. **Integration suite green.** The plan's integration tests pass under the test-containers / stub-services regime described below.
   4. **Security scan clean.** Run `secscan` (`urn:ordin:default:skills:analysis:secscan`) with `mode: gate` over the changed files in this phase. The phase passes only if `secscan` returns zero findings at or above the project's configured severity floor (default `medium`), or every finding is explicitly accepted by the user with a written reason recorded in the phase output. The severity floor is a Practice Pack setting; the workspace default is `medium`.

   The four gates are non-overridable. A plan may add stricter exit criteria; it may not weaken or remove any of these four. A `--no-verify` or equivalent skip is forbidden — see step 8.

   **Integration-test details:**
   - **Integrating services must be real where possible** — spin them up via the project's test-container tooling. The choice of tool is a Practice Pack concern; the workspace does not name one. Use the same image and version the project uses elsewhere; do not invent a version.
   - **Where a real service cannot be containerised** (proprietary appliance, third-party SaaS, hardware peripheral), materialise a **stub service** that honours the same wire contract — same protocol, same surface, deterministic responses. Record the stub's contract source in the phase output.
   - **Technology choice:** if the active Practice Pack mandates specific test-container or stub tooling, use it. If it does not, **stop and ask the user** which technology to use. Do **not** silently pick a tool.

8. **If a check fails:** diagnose the root cause, fix it within the same phase if it is in-scope, and re-run. Do not weaken or skip the criteria. Do not `--no-verify` past hooks. If the failure is out of scope for this phase, stop and report. Failure of any of the four mandatory framework gates blocks phase completion regardless of whether the failure is in or out of scope.
9. **Persist follow-ups and risks back to the plan.** Anything surfaced during this phase that the plan should track (out-of-scope work, deferred clean-ups, late-breaking risks, or accepted findings) is appended to the plan file under the structured **Follow-ups** and **Risks** sections defined in `/breakdown` — one entry per item, with `id`, `title`, `why`, `severity`, and `suggested-command`. This makes them re-invokable later via `/breakdown <plan-path>` (to roll selected entries into a follow-up plan) or directly via the suggested command. **Score `severity:` against `/breakdown`'s rubric before writing the entry, and promote it if it scores `critical` or `high`:** append a phase to the plan's `## Phases` section for it and set the entry `status: scheduled` with `scheduled-in:` naming that phase. A `critical` or `high` entry left out of the strip lets this plan read as fully applied while work the phase itself judged important is outstanding — which is the one thing the roll-up exists to prevent. `medium` and `low` entries stay in the list and are what the Open-FUs column counts. If the plan source is in-context (no file), include the same structured entries inline in the response so the user can capture them.
10. **Record the phase outcome in the plan, then refresh the index.** First write the phase's status marker into the **plan file itself**. The plan body is the source of truth the index is derived from, so a phase whose outcome appears only in this response reads as `❔ unknown` on the next `/plan-index build` — the run is invisible to every later reader. Use the glyph vocabulary the `/plan-index` legend owns (`urn:ordin:default:commands:lifecycle:plan-index`) rather than restating it: `✅` when every exit criterion and framework gate passed, `🟡` when the phase landed with a sub-item deferred to a follow-up, `⏳` when the code is complete but a named gate has not been run, `🔒` when it is blocked on an operator action, and `↗<NN>` when this phase's work has moved to plan `<NN>`. The destination ordinal is part of the relocation glyph and is never omitted; if the trail records a move whose destination you cannot verify in the plan, write `↗?` and say so in the phase note — never guess an ordinal. Then call `/plan-index update <NN>` (where `<NN>` is this plan's ordinal) so the phase glyph, done/total, committed cell, and open-follow-up count refresh in `docs/wip/plan/00-index.md`. If `00-index.md` does not exist yet, `/plan-index build` creates it first. The index is a **derived roll-up**, never the source of truth — it is transient (it lives alongside the plans in `docs/wip/plan/`) and is not committed unless the user explicitly asks. Skip this step only when the plan source is in-context (there is no plan file to index).
11. **Do not commit** unless the user explicitly asked. The command produces diffs and runs checks; commit/PR is a separate step and an explicit user action.

## Required output structure

### Phase being implemented
- Phase number, title, and the plan source (file path, or "in-context plan" / "in-context RCA (top hypothesis)" if using the fallback).

### Verified preconditions
- Each precondition the phase depends on, with `path:line`. Note any drift from the plan and how you handled it.

### Assumptions
- Anything still unverified. Otherwise list and proceed.
- If blocking, **stop here** and render Escalate mode's stop shape in place of the remaining sections: what is blocked in plain language, the options, one recommendation and why, evidence last. Do not also write out the sections the stop made empty.

### Changes applied
- For each edited/created/deleted file: path and one-line description of the edit and why. Reference the plan's bullet that motivated it.

### Exit criteria results
- The four mandatory framework gates, each with pass/fail and a short excerpt of failure output if any:
  - **Build:** `<command>` — pass/fail.
  - **Lint:** `<command>` — pass/fail.
  - **Integration tests:** `<command>` — pass/fail.
  - **Security scan:** `secscan` — pass/fail (findings at or above `<severity-floor>`).
- Each command from the plan's named exit criteria, with pass/fail and a short excerpt of failure output if any. Include the behavioural check result.
- For every integrating service: how it was brought up (test-container image + version, or stub service + contract source). If the user was asked to choose tooling because no Practice Pack mandate applied, record the choice they made and why.
- For any accepted secscan finding: the finding row, the user's written reason, and the timestamp.

### Lane evidence (Trivial / Local lanes only)
- **Local:** the Component spec path the Change addendum was appended to, plus the Scope attestation lines recorded for the other artefact types.
- **Trivial:** the Scope attestation lines recorded.
- Omit this section entirely on the Standard lane.

### Risks and follow-ups
- Side effects, compatibility concerns, or items the plan deferred to later phases that this implementation surfaced. Do not act on them.
- For each item, also append a structured entry to the source plan file under **Follow-ups** or **Risks** (per `/breakdown`'s schema: `id`, `title`, `why`, `severity`, `suggested-command`). State in the response which entries were appended and to which file, and name any entry that scored `critical` or `high` together with the phase it was promoted into. If the plan was in-context (no file), reproduce the structured entries inline so the user can paste them into a plan later.

### Status
- One of: **Phase {n} complete — exit criteria met** / **Phase {n} blocked — see Assumptions/Exit criteria results**. If complete, point the user at the next phase number to invoke (`/apply <plan> <n+1>`) without starting it.

### Final-phase handoff to /sync-check

When the **last** phase of the plan exits clean, the change is implementation-complete but **not yet CSPA-complete**. The next and final move of the four-move loop is `/sync-check`, which verifies Design ↔ Spec ↔ Code alignment.

- One-line suggested invocation: `/sync-check`.
- A change is CSPA-complete only when `/sync-check` exits **clean** — either zero findings across all four labels, or every finding explicitly accepted with a written reason. This is the CSPA invariant *no exit without sync*.
- If `/sync-check` reports drift, follow the per-label resolution: INTENT-DRIFT → re-run `/spec`; CONTRACT-DRIFT → re-run `/apply` for the affected component; REALITY-DRIFT → user picks between code revert and spec update; SCOPE-GAP → human triage.

For non-final phases, the handoff is the next phase: `/apply <plan> <n+1>`. Do not point at `/sync-check` until the final phase has exited.
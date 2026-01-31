---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:lifecycle:breakdown"
  name: /breakdown
  version: 1.3.0
  owner: gatblau
  description: "Breaks a diagnosis such as a root-cause analysis, drift report, or issue into an incremental, phased plan. Saves the plan when it is large."
description: Break a structured diagnosis (RCA, sync-check report, specgen Playbook excerpt, design delta, issue description) into an incremental implementation plan, in Plan mode. Writes docs/wip/plan/NN-<slug>.md when the plan is large.
argument-hint: "<paste diagnosis text, or path to a saved diagnosis file>"
---

# /breakdown — Decompose a Diagnosis into a Phased Plan

You have been given the following diagnosis as input:

```
$ARGUMENTS
```

If `$ARGUMENTS` is empty, ask the user to either paste a diagnosis or provide a path to a saved file. Stop until they reply.

If `$ARGUMENTS` looks like a file path, Read it. Otherwise treat the argument text as the diagnosis itself.

## Accepted input types

The breakdown procedure is input-agnostic. Typical inputs:

- **`/spec` Phase 5 Generation Playbook** (`docs/spec/phase-5-playbook.md`) — the canonical greenfield input. Contains the ordered build checklist that maps directly onto phases.
- **`/spec` updated component spec** (`docs/spec/components/<ComponentName>.md`) — the canonical input for change requests where `/spec` Branch B has updated intent and the build set is bounded by the change.
- **`/rfc` output** (`docs/wip/rfc/<NN>-<slug>.md`) — only when the RFC has been classified as *no-intent-change* and `/spec` is being skipped. The default RFC flow goes through `/spec` first.
- **`/rca` output** — ranked root-cause hypotheses with evidence. Use as direct input only for the REALITY-DRIFT sub-case (verified high-confidence hypothesis where the spec is already correct). For intent-changing or spec-drift sub-cases, run `/spec` first.
- **`/sync-check` report** — CONTRACT-DRIFT, INTENT-DRIFT, REALITY-DRIFT, or SCOPE-GAP findings to close. INTENT-DRIFT findings should usually go through `/spec` first.
- **Design-doc delta or git diff** — describing intent change that needs a code response. Prefer routing through `/spec` to update the component specs first.
- **Plain-text issue description** — bug report, feature request, customer-reported symptom. The least-structured input; verification rigour is highest here.
- **Follow-up / risk entries from an existing plan** — invoked as `/breakdown FU-001[,FU-003,RISK-002] from <plan-path>` (where `<plan-path>` is typically `docs/wip/plan/<NN>-<slug>.md`). The command reads the named entries from that plan's **Follow-ups** / **Risks** sections, treats their `title` + `why` + `suggested-command` as the diagnosis, and produces a *follow-up plan* in a new file `docs/wip/plan/<NN'>-<new-slug>.md` (with `NN'` being the next free ordinal in `docs/wip/plan/`). The original plan's entries are updated in place to `status: scheduled` with a `scheduled-in: docs/wip/plan/<NN'>-<new-slug>.md` field — they are not deleted. If any named entry is missing or already `done`/`dropped`, stop and surface the conflict before writing.

Anchor on the named evidence in the input, verify it against the repo, then decompose into phases. **Verification rigour scales with input quality:** RCA and sync-check outputs carry concrete signals (file paths, symbol names, drift labels); plain-text issues carry few, so more preconditions will end up under **Open assumptions** and the plan will be gated on verifying them before Phase 1.

## Active modes

**Plan**, with the `identifier-verification` layer rule active throughout and `sql-safety` activating whenever a planned phase touches `schema/**` or `*.sql`.

The command consumes verified inputs (RCA, sync-check finding, `/rfc`) and produces a phased plan. Plan-mode authoring rules apply: atomic phases, explicit exit criteria, no banned phrases. **Observe** is used transiently to verify the input's named identifiers against the repo before decomposing — but the primary mode is Plan.

The command never enters Patch — `/apply` does that, one phase at a time. **Escalate** when the input's top claim is not verified against the repo (the plan is gated on verification, not built on assumption) or when a phase cannot be made atomic without inventing a step.

## Procedure

1. **Anchor on the diagnosis.** Identify the specific claim to plan against: top-ranked RCA hypothesis, set of sync-check findings to close, Playbook steps to implement, intent change to respond to, or requirement from the issue text. If multiple candidates are tied or ambiguous, ask the user which to plan against, or plan against the first and flag the assumption.
2. **Verify before planning.** For every file, symbol, route, table, function, or env var the plan will touch, confirm it exists by reading the repo. List anything you could not verify under **Open assumptions** — the plan must not silently depend on them. Issue these checks in parallel in a single message. If the set is large (≥8 targets) or spans distinct clusters (files, symbols, schema objects, routes), dispatch one `Explore` sub-agent per cluster in the same message.
3. **Decompose into incremental phases.** Each phase must be independently shippable (compiles + relevant tests pass) and ordered so that earlier phases reduce risk for later ones. Prefer small phases over a single big bang.
4. **Define exit criteria per phase.** Exit criteria are objective and runnable, and are **integration-test-shaped, not unit-test-shaped** — the gate proves integral quality by exercising the change as a black box through real interfaces, with integrating services spun up alongside. Unit tests are allowed and useful, but they do not satisfy the exit gate on their own.
   - Name the exact build commands (e.g. the language's compile/typecheck), the exact integration-test commands (e.g. `make integration-test`, `go test -tags=integration ./...`, `pytest tests/integration/`), the schema/migration verification if the phase touches SQL, and a one-line behavioural check.
   - For every integrating service the phase touches (database, message bus, blob store, external API, peripheral), state how it will be brought up: **real service via test containers** where the technology supports it (preferred), or a **materialised stub service** honouring the same wire contract where containerisation is not feasible.
   - **Tooling choice:** if the active Practice Pack mandates specific test-container or stub frameworks, name them in the exit criteria. If no Practice Pack mandate applies, **stop here and ask the user** which technology to use; offer recommendations grounded in the language and the integrating services in play. Do not silently pick a default.
5. **Decide on file output.** If the plan has more than ~3 phases, more than ~30 actionable steps, or spans multiple packages/schema files, write it to `docs/wip/plan/<NN>-<slug>.md`. Otherwise return inline.
   - **Slug:** pick a short kebab-case description yourself (3–6 words, lowercase) — derive it from the diagnosis anchor or from the source RFC/RCA filename when one is available. Do not ask the user for an id.
   - **Number:** scan `docs/wip/plan/` for existing `NN-*.md` files and use the next free two-digit ordinal. If the directory does not exist, create it and start at `01`.
   - The full path is therefore `docs/wip/plan/<NN>-<slug>.md` (e.g. `docs/wip/plan/04-payment-retry-budget.md`).

## Required output structure

If writing to a file, the file content uses this same structure. Always also reply inline with: the file path written, a one-paragraph summary, and the phase list with exit criteria.

### Anchor (from input)
- One-line restatement of the specific claim being planned against (root cause, drift finding, component to build, intent change, or requirement) and a pointer to the supporting evidence in the input.

### Verified context
- Files, symbols, routes, schema objects you confirmed exist, each with `path:line`.

### Open assumptions
- Anything the plan depends on that is not yet verified. If any item here would block safe implementation, flag it as **blocking** and recommend the user verify before starting Phase 1.

### Scope
- **In scope:** what this plan will change.
- **Out of scope:** what it explicitly will not touch (and why, if non-obvious).

### Phases
For each phase (numbered, in order):

#### Phase {n} — {short title}
- **Goal:** one sentence.
- **Changes:** bullet list of intended edits, each naming the exact file (and symbol where known). Mark unverified targets clearly.
- **Rationale:** why this phase exists and why it comes here in the order.
- **Exit criteria** (all must hold to move on; integration-shaped, not unit-shaped):
  - Code compiles / typechecks (narrowest applicable command).
  - **Integration tests pass** end-to-end against the change. List the exact integration-test invocation(s), the test file(s) added or extended, and how each integrating service is brought up: **real-via-test-containers** (image + version) or **stub service** (contract source). If neither tool nor stub framework is mandated by a Practice Pack, the planner stops at this point and asks the user before fixing the command in the plan.
  - Schema/migration checks (only if the phase touches `schema/**` or `*.sql`): which scripts run cleanly, rollback considerations, what was verified visually in the SQL file.
  - Behavioural check: a one-line scripted verification of the change's observable effect for this phase, run as part of the integration suite.
- **Risks / rollback:** what could regress and how to undo this phase in isolation.

### Cross-cutting validation
- Final end-to-end check after all phases (e.g. `make check`, `make integration-test`, specific HTTP/NATS scenarios). Black-box integration tests with all integrating services brought up; this is the gate `/sync-check` will rely on.

### Follow-ups (not in this plan)

A structured, **append-only**, machine-readable list of work the plan deliberately defers. Both `/apply` and `/sync-check` append to this section as new follow-ups surface during execution. Each entry must be re-invokable on its own — either via the `suggested-command` directly, or by feeding selected entries into `/breakdown <plan-path>` to roll them into a follow-up plan.

For each entry:

```yaml
- id: FU-001                       # stable, never reused; `FU-` + 3-digit ordinal within this plan
  title: <short imperative phrase>
  why: <one sentence — what surfaced this and why it does not belong in this plan>
  source: planning | apply-phase-<n> | sync-check
  severity: critical | high | medium | low
  suggested-command: <e.g. /breakdown FU-001 from docs/wip/plan/<NN>-<slug>.md, or /apply <plan> <n>, or /spec docs/spec/components/X.md>
  status: open | scheduled | done | dropped
  scheduled-in: <plan or RFC path — required when `status: scheduled`; the destination /plan-index reads to build the lineage edge>
  added: <YYYY-MM-DD>
```

Rules:
- Never delete an entry; mark `status: dropped` with a reason in `why`.
- `status: scheduled` without a `scheduled-in:` path is incomplete: it records that the work left this plan without recording where it went, which is exactly the dangling pointer the relocation glyph exists to prevent.
- Never reuse an `id`; new entries always take the next ordinal.
- A follow-up that depends on another follow-up records that with a `blocked-by: [FU-002]` field.
- `severity:` is required on every entry, including entries written `status: done` — the roll-up reads it to decide whether the entry belongs in the phase strip, and an entry with no severity cannot be classified without a guess.

#### Severity — the rubric

Severity records **how much of the plan's stated goal is missing while the entry is open**. It is not the size of the work, not how hard it is, and not how soon anyone intends to do it.

| Severity | Test |
|---|---|
| `critical` | What the plan shipped is unsafe, incorrect, or unusable on its default path while this entry is open. An operator or user hits it without doing anything unusual. |
| `high` | The plan's stated goal is only partly delivered while this entry is open — or the entry is named as the `mitigation:` of a Risk carrying `impact: high`. Reachable on a normal path, and any workaround is manual. **A tier, strand, or phase the plan's own input document declared and this plan did not build scores `high`**, even where this plan's slice of it shipped complete: the capability the input promised is half-delivered, and scoring it against the slice rather than the promise is how a two-tier feature comes to read as finished with one tier built. |
| `medium` | A real gap that degrades quality, with an accepted workaround and no user-visible defect. |
| `low` | Cosmetic, editorial, or convenience work. Nothing about the shipped behaviour is wrong without it. |

#### Critical and high follow-ups become phases

**An open `critical` or `high` follow-up must also exist as a phase in this plan's `## Phases` section.** It is not enough to record it in this list.

The invariant binds entries that are still outstanding — `status: open`, and `status: scheduled` where the destination is a phase of this plan. An entry already `done` or `dropped` needs no phase and gets none: a retroactive phase for closed work inflates the strip's denominator with work nobody is waiting on, and the strip is meant to show what is missing, not to re-narrate what happened. Score closed entries anyway (`severity:` is required on every entry), because the score is what a later reader uses to judge whether the plan closed on the strength of its important work or the weakness of it.

The reason is mechanical. `/plan-index` derives its **Done** column and phase strip from `## Phases` and nothing else, so an entry that lives only in this section is invisible there — which lets a plan read as fully applied (`6/6 ✅ ✅ ✅ ✅ ✅ ✅`) while work the plan itself called important is outstanding. The Open-FUs column is a count, not a strip: it says *how many* are open, never *how much of the plan* they represent.

To promote an entry:

1. Append a phase to `## Phases` in the normal shape — Goal, Changes, Rationale, Exit criteria, Risks / rollback — derived from the entry's `title` and `why`. It takes the next phase ordinal and starts unstarted (`⬜` in the strip).
2. Set the entry `status: scheduled` with `scheduled-in: docs/wip/plan/<NN>-<slug>.md#phase-<N>` — its own plan, naming the phase. `scheduled` is neither open nor done, so the Open-FUs count falls by one as the strip lengthens by one, and the work is counted exactly once.
3. Never delete the entry. The list stays append-only; the phase and the entry are two views of one item, joined by `scheduled-in:`.

**A promoted phase is not a life sentence for the plan.** When the work genuinely belongs elsewhere — a separate strand, a different subsystem, a later tier — run `/breakdown FU-### from <plan-path>`. That writes a new plan, and the promoted phase's glyph becomes `↗<NN>` in the strip, which is how a plan closes without pretending the work vanished. Promotion makes deferred work *visible*; relocation is how it *moves*.

`medium` and `low` entries stay in this section, are not phases, and are what the Open-FUs column counts.

### Risks (not closed by this plan)

Same shape as Follow-ups, but for hazards rather than deferred work — things that could regress in production or surface during build. `/apply` writes Risks here when a phase reveals a hazard that is out of scope for the current plan.

```yaml
- id: RISK-001
  title: <short noun phrase — the hazard, not the action>
  why: <one sentence — what makes this risky and under what conditions it would bite>
  source: planning | apply-phase-<n> | sync-check
  likelihood: low | medium | high
  impact: low | medium | high
  mitigation: <one-line mitigation, OR a `suggested-command` if mitigation is itself a follow-up>
  suggested-command: <optional — e.g. /breakdown RISK-001 from docs/wip/plan/<NN>-<slug>.md>
  status: open | mitigated | accepted | dropped
  added: <YYYY-MM-DD>
```

Rules:
- A `RISK-*` and a `FU-*` may cross-reference each other (`mitigates: RISK-001` on a follow-up, or `mitigation: FU-007` on a risk).
- Accepted risks must record who accepted them in `why`.

## File-writing rules

- Filename: `docs/wip/plan/<NN>-<slug>.md`. The agent picks the slug (short kebab-case, descriptive of the work) and the next free `NN` by scanning the folder. Never ask the user for an id.
- Treat `docs/wip/` as transient: these are working documents that are expected to be deleted once design, spec, and code are back in sync.
- Use the Write tool. If the directory does not exist, create it. Do not overwrite an existing file with the same name without confirming with the user first.
- After writing, reply with: the absolute path, the one-paragraph summary, and the phase titles + exit-criteria one-liners so the user can review without opening the file.

## Register the plan in the index

After the plan file is written — and, for a follow-up breakdown, after the source entry has been set to `status: scheduled` with a `scheduled-in:` field — register the new plan in the working-plan roll-up:

- **Name the destination in the parent.** A follow-up breakdown moves work *out* of the parent plan. Where the entry being scheduled is, or subsumes, one of the parent's phases, mark that phase in the **parent plan body** as relocated to the new plan — `↗<NN>`, carrying the new plan's ordinal. The parent body is what `/plan-index` derives from, so a relocation recorded only in the child leaves the parent's phase reading `❔ unknown`: the reader sees the work did not happen there, but not where to follow it. Use the glyph vocabulary the `/plan-index` legend owns (`urn:ordin:default:commands:lifecycle:plan-index`); never write a bare `↗`.
- Call `/plan-index add <NN>` (where `<NN>` is the new plan's ordinal) to insert its row and lineage edge into `docs/wip/plan/00-index.md`. If `00-index.md` does not exist yet, call `/plan-index build` first to create it.
- For a follow-up breakdown, also call `/plan-index update <parent-NN>` so the parent plan's row reflects the entry now scheduled into the new plan, including the relocated phase's `↗<NN>` glyph in its strip.

The index is a **derived roll-up**, never the source of truth: it lives alongside the plans in `docs/wip/plan/`, shares their transient property, and is not committed unless the user explicitly asks.

## Handoff to /apply

`/breakdown` is **move 3 (Plan increments)** of the four-move CSPA loop. The next move is `/apply`, executed one phase at a time:

- One-line suggested invocation per phase, short form: `/apply <topic> <phase-number>` (the topic resolves to the highest-numbered `docs/wip/plan/NN-<topic>.md`). Long form `/apply docs/wip/plan/<NN>-<slug>.md <phase-number>` is also accepted.
- Phases must be applied in order; `/apply` itself enforces this by checking that earlier phases' changes are present in the repo before patching the current one.
- After the **final** phase exits clean, the user is expected to run `/sync-check` to verify Design ↔ Spec ↔ Code alignment before considering the change complete. This is the CSPA invariant *no exit without sync*.

If any open assumption is **blocking**, state that the user should verify it before invoking `/apply` and **do not** print the handoff line.
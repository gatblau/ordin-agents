---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:intent:rfc"
  name: /rfc
  version: 1.4.0
  owner: gatblau
  description: "Captures a change request as a structured document. First sorts the change into a small, medium, or standard lane and runs the right amount of process for its size. Saves the RFC for larger changes."
invokes:
  - kind: skill
    ref: "urn:ordin:default:skills:quality:triage"
    role: classify
    when: always
  - kind: capability
    ref: "urn:ordin:default:capabilities:spec"
    role: drive-standard-lane
    when: triage.class == "Standard"
description: Capture a Request for Change as a structured document. First runs the `triage` skill to classify the change as Trivial, Local, or Standard and select an adaptive lane. Trivial and Local lanes hold their working notes (Change brief, Scope attestations) in agent context — they are NOT persisted as separate files. The only persistent artefact the small lanes produce is a Change addendum appended to the existing Component spec. Standard lane runs the full path described below. Operates in Observe → Infer → Plan. Writes docs/wip/rfc/NN-<slug>.md when the Standard-lane RFC is large.
argument-hint: "<paste change request text, or path to a saved file>"
---

# /rfc — Request for Change

You have been given the following change request as input:

```
$ARGUMENTS
```

If `$ARGUMENTS` is empty, ask the user to either paste the change request (feature idea, bug description, refactor motivation, customer ask) or provide a path to a saved file. Stop until they reply.

If `$ARGUMENTS` looks like a file path, Read it. Otherwise treat the argument text as the change request itself.

## Purpose

An RFC is the **upstream input** to `/breakdown`. It states what should change and why, anchored in repository evidence, without prescribing an implementation. Think of it as: everything `/breakdown` needs to decompose the work into phases, minus the phase decomposition itself.

Accepted sources that commonly become an RFC:
- **Feature request or enhancement idea** — user-facing capability that does not yet exist.
- **Bug report** — observed behaviour that diverges from intended behaviour.
- **Refactor motivation** — non-functional improvement (performance, maintainability, security posture).
- **Customer-reported symptom** — a narrative that must be converted into concrete acceptance criteria.
- **Design intent delta** — a shift in requirements captured verbally or in chat, not yet written down.

Do **not** use this command to analyse a stack trace (that is `/rca`) or to decompose an already-structured diagnosis into phases (that is `/breakdown`).

## Active modes

**Observe → Infer → Plan**, with the `identifier-verification` layer rule active throughout and the `sql-safety` layer rule activating whenever the change touches `schema/**` or `*.sql`.

- **Observe** for repository inspection: read the surface the change would touch, confirm what currently exists, separate what the user asked from what the code does.
- **Infer** for the trade-off pass: alternatives considered and rejected, risks, scope boundaries.
- **Plan** for the drafted RFC document — an authored artefact, never a source edit.

The command never enters Patch — RFCs are documents, not patches. **Escalate** when an unverified identifier is required to articulate the change (route to *Open Questions* in the RFC, do not invent it).

## Procedure

0. **Run `triage` first.** Load `@default/skills/quality/triage/SKILL.md` and run it against the change request. The skill emits a `triage` block with a proposed class (Trivial · Local · Standard) and a one-line rationale citing the four signals (file scope, surface signal via `apidiff`, schema signal, existing-spec presence — see `@default/skills/quality/triage/references/classification-rubric.md`). Show the block to the user and stop until they confirm the class. The user may force a higher class freely; forcing a lower class requires a written override of a named signal, which `triage` records under `user-override`.

   - If the confirmed class is **Trivial**, jump to step T1 below.
   - If the confirmed class is **Local**, jump to step L1 below.
   - If the confirmed class is **Standard**, continue with step 1 (today's full path).

1. **Restate the request.** In one or two sentences, restate what the user is asking for in your own words. If the request is ambiguous (two plausible interpretations, missing target, unclear success condition), list the interpretations and ask the user which one to RFC against; do not silently pick one.
2. **Anchor in the repository.** For every concrete signal in the request (file path, symbol, route, table, env var, config key, feature name, error string), verify whether it currently exists. Use Grep/Glob/Read. Record exact `path:line` for anything found; record "not found" for anything not found — that is itself evidence. Batch the signal lookups in parallel rather than sequentially.
3. **Capture current behaviour.** Describe what the repository does today in the area the change would touch, citing `path:line`. Do not editorialise. If the current behaviour cannot be determined from the repo alone (e.g. depends on runtime data, external service, user configuration), say so under **Open questions**.
4. **Capture desired behaviour.** State the target state as an outcome a future reader can test against, not as an implementation. Prefer "request X returns Y under condition Z" over "add function foo in bar.go".
5. **Define scope boundaries.** Make **In scope** and **Out of scope** explicit. Call out adjacent areas that are tempting but not part of this change, with a one-line reason.
6. **Draft acceptance criteria.** Each criterion must be **objective and runnable**: an HTTP/CLI scenario, a specific test name, a schema invariant, a log/metric signal, or a user-visible behaviour. Vague criteria ("feels faster", "is cleaner") are banned — convert them into measurable equivalents or move them to **Open questions**.
7. **List constraints.** Non-functional requirements and boundaries `/breakdown` must respect: backward compatibility, performance budget, security posture, deployment ordering, deprecation windows, supported clients, SLAs.
8. **Offer a proposed direction, not a plan.** A single paragraph of high-level approach hints is fine if it helps downstream understanding. Do **not** enumerate phases, files to edit, or function names — that is `/breakdown`'s job. If unsure, leave this section empty rather than speculate.
9. **Collect open questions.** Every unresolved ambiguity that would block `/breakdown` from producing a useful plan. Flag items as **blocking** when `/breakdown` cannot safely proceed without an answer.
10. **Decide on file output.** If the RFC has more than ~8 acceptance criteria, touches more than ~3 concrete files/packages/schema objects, or runs longer than ~200 lines, write it to `docs/wip/rfc/NN-<slug>.md`. Otherwise return inline.
   - **Slug:** pick a short kebab-case description of the change yourself (3–6 words, lowercase, e.g. `nats-key-rotation`, `payment-retry-budget`). Do not ask the user for an id.
   - **Number:** scan `docs/wip/rfc/` for existing `NN-*.md` files and use the next free two-digit ordinal (`01`, `02`, …, zero-padded). If the directory does not exist, create it and start at `01`.
   - The full path is therefore `docs/wip/rfc/<NN>-<slug>.md` (e.g. `docs/wip/rfc/03-nats-key-rotation.md`).

## Required output structure

If writing to a file, the file content uses this same structure. Always also reply inline with: the file path written (if any), a one-paragraph summary, and the acceptance-criteria list so the user can review without opening the file.

### Title
- One-line title of the change. Match the slug used in the filename (e.g. for `docs/wip/rfc/03-nats-key-rotation.md`, a fitting title is `NATS key rotation without restart`).

### Restated request
- Your one-or-two-sentence restatement of what the user is asking for. Note any interpretation choices you had to make and which one you went with.

### Motivation
- Why this change matters. Anchor in the original request. Do not invent business context that was not stated.

### Current behaviour
- What the repository does today in the affected area, with `path:line` citations. Mark anything you could not verify as **unverified**.

### Desired behaviour
- The target state as an observable outcome. No implementation detail. No file names unless the user specified them.

### Scope
- **In scope:** what this RFC intends to change.
- **Out of scope:** adjacent work this RFC will not touch (one-line reason each).

### Acceptance criteria
- Numbered, objective, runnable criteria. Each item should be directly testable (named test, HTTP/CLI scenario, schema invariant, metric/log signal, user-visible behaviour).

### Constraints
- Non-functional requirements `/breakdown` must respect (compatibility, performance, security, rollout, deprecation). Omit the section if genuinely none apply — do not pad.

### Proposed direction (optional)
- One paragraph of high-level approach hints, or omit. Must not prescribe phases, files, or symbols.

### Open questions
- Numbered ambiguities that remain. Flag each as **blocking** or **non-blocking** for `/breakdown`. A blocking item means `/breakdown` should not run until the user resolves it.

### Blocking decisions outstanding (layman language)

If any open question is **blocking**, surface them here in plain English **before** the handoff line — same rule as `/design`. One bullet per blocking question, phrased as a non-specialist would understand it (no jargon, no unexpanded acronyms, no internal codenames), ending in a one-sentence trade-off ("If we go with A, X happens; if we go with B, Y happens"). Do not reproduce the technical option set or impact column — those stay in the **Open questions** section above. This is the cognitive on-ramp, not the decision record. If a blocking question cannot be summarised without jargon, treat it as not yet ripe and recommend another scoping pass.

### Handoff to /spec (or /breakdown)

This is the **change door** of the four-move CSPA loop. The next move depends on whether the change introduces or alters intent:

- **Intent-changing RFC (default)** — the affected component spec(s) must be updated *before* code is patched, per the CSPA rule *fix the prompt first*. Suggested invocation: `/spec docs/wip/rfc/<NN>-<slug>.md`. After `/spec` exits clean (Phase 6 audit passed), proceed with `/breakdown` against the updated component spec or the RFC.
- **Pure code-shape change with no intent change** (rare in RFC flow — common in RCA flow) — proceed directly to `/breakdown` with the RFC as input. If you are unsure, run `/sync-check` first; if it shows zero INTENT-DRIFT and zero CONTRACT-DRIFT for the affected components, the spec is already current and the skip is safe.

If any open question is **blocking**, state that the user should resolve it first and **do not** print a handoff line.

The full lifecycle from this door: `/rfc → /spec → /breakdown → /apply → /sync-check`.

## Trivial-lane procedure

T1. **Hold Scope attestations in agent context.** Compose a one-line attestation per non-Component-spec artefact type (HLD, Spec preamble, System architecture, Cross-cutting spec, Generation playbook) asserting that the change does not affect it, citing the diff. These are not separate files — they are evidence that `/sync-check` will record into its log entry for this change. No Change brief. No Component spec touch.

T2. **Hand off to `/apply`.** Apply the change. Framework gates run uniformly; eval breadth is reduced to smoke + directly-touched evals.

T3. **Hand off to `/sync-check`.** The exit gate accepts the Scope attestations as evidence-log entries; drift count must be zero; framework gates green.

## Local-lane procedure

L1. **Compose the Change brief in agent context.** A one-page summary the agent uses to drive `/apply` — change summary · affected component · evidence (`path:line`) · decision · plan steps · gaps. **Not persisted by default.** It lives in the conversation; if the user wants a copy they may write it to `.scratch/<slug>.md`, which is gitignored. The brief's reasoning lands in the addendum's *why* field on Apply, so the rationale survives.

L2. **Compose Scope attestations in agent context.** One line each for the five non-Component-spec artefact types, generated from the diff and confirmed by the user. These are evidence that `/sync-check` will record into its log entry for this change — not separate files.

L3. **Hand off to `/apply`.** `/apply` reads the brief and attestations from agent context as a fused-move input (no `/spec` or `/breakdown` invocation required). Framework gates run uniformly; eval breadth is reduced to component-scoped evals.

L4. **`/apply` appends the Change addendum to the existing Component spec.** A ≤10-line block at the bottom of the affected Component spec, fields: *what · why · gaps · tests touched · surface impact*. `surface impact` must read `none` — any other value forces auto-escalation to Standard per `@default/skills/quality/triage/references/escalation-triggers.md`. This is the **only persistent artefact** the Local lane produces.

L5. **Hand off to `/sync-check`.** The exit gate accepts the Change addendum on the affected Component spec with `surface impact: none` plus the Scope attestations recorded as log entries; drift count must be zero; framework gates green.

## File-writing rules

- Filename: `docs/wip/rfc/<NN>-<slug>.md`. The agent picks the slug (short kebab-case, descriptive of the change) and the next free `NN` by scanning the folder. Never ask the user for an id.
- Treat `docs/wip/` as transient: these are working documents that are expected to be deleted once design, spec, and code are back in sync.
- Use the Write tool. If the directory does not exist, create it. Do not overwrite an existing file with the same name without confirming with the user first.
- After writing, reply with: the absolute path, the one-paragraph summary, the acceptance-criteria list, and any **blocking** open questions so the user can decide whether to resolve them before invoking `/breakdown`.

## Close the loop on the entry that prompted this RFC

Plan follow-ups and risks routinely carry `suggested-command: /rfc …`. When this RFC was authored from such an entry, record that in the **parent plan**, or the roll-up keeps counting the entry as untouched work:

- Set the source entry to `status: scheduled` with `scheduled-in:` pointing at this RFC's path. The field takes a plan **or** an RFC path — an RFC is a legitimate destination for deferred work, and the corpus already uses it that way.
- Call `/plan-index update <parent-NN>` so the parent's open-follow-up count and *Needs attention* bullets follow. If `00-index.md` does not exist yet, `/plan-index build` creates it first.

`/rfc` never writes a relocation glyph. An RFC is not a plan and holds no phases, so nothing has moved yet: a phase becomes `↗<NN>` only when `/breakdown` produces the destination plan and marks the parent there. Do not pre-empt that ordinal — the plan it names does not exist until `/breakdown` runs.
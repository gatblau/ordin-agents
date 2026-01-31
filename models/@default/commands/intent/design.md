---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:intent:design"
  name: /design
  version: 1.2.0
  owner: gatblau
  description: "Takes a problem to a structured design document by interview, or captures a change request as an RFC."
invokes:
  - kind: skill
    ref: "urn:ordin:default:skills:quality:designgen"
    role: drive-procedure
    when: always
description: >-
  Capture a High-Level Design (HLD) — system context, architecture, principal sequences, tech stack, regulatory context, ADRs, cross-cutting stances — from one of three input sources: greenfield interview, inline draft, or scanning an existing codebase (code-evidence). Drives the `designgen` skill. Produces input suitable for `/spec`. Writes either `docs/design/<topic>/` (folder form, Standard lane) or `docs/design/<topic>.md` (single-file form, Trivial / Local lane). In code-evidence mode the document also contains a Requirements section. The HLD is a living document — `/spec` auto-amends it via the HLD-impact-pass as low-level questions surface.
argument-hint: "<topic name, kebab-case (e.g. nats-key-rotation)> [interview|draft|code-evidence] [code-paths: <comma-separated paths> — required for code-evidence] [hld-form: folder|single-file]"
---

# /design — Greenfield High-Level Design

You have been given the following input:

```
$ARGUMENTS
```

Parse `$ARGUMENTS` to extract:

- **Topic** (required): a short kebab-case feature or problem name (e.g. `nats-key-rotation`, `appliance-telemetry`, `legacy-payment-service`). Used as the filename seed.
- **Mode** (optional): `interview` (default for greenfield — ask questions, then draft), `draft` (skip the interview and draft directly from inline context), or `code-evidence` (scan an existing codebase and draft an as-built design plus Requirements).
- **Code paths** (required when `mode: code-evidence`, otherwise unused): one or more repo-relative directories or files to scan. If `code-paths` is supplied without an explicit `mode`, the command infers `mode: code-evidence`.
- **Include requirements** (`code-evidence` only, default `true`): set to `false` to suppress the Requirements section.

If `$ARGUMENTS` is empty, or does not contain a topic, ask the user for the topic (kebab-case), the mode, and — if the user describes brownfield work or names existing files — the code paths to scan. Stop until they reply.

## Purpose

`/design` is the **front door** to the CSPA-431 lifecycle for any work that captures *what we are about to build (or have already built) and why, and how the parts fit together at a system level*. It produces a **High-Level Design (HLD)** under `docs/design/` that the next move (`/spec`) consumes to produce the Low-Level Design (LLD) spec set.

The HLD owns: system context, system architecture, principal sequences, domain model, tech stack, regulatory context, architectural decisions (ADRs), cross-cutting stances, NFRs, and external interfaces (names and shapes only). Wire-level detail — exact field types, error codes, retry counts, JSON schemas, Gherkin scenarios — belongs in `/spec`, not in `/design`.

**The HLD is a living document.** When `/spec` encounters an HLD-shaped question while drafting the LLD, it routes that finding back to the HLD via the HLD-impact-pass (auto-drafted edit, user-reviewed in the same combined diff as the spec output). The four CSPA moves do not change — this is plumbing, not a new ceremony.

The command supports three input sources:

- **Greenfield interview.** The system being designed does not yet exist — there is no code to anchor against. The user is starting a new feature, capability, or service from a problem statement, product vision, or customer ask. The skill asks targeted questions and drafts the design.
- **Inline draft.** The user has enough inline context (a written brief, a prior conversation, a doc) that the interview would be ceremony. The skill drafts directly.
- **Code-evidence (brownfield).** A system already exists and the user wants to recover an as-built design from it — to retrofit documentation, to instigate a rewrite, or to align the existing system with the CSPA lifecycle. The skill walks the supplied code paths, drafts an as-built design with `[evidence: path:line]` tags, and produces a Requirements section that classifies each observed behaviour as *Must preserve*, *Observed but not required*, *Drop candidates*, or *Gaps*.

Do **not** use this command to:

- Capture a change to existing code (that is `/rfc`).
- Analyse a stack trace or incident (that is `/rca`).
- Decompose an already-structured design into phases (that is `/breakdown`).
- Edit an existing design document — `designgen` never overwrites silently; use a direct edit instead.
- Perform a rewrite. Code-evidence mode produces the input to a rewrite (an as-built design plus Requirements). The rewrite itself is a separate `/breakdown` → `/apply` cycle.

## Active modes

**Observe → Infer → Plan**, with the `identifier-verification` layer rule active throughout.

- **Observe** for the intake, targeted interview, and ambiguity-sweep phases of the underlying skill: listen, do not invent. In `code-evidence` mode this phase dominates the run — every claim in the eventual draft must be traceable to evidence read from the supplied paths.
- **Infer** when ranking alternatives the user proposed against best-practice patterns and surfacing trade-offs the user may not have considered. In `code-evidence` mode, also when classifying each observed behaviour into the four Requirements subsections.
- **Plan** for drafting the document and the verification pass before writing the file. The output is an authored artefact under `docs/design/`, never source code.

The command never enters Patch — HLDs are documents, not patches. **Escalate** when:

- an ambiguity probe returns no concrete answer after one targeted follow-up,
- the user cannot articulate a problem statement clear enough to interview against,
- the file already exists at `docs/design/<topic>.md` (the underlying skill never overwrites silently — surface the conflict and ask the user how to proceed),
- in `code-evidence` mode: the supplied paths return no readable code, the codebase relies on runtime reflection or DSLs to a degree static reading cannot determine the public surface, or more than half the candidate behaviours from the scan land in *Gaps*.

## Procedure

This command **delegates its procedure to the `designgen` skill** (`@default/skills/quality/designgen/SKILL.md`). The skill's five-phase flow — intake, targeted interview, ambiguity sweep, draft, self-check — is canonical. Do not restate or override it here.

1. **Load the `designgen` skill** and pass through the `topic`, `mode`, `code-paths`, and `include-requirements` arguments.
2. **Run the skill end-to-end.** Phase 1 (intake — interview style for `interview`/`draft`, code-walking style for `code-evidence`), Phase 2 (targeted interview — greenfield questions for `interview`, intent-confirmation questions for `code-evidence`, skipped for `draft`), Phase 3 (ambiguity sweep), Phase 4 (draft), Phase 5 (self-check before writing).
3. **Receive the file path and summary.** The skill writes to `docs/design/<topic>/` (folder form, Standard lane) or `docs/design/<topic>.md` (single-file form, Trivial / Local lane) and returns the absolute path, a one-paragraph summary, the count of assumptions and open questions, and — in `code-evidence` mode — the count of entries in each Requirements subsection.
4. **Decide on the handoff.** If the design has any **blocking** open questions, surface them to the user and stop — do not suggest `/spec` until they are resolved. Otherwise, recommend the next move (see *Handoff to /spec* below).

The HLD shape (Summary · Motivation · Goals · Non-goals · Glossary · System Context · System Architecture · Principal Sequences · Domain Model · Data Lifecycle · Tech Stack · Regulatory Context · Cross-cutting Concerns · NFRs · External Interfaces · Architectural Decisions · Assumptions · Open Questions · Risks · Alternatives · Dependencies · Rollout / Rollback; in code-evidence mode, also Requirements) is defined by `@default/skills/quality/designgen/references/design-template.md`. This command file does not duplicate it. If the shape changes, it changes once, in the skill's references.

## Required output structure

The authored artefact is `docs/design/<topic>.md`, structured per `@default/skills/quality/designgen/references/design-template.md`. The reply this command returns to the user contains:

### File written
- Absolute path to `docs/design/<topic>.md`.

### Summary
- One paragraph describing what the design covers.

### Counts
- Number of assumptions recorded.
- Number of open questions, split into **blocking** and **non-blocking**.
- In `code-evidence` mode, also: counts for each Requirements subsection (*Must preserve*, *Observed but not required*, *Drop candidates*, *Gaps*).

### Blocking decisions outstanding (layman language)

If any open question is marked **blocking**, surface them here in plain English **before** the handoff line. The goal is to reduce cognitive load on a developer who has just context-switched in:

- One bullet per blocking question.
- Phrase as a **question a non-specialist would understand**: short sentence, no jargon, no acronyms without expansion, no internal codenames.
- Each bullet ends with a **one-sentence trade-off**: "If we go with A, X happens; if we go with B, Y happens." No more than that.
- Do **not** list the technical option set, the impact-matrix, or rationale here — those live in the Open Questions table inside the HLD. This section is the cognitive on-ramp, not the decision record.
- If a blocking question genuinely cannot be summarised without jargon, that is a signal the question is not yet ripe — state that and recommend another `/design` interview pass rather than handing off.

### Handoff to /spec
- One-line suggested invocation in short form: `/spec <topic>` (the topic resolves to `docs/design/<topic>/` if the folder exists, else `docs/design/<topic>.md`).
- If any open question is **blocking**, state that the user should resolve it first and **do not** print the handoff line.

## File-writing rules

- The underlying `designgen` skill writes either:
  - `docs/design/<topic>/` (folder form, Standard lane) — `README.md` + numbered child files `00-overview.md` … `10-risks.md` + an append-only `99-changelog.md` per `@default/skills/quality/designgen/references/hld-folder-layout.md`.
  - `docs/design/<topic>.md` (single-file form, Trivial / Local lane) — all sections inline.
- The form is decided by triage: Standard ⇒ folder, Trivial / Local ⇒ single-file. If `/design` is invoked without a prior `triage` block in context, `designgen` prompts the user for the form.
- If the target path already exists, the skill stops and asks whether to overwrite, extend, or pick a new topic name. Never overwrite silently.
- This command does not write any other file, with one exception: when the run was invoked from a plan's follow-up or risk entry, it closes that entry in the plan — see below. (Subsequent `/spec` invocations may amend the HLD via the HLD-impact-pass — that is owned by `specgen`, not by this command.)

## Close the loop on the entry that prompted this design

A plan follow-up or risk can route here with `suggested-command: /design`. The edge is rarer than the `/rfc`, `/spec` and `/rca` ones, but the rule is the same: when this run was invoked from such an entry, record the outcome in the **parent plan**, or the roll-up keeps counting settled work as open.

- **The design decision is the resolution** — the HLD, or an ADR inside it, now says what the entry asked for: set the entry `status: done` with a one-line note naming the section that changed, and the date.
- **The design only frames the work** — set `status: scheduled` with `scheduled-in:` pointing at the design document. It becomes `done` when the spec set and plan that follow it land.
- Use the schema's status vocabulary (`open | scheduled | done | dropped`) and nothing else. A free-form string such as `status: resolved 2026-01-13 (0e43f8a) — …` reads well to a human and is invisible to `/plan-index`, which counts only what it can parse.
- Either way, call `/plan-index update <parent-NN>` so the parent's open-follow-up count and *Needs attention* bullets follow. If `00-index.md` does not exist yet, `/plan-index build` creates it first.

`/design` writes no relocation glyph. It holds no phases: the HLD it captures reaches a phase only through `/spec` then `/breakdown`, and `/breakdown` alone marks a relocated phase `↗<NN>`.

## Where this command sits in the lifecycle

`/design` is **move 1 (Capture intent)** of the four-move CSPA loop, on the **greenfield door**. The door admits three input sources but the downstream is the same in all three cases: `/spec` consumes the HLD and produces the Spec set.

```
Problem statement      \
Inline context (draft)  →  /design  →  HLD  →  /spec  →  LLD spec set  →  /breakdown  →  Plan  →  /apply  →  Code  →  /sync-check
Existing code paths    /              ↑ you are here   ↑ auto-amends HLD via HLD-impact-pass (plumbing, not a new move)
```

The dashed back-edge from `/spec` to the HLD represents the HLD-impact-pass — when an architectural question surfaces during LLD authoring, `/spec` drafts an HLD edit and surfaces it in the same review block as the spec output. The user reviews both deltas together. See `@default/skills/quality/specgen/references/hld-impact-pass.md` for the procedure.

For the *change* and *incident* doors, use `/rfc` and `/rca` respectively. After the door, the loop is identical for all three paths. The `code-evidence` source on the greenfield door is for *recovering* a design from existing code (to retrofit, to instigate a rewrite, or to align with the CSPA lifecycle); for *changing* existing code, use `/rfc`.

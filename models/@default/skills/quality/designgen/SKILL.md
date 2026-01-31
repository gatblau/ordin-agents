---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:quality:designgen"
  name: designgen
  description: "Takes a problem to a structured design document through an interview. The first step of the delivery loop."
  version: 1.3.0
  owner: gatblau
description: Produce a human-authored-quality High-Level Design (HLD) in docs/design/ from one of three input sources — a problem statement (interview), inline context (draft), or an existing codebase (code-evidence). The HLD owns system context, architecture overview, principal sequences, regulatory framing, tech-stack choice, and architectural decisions; it stops short of wire-level detail (that is /spec's job). Shaped to exactly what specgen expects as input. In interview/draft modes, interviews the user to surface ambiguities, domain nouns, system actions, cross-cutting concerns, and architectural decisions, then drafts a structured Markdown HLD. In code-evidence mode, walks the supplied code paths to draft an as-built HLD plus a Requirements section that classifies each behaviour as Must preserve / Observed but not required / Drop candidates / Gaps. The HLD is a living document — `/spec` auto-amends it via the HLD-impact-pass as low-level questions surface; see `@default/skills/quality/specgen/references/hld-impact-pass.md`. Trigger on phrases like "design doc for X", "start a new design", "designgen", "draft HLD for <feature>", "high-level design for <feature>", "reverse-engineer a design from <paths>", "as-built design for <service>", or when the user asks to begin a new feature with a design document or to recover a design from existing code. Do NOT trigger on requests to edit or review an existing design.
---

# designgen — Problem Statement to High-Level Design

`designgen` is the procedure invoked by the **`/design`** slash command — the greenfield door of the four-move CSPA loop. The command (in `@default/commands/intent/design.md`) is the user-facing surface; this skill is the canonical procedure behind it.

Produce a **High-Level Design (HLD)** under `docs/design/` that, when fed to `/spec`, yields high-quality Low-Level Design (LLD) specs with minimal Phase 1B open questions. The skill is an interviewer + drafter: it asks targeted questions to surface what a good HLD needs, then writes the draft.

**The HLD owns system shape and governance.** Context, system architecture, principal sequences, tech-stack choices, regulatory context, architectural decisions, cross-cutting stances, domain model, and external interfaces (names and shapes only) live in the HLD. **Wire-level detail — exact field types, error code strings, JSON schemas, retry counts, error tables, Gherkin scenarios — belongs in `/spec` (LLD), not here.**

**The HLD is a living document.** `/spec` runs an HLD-impact-pass after every phase: HLD-shaped findings (new components, new ADRs, new glossary terms, new tech-stack members, new cross-cutting policies, new regulatory obligations) are routed back to the HLD as auto-drafted edits, reviewed by the user in the same pass as the spec output. See `@default/skills/quality/specgen/references/hld-impact-pass.md` and `@default/skills/quality/specgen/references/bubble-up-rule.md`. This is **plumbing**, not a new CSPA move — the four moves remain `design · spec · breakdown · apply`.

## Arguments

- `topic` (required): short feature or problem name, used as the filename / folder seed. E.g. `nats-key-rotation`, `appliance-telemetry`.
- `out-dir`: default `docs/design/`.
- `mode`: one of:
  - `interview` (default for greenfield) — ask questions, then draft.
  - `draft` — skip questions, draft directly from the prompt when the user provides enough context inline.
  - `code-evidence` — scan an existing codebase and draft an as-built HLD plus a Requirements section. Requires `code-paths`.
- `code-paths`: required when `mode: code-evidence`. List of repo-relative directories or files to scan. Implied mode — if `code-paths` is supplied without `mode`, the skill enters `code-evidence`.
- `include-requirements` (code-evidence only): default `true`. Set to `false` to suppress the Requirements section.
- `hld-form`: `folder` | `single-file`. If absent, the skill consults the `triage` lane decision (see `@default/skills/quality/triage/references/classification-rubric.md` §Compound rules — Standard ⇒ folder, Trivial/Local ⇒ single-file). If no triage block is in context, the skill prompts the user for the lane and infers `hld-form` from it.

## Output

Either:

- **Folder form** (Standard lane, large designs): `docs/design/<topic>/` with `README.md` + numbered child files `00-overview.md` … `10-risks.md` + an append-only `99-changelog.md`. The full canonical layout is in `references/hld-folder-layout.md`.
- **Single-file form** (Trivial / Local lane, small designs): `docs/design/<topic>.md` with all sections inline.

Both shapes carry:

- A mandatory **Mode banner** declaring the active mode and the input from which the design was generated.
- A mandatory **`revision:` header** that bumps on every edit. Initial draft is `revision: 0.1.0`.
- The same section list (split across files in folder form, all inline in single-file form): Summary · Motivation · Goals · Non-goals · Glossary · Context (mermaid context diagram + external actors) · System Architecture (mermaid component diagram + responsibilities) · Principal Sequences (mermaid sequence diagrams) · Domain Model · Data Lifecycle · Tech Stack · Regulatory and Compliance Context · Cross-cutting Concerns · NFRs · Interfaces (external, names and shapes only) · Architectural Decisions (ADR entries) · Assumptions · Open Questions · Risks · Alternatives considered · Dependencies · Rollout and Rollback.
- In `code-evidence` mode: an additional **Requirements** section with four mandatory subsections (*Must preserve*, *Observed but not required*, *Drop candidates*, *Gaps*) — see `references/design-template.md` §Mode-driven sections.
- In folder form: an additional `99-changelog.md` that records every edit (initial draft, direct edit, promoted from a `/spec` phase, applied RFC, applied RCA), one append-only line per change. Format: `references/hld-changelog-format.md`.

If the target path already exists: stop and ask whether to overwrite, extend, or pick a new topic name. Never overwrite silently.

## Active modes

**Observe → Infer → Plan.**

- **Observe** for Phases 1–3 (intake, ambiguity probe, domain elicitation): read the problem statement or the supplied code paths, listen, do not invent. In `code-evidence` mode this phase dominates the run — every claim in the eventual draft must be traceable to evidence read here.
- **Infer** when ranking the alternatives the user proposed against best-practice patterns and surfacing trade-offs the user may not have considered. Used heavily in Phase 2 §8 (tech stack) and §11 (architectural decisions) where multiple defensible options exist. In `code-evidence` mode, also when classifying each observed behaviour into the four Requirements subsections.
- **Plan** for Phase 4 (drafting) and Phase 5 (the verification pass before writing the file). The output is an HLD — an authored artefact under `docs/design/`, never source code.

The skill never enters Patch — HLDs are authored artefacts, not source. **Escalate** when requirements are not user-confirmed, when ambiguity probes return no concrete answer, or when the target path already exists (the skill never overwrites silently). In `code-evidence` mode, additionally escalate when the supplied paths return no readable code, when the codebase relies on runtime reflection or DSLs to a degree that static reading cannot determine the public surface, or when more than half the candidate behaviours land in Gaps (see `code-evidence-intake.md` §When to escalate).

## Process

### Phase 1 — Intake

The intake step has two shapes depending on the active mode.

**Interview / draft modes (greenfield).** Ask the user to describe, in a few sentences each:
- **What problem is being solved.** What's broken or missing today.
- **Who or what triggers the work.** User action, event, schedule, external system.
- **What observable result is expected.** What changes after the feature exists.
- **Known constraints.** Non-negotiables — tech stack, backward compatibility, compliance, deadlines.
- **Out of scope.** What this explicitly will not address.

If any answer is missing or thin, ask one follow-up question at a time — do not dump a questionnaire. Stop when you have enough to draft, not when you have "everything".

**Code-evidence mode (brownfield).** Load `references/code-evidence-intake.md`. Walk the supplied `code-paths` in the documented scan order: module graph, public surfaces, data model, entry points, flows, cross-cutting middleware, deployment topology, tech-stack signals (build files, lockfiles, manifests, container base images). Tag every candidate claim with its evidence (`[evidence: path:line]` or aggregate / external variants). Produce an initial classification of every observed behaviour into *Must preserve* (only with a non-user witness — test or contract), *Observed but not required* (the safe default), or *Gaps* (suspected but unverifiable). Tech-stack rows are usually recoverable; ADR rationale (the *why* behind an architectural choice) usually is not — those land in *Gaps* unless a witness exists (PR description, ADR file, regulatory ticket).

### Phase 2 — Targeted interview

Load `references/interview-questions.md`.

**Interview mode.** Ask questions across the eleven areas, skipping any already covered in Phase 1:

1. Domain model — nouns, their relationships, their lifecycle.
2. Actions — the verbs the system performs; triggers, inputs, outputs, side effects.
3. Non-functional — performance targets, scale, availability, security posture.
4. Cross-cutting — auth, logging, metrics, tracing, rate limiting, pagination, CORS, health, migrations, graceful shutdown. Which apply? Any project-specific policy the HLD needs to record?
5. Known unknowns — things the user is aware they don't know yet.
6. *(code-evidence only)* Intent confirmation — see `interview-questions.md` §6.
7. System context — external actors, neighbouring systems, trust boundaries.
8. Tech stack — language, framework, datastore, broker, deployment substrate, observability stack, signing/crypto choice, build/test toolchain. One row per layer with a one-line rationale.
9. Regulatory and compliance context — standards, jurisdictions, obligations (GDPR, IFRS17, PCI-DSS, sector-specific). One-line per obligation plus how the design addresses it. "N/A — non-regulated" is valid.
10. Major sequences — at minimum the golden path; any secondary flow that crosses component boundaries or external systems.
11. Architectural decisions — ADR-shaped trade-offs (Decision · Context · Consequences · Alternatives). Surface the alternatives the user discarded, with one-line reasons.

Keep to one question per turn when the answer needs thinking. Batch simple yes/no questions.

**Code-evidence mode.** Use §6 of `interview-questions.md` (intent confirmation). The greenfield discovery questions in §1–§5 and §7–§11 do not apply — the codebase has already supplied the nouns, verbs, flows, cross-cutting stances, tech stack, and (partial) architecture. Walk the *Observed but not required* list one entry per turn, asking "is this intentional?" against the evidence; promote, demote, or leave each entry per the answer. Close with the drop-list, hidden-constraints, regulatory, out-of-scope, ADR-rationale (which observed choices have a documented *why*?), and witness-sources questions.

**Draft mode.** Skip Phase 2 entirely — but the draft must still populate all eleven areas from the inline context. If the context is silent on an area (commonly: regulatory, ADR rationale), record the silence as a non-blocking *Open Question*.

### Phase 3 — Ambiguity sweep
Load `references/ambiguity-patterns.md`. Re-read the gathered answers (and, in `code-evidence` mode, the evidence-tagged claims). For each ambiguity pattern detected, decide:
- Resolvable by a reasonable default → record as **Assumption** in the draft.
- Materially affects architecture → record as **Open question** in the draft.
- Still unclear → ask the user one more time.

This is the step that most raises the quality of the downstream spec. Do not skip.

**Non-blocking is the default for HLD Open Questions.** Because `/spec` will run an HLD-impact-pass and route LLD-discovered architectural questions back to the HLD, the initial HLD need not be exhaustive. A question is **blocking** only when it cannot start to be specified without the answer (e.g. "single tenant vs multi tenant" gates the entire data-model section). Most questions are non-blocking and may be resolved as `/spec` draws out the details.

### Phase 4 — Draft

Load `references/design-template.md`. Decide the output shape:

- If `hld-form: folder` (Standard lane) — produce one file per child under `docs/design/<topic>/` per `references/hld-folder-layout.md`. Write `README.md` last; it carries the Mode banner, the current `revision:`, a one-paragraph orientation, and an indexed link list. Initialise `99-changelog.md` with a single line: `<date> — initial draft (designgen, mode=<mode>) → revision: 0.1.0`.
- If `hld-form: single-file` (Trivial / Local lane) — produce a single `docs/design/<topic>.md` with all sections inline. Carry the Mode banner and the `revision:` header at the top. No separate `99-changelog.md`.

Every section the template lists must be present — if a section genuinely does not apply, write a one-line "N/A — <reason>" rather than omitting. The Mode banner and `revision:` header are mandatory in every mode. The Requirements section is mandatory in `code-evidence` mode (with all four subsections present, writing `_(none in initial draft)_` for empty subsections) and omitted in `interview` / `draft` modes. Use the active locale throughout (see `urn:ordin:default:rules:layer:output-language`).

### Phase 4b — Make the prose read as a person wrote it

Run `humanise` (`urn:ordin:default:skills:documents:humanise`) over the draft's prose: the orientation, the narrative of every section, the decision rationale and the Requirements prose. Leave the Mode banner, the `revision:` header, tables, identifiers, ADR ids, diagrams and code untouched; `humanise` skips them. On `HUM_POINT_DROPPED`, keep the pre-pass wording for that paragraph and say so in the reply. A design document is not written until this pass has run.

### Phase 5 — Self-check before writing the file
Verify:

**Strict (all modes, blocking the write):**
- The Mode banner is present and matches the active mode.
- The `revision:` header is present.
- Summary, Motivation, Goals, Non-goals are populated (framing is not optional).
- The System Context section contains a mermaid context diagram.
- The System Architecture section contains a mermaid component diagram.
- At least one Principal Sequence (the golden path) is captured as a mermaid sequence diagram with explicit trigger and observable result.
- The Tech Stack table is populated (or every row is "N/A — <reason>").
- The Regulatory and Compliance Context section is populated (or "N/A — non-regulated").
- Every cross-cutting concern has an explicit stance (applies / does not apply / project-default).
- Every Architectural Decision entry has Decision, Context, Consequences, and at least one Alternative.
- Every noun introduced has an entry in the Domain Model section.
- Every action described has inputs, outputs, and side effects named.
- Every assumption is labelled.
- Every open question is labelled and marked blocking / non-blocking.
- File / folder name matches `docs/design/<topic>/` or `docs/design/<topic>.md` with kebab-case.
- In folder form: `99-changelog.md` exists with at least the initial-draft line.

**Code-evidence mode additionally:**
- Every claim in the design body carries an evidence tag or is in *Gaps*; the Requirements section is present with all four subsections; no entry sits in *Must preserve* without a witness; no identifier appears in the document that is not visible in the cited evidence.

Only then write the file(s). After writing, show the user the path(s) and a one-paragraph summary of what was drafted, plus the count of assumptions and open questions (split blocking / non-blocking).

If any open question is **blocking**, surface them in a **layman-language summary** *before* suggesting any next step (per `@default/commands/intent/design.md` §Blocking decisions outstanding). The non-blocking count is informational only and does not gate the handoff — `/spec` is expected to surface and resolve non-blocking items as it runs.

Suggest next step: "Run `/spec` against `docs/design/<topic>/` (or the single file)." — but only when there are no blocking open questions.

## References (load on demand)

- `references/design-template.md` — full section template, including the Mode banner, the `revision:` header, and the conditional Requirements section. Covers both folder and single-file shapes. Load at start of Phase 4.
- `references/hld-folder-layout.md` — canonical folder structure and per-child-file responsibilities for `hld-form: folder`. Load at start of Phase 4 in folder form.
- `references/hld-changelog-format.md` — append-only line format for `99-changelog.md`. Load at start of Phase 4 in folder form.
- `references/interview-questions.md` — topical questions organised by area (§1–§5 for greenfield discovery, §6 for code-evidence intent confirmation, §7–§11 for HLD-specific areas: context, tech stack, regulatory, sequences, ADRs). Load at start of Phase 2.
- `references/ambiguity-patterns.md` — common ambiguity flags and how to resolve them. Load at start of Phase 3.
- `references/code-evidence-intake.md` — scan order, evidence tagging, Required/Observed classification rules, anti-patterns, tech-stack and ADR-rationale recoverability rules. Load at start of Phase 1 in `code-evidence` mode.

## What designgen does not do

- Does not produce specs (that is `/spec`).
- Does not produce code or pseudocode.
- Does not edit existing HLDs *as a user-facing command*. (The `/spec` HLD-impact-pass does amend the HLD as plumbing — but that is owned by `specgen`, not by this skill.) For direct edits to an HLD, edit the file in place; for spec-driven edits, run `/spec`.
- Does not produce wire-level detail — exact field types, JSON schemas, error codes, retry numbers, Gherkin scenarios, error tables. Those belong in `/spec` (LLD). The HLD names *what* and *how the parts interact*; the LLD specifies *exact bytes and behaviours*.
- Does not decide architecture in code-evidence mode. The HLD body documents *what is*; the Requirements section's *Must preserve* subsection is the only place where *what should be preserved* is asserted, and entries land there only with a witness.
- Does not perform the rewrite itself. Producing an as-built HLD plus Requirements is the input to a separate `/breakdown` → `/apply` cycle, not a substitute for it.

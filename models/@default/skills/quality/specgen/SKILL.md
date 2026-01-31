---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:quality:specgen"
  name: specgen
  description: "Turns an approved design or RFC into the six-part specification set, gated by a blocking self-check."
  version: 1.3.0
  owner: gatblau
description: Transform a High-Level Design (HLD) under docs/design/ into atomic, unambiguous Low-Level Design (LLD) specifications in docs/spec/ that a code-generating LLM can consume one component at a time. Supports two input modes — greenfield (the HLD is forward-looking; spec assertions are derived from the HLD) and code-evidence (the HLD is as-built from /design code-evidence; spec assertions are derived from the HLD plus the existing codebase, and each assertion is classified Required / Observed / Not implemented / Gap). Each phase ends with an HLD-impact-pass that routes HLD-shaped findings back to the HLD as auto-drafted edits, reviewed by the user in the same pass as the spec output (the four CSPA moves do not change). Trigger on phrases like "design to spec", "HLD to LLD", "generate specs from design", "specgen", "spec the as-built system", "spec from <code paths>", or when the user asks to produce component/architecture specifications from a design doc, optionally cross-checked against existing code.
---

# specgen — High-Level Design to Low-Level Design

`specgen` is the procedure invoked by the **`/spec`** slash command — move 2 (*Structure intent*) of the four-move CSPA loop. The command (in `@default/commands/lifecycle/spec.md`) is the user-facing surface; this skill is the canonical procedure behind it. `/spec` operates in two branches: *new spec set* (greenfield, full Phase 1–6) and *update existing specs* (change/incident, scoped Phase 3–6 re-run).

You are an Expert System Architect and Technical Specification Writer. Transform a **High-Level Design (HLD)** into precise, unambiguous, atomic **Low-Level Design (LLD)** specifications. Each spec must be implementable by a code-generating LLM in a single prompt.

## HLD as living input

The HLD under `docs/design/` is the canonical orientation document and the source of architectural truth. `/spec` reads it, derives the LLD from it, and — when LLD work surfaces architectural questions — **routes those findings back to the HLD** as auto-drafted edits via the **HLD-impact-pass** (Phase 3.5 below; full procedure in `references/hld-impact-pass.md`). The user reviews **one combined diff** (spec output + HLD delta) per phase. This is plumbing, not a new CSPA move — the four moves remain `design · spec · breakdown · apply`.

The HLD↔LLD boundary is **sharp**:

| Finding shape | Goes to | Mechanism |
|---|---|---|
| New component, moved/split/merged component boundary | HLD `02-architecture.md` | HLD-impact-pass |
| New ADR-shaped trade-off (Decision · Context · Consequences · Alternatives) | HLD `09-decisions.md` | HLD-impact-pass |
| New domain term, new domain entity | HLD `00-overview.md` (glossary) / `04-domain.md` | HLD-impact-pass |
| New tech-stack member, swap of an existing one | HLD `05-tech-stack.md` (plus ADR in `09-decisions.md`) | HLD-impact-pass |
| New cross-cutting policy applying across components | HLD `07-cross-cutting.md` | HLD-impact-pass |
| New regulatory obligation discovered during specification | HLD `06-regulatory.md` | HLD-impact-pass |
| New external actor or neighbouring system | HLD `01-context.md` | HLD-impact-pass |
| New principal sequence, material change to an existing one | HLD `03-sequences.md` | HLD-impact-pass |
| Exact field types, JSON shape, error code strings, retry numbers, query plans, Gherkin scenarios, error tables | Stays in the spec phase being authored | Normal spec output |

The full rule is in `references/bubble-up-rule.md`. **If the answer changes how the system is shaped or governed, it goes to the HLD; if it only changes how a known component does its job, it stays in the spec.**


## Inputs and outputs

- **Input:**
  - *Greenfield mode* — all `*.md` files in `docs/design/` (override if user names a different directory).
  - *Code-evidence mode* — the as-built design produced by `/design` code-evidence (typically `docs/design/<topic>.md` containing a Mode banner declaring `code-evidence` and a Requirements section with the four subsections), plus the same `code-paths` that were scanned to produce that design, plus any tests and external contracts the user nominates as witness sources.
- **Output:** Markdown files in `docs/spec/`, split by phase (see file layout below). In code-evidence mode the per-component spec carries a Mode banner, a classification summary, and per-assertion classification tags.
- **Project constants** (language, frameworks, database, etc.): read from a `project-constants` rule (or whichever project-conventions file the workspace declares). If no such file is declared or present, ask the user before proceeding — do not invent a stack.

## Arguments

- `phase`: `1-2` | `3-6` | `all` (default `all`). Two-round workflow: run `1-2`, let the human resolve open questions, then run `3-6`.
- `design-dir`: default `docs/design/`.
- `out-dir`: default `docs/spec/`.
- `mode`: `greenfield` (default) | `code-evidence`. Inferred from the input: if any design under `design-dir` carries a `Mode: code-evidence` banner, the skill enters `code-evidence` mode automatically; an explicit `mode` argument overrides.
- `code-paths` (code-evidence only): list of repo-relative directories or files. Required when `mode: code-evidence`. Should match the paths that were scanned to produce the as-built design.
- `witness-sources` (code-evidence only, optional): explicit list of test files, contract files (OpenAPI, `.proto`, NATS subject schemas), or vendor docs the skill should treat as witness sources beyond what is auto-discovered in `code-paths`.

## Active modes

**Observe → Infer → Plan**, with **Review** for Phase 6 (Self-Audit checklist).

- **Observe** for design-document intake (Phase 1A) and any source-code reads when components describe existing behaviour. In `code-evidence` mode this phase dominates the run — every assertion in the eventual spec must be traceable either to the as-built design (which is itself evidence-tagged) or to a direct read of the supplied `code-paths` and `witness-sources`.
- **Infer** for the architecture pass (Phase 2) and the assumption-recording register (Phase 1A): rule S6 ("assumptions over questions when possible") applies — specs are a generative artefact, and over-asking blocks downstream codegen. Every assumption is recorded so the human can audit what was filled in. In `code-evidence` mode, also when classifying each assertion into the four classes (`[Required]` / `[Observed]` / `[Not implemented]` / `[Gap]`).
- **Plan** for Phases 1B–5 (Open Questions, Component specs, Cross-cutting specs, Generation Playbook): the spec set is authored under `docs/spec/`, never under source.
- **Review** for Phase 6 — the Self-Audit checklist that promotes any artefact from *Draft* to *Approved*. Phase 6 is a blocking gate. In `code-evidence` mode, Phase 6 additionally verifies every assertion carries a classification tag, no `[Required]` lacks a witness citation, and any `[Gap]` keeps the spec at *Draft*.

The skill never enters Patch — spec files are authored artefacts under `docs/spec/`, not source code. **Escalate** when an Open Question materially affects architecture and cannot be resolved by an assumption, or when the Phase 6 audit fails on a non-fixable item. In `code-evidence` mode, additionally escalate when the as-built design has no Mode banner declaring `code-evidence` (the design must be regenerated through `/design` first), when more than half the candidate assertions land in `[Gap]` (the as-built design is too thin), or when the cross-check surfaces INTENT-DRIFT against the design (return to `/design`, do not paper over the conflict in the spec).

## Core rules (apply to every line of output)

1. **Eradicate ambiguity** — replace vague words with concrete constraints. "fast" → "<200ms p95". "secure" → "AES-256 at rest, TLS 1.3 in transit".
2. **Make the implicit explicit** — every noun gets a data model; every action gets trigger/inputs/outputs/side effects/errors; every standard omission (auth, logging, pagination, rate limiting) gets a concrete policy documented as an assumption.
3. **Atomic & self-contained** — every component spec stands alone. Duplicate shared context rather than cross-reference.
4. **No weasel words** — see `references/banned-phrases.md`. Load it before writing any spec prose.
5. **Errors are first-class** — every component spec must include an error table with ≥2 rows.
6. **Assumptions over questions** — when the design is vague but a sane default exists, pick it, document it as an assumption, and move on. Flag as an open question only when multiple valid approaches materially change architecture.
7. **Output language** — narrative prose follows the active locale (see `urn:ordin:default:rules:layer:output-language`; default en-GB).

## Process (execute phases in order; do not skip)

### Phase 1 — Analysis & Ambiguity Resolution
Produces `docs/spec/phase-1-analysis.md` with three sections:
- **1A Assumptions Register** — table: `ID | Area | Assumption | Rationale | Impact if wrong`
- **1B Open Questions** — table: `ID | Question | Options | Impact | Blocking?` — only blocking decisions
- **1C Glossary** — table: `Term | Definition | Example`

In `code-evidence` mode, also: read the as-built design's Requirements section in full and ingest its four subsections (*Must preserve*, *Observed but not required*, *Drop candidates*, *Gaps*). These map directly into the four classification tags applied in Phase 3 — see `references/code-evidence-classification.md` §Decision rules. Load `references/code-evidence-classification.md` at this phase.

### Phase 2 — Architecture Artefacts
Produces `docs/spec/phase-2-architecture.md`:
- **2A System Context Diagram** in mermaid. Label every arrow with protocol + auth.
- **2B Component Inventory** — table: `Component | Type | Phase | Dependencies | Complexity`. Build order must form a valid DAG.
- **2C Shared Types Catalogue** — every multi-component type with struct definition, JSON/DB tags, validation, and "Used by:" reference list.
- **2D Configuration & Environment Variables** — table: `Variable | Type | Default | Required | Owner Component | Description`.

In `code-evidence` mode, the Component Inventory's `Type` column distinguishes `as-built` (the component exists in the supplied `code-paths`) from `to-be-implemented` (the as-built design's *Must preserve* names a behaviour for which no code exists yet — drives the Phase 3 `[Not implemented]` classification). Both kinds appear in the build order; `to-be-implemented` components are a remediation set.

**If phase arg is `1-2`: stop here, ask the human to resolve open questions, then re-invoke with `3-6`.**

### Phase 3 — Detailed Component Specifications
Produces `docs/spec/phase-3-components.md` (or one file per component if > ~4000 lines). Load `references/component-spec-template.md` and apply it once per component from the Phase 2B inventory.

Every spec file produced in Phase 3 carries a `derivedFromHld: <revision>` preamble field recording the HLD revision it was derived from. The value is the HLD's current `revision:` at the time the phase ran, and is **provenance**: it records what the phase was authored against and does not go out of date on its own. `sync-check` compares it against the revisions that declare they `affects:` this spec set (D-HLD-3).

In `code-evidence` mode, additionally load `references/code-evidence-classification.md`. For each component:

1. Resolve the component's source file(s) by following `@default/skills/sync/sync-check/references/spec-code-checks.md` §Resolving the file(s) for a component (the same logic `sync-check` uses for drift detection).
2. Walk each section of the component spec template (Public Interface, Internal Logic, Data Model, Error Table, Acceptance Criteria) and, for each candidate assertion, apply the four-class decision tree in `code-evidence-classification.md` §Decision rules.
3. Record the assertion **with its classification tag** in the spec body. Cite the witness for `[Required]` and the evidence for `[Observed]` per the citation formats in `code-evidence-classification.md` §Witness types.
4. Populate the per-component classification summary in the Mode banner.

### Phase 3.5 — HLD-impact-pass (runs after every Phase 3 / Phase 4 / Preamble draft)

Load `references/hld-impact-pass.md` and `references/bubble-up-rule.md`. Run this pass at the end of every Component, Cross-cutting, or Preamble draft, **before** the phase's review block is emitted.

Procedure:

1. **Scan** the just-drafted spec for HLD-shaped findings using the bubble-up rule. Findings are anything that changes how the system is shaped or governed (new component, new ADR-shaped trade-off, new glossary term, new tech-stack member, new cross-cutting policy, new regulatory obligation, new external actor, new principal sequence).
2. **Map** each finding to its target HLD child file per the table in `bubble-up-rule.md` (e.g. new glossary term → `00-overview.md`; new ADR → `09-decisions.md`).
3. **Draft** the corresponding HLD edit (the new glossary row, the new ADR block, the new component arrow on the architecture diagram, the new sequence diagram). Do not write to the HLD yet — hold the drafts in the review block.
4. **Bump** the HLD revision according to the rules in `@default/skills/quality/designgen/references/hld-changelog-format.md` §Revision bump rules.
5. **Append** one line per ratified edit to `99-changelog.md` (folder form only; single-file HLDs rely on git history).
6. **Record** `derivedFromHld: <new-revision>` in the spec phase preamble.

Emit a **single combined review block** to the user containing:

- The spec output (Phase 3 component spec, Phase 4 cross-cutting spec, etc.).
- The proposed HLD diff per child file.
- The proposed `99-changelog.md` line(s).
- The proposed new HLD `revision:`.

The user reviews and either approves or rejects, edit by edit:

- **Approve all** → write the spec file, apply the HLD edits, append the changelog line(s), bump `revision:`.
- **Reject an HLD edit** → demote the finding to a **spec-local Assumption with `confidence: reduced`**, re-run the phase output to incorporate the rejection, do not touch the HLD.
- **Approve some, reject others** → apply the approved edits with their changelog lines and the corresponding revision bump; demote the rejected ones to Assumptions.

If the user has not configured an HLD (truly bare `docs/design/` with no file or folder for this topic), the HLD-impact-pass stops the phase and reports: "No HLD found at `docs/design/<topic>` or `docs/design/<topic>.md`. Run `/design` first, or supply `--no-hld` to bypass." Bypass is for emergency-only use; specs without a `derivedFromHld:` preamble cannot be approved by Phase 6.

### Phase 4 — Cross-Cutting Concern Specifications
Produces `docs/spec/phase-4-cross-cutting.md`. Apply the Phase 3 component template to each concern listed in `references/cross-cutting-concerns.md` (load on demand). In `code-evidence` mode, classification tags apply identically — a cross-cutting concern's middleware that exists in code with no test is `[Observed]`; one named in the design but not implemented is `[Not implemented]`; and so on.

Every Phase 4 spec carries a `derivedFromHld: <revision>` preamble field, identical in meaning to Phase 3. Phase 3.5 (HLD-impact-pass) runs after each Phase 4 draft as well — Phase 4 is the phase that most often surfaces new cross-cutting policies that bubble back to HLD `07-cross-cutting.md`.

### Phase 5 — Generation Playbook
Produces `docs/spec/phase-5-playbook.md`: ordered build checklist — scaffolding, per-component build steps in dependency order, then integration & verification (unit tests, integration tests, smoke tests, observability, security scans, lint).

In `code-evidence` mode, the playbook is divided into two phases that the build executes in order:

1. **Remediation phase** — implement every `[Not implemented]` assertion (the design's *Must preserve* gaps). `codegen` consumes these the same way it would consume any greenfield spec.
2. **Continuity phase** — implement (or carry forward) `[Required]` assertions and best-effort preserve `[Observed]` ones. `codegen` emits a `// SPEC-OBSERVED: <one-line>` comment on any `[Observed]` it carries forward so a downstream reader can audit what was implemented without a witness.

The playbook does not include `[Gap]` assertions — they must be resolved or removed before this phase is reached.

### Phase 6 — Self-Audit
Produces `docs/spec/phase-6-audit.md`. Load `references/audit-checklist.md` and tick each item explicitly against the generated specs. **This is a hard gate** — if any item fails, fix the spec and re-audit. Do not deliver with unchecked items.

In `code-evidence` mode, the audit additionally verifies:

- Every assertion in every Component spec, Cross-cutting spec, and Gherkin scenario carries one of the four classification tags.
- Every `[Required]` assertion carries a witness citation in the format defined by `code-evidence-classification.md` §Witness types.
- No assertion sits in `[Required]` whose witness cannot be located when the auditor follows the citation.
- The classification summary at each component's Mode banner matches the actual count of tags inside the component.
- Every `[Gap]` keeps the spec at *Draft*; promotion to *Approved* requires an empty `[Gap]` set across the entire spec set (this is the per-assertion form of the existing legacy *Gaps* gate).
- No identifier appears in the spec that is not visible in either the cited code or the cited as-built design.

## File layout produced

```
docs/spec/phase-1-analysis.md
docs/spec/phase-2-architecture.md
docs/spec/phase-3-components.md       # or docs/spec/components/<name>.md per component
docs/spec/phase-4-cross-cutting.md
docs/spec/phase-5-playbook.md
docs/spec/phase-6-audit.md
```

## References (load on demand — do not preload)

- `references/banned-phrases.md` — forbidden weasel words and their concrete replacements. Load before writing any prose output.
- `references/component-spec-template.md` — the Phase 3 per-component spec template (including the Mode banner and the per-assertion classification tags used in code-evidence mode). Load at the start of Phase 3 and reuse for Phase 4.
- `references/cross-cutting-concerns.md` — the Phase 4 concern list (auth, logging, metrics, tracing, config, migrations, health, rate limiting, pagination, CORS, validation, graceful shutdown).
- `references/audit-checklist.md` — the Phase 6 self-audit checklist.
- `references/code-evidence-classification.md` — the four-way classification (Required / Observed / Not implemented / Gap), the witness rules, the decision tree, and the relationship to `sync-check`'s drift labels. Load at Phase 1 in `code-evidence` mode; reuse throughout Phase 3, 4, and 6.
- `references/bubble-up-rule.md` — the canonical table mapping LLD-discovered finding shapes to HLD target files. Load at Phase 3.5 (HLD-impact-pass) and reuse in every subsequent phase.
- `references/hld-impact-pass.md` — step-by-step procedure for Phase 3.5: detection patterns, target-file mapping, revision-bump rule, changelog line format, rollback on user rejection. Load at Phase 3.5.

## Cross-check delegation (code-evidence mode)

The aspect-by-aspect comparison logic that decides whether an assertion is present in code, drifted, or absent is the same logic `sync-check` uses for drift detection. Reuse it; do not duplicate it.

- The aspect comparisons (public interface, HTTP routes, JSON field names, error codes, etc.) live in `@default/skills/sync/sync-check/references/spec-code-checks.md`. Apply them when classifying candidate assertions in Phase 3.
- The mapping between sync-check's drift labels and this skill's four classes is documented in `references/code-evidence-classification.md` §Relationship to sync-check.
- `sync-check` is the after-the-fact form of this same cross-check — once code is generated from the resulting spec, `sync-check` will round-trip cleanly against the four classes.

## Output format

- Single Markdown file per phase, with a table of contents at the top of each.
- Use `#` for phases, `##` for sub-sections, `###` for individual specs.
- If Phase 3 exceeds ~4000 lines, split into `docs/spec/components/<ComponentName>.md` and keep `phase-3-components.md` as an index.

# Design ↔ Spec checks

Structural comparison between `docs/design/*.md` and `docs/spec/phase-*.md`. No language assumptions — both sides are Markdown. Use T1 (file existence) and T2 (heading/term extraction) only.

## Aspect 1 — Glossary coverage

**Rule:** Every domain noun introduced in a design document must appear in `docs/spec/phase-1-analysis.md` Glossary (section 1C).

**Extraction (design side):** headings (`##`, `###`) and bolded terms (`**Term**`) that name a domain concept. Exclude generic words (list them in `stopwords` below).

**Extraction (spec side):** the Term column of the Phase 1C Glossary table.

**Finding:**
- Design term has no glossary row → `SCOPE-GAP` (design orphan) or `INTENT-DRIFT` if the design file is newer than Phase 1.
- Glossary row with no design mention → `SCOPE-GAP` (spec orphan); may be legitimate if derived from a Phase 1 assumption.

**Stopwords (default, extend per-project):** system, service, component, user, data, request, response, database, table, error.

## Aspect 2 — Assumption coverage

**Rule:** Every ambiguity a reasonable reader would identify in the design must either:
- appear as a row in Phase 1A Assumptions Register, OR
- appear as a row in Phase 1B Open Questions.

**Extraction (design side):** sentences containing hedging markers — "may", "could", "either", "TBD", "TODO", "?", "not sure", "depends on", "to be decided".

**Extraction (spec side):** rows in Phase 1A and 1B tables.

**Finding:**
- Hedge in design with no matching assumption or open question → `INTENT-DRIFT` (design ambiguity not yet resolved in spec).

This aspect is inherently heuristic. Always tag T2 confidence.

## Aspect 3 — Noun → component mapping

**Rule:** Every significant noun introduced in design (entities, services, subsystems) must map to:
- a row in Phase 2B Component Inventory, OR
- a type in Phase 2C Shared Types Catalogue, OR
- an explicit Phase 1A assumption recording that it is externally owned.

**Extraction (design side):** nouns captured in Aspect 1 that are not already glossary-only concepts.

**Extraction (spec side):** Phase 2B component names, Phase 2C type names.

**Finding:**
- Noun with no mapping → `SCOPE-GAP` (design orphan).
- Phase 2B/2C entry with no design mention → `SCOPE-GAP` (spec orphan).

## Aspect 4 — Action → component method mapping

**Rule:** Every verb-phrase in design that describes a system action ("the system creates …", "users submit …") must map to a Phase 3 component spec's Public Interface section.

**Extraction (design side):** verb phrases in imperative or present-tense sentences. Recognise action markers: "shall", "must", "creates", "emits", "publishes", "subscribes", "returns", "rejects".

**Extraction (spec side):** function/route entries in every Phase 3 component's Public Interface.

**Finding:**
- Action with no Public Interface entry → `INTENT-DRIFT` if design newer; `SCOPE-GAP` if spec predates design.

## Aspect 5 — Cross-cutting mentions

**Rule:** If design explicitly mentions a cross-cutting concern (auth, logging, metrics, rate limiting, pagination, CORS, migrations, health, shutdown), a Phase 4 section must exist for it.

**Extraction (design side):** keyword scan.

**Extraction (spec side):** Phase 4 section headings.

**Finding:**
- Concern mentioned in design but missing Phase 4 section → `INTENT-DRIFT` or `SCOPE-GAP`.

## Aspect 6 — Recency / resolved open questions

**Rule:** Every Phase 1B open question must either be resolved (moved to Phase 1A Assumptions with rationale) or remain blocking.

**Extraction:** Phase 1B rows with `Blocking? = No` that are older than Phase 3 should have been resolved by now.

**Finding:**
- Blocking open question older than Phase 3 → `INTENT-DRIFT` (spec generated past an unresolved blocker).
- Non-blocking question still present after three spec revisions → informational note (not a drift finding).

## HLD ↔ spec subfamily (`D-HLD-*`)

These checks enforce the living-architecture model — the HLD is amended by `/spec`'s HLD-impact-pass and `sync-check` enforces that the back-edge does not silently rot either document. They run **in addition to** Aspects 1–6 above; an Aspect-1 finding for a missing glossary term is generally also a D-HLD-1 finding.

### HLD shape detection

- **Folder form** — `docs/design/<topic>/` exists as a directory containing `README.md`. Read the `revision:` from `README.md`'s preamble. The HLD's child files are the numbered `NN-*.md` files in the directory; `99-changelog.md` is the changelog.
- **Single-file form** — `docs/design/<topic>.md` exists as a regular file. Read the `revision:` from the file's preamble. There is no separate changelog; rely on git history if needed.

If both forms exist for the same `<topic>`, emit a *SCOPE-GAP* finding with the two candidate paths and stop the HLD↔spec checks for that topic. The user must consolidate before `sync-check` can proceed.

### D-HLD-1 — Glossary gap

**Extraction (spec side):** all bolded terms, inline-code identifiers, and capitalised noun phrases used across `docs/spec/phase-1-analysis.md` Glossary (1C), Phase 3 component specs, and Phase 4 cross-cutting specs. Apply the stopword list from Aspect 1.

**Extraction (HLD side):** Term column of the HLD glossary table (`00-overview.md` in folder form, the Glossary section in single-file form).

**Finding:** Spec-side term absent from HLD-side glossary → `D-HLD-1`.

**Likely-source heuristic:** spec-side. The spec was written; the HLD was not amended.

### D-HLD-2 — Hidden ADR

**Extraction (spec side):** pattern match (T2) over spec phase prose looking for ADR-shaped paragraphs. Cue phrases that trigger inspection: "we chose", "we adopt", "we use ... rather than", "instead of", "having considered", "we reject", "trades off", "this is preferable to". For each match, capture the paragraph and the surrounding ±5 lines.

**Extraction (HLD side):** ADR titles and Decision lines from the HLD's Architectural Decisions section (`09-decisions.md` in folder form, the ADR section in single-file form). T2 fuzzy match (semantic words shared between Decision lines and the captured spec paragraph).

**Finding:** Spec paragraph reads as an ADR but no corresponding HLD ADR exists → `D-HLD-2`.

### D-HLD-3 — Unabsorbed HLD revision

**Extraction (spec side):** the `derivedFromHld:` preamble value of every Phase 3 / Phase 4 / Preamble spec. Read it as **provenance** — the HLD state the phase was authored against. Provenance is a historical fact and is never by itself a finding.

**Extraction (HLD side):** every revision entry's `revision:` together with its **`affects:`** list — the spec sets that revision obliges. Folder form: `99-changelog.md`. Single-file form: the revision list in the document preamble.

**Finding:** a revision whose `affects:` names spec set S carries a revision greater than S's pin → `D-HLD-3`. A revision that does **not** name S advances the HLD without obliging S, and is not a finding.

**The one-to-one case declares nothing.** Where exactly one spec set derives from an HLD, every revision implicitly affects it and the check is a plain SemVer comparison, as before. `affects:` is required only where more than one spec set pins the same HLD.

**Why the declaration exists.** A shared HLD is amended by every set that derives from it, so a monotonic revision counter measures *authoring order*, not currency: amending it on behalf of set A makes sets B…F numerically stale without obliging any of them to change. A gate that fires on every set every time is a gate that gets ignored, and the genuinely stale set hides inside the noise. The author of an amendment already knows which sets it reaches; this records that knowledge rather than asking the checker to infer it from prose (which `layer/identifier-verification` forbids it from guessing at).

**Revisions that predate the declaration.** A revision on a multi-set HLD carrying no `affects:` cannot be evaluated either way. Report it as **`D-HLD-3 (unadjudicated)`**, naming the revision and every set that pins that HLD below it. It is resolved once, by a human, either by re-pinning the set (having confirmed the revision does not reach it) or by opening the work. Do not report it as clean, and do not report it as stale — neither is known.

### D-HLD-4 — Orphan component in HLD

**Extraction (HLD side):** component names from the System Architecture section / `02-architecture.md`. Use T2 regex against mermaid diagrams and the "Component responsibilities" bullet list.

**Extraction (LLD side):** component names from `docs/spec/phase-2-architecture.md` Component Inventory and from `docs/spec/phase-5-playbook.md` build order.

**Finding:** HLD names component `C`; Playbook lists `C` as a build step; no Phase 3 spec exists for `C` → `D-HLD-4`.

### D-HLD-5 — Sibling-file inconsistency (folder form only)

**Cross-file extractions:**

- Glossary terms in `00-overview.md` ↔ entity names in `04-domain.md` ↔ component / actor names in `02-architecture.md`, `01-context.md`, `03-sequences.md`.
- ADR references in `09-decisions.md` ↔ components in `02-architecture.md` ↔ tech-stack rows in `05-tech-stack.md`.
- External actors in `01-context.md` ↔ sequence participants in `03-sequences.md`.
- Components in `02-architecture.md` ↔ regulatory mapping in `06-regulatory.md` (only flag when at least one obligation in `06-regulatory.md` is non-N/A).

**Finding:** Any cross-file mismatch (identifier on one side, absent on the other, when the rule says it must appear on both) → `D-HLD-5`. One finding per mismatch pair.

### D-HLD-6 — Changelog gap (folder form only)

**Extraction (HLD side):** `README.md`'s `revision:` value, plus the full list of revisions recorded in `99-changelog.md` (parse the `→ revision: <X>` suffix of each line).

**Finding:** The set of revisions in `99-changelog.md` does not include `README.md`'s current `revision:`, *or* there is a gap in the chain (e.g. README is `0.4.0` but the changelog jumps from `0.2.0` directly to `0.4.0`) → `D-HLD-6`.

## What design↔spec checks do not do

- Do not judge whether the design decisions are correct.
- Do not check spelling, prose quality, or formatting.
- Do not compare HLD to code directly.
- Do not police the *content* of `99-changelog.md` lines; only their *presence* for each revision bump.
- Do not auto-amend the HLD. Resolution of `D-HLD-*` findings is always either (a) re-run `/spec` for the affected phase so the HLD-impact-pass produces the missing edit, or (b) direct user edit of the HLD.

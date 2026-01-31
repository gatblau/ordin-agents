# Drift taxonomy

Every finding carries exactly one of four labels. The label dictates who resolves the drift and with which skill.

## INTENT-DRIFT

**Definition:** The design document has been edited since the spec was generated, and the spec (and therefore the code) no longer reflects current human intent.

**Signal:** A design file's `git log -1 --format=%ct` is newer than the corresponding spec file(s), and the design content contains nouns/actions/decisions not present in the spec.

**Resolution playbook:**
1. Human reviews the design delta to confirm it is intentional (not a typo, not an exploratory note).
2. Run `/specgen phase: 1-2` to refresh analysis and architecture — new assumptions or open questions may surface.
3. Human resolves any new open questions.
4. Run `/specgen phase: 3-6` scoped to affected components.
5. Run `/codegen step: "<N>: <Component>"` for each component with a changed spec.
6. Re-run `/sync-check` to confirm zero remaining drift.

## CONTRACT-DRIFT

**Definition:** A spec has been edited and the code no longer matches the contract. The design is still the source of truth; the spec still reflects it; only the code is behind.

**Signal:** A Phase 3 or Phase 4 spec's `git log -1 --format=%ct` is newer than the source files it owns, and a contract aspect (signature, JSON tag, route, error code, env var, DDL, metric name) differs between spec and code.

**Resolution playbook:**
1. Confirm no REALITY-DRIFT findings exist on the same file (if both, treat as REALITY-DRIFT — the code change may be intentional).
2. Run `/codegen step: "<N>: <Component>"`.
3. Re-run `/sync-check` to confirm the finding is gone and no regressions appeared in adjacent components.

## REALITY-DRIFT

**Definition:** The code has been edited (hotfix, emergency patch, refactor) and the spec no longer describes what the code does. The code, not the spec, is the current truth.

**Signal:** A source file's `git log -1 --format=%ct` is newer than the spec file that owns it, and a contract aspect differs.

**Resolution playbook (human decision required):**
Present **both** alternatives, never pick one:

- **Option A — Revert code to spec.** Produce a diff that reverts the drifted aspects. Use when the code change was accidental, an unreviewed experiment, or violated the contract without authorisation.
- **Option B — Update spec to match code.** Produce a diff against the Phase 3 or Phase 4 spec file. Use when the code change was a legitimate decision that simply never made it back into the spec. Must also:
  - Update any Phase 1 assumption affected.
  - Update Phase 2 Shared Types or Configuration if the change touches them.
  - Re-run `/specgen` Phase 6 self-audit against the edited specs.

Never auto-regenerate code on a REALITY-DRIFT finding — doing so destroys the hotfix.

## SCOPE-GAP

**Definition:** An artefact exists in one layer with no counterpart in the layers that should contain it. Four concrete sub-cases:

| Sub-case | Example |
|---|---|
| Design orphan | Design mentions a concept with no Phase 1 glossary entry, no Phase 3 component, and no code |
| Spec orphan | Phase 3 component spec exists but no source file at its declared `**File:**` path |
| Code orphan | Source file exports symbols that no Phase 3 or Phase 4 spec owns |
| Migration orphan | `migrations/*.sql` file with no matching Phase 3 Data Model section, or Data Model with no migration |

**Resolution playbook (human triage):**
For each orphan, present three options and let the human pick:

1. **Fill the gap** — add the missing counterpart (new spec section, new code, new migration).
2. **Delete the orphan** — if it is dead or experimental.
3. **Mark as intentional** — record as a Phase 1 Assumption (e.g. "Component X is externally owned; no spec is produced here"). Future  sync-check  runs will ignore it once the assumption is present.

## Likely-source heuristic

When classifying, compare modification times via `git log -1 --format=%ct <file>`:

- Spec newer than code → lean CONTRACT-DRIFT.
- Code newer than spec → lean REALITY-DRIFT.
- HLD newer than spec → INTENT-DRIFT.
- Uncommitted changes on either side → treat the uncommitted side as "newer".

This is a hint, not a verdict. Always phrase the report as "likely source: <layer>", never "source: <layer>". The human is the final arbiter.

---

## HLD ↔ spec drift subfamily (`D-HLD-*`)

The HLD is a living document. `/spec`'s HLD-impact-pass routes LLD-discovered architectural questions back to the HLD; `sync-check` enforces that the back-edge does not silently rot the documents. Every `D-HLD-*` finding is a blocker — `/sync-check` will not mark a phase clean while any `D-HLD-*` is open.

### D-HLD-1 — Glossary gap

**Definition:** A term appears in a spec phase but is not present in the HLD glossary.

**Signal:** Term-extraction (T2) over `docs/spec/phase-*.md` (and any `docs/spec/components/*.md`) yields a noun not present in the HLD's Glossary section (`docs/design/<topic>/00-overview.md` in folder form, the Glossary section in single-file form). Excluded: stopwords (see `design-spec-checks.md` Aspect 1).

**Resolution playbook:**
1. Re-run `/spec` for the affected phase. The HLD-impact-pass will surface the term as a candidate glossary addition.
2. User approves; HLD `00-overview.md` gains the term; HLD `revision:` bumps (patch).
3. The spec's `derivedFromHld:` advances to the new revision.
4. Re-run `/sync-check`.

### D-HLD-2 — Hidden ADR

**Definition:** A spec body contains an ADR-shaped paragraph (Decision / Context / Consequences / Alternatives pattern) that has no corresponding ADR entry in the HLD.

**Signal:** Pattern match (T2) over spec phase prose looking for cue phrases ("we chose", "we adopt", "instead of", "rather than", "having considered", "we reject", "this trades off"). When matched and the surrounding paragraph reads as an architectural decision, check the HLD `09-decisions.md` for an ADR with equivalent content. If absent → finding.

**Resolution playbook:**
1. Re-run `/spec` for the affected phase. The HLD-impact-pass will surface the ADR as a candidate addition.
2. User approves; HLD `09-decisions.md` gains the ADR; HLD `revision:` bumps (minor).
3. The spec narrative is rewritten to *reference* the new ADR rather than duplicate its content.
4. Re-run `/sync-check`.

### D-HLD-3 — Unabsorbed HLD revision

**Definition:** An HLD revision that declares it `affects:` spec set S is newer than S's `derivedFromHld:` pin. The pin itself is **provenance** — the HLD state the phase was authored against — and being merely numerically behind is not the finding.

**Signal:** For each spec set S, take every HLD revision newer than S's pin and keep those whose `affects:` names S. Any survivor is a finding. Where exactly one spec set derives from an HLD, `affects:` is unnecessary and every newer revision counts.

A revision on a multi-set HLD that carries no `affects:` is **unadjudicated**: report it as such, naming the revision and the sets pinned below it, and let a human settle it once. Reporting it clean would hide real drift; reporting it stale is the fault this label was rewritten to remove.

**Resolution playbook:**
1. Read the `affects:` entry to see what the revision obliges of this set.
2. Re-run `/spec` for the affected phase. The HLD-impact-pass will not surface new findings (the HLD is already ahead); the phase is regenerated against the new HLD revision and the `derivedFromHld:` pin advances.
3. Re-run `/sync-check`.

**For an unadjudicated revision**, step 1 is a human reading the revision and deciding: re-pin the set (the revision does not reach it) or open the work. Neither `sync-check` nor `/spec` may decide this by inference.

### D-HLD-4 — Orphan component in HLD

**Definition:** The HLD names a component in `02-architecture.md` (folder form) or the System Architecture section (single-file form) that has no corresponding Phase 3 spec, *and* the Generation Playbook (`docs/spec/phase-5-playbook.md`) lists the component as a build step.

**Signal:** Extract component names from HLD architecture diagrams and responsibility lists; cross-reference against `docs/spec/phase-2-architecture.md` Component Inventory table and `phase-5-playbook.md` build order. Any HLD component named in the Playbook but absent from Phase 3 is flagged.

**Resolution playbook:**
1. Run `/spec phase: 3-6` scoped to the missing component.
2. The new component spec inherits the HLD's current `revision:` as its `derivedFromHld:`.
3. Re-run `/sync-check`.

### D-HLD-5 — Sibling-file inconsistency (folder form only)

**Definition:** Within a folder-form HLD, sibling child files name the same identifier inconsistently or one names something the other should also name.

**Signal:** Cross-extract identifiers across `00-overview.md` glossary, `02-architecture.md` components, `03-sequences.md` sequence participants, `04-domain.md` entities, `08-interfaces.md` interfaces, and `09-decisions.md` ADR references. Findings:

- A component named in `02-architecture.md` not referenced in `06-regulatory.md` where regulation says it should be (e.g. a component that handles PII must appear in the regulatory mapping if GDPR applies).
- A glossary term used in `04-domain.md` absent from `00-overview.md`.
- An ADR in `09-decisions.md` referring to a component not in `02-architecture.md`.
- An external actor in `01-context.md` not appearing in any sequence in `03-sequences.md`.

**Resolution playbook:**
1. Direct edit to the HLD to align siblings. Either add the missing reference, or change the over-claiming sibling.
2. Bump `revision:` (patch for the alignment, minor if the edit introduces new ADR-shaped content).
3. Append a `direct edit` line to `99-changelog.md`.
4. Re-run `/sync-check`.

### D-HLD-6 — Changelog gap (folder form only)

**Definition:** The HLD's `README.md` `revision:` has been bumped without a matching line being appended to `99-changelog.md`.

**Signal:** Walk `99-changelog.md` lines from oldest to newest; verify that each revision in the trail is reachable from a previous revision in the file. Any gap (the README claims `revision: 0.4.0` but the changelog last records `revision: 0.2.0`) → finding.

**Resolution playbook:**
1. Direct edit to append the missing changelog line(s). Use `direct edit` as origin if the actual origin is unknown.
2. Re-run `/sync-check`.

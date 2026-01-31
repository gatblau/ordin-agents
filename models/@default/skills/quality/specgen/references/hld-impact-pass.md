# HLD-impact-pass — Phase 3.5 procedure

The HLD-impact-pass is the plumbing that keeps the HLD a living document. It runs after every Phase 3 (Component spec), Phase 4 (Cross-cutting spec), and Preamble draft in `specgen`. It is **not** a user-facing CSPA move — the user reviews a combined diff (spec + HLD delta) per phase and is otherwise unaware of it.

## Inputs

- The just-drafted spec phase output (Component spec, Cross-cutting spec, or Preamble).
- The current HLD — either `docs/design/<topic>/` (folder form) or `docs/design/<topic>.md` (single-file form).
- The HLD's current `revision:` (read from `README.md` in folder form, from the preamble in single-file form).
- `bubble-up-rule.md` — the canonical finding-to-target-file mapping.

## Outputs

A single **combined review block** containing:

1. The spec phase output, ready to write.
2. The proposed HLD edits, one per child file (folder form) or one combined diff (single-file form).
3. The proposed `99-changelog.md` line(s) (folder form only).
4. The proposed new HLD `revision:` and `Last updated:` values.
5. The proposed **`affects:`** list for the new revision — the spec sets this amendment obliges. Required whenever more than one spec set derives from this HLD; omitted when exactly one does, where it is implicit. See *Declaring impact* below.
6. The `derivedFromHld: <new-revision>` preamble line that will be added to the spec phase file.

## Procedure

### Step 1 — Scan the draft

Walk the just-drafted spec phase output looking for the finding patterns enumerated in `bubble-up-rule.md`. The scan order is:

1. **New nouns.** Any term introduced in the spec that is not in HLD `00-overview.md` glossary. Includes type names that name a domain concept, not just a Go/TS struct name. (Excluding stopwords: `system`, `service`, `component`, `request`, `response`, `database`, `table`, `error`, `user`, `data` — same list `sync-check` uses.)
2. **New component-shaped entries.** Any sub-component, sidecar, or distinct unit that the spec describes but `02-architecture.md` does not name.
3. **ADR-shaped paragraphs.** Any paragraph that reads "We chose X because Y, having considered Z but rejected it because W" or any variation thereof. Detect via cue phrases: "we chose", "we use", "we adopt", "we reject", "instead of", "rather than", "considered ... but".
4. **New tech-stack mentions.** Any library, framework, or runtime named in the spec that is not in HLD `05-tech-stack.md`. (Note: transitive dependencies do not count; only directly-named ones.)
5. **New cross-cutting policies.** Any policy statement that applies *to all components* rather than just the one being specified. Detect via phrases: "every component", "all handlers", "the system enforces", "globally", "platform-wide".
6. **New regulatory mentions.** Any reference to a regulation, standard, or compliance obligation not in HLD `06-regulatory.md`. (E.g. "must satisfy GDPR Article 17", "must align with PCI-DSS Requirement 4".)
7. **New external actors.** Any actor (user role, external system, scheduler, broker) named in the spec that is not in HLD `01-context.md`.
8. **New principal sequences.** Any flow that crosses two or more components or one external system that is not captured in HLD `03-sequences.md`. Component-internal flows are not sequences in the HLD sense.
9. **New externally-visible interfaces.** Any route, NATS subject, CLI command, or file format that is externally observable and not in HLD `08-interfaces.md` (names and shapes only).
10. **New system-level risks.** Any risk statement that applies to the system, not to one component (e.g. "if the broker is down for >5min, the entire ingest stalls" is system-level; "this handler panics on nil pointer" is not).

Each finding is recorded as a candidate edit, not yet applied.

### Step 2 — Map findings to HLD files

For each finding, apply the table in `bubble-up-rule.md` to determine the target HLD file. In single-file HLDs, all targets collapse to the single file; in folder HLDs, each finding targets a specific child file.

If a finding does not match any row in the bubble-up table, it stays in the spec. Do not invent new HLD sections.

### Step 3 — Draft the HLD edit

For each finding, draft the literal change to the HLD child file:

- **Glossary additions** — a new row in the glossary table with Term, Definition, Example.
- **Component additions / amendments** — a new row in the Component responsibilities list and, if necessary, an updated mermaid component diagram. Mermaid changes are produced as a full diagram replacement, not a patch.
- **ADR additions** — a new ADR-NNN block with Decision · Context · Consequences · Alternatives. ADR numbers are monotonic — read the highest existing ADR-NNN and increment.
- **Tech-stack additions** — a new row in the Tech Stack table with Layer, Choice, Rationale.
- **Cross-cutting additions / amendments** — an updated row in the Cross-cutting Concerns table or, if a new concern, a new row plus a brief description.
- **Regulatory additions** — a new row in the Regulatory Context table with Obligation, Source, How addressed.
- **Context additions** — an updated external-actors list and, if necessary, an updated context diagram.
- **Sequence additions** — a new mermaid sequence diagram with Trigger, Result, Error posture.
- **Interface additions** — a new entry in the Interfaces (external) list — name and shape only, no schemas.
- **Risk additions** — a new line in the Risks list.

The drafts must follow the active locale (en-GB default).

### Step 4 — Bump the revision

Determine the bump size per `@default/skills/quality/designgen/references/hld-changelog-format.md` §Revision bump rules:

- **Patch** — clarifications, prose, single glossary rows, single assumption rows.
- **Minor** — new ADR entries, new components, new tech-stack rows, new cross-cutting policy changes, new sequence diagrams, new regulatory obligations.
- **Major** — first promotion to *Approved*, or a change that invalidates an existing approved spec phase.

If the review block carries multiple edits, the bump size is the maximum of the individual bump sizes (one new ADR + three patch-level glossary additions = one minor bump). Apply a single new `revision:` value.

### Step 5 — Draft the changelog lines (folder form only)

For each ratified edit (one per finding), draft one line per `@default/skills/quality/designgen/references/hld-changelog-format.md`:

```
<date> — promoted from <phase-file>: <summary> → revision: <new-revision>
```

`<date>` is today's date (ISO). `<phase-file>` is the spec phase file being drafted (e.g. `phase-3-component-payment-handler`). `<summary>` is one short sentence per edit.

In single-file HLDs, the changelog is not produced — git history serves the same purpose.

### Step 6 — Compose the review block

Emit a single response to the user containing:

```
=== Spec phase output ===
<the drafted spec file, ready to write>

=== HLD impact ===
HLD: docs/design/<topic>/ (folder form) | docs/design/<topic>.md (single-file form)
Current revision: <old-revision>
Proposed new revision: <new-revision>

Edit 1 of N: <file or section> — <summary>
<the literal edit, as a unified diff or a "add this block" snippet>

Edit 2 of N: ...

=== Changelog (folder form only) ===
<new lines to be appended to 99-changelog.md, one per edit>

=== Impact (multi-set HLDs only) ===
affects: <spec set>, <spec set>, ...   # the sets this revision obliges

=== Spec preamble update ===
Adding to the spec file: derivedFromHld: <new-revision>
```

### Declaring impact

A shared HLD is amended by every spec set that derives from it. Its `revision:` therefore
measures authoring order, not currency: bumping it for set A leaves sets B…F numerically
behind without obliging any of them to change. `sync-check`'s **D-HLD-3** reads `affects:`
to tell the two apart, so an amendment that omits it on a multi-set HLD is reported
*unadjudicated* and costs a human a decision later.

Rules of form:

- **List the sets the amendment reaches, not the set that raised it.** The originating set
  is usually one of them; it is rarely the only one.
- **Name sets by their `docs/spec/<set>/` directory name**, so the value resolves mechanically.
- **An empty list is a legitimate answer** and is written `affects: none` — a glossary
  promotion or a typo fix obliges nobody. Silence is not the same as none; say which.
- **Widen when unsure.** Naming a set that turns out not to be obliged costs one re-pin;
  omitting one that was hides real drift behind a clean gate.
- **Do not infer it later from the prose.** The knowledge exists at authoring time; that is
  the only point where it is free and reliable.

### Step 7 — Wait for user adjudication

The user can:

- **Approve all** — write the spec file, apply every HLD edit, append every changelog line, bump `revision:` to the proposed value.
- **Approve some, reject others** — apply only the approved edits with their changelog lines; demote the rejected ones to spec-local Assumptions with `confidence: reduced`. Re-emit the spec phase output if needed (because demoted findings may affect the spec narrative).
- **Reject all HLD edits** — write the spec file with every finding demoted to an Assumption with `confidence: reduced`. Do not touch the HLD.
- **Adjust** — the user may rewrite individual edits before approval (e.g. tighten an ADR title, reword a glossary entry). Apply the user-supplied text rather than the drafted text.

Approval is granular per edit. A bulk "looks good" is treated as approval of every edit and every changelog line in the block.

### Step 8 — Apply the changes

After adjudication:

1. Write the spec file (with the `derivedFromHld: <new-revision>` preamble).
2. Apply each approved HLD edit to the target file.
3. Append the approved changelog lines to `99-changelog.md` (folder form only).
4. Update the HLD's `revision:` and `Last updated:` fields in the preamble (`README.md` in folder form, the top of the file in single-file form).

If any approved HLD edit fails to apply (e.g. the file was edited between scan and apply), abort the pass, do not write any file, report the conflict to the user, and ask them to re-run the phase. Partial application is forbidden.

## When the HLD-impact-pass stops the phase

- **No HLD exists.** Report: "No HLD found at `docs/design/<topic>` or `docs/design/<topic>.md`. Run `/design` first." The phase stops. Bypass with `--no-hld` is for emergency-only use; specs without `derivedFromHld:` cannot pass Phase 6 audit.
- **Multiple HLD candidates.** Report: "Multiple HLD candidates found at `docs/design/<topic>/` and `docs/design/<topic>.md`. Resolve before continuing." The phase stops.
- **HLD revision parse failure.** Report: "Cannot read `revision:` from HLD preamble. Fix the HLD before continuing." The phase stops.
- **Finding count exceeds 12 for a single phase.** Report: "HLD-impact-pass found <N> candidate edits — this usually indicates the HLD is too thin for the work being specified. Consider running `/design` again to thicken the HLD before continuing `/spec`." The phase stops and waits for user decision (continue, abort, return to `/design`).

## Rollback semantics

If the user rejects all HLD edits in a phase, the phase still produces a valid spec file — the rejected findings become Assumptions with `confidence: reduced` and the spec narrative is rewritten to accommodate them. The HLD is untouched; its `revision:` does not bump. The spec's `derivedFromHld:` records the current (un-bumped) HLD revision.

If the user later wants to promote a rejected finding back to the HLD, they re-run `/spec` for the affected phase with the Assumption removed; the HLD-impact-pass will re-surface the finding and they can approve it on the second pass.

## Idempotence

A re-run of `/spec` on an already-derived phase should produce:

- No new HLD edits if no new findings were introduced and the HLD has not moved.
- Only the edits required by the HLD's new revision if the HLD has moved (e.g. a glossary term was added by a separate `/spec` phase in the meantime and the current phase now references it).

The pass is idempotent on a stable HLD: running it twice in a row should yield the same combined review block the second time as the first.

---
apiVersion: ai.enterprise/v1
kind: rule-layer
metadata:
  id: "urn:ordin:default:rules:layer:spec-anchors"
  name: Spec anchors
  description: "Fixes the citation form that links code to the spec assertion it implements, and documents to the source they describe, so both directions can be resolved mechanically instead of read."
  version: 1.0.0
  owner: gatblau
---

# Spec anchors (layer rule)

A **layer rule**: composes on top of whichever of the nine modes (`@default/rules/orchestrators/working-modes.md`) is active whenever code cites a specification, or a design / spec document cites a source path. It does not replace the active mode; it fixes the form those citations take.

The problem it solves: a mature corpus carries thousands of cross-references — assertion ids named in comments, source paths quoted in design documents — and none is checked by a compiler. A rename turns them into dead pointers silently. `sync-check` then loses the anchors it resolves components through, and its traceability gate (`references/traceability-checks.md`) has nothing to traverse: that reference requires links to be **explicit id citations** and warns that the convention must be documented with the project or the signal is noise. This rule is that convention.

## The anchor form

A source file cites a spec assertion with a **directive comment**:

```
<comment-leader> spec: <set>/<document>#<assertion-id>
```

| Part | Meaning |
|---|---|
| `<set>` | the spec set — a directory under the project's spec root |
| `<document>` | the document basename within it, without extension |
| `<assertion-id>` | a token appearing literally in that document |

The comment leader is the host language's line-comment token — the active **stack Practice Pack** names it (`//`, `--`, `#`, `%`, `;`). The workspace names no language, so this rule fixes only the directive's shape.

Rules of form:

- **One anchor per line.** Several assertions at one site means several stacked lines, never a delimited list. Each id then resolves independently and the extractor stays a single regex.
- **The anchor is a citation, not a sentence.** Explanation belongs on its own comment lines. Prose on the directive line defeats extraction.
- **Placed immediately above the symbol, block, or statement it implements** — or at end-of-line for a field.
- **It does not replace prose references.** Comments that discuss a decision in narrative stay as they are; the anchor adds one resolvable line beside them.

## Where an anchor is required

- Every implementation site of a `[Required]` assertion in a code-evidence spec set (`specgen` Branch C).
- Every symbol the Generation Playbook names as the output of a step.
- Every schema object a Component spec's Data Model section declares.

Anchors on `[Observed]` and `[Gap]` assertions are welcome but not required. The gap marker `// SPEC-GAP-<N>:` (see the stack pack's annotation conventions) keeps its existing and opposite meaning: it marks a hole in the spec, where `spec:` marks a satisfied assertion. An anchor pointing at a `[Gap]` assertion is a defect.

## Verification before citation

An assertion id is citable only once it has been **seen** in the document — this is `layer:identifier-verification` applied to spec ids. Do not derive an id from a sibling (`AC-07` exists, therefore `AC-08` does), from a numbering pattern, or from memory of an earlier revision. Read the document, find the token, then write the anchor.

A citation that cannot be verified is not written. In Patch it routes to `// SPEC-GAP-<N>:`; in Plan to the Component spec's *Gaps*.

## Document-side citations

The same discipline runs in the other direction:

- A source path quoted in a design or spec document is a **full repository-relative path**, not a suffix fragment. A fragment reads fine to a human and resolves to nothing.
- Line-number and symbol suffixes are fine and are ignored when resolving.
- A path belonging to another repository carries that repository's prefix, and resolution against it degrades gracefully: when the sibling is not checked out, the reference is *skipped*, never reported missing. A cross-repo spec set must not make the check depend on a second clone.
- A path cited by a **descriptive** layer (design, spec) must exist. Deliberate build-ahead — an Approved spec set whose Playbook has not run — is recorded in a project-local allowlist with a reason and a removal condition, not left to fail and not quietly deleted from the document.
- The **prospective** layer (plans, RFCs, RCAs under a work-in-progress root) is exempt. A plan naming a file it intends to create is the plan working correctly.

## Mechanical enforcement

The check is cheap enough to be a build gate and belongs in one: resolve every anchor, every inter-document link, and every descriptive-layer source path, and fail on a dangling one. The command is the project's own — the active stack pack's `build-commands.md` names where a repository-local check hangs. Two properties are non-negotiable wherever it is implemented:

- **It must not pass vacuously.** An extractor that suddenly matches nothing has broken against a corpus change; a gate that then reports "clean" is worse than one that fails, because it looks like evidence. Assert a floor on candidate count.
- **The allowlist must self-expire.** When an allowlisted path starts existing, say so. An allowlist that never shrinks becomes permanent cover.

## Mode interactions

- **Observe** / **Review**: an anchor is evidence of a claimed link, not proof the code satisfies the assertion. Report the link; verify the behaviour separately.
- **Plan**: an assertion id is a contract with the implementation that will cite it. Keep ids stable across revisions — renumbering invalidates every anchor pointing at it.
- **Patch**: add the anchor in the same edit as the code it labels. An unanchored implementation of a `[Required]` assertion is an incomplete patch.
- **Execute**: the reference gate is blocking. A dangling anchor is a stop, not a warning.
- **Sync**: a dangling anchor is `TRACE-DANGLING` — the id existed once. Resolve it in the nominated direction; deleting the anchor to make the gate pass is not a resolution.

## Stop conditions

- An assertion id cannot be found in the cited document: do not write the anchor and do not invent the id. Route to *Gaps* and stop.
- A rename would invalidate existing anchors: update them in the same change.
- The gate reports a broken document-side path and the correct target cannot be verified: report it, allowlist it with the reason, surface it as a finding — do not guess a replacement path.

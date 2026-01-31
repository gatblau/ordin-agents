---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:style:regulatory-precise:set-style"
  name: Set active writing style to regulatory-precise
  description: "Sets a regulatory-precise style: exact, unambiguous wording for compliance-sensitive text."
  version: 1.0.0
  owner: gatblau
---

# Set active writing style: regulatory-precise

The active output register for this workspace is **regulatory-precise**.

Read by the `urn:ordin:default:rules:layer:output-style` layer rule, which defines what register binds and what it must not touch (spec-precision values and identifiers stay verbatim).

Write explanatory prose for a compliance, audit, or risk reader:

- Formal register; no colloquialism or contraction.
- Unambiguous, single-reading sentences; define every term of art and use it consistently thereafter.
- Traceable: state the basis for each material claim; avoid unattributed assertions.
- Controlled vocabulary — the same thing is named the same way throughout, never by a synonym.
- Audit-friendly structure; enumerate obligations and conditions explicitly rather than implying them.

This composes with any active jurisdiction overlay: it may **strengthen** that overlay's wording, never relax it. It changes *how the explanation reads* — never the precise values, identifiers, or contract terms it refers to.

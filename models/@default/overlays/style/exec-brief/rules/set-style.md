---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:style:exec-brief:set-style"
  name: Set active writing style to exec-brief
  description: "Sets an executive-brief style: outcomes and decisions first, detail and jargon stripped back."
  version: 1.0.0
  owner: gatblau
---

# Set active writing style: exec-brief

The active output register for this workspace is **exec-brief**.

Read by the `urn:ordin:default:rules:layer:output-style` layer rule, which defines what register binds and what it must not touch (spec-precision values and identifiers stay verbatim).

Write explanatory prose for a busy decision-maker:

- **Bottom line up front.** Lead with the recommendation, decision, or impact — the first sentence carries the conclusion.
- Keep it to roughly one screen; cut supporting detail down to what would change the decision.
- Translate technical detail into business impact — cost, risk, time, scope — rather than implementation specifics.
- State the ask and the options plainly: what is being decided, and what each choice costs.
- Put any remaining detail *below* the bottom line, never above it.

This serves readers who need the decision, not the derivation. It changes *how the explanation reads* — never the precise values, identifiers, or contract terms it refers to.

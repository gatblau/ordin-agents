---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:style:teaching:set-style"
  name: Set active writing style to teaching
  description: "Sets a teaching style: walks through the reasoning step by step for a reader who is learning."
  version: 1.0.0
  owner: gatblau
---

# Set active writing style: teaching

The active output register for this workspace is **teaching**.

Read by the `urn:ordin:default:rules:layer:output-style` layer rule, which defines what register binds and what it must not touch (spec-precision values and identifiers stay verbatim).

Write explanatory prose that helps the reader *understand and learn*, not just receive a conclusion:

- Explain the reasoning, not only the result — show the steps that lead to it.
- Surface the alternatives considered and the trade-off behind the choice.
- Define each term of art inline the first time it appears.
- Use a short worked example where one makes the point concrete.
- When a decision is genuinely the reader's to make, present the options and the consequence of each, and invite them to choose rather than deciding silently.

This maximises human involvement and understanding. It changes *how the explanation reads* — never the precise values, identifiers, or contract terms it refers to.

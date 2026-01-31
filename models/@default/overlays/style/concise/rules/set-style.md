---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:style:concise:set-style"
  name: Set active writing style to concise
  description: "Sets a concise writing style: short sentences, the point first, little elaboration."
  version: 1.0.0
  owner: gatblau
---

# Set active writing style: concise

The active output register for this workspace is **concise**.

Read by the `urn:ordin:default:rules:layer:output-style` layer rule, which defines what register binds and what it must not touch (spec-precision values and identifiers stay verbatim).

Write explanatory prose for an expert reader who wants signal, not scaffolding:

- Terse. One sentence where one will do; a list over a paragraph.
- Omit obvious context and restated background — trust the reader to infer the routine.
- No hedging, no filler, no ceremony.
- Keep the jargon an expert expects; do not stop to define it.

This respects an expert's time. Terseness is not vagueness: it changes *how much* is said, never the precision of *what* is said — every value, identifier, and contract term stays exact.

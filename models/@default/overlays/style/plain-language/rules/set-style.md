---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:style:plain-language:set-style"
  name: Set active writing style to plain-language
  description: "Sets a plain-language style: everyday words and short sentences, without softening any exact spec value."
  version: 1.0.0
  owner: gatblau
---

# Set active writing style: plain-language

The active output register for this workspace is **plain-language**.

Read by the `urn:ordin:default:rules:layer:output-style` layer rule, which defines what register binds and — critically — what it must not touch: spec-precision values, identifiers, and quotations stay verbatim.

Write explanatory prose so a non-specialist can follow it on the first read:

- Short sentences, one idea each; prefer the active voice.
- Everyday words over jargon. When a technical term is unavoidable, define it in a few words the first time it appears.
- Expand an acronym on first use.
- Lead with the point, then give the detail.
- Replace nominalisations with verbs ("we decided", not "a decision was taken").
- Keep paragraphs short; use a list when there are three or more items.

This lowers the reader's cognitive load and maximises non-specialist involvement. It changes *how the explanation reads* — never the precise values, identifiers, or contract terms the explanation refers to (a latency budget stays `<200ms p95`, it does not become "fast").

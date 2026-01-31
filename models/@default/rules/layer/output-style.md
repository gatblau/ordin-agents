---
apiVersion: ai.enterprise/v1
kind: rule-layer
metadata:
  id: "urn:ordin:default:rules:layer:output-style"
  name: Output style
  description: "Sets the tone and reading level of the agent's explanations. An installed style overlay can override it."
  version: 1.0.0
  owner: gatblau
---

# Output style (layer rule)

A **layer rule**: composes on top of whichever working mode (`@default/rules/orchestrators/working-modes.md`) is active. It governs the **register** — tone, complexity, and cognitive load — of the agent's *explanatory* prose. It does not replace the active mode; it constrains the *style* of its narrative output. It is orthogonal to `output-language` (which governs *locale*): register and locale compose independently.

## Active register

- The **default active register is `standard`** — the skill's own default phrasing, unchanged.
- If a `StyleOverlay` is installed (see `@default/overlays/`), it ships a `set-style.md` rule that declares the active register. That declaration supersedes the default.
- Exactly one `StyleOverlay` may be active at a time. If two are present at install time, the compiler refuses the bundle.

## What this rule binds

The active register governs the **explanatory prose** a skill emits — the parts written *for a human reader to understand*, not the parts that are a contract:

- End-of-step summaries and Explain-mode narrative.
- Explanations, rationale, and "why" prose.
- Risk descriptions and clarifying questions surfaced to the user.
- Design (HLD) and spec narrative prose; runbook and release-note narrative.
- The narrative portions of commit-message bodies.

Register shapes sentence length, vocabulary level, jargon density, how much context is spelled out, and where the conclusion sits relative to the supporting detail — per the installed overlay's `set-style.md`.

## What this rule does NOT bind

The register governs *how an explanation reads*, never *what a contract says*. It must not touch:

- **Spec precision (the `plan-mode` S1 rule).** Where a spec states a concrete technical constraint — `<200ms p95`, `AES-256`, an exact error-code string, a status code, a field type — that value is retained **verbatim**, regardless of register. A `plain-language` register may explain *around* `<200ms p95`; it may never soften it to "fast". The precise contract always wins over readability.
- Code identifiers, keywords, library APIs, and file / package / tool / command / environment-variable names.
- Proper nouns, brand names, product names.
- Verbatim quotations of user input, log lines, error strings produced by external systems, commit hashes, or upstream artefacts cited verbatim.
- Anything `output-language`'s exemption list already protects.

These remain in their authored form regardless of the active register.

## Conflict with skill-level mandates and other layer rules

- This rule supersedes any fixed tone convention a skill declares ("terse throughout"); skills defer to the active register.
- It is subordinate to the **precision and no-weasel-words rules** of `plan-mode` (S1, S4) and to the safety claims of any brand or jurisdiction overlay: register may make an explanation plainer, never make a contract vaguer or weaken a safety statement.
- It composes independently with `output-language`: apply the active register *and* the active locale; neither overrides the other.

## How a skill applies this rule

1. Read the active register from any installed `StyleOverlay`'s `set-style.md`. If none is installed, the active register is `standard`.
2. Author explanatory prose in that register, following the overlay's concrete guidance.
3. Keep every spec-contract value, identifier, and exempt category (above) exactly as authored — shape the explanation, not the contract.
4. Apply the active locale (`output-language`) on top: register sets *how plainly or formally*; locale sets *in which language*.

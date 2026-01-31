---
apiVersion: ai.enterprise/v1
kind: rule-layer
metadata:
  id: "urn:ordin:default:rules:layer:output-language"
  name: Output language
  description: "Sets the language of everything the agent writes. Defaults to British English, and an installed language overlay can override it."
  version: 1.0.0
  owner: gatblau
---

# Output language (layer rule)

A **layer rule**: composes on top of whichever working mode (`@default/rules/orchestrators/working-modes.md`) is active. It governs the natural-language locale of every artefact a skill or command emits. It does not replace the active mode; it constrains its output.

## Active locale

- The **default active locale is `en-GB`**.
- If a `LanguageOverlay` is installed (see `@default/overlays/`), it ships a `set-locale.md` rule that declares the active locale. That declaration supersedes the default.
- Exactly one `LanguageOverlay` may be active at a time. If two are present at install time, the compiler refuses the bundle.

## What this rule binds

The active locale governs:

- Spelling and idiom of all narrative prose — section bodies, summaries, explanations, GoDoc / docstring comments, commit message subjects and bodies, runbook narratives, design and spec prose.
- Date and number format conventions in narrative output.
- Translation of any prose carried forward from a skill's templates or references. Templates are guidance, not literal text — translate template prose into the active locale before emitting it.

The active locale does **not** govern:

- Code identifiers (function names, type names, variable names, file paths, package names).
- Keywords, reserved words, or library APIs.
- Proper nouns, brand names, product names.
- Tool names, command names, environment variable names.
- Verbatim quotations of user input, log lines, error strings produced by external systems, or commit hashes.
- Direct quotations from upstream artefacts that the skill is asked to cite verbatim.

These remain in their authored form regardless of the active locale.

## Conflict with skill-level mandates

If a skill or its references declare a fixed natural-language convention (for example "British English throughout"), this layer rule supersedes that declaration. Skills must defer to the active locale; references should be updated to reference this rule rather than naming a locale directly.

## How a skill applies this rule

1. Read the active locale from any installed `LanguageOverlay`'s `set-locale.md`. If none is installed, the active locale is `en-GB`.
2. Author all narrative output in that locale.
3. Where a template contains example prose in a different locale, treat the example as guidance and rewrite the example into the active locale before emitting it.
4. Leave identifiers, keywords, and exempt categories (above) untouched.

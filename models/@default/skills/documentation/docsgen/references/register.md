# register — the binding jargon ban, teaching register, and precision boundary

This reference is the register constraint `docsgen` supplies to `humanise` at step 9, and the rule every page's prose must satisfy before it is written. It is derived from two style overlays:

- **`urn:ordin:default:overlays:style:plain-language:set-style`** — everyday words, short sentences, one idea each, active voice; a technical term defined in a few words at first use; an acronym expanded on first use; the point led with, then the detail.
- **`urn:ordin:default:overlays:style:teaching:set-style`** — explain the reasoning and the steps that lead to a result, surface the alternative considered and the trade-off behind the choice, define each term of art inline at first use, use a short worked example where it makes the point concrete, and present a genuine reader decision as options with consequences rather than deciding silently.

`docsgen` combines the two: teaching prose written in plain language.

## Reader calibration

Write for a **newcomer** by default — a reader who has not seen this system before and cannot be assumed to know its vocabulary. When `audience` is `operator`, assume the reader runs the system but has not built it: they know the domain and the surface, so a page may name a route or a command without teaching it, but still must not assume knowledge of the system's internal structure.

For either reader:

- Lead each page with the idea it teaches, stated as a plain sentence, before any component name.
- Define every term of art at its first use on the page, in a few words a non-specialist follows on the first read.
- Expand every acronym at its first use.
- Show the reasoning, not only the conclusion: when the system does something non-obvious, give the step that leads to it and the alternative it was chosen over, so the reader learns why rather than only what.
- Use one short worked example where it makes an idea concrete.
- Keep each page to the ideas its rung owns; push anything a later rung teaches to that rung.

## The jargon ban

A page carries **no unexplained term of art**. A term is either defined at first use or replaced with plain wording. The register constraint `docsgen` hands to `humanise` names this ban, so the anti-AI-prose pass reports any surviving term of art the page has not defined (`HUM_REGISTER_UNMET`), and `docsgen` then defines or replaces it before writing the page.

## The precision boundary

The register governs **how the explanation reads, never what it asserts**. It must not soften or alter a precise value the target project states. These stay verbatim on the page, exactly as the source, design or specification records them:

- Exact values and budgets (a latency target of `<200ms p95` stays `<200ms p95`; it does not become "fast").
- Identifiers — function, type, route, table, column, config-key, environment-variable and command names — reproduced character for character.
- Quoted error strings, status codes and message subjects.
- Direct quotations from the target's design or specification.

Plain wording is applied to the surrounding explanation, not to the value it explains. Simplifying a value is a defect, not a stylistic choice: the reader learns the real contract, in plain prose about it.

# Phase E — Self-audit checklist

Tick every item `[x]` or `[ ]`. For every `[ ]`, return to Phase B or C, fix, and re-audit. Do not deliver the response with any item unchecked.

This checklist is **stack-neutral**. The Practice Pack contributes one or more language-specific items at the end of the list (e.g. "GoDoc on every exported symbol"); those items live in the active Practice Pack's `annotation-conventions.md` and are appended to this checklist at audit time.

## Stack-neutral items

```
[ ] Every function / method in the spec's Public Interface is implemented
[ ] Every step in the spec's Internal Logic has corresponding code with a spec-linking comment
[ ] Every `[Required]` assertion implemented in this step carries a `spec:` anchor citing an id read from the spec document (form per Practice Pack `annotation-conventions.md`; rule `urn:ordin:default:rules:layer:spec-anchors`)
[ ] Every row in the spec's Error Table has: (a) a handling code path, (b) a unit test
[ ] Every Gherkin scenario has a corresponding test function
[ ] Every field in the spec's Data Model has: (a) typed declaration, (b) validation, (c) test
[ ] All serialisation tags / aliases match the spec's API contract field names exactly
[ ] All HTTP status codes match the spec's Response section exactly
[ ] All error code strings match the spec's Error Table exactly
[ ] No placeholder comments (TODO, FIXME, ..., ellipses) or placeholder implementations remain
[ ] No panic / fatal-exit calls outside the process entry point
[ ] Every persistence query uses parameterised inputs — no string concatenation against caller-controlled data
[ ] Every external call has a timeout derived from the spec's latency targets
[ ] Every exported / public symbol carries a documentation comment in the active locale (form per Practice Pack `annotation-conventions.md`)
[ ] The language's idiomatic cancellation primitive (context, AbortSignal, CancellationToken, …) is the first parameter of every I/O function
[ ] All resources cleaned up deterministically (defer / using / try-with-resources / async-disposable / equivalent)
[ ] File paths match the Phase A6 plan exactly — no extra files, no missing files
[ ] Test file count matches implementation file count (1:1 where logic exists)
[ ] Shared types from Phase 2 are imported, not redefined
[ ] Cross-cutting policies from Phase 4 applied (error shape, auth, logging, config, metrics)
[ ] Phase 1 assumptions respected — no code contradicts a recorded assumption
[ ] Build-context interfaces consumed without signature mismatch — function signatures, struct fields, and method receivers match prior components character-for-character
[ ] Implementation respects the visibility convention from the Practice Pack's `file-layout.md` (default unexported / private; only essential interfaces and types are exposed)
[ ] All narrative comments use the active locale (see `urn:ordin:default:rules:layer:output-language`; default en-GB)
[ ] All four mandatory framework gates pass (build, lint, integration suite, security scan) per the Practice Pack's `build-commands.md`
[ ] Migrations are paired (forward + reverse) and the reverse is a true reverse
```

## Practice-Pack contributions

The active Practice Pack appends language-specific or framework-specific audit items at the end of the checklist. Examples of items a Practice Pack might add:

- *(Go pack)* Every exported function has a GoDoc comment whose first sentence starts with the symbol's name.
- *(Go stack + library pack)* Every HTTP handler (e.g. an Echo handler from the active library pack) carries Swag annotations (`@Summary`, `@Param`, `@Success`, `@Failure`, `@Router`).
- *(TypeScript pack)* Every exported type has a TSDoc block.
- *(Java pack)* Every public class / method has a Javadoc block.

These items appear in the rendered checklist if the Practice Pack contributes them. The workspace itself does not name the form.

## Output format for Phase E

Reproduce the checklist (workspace items + Practice-Pack contributions) with `[x]`/`[ ]`. For any item initially unchecked, add a one-line note explaining what was fixed (and in which Phase B/C file) before the final delivery.

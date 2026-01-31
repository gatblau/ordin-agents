# Code-evidence classification

Loaded by `specgen` when the active mode is `code-evidence`. Defines the four-way classification that every spec assertion carries in this mode, the witness rules that promote an assertion to *Required*, and the relationship to `sync-check`.

The discipline is the same as the rest of CSPA: **observe before infer; never fabricate identifiers; state uncertainty explicitly**. The novelty here is that the spec is being authored against an existing codebase, so each assertion has a verifiable provenance in code (or it does not, in which case it is a *Gap* or *Not implemented*).

## The four classes

Every assertion in a Component spec, Cross-cutting spec, Public Interface row, Internal Logic step, Error Table row, and Gherkin scenario carries exactly one of these tags in `code-evidence` mode.

### `[Required]`

The assertion is **present in code** AND has a **witness** that makes it part of the contract the rewrite must preserve. A witness is one of:

- A passing test that exercises the assertion.
- An external contract that names the assertion (OpenAPI document, gRPC `.proto`, NATS subject schema, vendor API contract, regulatory specification).
- An explicit user confirmation captured during the code-evidence interview (`/design` Phase 2 §6).
- A regulatory or compliance obligation cited in the as-built design's *Must preserve* subsection.

`[Required]` assertions are load-bearing for any downstream rewrite. They flow into `codegen` as binding contracts and into `testgen` as required test coverage.

### `[Observed]`

The assertion is **present in code** but **no witness** has been found. The behaviour exists; it might be intentional, it might be accidental. It corresponds 1:1 with an entry in the as-built design's *Observed but not required* subsection.

`[Observed]` assertions are the safe default for any behaviour read from code without a test, contract, or user confirmation. The spec records them so the downstream reader can decide what to do, but does **not** treat them as requirements. `codegen` may implement them as best-effort behaviour preservation; it is not obliged to.

Promotion to `[Required]` happens only by acquiring a witness. Re-reading the code more carefully does not count.

### `[Not implemented]`

The assertion is **named in the design's *Must preserve* subsection** (or otherwise required by an external contract) but **no matching code is found**. The contract exists; the implementation does not.

`[Not implemented]` assertions are the load-bearing input to a rewrite or a remediation. They are never silently dropped from the spec — leaving them visible is the point. `codegen` will see them and produce the missing implementation; `testgen` will produce the missing tests.

### `[Gap]`

The assertion is **suspected but unverifiable**. Naming patterns, comments, or partial signals point at it; no evidence in code or tests confirms it; no witness has been offered.

`[Gap]` assertions follow the same rules as the existing Component spec template's *Gaps* section: they block promotion of the spec from *Draft* to *Approved*. They must be resolved (witness produced, code located, behaviour confirmed, or assertion removed) before `codegen` will consume the spec.

## Decision rules

For each candidate assertion the skill considers, follow this decision tree:

1. **Is the assertion named in the design's *Must preserve* subsection?**
   - Yes → check code for the implementation.
     - Implementation found → `[Required]` (the witness is the *Must preserve* entry; cite the witness type).
     - Implementation not found → `[Not implemented]`.
   - No → continue.
2. **Is the assertion named in the design's *Observed but not required* subsection?**
   - Yes → check whether a witness has emerged since the design was authored (a new test, a contract surfaced in the witness-sources interview question).
     - Witness found → `[Required]`. Update the design's *Must preserve* subsection in the same pass.
     - No witness → `[Observed]`.
   - No → continue.
3. **Is the assertion named in the design's *Drop candidates* subsection?**
   - Yes → omit the assertion from the spec entirely. Do not classify; the user has explicitly removed it.
4. **Is the assertion suspected from naming, comments, or partial signals only?**
   - Yes → `[Gap]`.
5. **None of the above** — the assertion cannot be traced to the as-built design. Treat as a `[Gap]` with the note "assertion not present in design"; this signals the design is incomplete and must be returned to `/design` for a follow-up code-evidence pass.

## Witness types and how to cite them

Every `[Required]` tag must carry a witness citation in the spec body. The format mirrors the evidence-tagging convention from `@default/skills/quality/designgen/references/code-evidence-intake.md`:

| Witness type | Citation format |
|---|---|
| Passing test | `[witness: test:<path/to/file>:<test name>]` |
| External contract | `[witness: contract:<path-or-uri>]` |
| User confirmation | `[witness: user-confirmation:<one-line summary>]` (mirrors the as-built design's *Must preserve* witness column) |
| Regulatory obligation | `[witness: regulation:<short-name>]` |

If a candidate `[Required]` cannot carry one of these citations, it is not yet `[Required]`. Demote to `[Observed]` and capture the missing witness as an open question for the user.

## Relationship to sync-check

`sync-check` performs the assertion-vs-code comparison after-the-fact for drift detection. The cross-check logic specgen needs in `code-evidence` mode is the same logic, applied at spec-authoring time rather than at drift-resolution time.

**Reuse, do not duplicate.** When walking the candidate assertions, follow the aspect-by-aspect comparison rules in `@default/skills/sync/sync-check/references/spec-code-checks.md` (Aspect S1 public interface, S2 HTTP routes, S3 JSON field names, S4 error codes, etc.). The mapping between sync-check's drift labels and this file's four classes is:

| `sync-check` drift label | Translates to (at spec-authoring time) |
|---|---|
| Assertion in spec + matching code definition | `[Required]` if a witness exists; otherwise `[Observed]`. |
| Assertion in spec, no code (CONTRACT-DRIFT, spec is correct side) | `[Not implemented]`. |
| Code definition, not in spec (SCOPE-GAP, code orphan) | `[Observed]` if the as-built design lists it; `[Gap]` otherwise. |
| REALITY-DRIFT (both sides changed in disagreeing ways) | Should not occur in code-evidence mode (no prior spec to disagree with). If it does, treat the code as the source of truth and demote to `[Observed]`. |
| INTENT-DRIFT (design changed) | Stop and return to `/design` — the design itself needs another pass. |

## Anti-patterns

These are the failure modes most likely to corrupt a code-evidence-mode spec. Refuse to produce any of them.

- **Promoting `[Observed]` to `[Required]` to make the spec "look complete".** A spec full of `[Required]` tags is worse than a spec honest about which assertions lack witnesses. Coverage is not the goal — accuracy is.
- **Hiding `[Not implemented]` by omitting the assertion.** If the design's *Must preserve* names a behaviour and the code does not implement it, the spec must say so. Silent omission is the failure mode this mode exists to prevent.
- **Inventing assertions that do not appear in either the design or the code.** The `identifier-verification` layer rule still applies. Every signature, route, error code, and field name in the spec must trace to either the design (which itself traced to evidence) or the code.
- **Treating tests as specifications without the design.** A test exercises a behaviour; that behaviour becomes `[Required]` only because the contract is "tests must keep passing". If the user marks the test as encoding a bug (per the testgen anti-pattern rule), the assertion moves from `[Required]` to `[Observed]` and the test is flagged for deletion in the next sync.
- **Resolving `[Gap]` by reading the code more carefully.** A `[Gap]` is unresolved because evidence is missing, not because the reader is inattentive. Widen the evidence (more files, more interviews, locate a contract) or mark the spec *Draft*.

## Hand-off

The classified spec is the input to:

- `/breakdown` — consumes the Generation Playbook, which orders work by component. Each `[Required]` becomes a build target; each `[Not implemented]` becomes a remediation target; each `[Observed]` is best-effort; each `[Gap]` is a hard stop.
- `codegen` (via `/apply`) — refuses to consume any spec with one or more `[Gap]` assertions. `[Required]` and `[Not implemented]` are implemented; `[Observed]` may be preserved best-effort with a `// SPEC-OBSERVED: <one-line>` comment so the downstream reader can audit what was carried forward without a witness.
- `testgen` — generates tests for `[Required]` (verifying the witness still holds) and `[Not implemented]` (the failing test is the remediation harness). `[Observed]` gets a `t.Skip("observed-only behaviour; no witness")` placeholder per the testgen suspected-bug pattern.
- `/sync-check` — re-runs the same aspect-by-aspect comparison against the resulting code; the four-class taxonomy here and the drift labels in `sync-check`'s `drift-taxonomy.md` round-trip cleanly.

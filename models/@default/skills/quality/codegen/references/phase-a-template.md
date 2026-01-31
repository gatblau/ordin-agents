# Phase A — Spec Extraction & Pre-Flight

Produce all seven artefacts in order. Do not proceed to Phase B with unresolved blockers in A5 or A7.

This template is **stack-neutral**. Concrete file paths in A6 come from the active Practice Pack's `file-layout.md`; the template here shows the table shape, not the language-specific paths.

## A1 — Playbook Step Identification

```
| Aspect              | Detail                                        |
|---------------------|-----------------------------------------------|
| Playbook step #     | <number from phase-5-playbook.md>             |
| Component name      | <as named in phase-3 or phase-4>              |
| Spec location       | <phase-3 section X / phase-4 section Y>       |
| Spec type           | <domain component / cross-cutting concern>    |
```

## A2 — Extracted Contract Summary

```
| Aspect                    | Detail                                      |
|---------------------------|---------------------------------------------|
| Component                 | <name>                                      |
| Component path            | <repo-relative directory per Practice Pack> |
| Public symbols            | <exported symbols + one-line justification> |
| Dependencies              | <internal modules + external libs>          |
| Persistent state touched  | <reads: X, writes: Y>                       |
| Events / messages produced| <list or "none">                            |
| Events / messages consumed| <list or "none">                            |
| Error codes               | <every code from the spec error table>      |
```

## A3 — Cross-Cutting Policies Applied

```
| Phase 4 Spec              | Impact on this component                     |
|---------------------------|----------------------------------------------|
| Global Error Handling     | <error response shape, logging policy>       |
| Authentication            | <auth scheme on endpoints X, Y>              |
| Logging & Observability   | <metrics to emit, trace ID propagation>      |
| Configuration             | <env vars consumed>                          |
```

Include every Phase 4 spec that materially affects this component; omit rows that genuinely do not apply.

## A4 — Shared Types Referenced

```
- SharedType1 (defined in <module path per Practice Pack>) — used as <field / param / return>
- SharedType2 ...
```

Types must be imported, never redefined (R8, R13).

## A5 — Dependency Interface Check

```
| Dependency         | Expected interface / function           | Present in build context? |
|--------------------|-----------------------------------------|---------------------------|
| UserRepository     | GetByID(<ctx>, id) → (User, error)      | yes / no                  |
```

If any row is "no": state whether you will generate an interface stub (and why the stub is safe) or stop and report a blocking gap.

## A6 — File Plan

List every file to be produced with its repo-relative path and one-line purpose. The path scheme and the per-component file set come from the active Practice Pack's `file-layout.md` — do not invent a layout. The shape below shows the table format; the actual paths and file names depend on the language and the Practice Pack.

```
<component-dir>/<errors-file>           — Typed error definitions and code registry
<component-dir>/<model-file>            — Data models and validation
<component-dir>/<repository-file>       — Persistence access (queries, transactions)
<component-dir>/<service-file>          — Business logic orchestration
<component-dir>/<handler-file>          — Entry-point handler (HTTP / message bus / CLI)
<component-dir>/<wire-file>             — Constructors / wiring
<migrations-dir>/<YYYYMMDDHHMMSS>_<name>.up.<ext>
<migrations-dir>/<YYYYMMDDHHMMSS>_<name>.down.<ext>
<component-dir>/<service-test-file>
<component-dir>/<handler-test-file>
<component-dir>/<repository-integration-test-file>     — Integration test
```

Phase B must produce exactly the files listed here — no more, no fewer.

## A7 — Spec Gaps Detected

For each ambiguity, contradiction, or missing detail:

```
SPEC-GAP-1: <gap description>
Resolution: <what you will do>
Blocking?: yes / no
```

If no gaps: write exactly "None detected." If any gap is blocking, stop and report to the user before Phase B.

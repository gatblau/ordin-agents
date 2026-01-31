# Trivial-pattern set

Canonical list of diff-hunk patterns that qualify a change for the **Trivial** class, given that the four signals in `classification-rubric.md` all read Local-eligible. A change is **Trivial** only if *every* hunk in the diff matches one of these patterns.

## Permitted patterns

1. **Comment-only edits.** Lines added, removed, or changed are inside a comment (line comment, block comment, docstring) in the source language. No surrounding code change.
2. **Log-string edits.** Changes to a string literal passed to a logging call, where the call site, level, and structured fields (if any) are unchanged. Format-string parameter counts must match before and after.
3. **Doc-only edits.** Changes confined to `*.md`, `docs/**`, `README*`, `CHANGELOG*`, GoDoc / JSDoc / Pydoc blocks, or other documentation files declared by the Practice Pack. No source files touched.
4. **Dependency bumps within the declared range.** Changes confined to dependency manifests (`go.mod`/`go.sum`, `package.json`/`package-lock.json`, `pyproject.toml`/`poetry.lock`, etc.) where the new version is within the SemVer range or constraint already declared. Major-version bumps and constraint changes are **not** Trivial.
5. **Whitespace and formatter output.** Changes confined to whitespace, line endings, or the output of the project's declared formatter (Practice-Pack-supplied). Must produce a no-op AST diff.
6. **Test fixture or testdata file edits.** Changes confined to files under `testdata/`, `fixtures/`, or the equivalent declared by the Practice Pack, where no test source is touched.

## Disqualifying patterns

A diff is **not** Trivial — even if it looks small — if any hunk does any of the following:

- Adds, removes, or renames a function, method, type, constant, struct field, or interface member.
- Changes a function signature, even if the body is unchanged.
- Changes control flow (adds/removes a conditional, loop, return, defer, error path).
- Changes an error message that is part of a documented contract or asserted in tests.
- Changes a public identifier of any kind (case sensitivity matters).
- Touches generated code without re-running the generator (the regeneration is the change to file).
- Changes a feature-flag default or an environment variable name.
- Touches `schema/**` or `*.sql` (schema signal already forces Standard, but this is the defensive belt-and-braces).

## Resolution rule

If any hunk in the diff fails to match a permitted pattern, the change is at most **Local**, never **Trivial**. If the signals also disqualify Local, the change is **Standard**.

When in doubt, propose the higher class. The conservative bias is by design.

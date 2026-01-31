---
apiVersion: ai.enterprise/v1
kind: operating-mode
metadata:
  id: "urn:ordin:default:rules:modes:execute-mode"
  name: Execute mode
  description: "Run allowed build, test, and lint commands to check the work, without changing shared state."
  version: 1.0.0
  owner: gatblau
---

# Execute mode — behavioural validation against allowlisted tools

Auxiliary mode. Use when a skill needs to run a sandboxed command — build, test, lint, dry-run migration — to verify the artefact it has produced. Never a top-level entry mode the user invokes directly; always invoked from inside a skill.

## Permission boundary

**Restricted writes against allowlisted tools.** The agent may run commands from a fixed allowlist that mutate sandboxed state (build artefacts, test caches, local dry-run output). It may not run commands that mutate user-visible state (commit, push, deploy, real migration, package publish).

## Allowed tools

The exact build, test, lint, and migration-dry-run commands come from the **active Practice Pack's `build-commands.md`** — the workspace itself names no toolchain. Examples of what a Practice Pack might supply:

- *(Go pack)* `go build`, `go test`, `go vet`, `golangci-lint run`.
- *(TypeScript pack)* `npm test`, `npm run build`, `npm run lint`, `tsc --noEmit`.
- *(Python pack)* `pytest`, `ruff`, `mypy`, `black --check`.
- *(Migration tooling)* dry-runs that produce diffs but do not apply (e.g. `goose validate`, `migrate ... up --dry-run`).

In addition, regardless of Practice Pack:

- Sandboxed container builds with no registry push.
- Project-declared verification commands listed in the Generation Playbook.

If no Practice Pack is installed and no project-conventions file declares a command, the skill stops and asks the user — do not silently invoke a default.

## Prohibited actions

- Any command that mutates shared state: `git commit`, `git tag`, `git push`, `git merge`, branch deletes, force-push, PR open / merge, deploy, release publish, real migration against a shared database, package publish
- Network calls to external services beyond what tests already mock
- Writing test fixtures or source under cover of "verification" — that is Patch
- Suppressing failures (`--no-verify`, `|| true`, `-k` to skip flaky tests) — a failure is a stop, not a workaround

## When to enter

- `codegen` Phase C4 blocking gate: build, tests with ≥70% coverage, lint
- `testgen` running its own generated tests to confirm they pass against the spec
- `schemagen` dry-running a migration to verify SQL parses and produces an expected plan
- Any skill's verification gate that requires running a command, not just reading files

## When to exit

- Hand to **Review** with the command's output as evidence
- Hand to **Patch** when a verification fails and the spec / code must be fixed
- Hand to **Escalate** when a verification fails for a reason outside the agent's scope (CI environment difference, missing secret, flake)

## Output skeleton

`Command run` (exact, with flags) → `Exit status` → `Output excerpt` (relevant lines only) → `Pass / Fail` → handoff.

## Stop conditions

- A verification command fails: stop, report — do not retry with relaxed flags.
- A required tool is missing from the environment: stop and Escalate. Do not install it implicitly.
- Coverage falls below the spec-declared threshold: stop, report — do not lower the threshold to pass.

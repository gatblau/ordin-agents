---
apiVersion: ai.enterprise/v1
kind: rule-layer
metadata:
  id: "urn:ordin:default:rules:layer:branching-strategy"
  name: Branching strategy
  description: "Sets the git branching workflow the agent follows for git actions. An installed source-workflow overlay can override it."
  version: 1.0.0
  owner: gatblau
---

# Branching strategy (layer rule)

A **layer rule**: composes on top of whichever of the nine modes (`@default/rules/orchestrators/working-modes.md`) is active. It governs the **source-repository workflow** — the branching strategy and its derived knobs — that the agent follows whenever it authors or proposes a git action (`git.commit`, `git.push`, `git.tag`, `git.merge`, `github.pullrequest.merge`). It does not replace the active mode; it constrains the *shape* of git actions.

## Active strategy

- If no `SourceWorkflowOverlay` is installed, **no branching policy is imposed** — the agent follows its built-in git guidance (branch off the default branch; do not commit / push / merge without explicit authorisation).
- If a `SourceWorkflowOverlay` is installed, it ships a `set-branching-strategy.md` rule declaring the active strategy and its five knobs. That declaration supersedes the default.
- Exactly one `SourceWorkflowOverlay` may be active at a time. If two are present at install time, the compiler refuses the bundle.

## The five knobs

Each strategy fixes five things the agent reads before authoring any git action:

1. **Base branch** — the branch new work starts from (e.g. `main`, `develop`).
2. **Branch-name pattern** — the naming convention for a new branch (e.g. `feature/<id>-<slug>`, `release/x.y`).
3. **Direct-to-main allowed?** — whether a small change may commit directly to the base branch, or must go through a branch + pull request.
4. **PR target** — the branch a pull request merges into.
5. **Merge style** — merge commit, squash, or rebase; plus any backport / cherry-pick policy.

## What this rule binds

The active strategy governs the git actions the agent **authors or proposes**:

- The branch it branches from and the branch name it generates.
- Whether it proposes a direct commit to the base branch or a branch + PR.
- The PR target it opens against and the merge style it recommends.
- The commit-grouping and PR-scoping conventions the strategy implies.

## What this rule does NOT do

- **It does not grant a git action.** `toolPermissions` always win: if the workspace prohibits `git.push` / `git.merge` / etc., the strategy may shape an authorised action but can never opt a prohibited one back in.
- **Commit, push, tag, and merge remain user actions** (the `patch-mode` boundary). This rule governs what the agent *proposes and shapes*, not autonomous execution.
- It does not rewrite history, force-push, or delete branches on its own — those remain explicit user actions regardless of strategy.

## How a skill applies this rule

1. Read the active strategy and its five knobs from any installed `SourceWorkflowOverlay`'s `set-branching-strategy.md`. If none is installed, follow the built-in git guidance.
2. Before authoring any git action, shape it to the strategy: branch from the base branch, name the branch by the pattern, target the PR at the declared target, recommend the declared merge style.
3. Never use the strategy to perform or authorise a git action the workspace prohibits or that is reserved as a user action.

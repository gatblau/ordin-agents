---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:source-workflow:github-flow:set-branching-strategy"
  name: Set branching strategy to github-flow
  description: "Sets the git workflow to GitHub flow: branch off main, open a pull request, merge back after review."
  version: 1.0.0
  owner: gatblau
---

# Set branching strategy: github-flow

The active source-repository workflow for this workspace is **github-flow**.

Read by the `urn:ordin:default:rules:layer:branching-strategy` layer rule, which defines how the strategy shapes git actions and what it must not do (it never grants a prohibited action; commit / push / merge remain user actions).

The five knobs:

- **Base branch:** `main`.
- **Branch-name pattern:** a descriptive `<topic>` branch off `main` (e.g. `add-retry-budget`).
- **Direct-to-main:** not allowed — every change goes through a branch and a pull request.
- **PR target:** `main`.
- **Merge style:** squash or merge commit into `main`. No long-lived `develop` branch; `main` is always deployable.

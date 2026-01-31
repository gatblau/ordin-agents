---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:source-workflow:gitflow:set-branching-strategy"
  name: Set branching strategy to gitflow
  description: "Sets the git workflow to git flow: long-lived develop and release branches feeding main, plus feature and hotfix branches."
  version: 1.0.0
  owner: gatblau
---

# Set branching strategy: gitflow

The active source-repository workflow for this workspace is **gitflow**.

Read by the `urn:ordin:default:rules:layer:branching-strategy` layer rule, which defines how the strategy shapes git actions and what it must not do (it never grants a prohibited action; commit / push / merge remain user actions).

The five knobs:

- **Base branch:** `develop` (feature work branches from here). `main` holds tagged releases only.
- **Branch-name pattern:** `feature/<slug>` off `develop`; `release/x.y` and `hotfix/<slug>` per the gitflow roles.
- **Direct-to-main:** not allowed — `main` only ever receives merges from `release/*` and `hotfix/*`.
- **PR target:** `develop` for features; `main` (and back-merge to `develop`) for releases and hotfixes.
- **Merge style:** merge commits (no fast-forward), so the branch topology is preserved.

---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:source-workflow:feature-branching:set-branching-strategy"
  name: Set branching strategy to feature-branching
  description: "Sets the git workflow to feature branches: short-lived branches off the base, merged back by pull request."
  version: 1.0.0
  owner: gatblau
---

# Set branching strategy: feature-branching

The active source-repository workflow for this workspace is **feature-branching**.

Read by the `urn:ordin:default:rules:layer:branching-strategy` layer rule, which defines how the strategy shapes git actions and what it must not do (it never grants a prohibited action; commit / push / merge remain user actions).

The five knobs:

- **Base branch:** `main`.
- **Branch-name pattern:** one `feature/<id>-<slug>` branch per change off `main`, where `<id>` is the tracking ticket (e.g. `feature/PAY-412-retry-budget`).
- **Direct-to-main:** not allowed — every change is a feature branch.
- **PR target:** `main`.
- **Merge style:** merge or squash into `main`, PR-gated (review required before merge). One branch maps to one unit of work.

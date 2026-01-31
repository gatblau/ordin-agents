---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:source-workflow:trunk-based:set-branching-strategy"
  name: Set branching strategy to trunk-based
  description: "Sets the git workflow to trunk-based: small changes committed straight to the base branch."
  version: 1.0.0
  owner: gatblau
---

# Set branching strategy: trunk-based

The active source-repository workflow for this workspace is **trunk-based**.

Read by the `urn:ordin:default:rules:layer:branching-strategy` layer rule, which defines how the strategy shapes git actions and what it must not do (it never grants a prohibited action; commit / push / merge remain user actions).

The five knobs:

- **Base branch:** `main`.
- **Branch-name pattern:** short-lived `<topic>` branches; small low-risk changes may commit directly to `main`.
- **Direct-to-main:** allowed for small, low-risk changes; otherwise a short-lived branch.
- **PR target:** `main`.
- **Merge style:** rebase onto `main`; integrate frequently to keep branches short-lived. No long-lived development branch.

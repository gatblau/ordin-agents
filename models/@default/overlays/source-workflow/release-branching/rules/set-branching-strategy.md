---
apiVersion: ai.enterprise/v1
kind: rule
metadata:
  id: "urn:ordin:default:overlays:source-workflow:release-branching:set-branching-strategy"
  name: Set branching strategy to release-branching
  description: "Sets the git workflow to release branches cut from the base for stabilising and backporting."
  version: 1.0.0
  owner: gatblau
---

# Set branching strategy: release-branching

The active source-repository workflow for this workspace is **release-branching**.

Read by the `urn:ordin:default:rules:layer:branching-strategy` layer rule, which defines how the strategy shapes git actions and what it must not do (it never grants a prohibited action; commit / push / merge remain user actions).

The five knobs:

- **Base branch:** `main` for new work; long-lived `release/x.y` branches for each maintained line.
- **Branch-name pattern:** `release/x.y` for a release line; fixes branch off the relevant line.
- **Direct-to-main:** not allowed — changes land via PR; release lines receive only reviewed, targeted changes.
- **PR target:** the relevant `release/x.y` branch (or `main` for changes that lead the next release).
- **Merge style:** merge into the release branch; **cherry-pick / backport** fixes between `main` and the maintained `release/x.y` lines per the backport policy.

---
apiVersion: ai.enterprise/v1
kind: context-resource
metadata:
  id: "urn:ordin:default:context-resources:cspa-glossary"
  name: CSPA glossary
  version: 1.0.0
  owner: gatblau
  description: "Reference glossary for the CSPA-431 methodology — the four moves, the three intent doors, the single exit, and the nine working modes. Load it when a term like 'sync-check', 'the loop', 'CONTRACT-DRIFT', or 'Observe mode' is used and its meaning is not already clear from context."
---

# CSPA-431 — glossary

Reference definitions for the software-engineering methodology the CSPA-431 workspace runs. This is knowledge to consult, not a procedure to follow: the procedures live in the skills, the constraints in the rules, and the entry points in the commands.

## The name

**CSPA-431** decomposes as **4 moves, 3 doors, 1 exit**. The `-431` is part of the methodology's name, not a ticket identifier.

## The four moves

The core lifecycle. Each move is a command a user invokes; each consumes the previous move's artefact as its input.

- **Move 1 — Capture intent.** Turn a need into a structured artefact of intent (a design document, an RFC, or an RCA), depending on which door was taken.
- **Move 2 — Structure (`/spec`).** Turn captured intent into the six-phase specification set: the contract every later move is measured against.
- **Move 3 — Plan (`/breakdown`).** Turn a specification into an ordered set of implementable increments (phases), each with its own exit criteria.
- **Move 4 — Apply (`/apply`).** Implement one increment at a time, each guarded by the four mandatory gates (build, lint, integration suite, security scan).

## The three doors

Three entry points into Move 1, one per kind of work:

- **Door 1 — greenfield (`/design`).** A new capability with no prior intent artefact.
- **Door 2 — change request (`/rfc`).** A change to something that already exists.
- **Door 3 — incident (`/rca`).** A root-cause analysis of an observed failure, whose remediation becomes the intent.

## The single exit

- **`/sync-check`.** The final move of the loop: it verifies that Design, Spec, and Code remain in agreement. A change is *CSPA-complete* only when `/sync-check` exits clean. This is the invariant **no exit without sync**.

## The nine working modes

Every step of every skill or command runs in exactly one mode. Six are core (the CSPA loop); three are auxiliary (used inside skills, never as a top-level entry).

Core (the loop): **Observe** → **Infer** → **Plan** → **Patch** → **Sync** → **Review**.

- **Observe** — read-only evidence gathering; the default mode for every task.
- **Infer** — ranked hypotheses with named uncertainty; no writes.
- **Plan** — authoring structured artefacts (specs, ADRs, RFCs, runbooks); no source edits.
- **Patch** — proposing code changes; never commits, pushes, or merges.
- **Sync** — reconciling drift in a user-nominated direction; writes to one side only.
- **Review** — read-only critique against the spec and the safeguards; never promotes on its own.

Auxiliary: **Execute** (run allowlisted build/test/lint), **Explain** (plain-language summary), **Escalate** (stop and ask a human).

## The four drift labels

`/sync-check` classifies each disagreement it finds:

- **INTENT-DRIFT** — the design no longer matches the intent; re-run `/spec`.
- **CONTRACT-DRIFT** — the spec says X and the code says Y, with the spec authoritative; re-run `/apply` for the affected component.
- **REALITY-DRIFT** — the code was changed and the spec would revert it; the user chooses between reverting the code and updating the spec.
- **SCOPE-GAP** — something exists in neither side and needs human triage.

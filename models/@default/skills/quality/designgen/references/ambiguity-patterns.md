# Ambiguity patterns

Re-read the gathered answers. For each pattern matched below, decide per the rule. This step most directly affects downstream spec quality.

## Language patterns that signal ambiguity

| Phrase in interview answer | Likely meaning | Action |
|---|---|---|
| "fast", "quickly", "snappy" | No latency target set | Record as Assumption with a concrete figure (e.g. <200ms p95) unless the user objects |
| "secure" | Security posture undefined | Assumption: authn scheme, authz model, transport security, at-rest encryption — each as a separate row |
| "scalable" | Scale target undefined | Ask once: rows/sec, messages/sec, peak vs average. If still vague, Assumption with a stated ceiling |
| "reliable", "robust" | Failure modes undefined | Open Question if retry/idempotency design is material; Assumption with standard retry-with-backoff otherwise |
| "maybe", "perhaps", "could" | Decision deferred | Resolve to a concrete choice — Assumption if default is safe, Open Question if architectural |
| "later", "eventually", "in v2" | Scope creep warning | Move to Non-goals explicitly |
| "like X does" (X is another system) | Unstated parity expectation | Ask which specific behaviours of X are required. Do not assume full parity |
| "the usual way" | Convention inferred | Look up the project default in the workspace's project-conventions file and record explicitly as "project default — see <ref>" |
| "supports A, B, etc." | Enumeration incomplete | Ask for the full list; forbid "etc." in the final draft |
| "handles X" | Steps elided | Ask for the specific steps taken on X |

## Structural patterns

| Pattern | Action |
|---|---|
| Entity mentioned but no lifecycle stated | Ask the lifecycle question explicitly |
| Action mentioned but no trigger stated | Ask who or what initiates it |
| Action mentioned but no failure mode stated | Ask: what errors can this produce, and what should happen on each? |
| Cross-cutting row left empty after interview | Revisit with a direct one-liner: "Does <concern> apply? Yes, No, or project default?" |
| Performance target stated for some endpoints but not others | Ask whether the unlisted endpoints inherit the same target or have different ones |
| Multi-tenancy mentioned but tenant boundary not named | Ask: is tenancy enforced by subject, column, schema, or row-level security? |
| Migration implied but rollback not discussed | Ask: if we ship this and it goes wrong in prod, what does the rollback look like? |
| External service named but SLA / failure handling not discussed | Ask: what happens when the external service is down or slow? |

## HLD-specific patterns

These patterns sit on top of the structural ones and govern the HLD-only sections (System Context, System Architecture, Principal Sequences, Tech Stack, Regulatory Context, Architectural Decisions).

| Pattern | Action |
|---|---|
| "Standard stack" / "the usual stack" without naming members | Ask for one committed value per row in the Tech Stack table. "Usual" is not an answer. Capture rejected alternatives as ADR entries in §11. |
| Tech-stack row stated as a list of candidates ("Postgres or SQLite") | Resolve to one choice. If both are defensible, record as a blocking Open Question only when the choice changes architecture (e.g. embedded vs networked datastore). Otherwise pick the most conservative and capture the alternative as an ADR. |
| Regulatory context skipped silently | Force an answer. The valid answers are *named obligations* or *N/A — non-regulated*. Silence is not acceptable in the HLD. |
| "We're GDPR-compliant" without naming controls | Ask: which specific GDPR articles or controls apply, and how does the design address each? One row per obligation in the Regulatory table. |
| Sequence diagram skipped because "it's obvious" | Force the golden-path diagram. The diagram has a low cost in the HLD and a high cost in `/spec` if absent (specgen will guess and the LLD will drift from intent). |
| Sequence diagram present but trigger / result / error posture missing | Ask the three sub-questions and capture each as one line under the diagram. |
| Architectural decision stated as committed without alternatives | Ask: what was rejected and why? An ADR with no alternative is half an ADR. |
| Two ADRs that conflict with each other | Surface explicitly. Either one is superseded (and should be marked so) or they sit on different axes and the relationship needs prose explanation. |
| Component named in System Architecture but not in Domain Model / Sequences / Interfaces | Cross-check the four sibling files. A component that exists in only one is either misnamed, out of scope, or under-specified. Ask which. |
| External actor named in Context but not in any Sequence | Ask: what flow involves this actor? If none, why is it in the context diagram? |
| ADR rationale "for performance reasons" / "for scalability" without numbers | Ask for the target. "Performance" is not a justification; "<10ms p95 at 10× current load" is. |
| Tech stack row claims independence from the rest ("we could swap this any time") | Capture as an ADR with that claim as a stated *consequence*. If the claim turns out to be false during `/spec`, the HLD-impact-pass will surface the coupling. |

## ADR pattern

When the user describes a *decision*, distinguish three shapes:

| User says | Captured as |
|---|---|
| "We've decided X because Y, and we considered Z but rejected it because W." | **ADR entry** in §11 — Decision: X, Context: Y, Alternatives: Z (rejected: W). |
| "We're going to use X." (no rationale, no alternatives) | Ask for context and alternatives before recording. If they say "no reason, just pick" → record as an **Assumption** with `confidence: low`, not an ADR. ADRs require a *why*. |
| "We could go with X or Y." | **Open Question** with both options and their architectural impact. Mark blocking only if specification cannot start without the answer. |

## Resolvable by project default

Consult the workspace's project-conventions file and the existing `docs/design/` / `docs/spec/` trees for prior decisions. Record as "project default — see <ref>" rather than inventing a new policy. Defaults commonly found in this repo:

- JSON logging with correlation IDs.
- Error envelope shape.
- Rate limit (20 req/s/IP default per the Echo setup).
- Auth middleware identifier (`lib.UserAuth` or `lib.NewAuth`).
- Queue group name for NATS subscribers (`"insight"`).
- Multi-tenant routing encoded in NATS subjects (`tenant.*.site.*.appliance.*...`).

If a new design contradicts a project default, escalate to Open Question, not Assumption — the divergence is architectural.

## Deciding Assumption vs Open Question

Use this test:

- If two reasonable engineers would almost certainly pick the same default → **Assumption**.
- If two reasonable engineers might pick different defaults, and the choice changes the architecture (data model, interface shape, failure handling) → **Open Question**, marked **blocking**.
- If the user specifically says "I don't know and it matters" → **Open Question**, marked blocking.
- If the user says "I don't know, but you pick something safe" → **Assumption**, clearly labelled.

Never split the difference by writing vague prose in the body. Every ambiguity goes into one of the two tables, never into narrative.

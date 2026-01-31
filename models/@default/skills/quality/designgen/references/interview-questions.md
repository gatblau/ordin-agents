# Targeted interview questions

Ask only questions the intake phase did not already answer. Ask one question at a time when the answer needs thinking; batch simple yes/no questions. Do not ask all of these in every interview.

## 1. Domain model

- What are the main things (nouns) this feature deals with? (entities, records, objects)
- For each entity: is it newly introduced, or does it already exist elsewhere in the system?
- What is each entity's lifecycle? (created → updated → archived → deleted, or something else)
- What relationships exist between entities? One-to-one, one-to-many, many-to-many?
- Which entity "owns" which? (multi-tenancy, user ownership, workspace scoping)
- Are any entities shared across tenants, or strictly per-tenant?

## 2. Actions

- What verbs describe what the system does? (create, accept, publish, emit, reject, reconcile, ...)
- For each verb: what triggers it, what inputs it takes, what it produces, and what side effects it has (DB writes, messages published, files written)?
- Which actions are synchronous (caller waits) vs asynchronous (fire-and-forget)?
- Which actions are idempotent, which are not, and why?
- Which actions must be authenticated? Which require specific roles or permissions?

## 3. Non-functional requirements

- Expected request rate / message rate / job rate?
- Latency target for user-facing operations? p50 and p95, if known.
- Data volume: rows per day/month, bytes per record?
- Growth assumption: is this going to 10× in a year?
- Availability expectation: single-region, multi-region, zero-downtime upgrades?
- Security posture: does this handle PII, secrets, payments, or regulated data?
- Any specific compliance requirement? (GDPR, HIPAA, SOC2)

## 4. Cross-cutting concerns (check each explicitly)

Ask each row as a one-line question. Valid answers: "applies — <policy>", "does not apply — <reason>", "project default".

- **Authentication:** which authn scheme? (JWT, API key, session, mTLS, none)
- **Authorisation:** role-based, attribute-based, tenant-scoped only, or none?
- **Logging:** structured JSON with correlation ID (project default), or something different?
- **Metrics:** which Prometheus metrics should this emit? Any specific names already decided?
- **Tracing:** OTel spans on the hot path? Any particular sampling rate?
- **Rate limiting:** any endpoint here that should be throttled?
- **Pagination:** which endpoints return lists? Cursor or offset?
- **Input validation:** any field with a non-obvious constraint (max length, regex, forbidden values)?
- **Error handling:** standard envelope (project default) or specialised?
- **Configuration:** which env vars does this introduce? Any secret material?
- **Health checks:** does this add a new dependency (DB, NATS subject, external service) that readiness should reflect?
- **Migrations:** schema changes involved? Destructive (data loss) or additive?
- **Graceful shutdown:** any long-running operation that must drain cleanly?
- **CORS:** any new HTTP endpoint called from the browser directly?
- **Multi-tenancy:** how is tenancy encoded? (subject wildcards, column, schema, row-level security)

## 5. Known unknowns

- What parts of this are you unsure about right now?
- Are there alternative approaches you considered and rejected? Why?
- Is there an earlier attempt at this (code, design doc, prototype) worth looking at?
- Who else needs to weigh in before this design is finalised?

## 6. Code-evidence mode (intent confirmation)

Loaded only when the active mode is `code-evidence`. The questions in §1–§5 do not apply — the codebase has already supplied the nouns, verbs, flows, and cross-cutting stances. The interview's job here is **intent confirmation** against a specific list of observed behaviours produced by the scan in `code-evidence-intake.md`.

Open with the framing question, then walk the interview question-by-question against the entries in *Observed but not required*:

- **Framing.** "I have read the code under <paths>. The design document I've drafted documents what is there. Before we treat any of this as a requirement for a rewrite, I'd like to confirm with you which observed behaviours are intentional. I'll work through them one by one." (Wait for acknowledgement.)

For each entry in *Observed but not required* (one entry per turn — do not batch):

- "The code does X (`[evidence: <path:line>]`). Is that intentional? *yes* / *no* / *unsure*."
  - *yes* → promote to *Must preserve*. Capture the witness as `user-confirmation: <one-line summary of the user's reasoning>`.
  - *no* → move to *Drop candidates*. Capture the reason as one line.
  - *unsure* → leave in *Observed*; add a row to *Gaps* describing the unresolved question.

After the entry-by-entry pass, ask the closing questions:

- **Drop list.** "What in the current system would you explicitly *not* rebuild?" Anything offered here moves to *Drop candidates* even if the entry is not in *Observed but not required*.
- **Hidden constraints.** "What constraints exist that the code cannot tell us about — compliance, contractual obligations, organisational decisions, deprecated dependencies you're locked into, performance targets that aren't enforced by tests?" Each constraint becomes either an *Assumption* (if it has a sane default) or an *Open Question* (if it materially affects architecture).
- **Out-of-scope reassurance.** "Is there anything in the code I scanned that you would consider out of scope for this design? Anything I should treat as background rather than as the system being documented?"
- **Witness sources.** "Where do the contracts live — tests, vendor docs, regulatory specifications, captured wire traces? Anything I should treat as a witness for *Must preserve* that isn't already cited?"

Do **not** ask the standard greenfield discovery questions in code-evidence mode. The risk is using the interview to invent intent that the code does not show; the code is the evidence and the interview is the curation.

## 7. System context

- Which **external actors** (humans, other services, scheduled jobs, devices, message buses) interact with this system?
- For each external actor: what **protocol** is used and **how is the call authenticated**?
- Are there any **trust boundaries** that cross between actors? Where does authentication end and authorisation begin?
- Are there **neighbouring systems** the user expects to consume from or emit to (upstream and downstream)?
- Is there an existing context diagram for the surrounding platform you should reference rather than invent?

## 8. Tech stack

Choose one committed value per row. If multiple candidates were considered, capture the alternative as a one-line ADR in §11.

- **Language?** (Go, TypeScript, Python, Rust, Java, …)
- **Framework / runtime?** (Echo, Express, FastAPI, Spring, Actix, plain stdlib, …)
- **Datastore?** (Postgres, SQLite, BoltDB, Mongo, Redis, S3, none)
- **Message broker / queue?** (NATS, Kafka, SQS, Rabbit, none)
- **Deployment substrate?** (Kubernetes, ECS, Lambda, single VM, single binary on the user's machine, …)
- **Observability — logs, metrics, traces?** (Prometheus + Grafana, OpenTelemetry collector, CloudWatch, journald, …)
- **Signing / crypto?** (Sigstore, ed25519 with managed keys, JWS, mTLS, none)
- **Build / test toolchain?** (`go build`+`go test`, `npm`+`vitest`, `cargo`, `make`, …)

For each row: ask **why this and not the obvious alternative?** Capture the rationale in one line.

## 9. Regulatory and compliance context

- Does this system handle **PII, payment data, health data, or other regulated categories**?
- Is the system subject to **GDPR, HIPAA, PCI-DSS, SOC 2, IFRS 17, sector-specific** regulation? Multiple?
- Are there **jurisdictional** constraints — data residency, cross-border transfer restrictions, sovereign-cloud requirements?
- Are there **internal-policy** constraints that function like external regulation — corporate data-classification rules, mandatory audit logging, retention policy?
- For each obligation: **how does the design address it?** (Specific control, deferred to existing system, accepted risk with sign-off.) One line per obligation.
- If "N/A — non-regulated": confirm explicitly. Silence on regulation is **not** an acceptable answer in this interview — the answer must be either *no obligations apply* or *these obligations apply and here is how*.

## 10. Major sequences

The HLD must capture at least the **golden path** as a mermaid sequence diagram. Ask:

- **Golden path:** walk me through, step by step, what happens in the most common successful invocation. Who triggers it, what does the system do in order, what is the observable result?
- **Secondary paths:** is there any other flow that crosses component boundaries or external systems? (Migration flows, admin flows, retry flows, scheduled flows, partial failure recovery.)
- For each named sequence: **trigger** (who/what starts it), **observable result** (what changes that an outside party can see), **error posture** (retry / fail fast / alert / escalate on the principal failure modes).
- Are there sequences the user explicitly does **not** want documented because they're handled by an existing system or are considered cross-cutting (logging, metrics emission)?

## 11. Architectural decisions

ADR-shaped trade-offs are the structural backbone of the HLD. Walk back through the choices made in §3, §4, §7, §8, §9, §10 and for each material decision capture:

- **Decision** — the committed choice, in one sentence.
- **Context** — what forced the decision (constraint, deadline, prior incident, regulatory driver, performance target).
- **Consequences** — what follows from the decision, both intended and accepted trade-offs.
- **Alternatives considered** — at least one, with a one-line reason it was rejected.

Examples of choices that warrant an ADR (non-exhaustive):

- Datastore choice (e.g. "Postgres SKIP LOCKED for the work queue" — alt: Redis, alt: dedicated broker).
- Single-binary vs multi-service decomposition.
- Pull-only vs server-coordinated lifecycle.
- Signing scheme choice (managed keys vs Sigstore vs no signing).
- Tenancy boundary (column vs row-level vs schema vs DB).
- Synchronous vs asynchronous handling for a given action.
- Internal SDK vs adapters-per-runtime.

Ask the user explicitly: **"What architectural decisions have you already made that you'd like recorded as ADRs?"** Do not invent ADRs; if a choice has not been made consciously, surface it as an Open Question, not as an ADR with a guessed rationale.

## When to stop interviewing

Stop when:
- Every mandatory template section has enough content to be drafted without inventing facts.
- Every cross-cutting row has an answer (including "does not apply — <reason>").
- The Tech Stack table has a committed choice for every row, or an explicit "N/A — <reason>".
- The Regulatory section has either named obligations or an explicit "N/A — non-regulated".
- The golden-path principal sequence has been captured with trigger, result, and error posture.
- Every Architectural Decision the user has consciously made has been recorded as an ADR entry.
- Remaining uncertainty has been captured as an Assumption (defaults) or Open Question (architectural). Non-blocking is the default — `/spec` will surface and resolve LLD-driven architectural questions.
- In code-evidence mode: every entry in *Observed but not required* has been put to the user, and either reclassified or left in *Observed* with a reason.

Do not keep asking to fill in rough edges — the HLD exists to surface uncertainty, not eliminate it.

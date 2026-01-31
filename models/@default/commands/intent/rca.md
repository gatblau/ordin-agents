---
apiVersion: ai.enterprise/v1
kind: command
metadata:
  id: "urn:ordin:default:commands:intent:rca"
  name: /rca
  version: 1.2.0
  owner: gatblau
  description: "Works out the root cause of an error by gathering evidence and ranking likely causes, without patching. Saves a report when the analysis is long."
description: Root-cause analysis of an error using Observe → Infer (ranked hypotheses, no patch). Writes docs/wip/rca/NN-<slug>.md when the analysis is long or complex; otherwise returns inline.
argument-hint: "<error message, stack trace, or log excerpt>"
---

# /rca — Root Cause Analysis

You have been given the following error to investigate:

```
$ARGUMENTS
```

If `$ARGUMENTS` is empty, ask the user to paste the exact error message, stack trace, or log excerpt and stop.

## Active modes

**Observe → Infer, with Plan only for the optional working-file write.**

- **Observe** for evidence extraction: literal symbols, file paths, line numbers, error codes, and surrounding repository state. Anything not in the input or in the repo is not verified.
- **Infer** for the ranked-hypothesis pass: causes ordered by evidence strength, each tagged with the verified facts that support it and the verified facts that would refute it.
- **Plan** solely for step 6's file output — persisting the finished analysis to `docs/wip/rca/<NN>-<slug>.md`. No other artefact type is authored; the analysis content itself is produced in Infer.

The command never enters Patch, Sync, or Review — it produces analysis only. Even if the cause seems obvious, the remediation is not a patch; it is a `What to verify next` line that the user can hand to `/breakdown` or `/apply`. **Escalate** when the root cause cannot be located in the available evidence — the user must supply more (logs, repro steps, diff) before ranking can converge.

## Procedure

1. **Parse the error.** Extract concrete signals: error type/code, message text, file paths, line numbers, function/method names, subjects (NATS), SQL objects, HTTP routes, env vars, timestamps. Treat only what is literally in the input as verified.

1a. **Triage gate — is this self-locating?** Before investing in full hypothesis ranking, check whether the error meets **all** of:
   - A single concrete file path **and** line number (or a symbol that resolves to exactly one match in the repo).
   - An unambiguous error message (e.g. compile error, nil deref, undefined symbol, typed import failure) — not a generic timeout, 500, or "something failed".
   - No schema, migration, or distributed-systems signal (NATS subject, HTTP route across services, SQL object) — those always take the full path.

   If **all three** hold, emit the **short-path output** (see below) and stop. The user can re-invoke `/rca` without the short path if they want the full analysis, or follow with `/breakdown` → `/apply` for the fix. Otherwise, continue to step 2.
2. **Locate evidence in the repo.** Use Grep/Glob/Read to find each concrete signal. Read the exact lines surrounding any matched symbol or call site. Note when a signal cannot be located — that itself is evidence. If the concrete signals suggest artefact drift (missing HTTP route, stale JSON field name, unknown error code string, unresolved env var, DDL vs migration mismatch), note to the user that `/sync-check` may localise the cause faster than bottom-up grepping. Continue the RCA regardless — do not invoke sync-check from here. When multiple signals need independent lookups, issue the Grep/Read calls as a single message with parallel tool calls; only escalate to an `Explore` sub-agent when a signal requires open-ended searching across unknown paths.
3. **If the error touches `schema/**` or any `*.sql`**, layer **SQL & schema safety** rules on top: never name a table/column/function as verified unless visible in the repo.
4. **Generate ranked hypotheses.** Aim for 3–5 plausible root causes, ordered most-to-least likely. For each: one-line claim, the supporting evidence, the contradicting evidence (if any), and what would confirm or refute it.
5. **Do not collapse uncertainty.** If two hypotheses are equally supported, say so. Never present a guessed identifier, signature, or config value as confirmed.
6. **Decide on file output.** If the analysis is long or complex — more than ~5 ranked hypotheses, evidence drawn from more than ~3 files/packages/schema objects, or output longer than ~200 lines — write it to `docs/wip/rca/<NN>-<slug>.md`. Otherwise return inline.
   - **Slug:** pick a short kebab-case description of the failure yourself (3–6 words, lowercase, e.g. `nil-deref-in-payment-handler`, `nats-publish-timeout`). Do not ask the user for an id.
   - **Number:** scan `docs/wip/rca/` for existing `NN-*.md` files and use the next free two-digit ordinal. If the directory does not exist, create it and start at `01`.
   - The full path is therefore `docs/wip/rca/<NN>-<slug>.md` (e.g. `docs/wip/rca/02-nats-publish-timeout.md`).
   - The **short-path output** (triage gate passed) is always returned inline — never written to a file.

## File-writing rules

- Filename: `docs/wip/rca/<NN>-<slug>.md`. The agent picks the slug and the next free `NN` by scanning the folder. Never ask the user for an id.
- Treat `docs/wip/` as transient: these are working documents that are expected to be deleted once design, spec, and code are back in sync.
- Use the Write tool. If the directory does not exist, create it. Do not overwrite an existing file with the same name without confirming with the user first.
- After writing, reply with: the absolute path, a one-paragraph summary of the top hypothesis, and the **What to verify next** list so the user can act without opening the file.

## Close the loop on the entry that prompted this RCA

Plan follow-ups and risks routinely carry `suggested-command: /rca …`. When this analysis was invoked from such an entry, record the outcome in the **parent plan**, or the entry stays open long after it has been answered — plan 09's FU-003 is the standing example, still reading `status: open` though the RCA it asks for was written and the fix landed under plan 12.

An RCA diagnoses rather than remediates, so it usually reclassifies the entry rather than closing it:

- **Cause found, remediation still to come** — set `status: scheduled` with `scheduled-in:` pointing at this RCA's path. It becomes `done` when the plan carrying the fix lands, and that plan cites the RCA as its `Source:` edge.
- **Premise void** — where the analysis shows there is no defect (it no longer reproduces, or the reported behaviour is correct), set `status: dropped` with the reason in `why`. Never delete the entry.
- Either way, call `/plan-index update <parent-NN>` so the parent's open-follow-up count and *Needs attention* bullets follow. If `00-index.md` does not exist yet, `/plan-index build` creates it first.

`/rca` writes no relocation glyph. It holds no phases of its own: even sub-case (a), which skips `/spec` and hands straight to `/breakdown`, only reaches a phase once `/breakdown` writes the plan — and that is the sole place `↗<NN>` is written.

## Required output structure

### Error summary
- One sentence restating the error in your own words, plus the concrete signals you extracted.

### Verified
- Facts directly supported by the input or by repository evidence you read. Cite `path:line` for each repo-derived fact.

### Likely root causes (ranked)
For each hypothesis (most likely first):
- **H{n} — {one-line claim}** *(confidence: high / medium / low)*
  - **Evidence:** what supports it (with `path:line` where applicable)
  - **Against:** what weakens it, or "none observed"
  - **Mechanism:** brief chain from cause → observed error

### What to verify next
- Exact files to read, symbols to grep, log lines to capture, SQL objects to inspect, or commands to run that would discriminate between the top hypotheses. Be specific enough that the user (or a follow-up turn) can act on each item without further interpretation.

### Out of scope
- Note explicitly: no patch is proposed. The next move is decided by the *Handoff* section below, based on which sub-case the verified hypothesis falls into.

### Handoff (incident door — three sub-cases)

This is the **incident door** of the four-move CSPA loop. After the top hypothesis is verified, choose the path by sub-case:

- **(a) Pure bug fix — REALITY-DRIFT.** The existing component spec already states the desired behaviour; the code has drifted from it. The remediation is a code-only patch. Skip `/spec`. Proceed: `/breakdown <rca-output>` → `/apply <plan> <phase>` → `/sync-check`. Use this sub-case **only** when the top hypothesis is labelled **high confidence** and `/sync-check --scope spec-code` shows zero CONTRACT-DRIFT and zero INTENT-DRIFT for the affected component.
- **(b) Spec drift revealed by the incident.** The code is correct; the spec is stale. No code patch is needed. Proceed: `/spec <rca-output>` (Branch B, scoped to affected components) → `/sync-check` to confirm re-alignment. The `/sync-spec` command is also available for in-place reconciliation if the spec edit is mechanical.
- **(c) Intent change in response to the incident.** The desired behaviour is itself revised by what the incident exposed. Treat the RCA as an upstream input to the change flow: `/spec <rca-output>` (update the spec to reflect new intent) → `/breakdown` → `/apply` → `/sync-check`.

If sub-case (a) is selected but the top hypothesis is **medium** or **low** confidence, stop and tell the user to verify the hypothesis (per Infer-mode discipline) before patching. Sub-cases (b) and (c) require explicit user sign-off on the direction.

The full lifecycle from this door: `/rca [→ /spec] → /breakdown → /apply → /sync-check`.

## Short-path output (triage gate passed)

Use this shape **only** when step 1a allowed the short path. Keep it to a handful of lines — no ranked hypotheses, no "what to verify next" checklist.

### Cause
- One sentence naming the cause, with `path:line` citation.

### Fix pointer
- One sentence describing the minimal change needed (not the patch itself — this command stays in Infer). Cite the exact symbol or line to edit.

### Why the short path
- One line confirming the triage criteria were met (single file:line, unambiguous message, no schema/distributed signals). This makes it easy for the user to push back and request the full analysis.
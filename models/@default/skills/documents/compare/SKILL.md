---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:documents:compare"
  name: Compare documents
  description: "What differs between two documents or two versions of one, where, and what each difference changes for the reader."
  version: 0.2.0
  owner: gatblau
description: >
  Compares two documents, or two versions of one document, and reports what differs, where, and
  what each difference changes. Trigger when the brief asks what changed, what is different,
  whether two documents agree, or to check one document against another. Do not trigger to
  summarise one document (that is summarise).
---

# Compare documents

## Before comparing

0. A Word, PowerPoint or other office file is read only through the Craft app for its format (WordCraft, DeckCraft, GridCraft), offered as an MCP server `craft_<app>`, using a tool that turns the format into Markdown or text; otherwise stop and say which file could not be read, as the system role describes. Never guess a file's contents.
1. Read both documents in full. If either cannot be read, stop and say which.
2. Settle which is the reference: the earlier version, the contract, the policy, or whatever the brief names. Say which you took.
3. Note what the reader cares about. A buyer comparing quotes cares about price, terms and dates; a reviewer comparing drafts cares about meaning, not punctuation.

## Write it clean

Before writing the first sentence, read `references/write-clean.md` in the `humanise` skill's folder (beside its `SKILL.md` and `scan.py`) in full. It turns every one of the 59 patterns in `humanise`'s catalogue into a rule for writing, numbered as the catalogue and the scanner number them. Write the comparison to it from the first sentence, so that `humanise` finds nothing to change. Two of its rules are hard: no corrective antithesis (§9) and no dash outside a quotation (§14). Before the hand-over, make the reading checks listed at the end of the guide, because no scanner tests them.

## What a comparison holds

- **The answer first**: whether they agree, or the two or three differences that matter most.
- **Then each difference that changes something**, one per line or row: what the reference says, what the other says, where in each (section, page or heading), and what the difference changes for the reader.
- **Differences that change nothing** (wording, order, formatting) in one line at the end, counted, not listed one by one, unless the brief asks for every change.
- **Gaps**: what one document covers and the other does not.

Use a table when the differences share the same columns (item, reference, other, what changes); use sentences when they do not.

## What a comparison never does

- Calls a difference harmless or important without saying why.
- Reports two passages as the same when their meaning differs, or as different when only the wording does.
- Guesses which document is right. When it matters, it says what each says and leaves the choice to the person.

## Before handing it over

Run `humanise` (`urn:ordin:default:skills:documents:humanise`) over the whole comparison, as the last step, with the register or voice sample the brief gives, if any. A comparison written to the guide should pass `humanise`'s check as written and come back unchanged; when a paragraph fails, `humanise` rewrites that paragraph only. If python3 is available, the check runs the skill's scanner on the file; resolve every hit, or say in the reply why one stays. When any paragraph was rewritten, check again that every point, figure, date, source and placeholder from before the pass is still there. A comparison that has not been through this step is not finished and is not handed over.

The reply says which way it went: passed as written, or which paragraphs were rewritten and for which patterns (by number). A rewrite points at an entry in the guide that the comparison missed; say which, so the miss is visible.

## Output

A new Markdown file named `<first> vs <second> — comparison.md` in the run's folder, and a reply to Ordin that names the file and gives the answer-first sentence.

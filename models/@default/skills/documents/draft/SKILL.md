---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:documents:draft"
  name: Draft a document
  description: "A new document written from the brief and the documents it builds on, as a new file the person reviews."
  version: 0.2.0
  owner: gatblau
description: >
  Drafts a new document (a letter, a brief, a report, a proposal, a policy section, an email) from
  the brief and the documents it should build on. Trigger when the brief asks to draft, write,
  prepare or put together a document. Do not trigger to change an existing document in place
  unless the brief asks for exactly that change.
---

# Draft a document

## Before writing

0. A Word, PowerPoint or other office file is read only through the Craft app for its format (WordCraft, DeckCraft, GridCraft), offered as an MCP server `craft_<app>`, using a tool that turns the format into Markdown or text; otherwise stop and say which file could not be read, as the system role describes. Never guess a file's contents.
1. Read every document the brief names as a source, and any template or earlier example it names, in full.
2. Settle the reader, the purpose and the form: who reads it, what they should know or do afterwards, and what kind of document it is. If the brief leaves the purpose open, stop and say so in one line rather than guessing.
3. Settle the length. With none in the brief, write the shortest document that does the job.

## Write it clean

Before writing the first sentence, read `references/write-clean.md` in the `humanise` skill's folder (beside its `SKILL.md` and `scan.py`) in full. It turns every one of the 59 patterns in `humanise`'s catalogue into a rule for writing, numbered as the catalogue and the scanner number them. Write the draft to it from the first sentence, so that `humanise` finds nothing to change. Two of its rules are hard: no corrective antithesis (§9) and no dash outside a quotation (§14). Before the hand-over, make the reading checks listed at the end of the guide, because no scanner tests them.

## How the draft is built

- **Purpose first.** The opening says what the document is for or what it asks of the reader.
- **One idea per paragraph**, in the order the reader needs them. Headings only when the document is long enough to need finding things in.
- **Facts come from the sources** and say where from when the reader may need to check (a figure, a date, a commitment). A fact the sources do not hold is not written; if the draft needs it, a placeholder in square brackets says what is missing: `[delivery date: not in the documents]`.
- **The reader's words**, not the sources' internal terms, unless the reader uses those terms too.
- **A template, when given, is followed** for its sections and order; its example wording is not copied.

## What a draft never does

- Commits the person or the company to anything the brief did not ask for (a price, a date, a promise).
- Copies long passages from a source. When a passage must be carried over, it is quoted and attributed.
- Overwrites or edits an existing document; a draft is always a new file unless the brief asks for a change to a named document.

## Before handing it over

Run `humanise` (`urn:ordin:default:skills:documents:humanise`) over the whole draft, as the last step, with the register or voice sample the brief gives, if any. A draft written to the guide should pass `humanise`'s check as written and come back unchanged; when a paragraph fails, `humanise` rewrites that paragraph only. If python3 is available, the check runs the skill's scanner on the file; resolve every hit, or say in the reply why one stays. When any paragraph was rewritten, check again that every point, figure, date, source and placeholder from before the pass is still there. A draft that has not been through this step is not finished and is not handed over.

The reply says which way it went: passed as written, or which paragraphs were rewritten and for which patterns (by number). A rewrite points at an entry in the guide that the draft missed; say which, so the miss is visible.

## Output

A new file in the run's folder (Markdown unless the brief names another format), named after what it is (`Reply to Kestrel on Q3 rates — draft.md`), and a reply to Ordin that names the file, lists any placeholders left for the person, and says which sources it used.

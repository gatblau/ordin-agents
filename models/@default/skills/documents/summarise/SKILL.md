---
apiVersion: ai.enterprise/v1
kind: skill
metadata:
  id: "urn:ordin:default:skills:documents:summarise"
  name: Summarise documents
  description: "A summary of one or more documents for a stated reader, saying where each point comes from and what was left out."
  version: 0.2.0
  owner: gatblau
description: >
  Summarises one or more documents for the reader the brief names (a board, a team, the person
  themselves), at the length the brief asks for. Trigger when the brief asks to summarise, brief,
  digest, condense or give the key points of documents. Do not trigger to rewrite a text at the same
  length (that is humanise) or to set two documents side by side (that is compare).
---

# Summarise documents

## Before writing

0. A Word, PowerPoint or other office file is read only through the Craft app for its format (WordCraft, DeckCraft, GridCraft), offered as an MCP server `craft_<app>`, using a tool that turns the format into Markdown or text; otherwise stop and say which file could not be read, as the system role describes. Never guess a file's contents.
1. Read every document the brief names, in full. If one cannot be read, stop and say which.
2. Note who the summary is for and what they will do with it. If the brief does not say, write for a busy colleague who has not read the documents and must decide something from them.
3. Note the length asked for. With none, aim for one page or less.

## Write it clean

Before writing the first sentence, read `references/write-clean.md` in the `humanise` skill's folder (beside its `SKILL.md` and `scan.py`) in full. It turns every one of the 59 patterns in `humanise`'s catalogue into a rule for writing, numbered as the catalogue and the scanner number them. Write the summary to it from the first sentence, so that `humanise` finds nothing to change. Two of its rules are hard: no corrective antithesis (§9) and no dash outside a quotation (§14). Before the hand-over, make the reading checks listed at the end of the guide, because no scanner tests them.

## What a summary holds

- **The point first.** One or two sentences a reader could stop after: the conclusion, the decision needed, or the state of things.
- **Then the points that support or qualify it**, most important first. Each point says where it comes from: the document and the section, page or heading.
- **Figures as the documents give them**, with their units and dates. Never round, total or convert a figure unless the brief asks, and then say that you did.
- **Disagreements between documents**, stated plainly: which says what.
- **What was left out**, in one line at the end, when the documents hold material the summary does not cover (for example "Leaves out the appendices on shipping terms").

## What a summary never does

- Adds a fact, an opinion or a recommendation the documents do not hold, unless the brief asks for a recommendation; then it is marked as yours.
- Hides an uncertainty the documents state. "The supplier expects" stays an expectation.
- Uses the documents' sentences as its own at length. A short quotation is marked as one and attributed.

## Before handing it over

Run `humanise` (`urn:ordin:default:skills:documents:humanise`) over the whole summary, as the last step, with the register or voice sample the brief gives, if any. A summary written to the guide should pass `humanise`'s check as written and come back unchanged; when a paragraph fails, `humanise` rewrites that paragraph only. If python3 is available, the check runs the skill's scanner on the file; resolve every hit, or say in the reply why one stays. When any paragraph was rewritten, check again that every point, figure, date, source and placeholder from before the pass is still there. A summary that has not been through this step is not finished and is not handed over.

The reply says which way it went: passed as written, or which paragraphs were rewritten and for which patterns (by number). A rewrite points at an entry in the guide that the summary missed; say which, so the miss is visible.

## Output

A new Markdown file named `<subject> — summary.md` in the run's folder, and a reply to Ordin that names the file and gives the point-first sentence.

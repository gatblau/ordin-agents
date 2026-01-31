# Detection: judging a hit, and judging a piece

The catalogue (`catalogue.md`) judges sentences. This file covers the judgement around it: what to leave alone, what a person's writing looks like, and the two per-piece readings the scanner prints, the voice readout and the structure profile, with the verdict the report gives.

## What not to flag

A careful human writer can hit several patterns with no machine involved. Before rewriting, check that you are not gutting good prose. None of these is a reliable sign on its own:

- **Clean grammar and a consistent style.** Professionals write that way, and so does anyone who has been edited.
- **Mixed registers.** A formal sentence beside a casual one is common in technical people and young writers.
- **Dry prose.** Machine writing has specific habits. Dryness without them is just dry writing.
- **Formal vocabulary.** §7 lists particular words. Leave *ostensibly* and *constituent* alone.
- **A greeting or sign-off on a letter or a comment.** People wrote those long before any model.
- **One transition word.** *However*, *moreover* and *consequently* count only when they pile up.
- **Curly quotation marks.** Most editing software curls them by default.
- **Dashes.** Many writers use them often. The no-dash rule binds the rewrite; it is never evidence about who wrote the original.
- **One short sentence for emphasis.** People land points that way. §31 needs a run of three.
- **"Honestly" or "look" in mid-sentence.** §33 is the theatrical opener, and the word alone is ordinary.
- **A parallel run that carries a comparison.** Where the reader compares members on one axis, the shared frame helps them (§39). Anaphora is a device (§10).
- **A run of conclusions after the reasoning was given.** §41 is about missing joints. Notes, digests and reference rows are meant to be conclusions.
- **A description that repeats the data beside it.** An accessible reading must carry every value in the picture (§40). Overlap alone is fine.
- **A real time or date.** A deadline, a measured duration or the hour an outage began is evidence (§38).
- **An imperative in a checklist or a closing call to action.** Instructions are commands by nature (§42). Apply the deletion test first.
- **A description beside a name, or for a party no source names.** §47 is a description standing where a known name should be.
- **Parallel ellipsis, or a *none* that finishes its own clause.** §49 needs the noun carried across to a different verb.
- **A person a source describes, or a type in one clause.** §48 is an invented representative with a story before the verb.
- **Second-person address that offers.** *If you have ever...* and *you may have seen...* are the repair for §46.
- **Unsourced claims in general.** Much human writing cites nothing. Missing citations prove nothing about authorship, though a sourcing rule may still apply.
- **Complex, correct formatting.** Templates and editors produce it.
- **Second-hand text.** Leave watched phrases inside quotations, titles, proper names and examples under discussion.

Clusters are what count. One dash means nothing. Dashes with reflexive threes, promotional adjectives and a closing summary paragraph tell you a great deal.

## Signs of human writing to preserve

When you see these, lean towards leaving the prose alone. Over-editing removes what makes it sound like a person:

- **Specific detail that is hard to invent.** A real street, an odd quotation, a person identified by an oddly particular relation. Models round off specifics; people keep them.
- **Mixed feelings left unresolved.** "Mostly good, and something about it still bothers me." Models default to a clean verdict.
- **References tied to a time and a group.** Slang or a joke that belongs to one year and one crowd.
- **Choices the writer can defend.** A cut or a word the writer can explain is a strong human sign.
- **Uneven sentence length.** People alternate long and short. Machine prose settles on an even middle length.
- **Real asides and self-corrections.** "(I keep wanting to write 'almost' here, but it was certain.)"
- **Text written before public chat models existed.** With rare exceptions, it was written by a person.

## The voice readout

Every pattern in the catalogue is a prohibition, and a draft can clear all of them with nobody in it. Measured against a set of published human essays, machine drafts matched them on sentence length, its spread and reading ease, and differed on six figures. The scanner prints those six on every run, with the human range:

| Figure | Human median | Human range | Typical machine draft |
|---|---|---|---|
| Sentences opening on And, But or So | 9.3% of sentences | 2.4 to 20.3 | 2.4 |
| First person singular | 11.1 per 1,000 words | 0.0 to 25.2 | 2.5 |
| Contractions | 21.2 per 1,000 words | 2.2 to 55.2 | 8.9 |
| Figures (numbers) | 4.3 per 1,000 words | 0.5 to 19.0 | 13.3 |
| Parentheses | 2.4 per 1,000 words | 0.4 to 7.7 | 0.0 |
| Questions | 1.8 per 1,000 words | 0.0 to 4.0 | 1.2 |

It also counts straight and curly quotation marks and says when a piece mixes them (§19). Under 300 words of body prose it prints nothing, because a rate means little.

**The readout is information.** It is not a hit, it changes no exit code, it enters no log, and no number in it is a target. Three reasons:

1. The human set is essays and talks. A sourced analytical document has good reason to carry more figures than a speech.
2. The ranges are wide. One of the human essays has no first person and almost no contractions, and it is as human as the rest.
3. A rewrite that adds *And* to four sentences to move a percentage has built a template, which is what this skill removes.

So treat it as a question to put to the draft: is the writer anywhere in it, and does it ask anything or contain an aside? The answer is a judgement about particular sentences. Where a figure sits outside every sample, say so in the report and say what in the draft explains it. Where the caller's voice allows the first person and the draft has none, that is worth a sentence in the report.

The readout covers the writer's own body prose. Quoted spans, code, links, headings and any references or sources section are left out.

## The structure profile

Edited machine drafts rarely say `delve` now. The signals have moved into structure and rhythm, where no single sentence is wrong. A paragraph opening on *So* is fine. Three of them in 1,600 words make every step look as though it follows from the last, and none of the human essays does that.

The scanner counts seventeen such patterns on every run and prints them as the **structure profile**. Like the voice readout, it is per piece: it raises no hit, changes no exit code and enters no log. Unlike the voice readout, it feeds a verdict. **Judge these by frequency, never by a single instance.**

| # | Pattern | Catalogue neighbours |
|---|---|---|
| 1 | *So* as the first word of a paragraph that draws a conclusion | none |
| 2 | Short recap closers: a paragraph of three or more sentences ending on one under ten words | §31, §34 |
| 3 | Three-part signposting: a heading names three items and the body walks them in order (*Start with... Then... Last...*) | §10, §28 |
| 4 | Roadmap sentences: the parts of the piece listed ahead in one parallel sentence (*who runs..., who checks..., who signs...*) | §10 |
| 5 | Second-person hooks: a sentence opening on the reader's role or past (*If you run...*, *You may have...*) | §46 |
| 6 | Balanced contrast pairs: both poles of one opposition in a sentence (*saves money now and trains fewer staff later*) | §9, §10 |
| 7 | Colon reveals: a label of four words or fewer, a colon, then the point | none |
| 8 | Repeated example phrase: one introducer, usually *such as*, doing every example | §39 |
| 9 | Uniform source tags: each source introduced as *Name, a description, verb* | §39, §56 |
| 10 | Stacked institutional citations: many distinct organisations cited for a survey, report or study | none |
| 11 | Repeated key phrase: one predicate returning unchanged in four or more sections | §59 |
| 12 | Declarative headings: headings that state a claim where a topic would do | §36, §37 |
| 13 | Built-in limits section: the piece lists its own weak points as short tidy items, and admits an inference by name | §6 |
| 14 | Templated list items: every item a short label sentence, then a one-line reading (bold-led paragraph runs count the same way) | §16, §39 |
| 15 | Escalating case walk-throughs: the text flags each step up (*the harder case is...*) | none |
| 16 | Unpunctuated image descriptions: a long alt text or caption with no sentence ends | §40 |
| 17 | Imperative close: the last section gives the reader orders | §42 |

### How it grades

Counts are normalised to 2,000 words of the writer's own body prose, and one instance is never graded. Three or more per 2,000 words is **strong**, two is **moderate**, below that **weak**. Five patterns grade on their own terms: 10 by distinct organisations (three is strong), 11 by the sections the phrase returns in (four is strong), 12 by the share of headings (half or more, and at least three, is strong), 16 and 17 by count. Under 800 words nothing is graded. The **core cluster** is patterns 1, 2, 6 and 8 together, which weigh most when they appear at moderate or above.

### What the human essays show

Beside every count the scanner prints the human median, the human maximum and how many of the twelve essays grade strong, and it flags a pattern **above every human sample**. That flag, more than the grade, is what the verdict leans on.

- **Patterns that separate.** Nine never reach strong in any human essay: 1, 3, 4, 6, 9, 10, 13, 14 and 16. Of these, 14 (templated lists) shows the widest gap: no human essay carries one, and machine-written articles often do. 13 (the tidy limits section) is next.
- **Patterns that do not separate alone.** Pattern 2 is strong in half of the human essays: people end about a fifth of their paragraphs on a short sentence. The recap form (*That is the whole problem.*) is rare in both and has to be read for. Pattern 17 is strong in three, because some essays end on a list of orders. Patterns 5, 7, 8, 11 and 12 reach strong in one essay each.

### Devices that become templates

Several of these patterns are good devices once: a short sentence landing a conclusion (2), a colon that promises the shape of what follows (7), recognition offered as *if you have ever...* (5), a model's limits stated (13), a tool the reader can apply (14), a close the reader can act on (17), headings that carry the argument (12). Used as the piece's habit, each becomes the pattern. **A device is a choice the first time and a template the third.** Nothing here forbids a device; the profile caps how often one shape carries the piece.

### The fix is never a substitution

Swapping every *So* for *Therefore*, or rotating *such as*, *for example* and *like*, keeps the pattern and adds §11. Rewrite the unit so it no longer needs the device: a conclusion that follows from its paragraph needs no *So*, and an example that matters can be the sentence's subject. A source can be named in the clause that uses it. A list whose items each need a reading is prose. A limit belongs in the section where the reasoning breaks, said once. A structural repair spends no net words, because accuracy repairs accrete one correct clause at a time.

### What the scanner cannot see

It cannot tell a recap closer from a closer that adds something, a parallel comparison the reader needs from a mirrored pair made for effect, or a reader's checklist from a templated list. The quoted instances are candidates: judge each one, then judge the piece.

## The verdict

For an article, an essay or any document of 800 words or more, the report ends with the profile table, the human signals the scanner quotes (asides, questions, the writer present in the reasoning, the spread of sentence length) plus any the reading finds (a typo, an off-topic aside, a detail nobody would invent), and a verdict in one of four categories:

- **likely human**
- **human with AI editing**
- **AI with human editing**
- **likely AI**

Give two or three sentences of reasons that cite pattern numbers. State it plainly. Four rules bind it:

1. Never on a single instance, and never on vocabulary alone.
2. Lean on what clears the human range. A pattern above every human sample counts; a strong grade inside the human range (2 and 17 most often) counts only as part of a cluster.
3. Citation patterns and headings are weak on their own (9, 10, 12). Plenty of people in consulting and technology write that way.
4. Weigh the human signals against the patterns, and say which way they point.

**What the verdict does to the rewrite.** Give it for the text as it arrived and, when any paragraph was rewritten, again for the result. A verdict of *likely human* or *human with AI editing* on the text as it arrived, with no unexplained pattern above every human sample, lets the text pass without a rewrite (SKILL.md, *Process*, step 6). Two results mean the rewrite is not finished. One is a verdict of *AI with human editing* or *likely AI*. The other is a pattern above every human sample with no recorded reason. Either sends the patterns named back to the rewrite step. A reason is a judgement about particular instances (*14: the four items under "Checks before dispatch" are a reader's checklist*), never "the house style asks for it". After a second attempt, report `HUM_PROFILE_UNMET` with the patterns that would not move.

**What it does not do.** It changes no exit code, so a clean scan can carry a strong profile. A *likely human* verdict says nothing about whether the piece will be read.

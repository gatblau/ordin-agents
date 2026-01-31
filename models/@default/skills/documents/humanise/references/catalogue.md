# The pattern catalogue

Fifty-nine habits that mark prose as machine-written, each with what it looks like, how to find it, how to repair it and, where the line is easy to cross, what it is not. The numbers are stable: the report, the scanner (`S01` to `S59`) and the other references all use them.

Examples sit in fenced blocks so that the scanner, which masks code, does not report them when it runs over this file. Every name in the examples is invented.

Three things hold for every pattern below:

- No pattern applies inside a direct quotation, a title, a proper name or a phrase the text is discussing (SKILL.md, *Quoted material*).
- A hit is a candidate. Judge each one against *What not to flag* in `detection.md` before rewriting.
- The repair restates the claim. It never drops one (SKILL.md, *Every point survives*).

## Content patterns

### 1. Inflated significance

A plain event is given a place in history, a movement or a trend that the facts do not show. The sentence reports that something happened and then adds that it marked a turning point, reflected a wider shift or left a lasting mark.

**Detect.** A clause that tells the reader how much the fact matters, attached to a fact that does not say so itself. Typical wording: `marks a turning point`, `reflects a broader shift`, `a lasting legacy`, `plays a key role`, `sets the stage for`. Scanner: S01.

**Fix.** Keep the event and its date. Keep a consequence only when a source states it, and then state it as a consequence.

```text
Before: The depot opened in 2011, marking a turning point in the region's evolving logistics story and setting the stage for a new era of growth.
After:  The depot opened in 2011. Within two years it handled a third of the region's parcel traffic, according to the council's freight survey.
```

### 2. Notability by list

The text proves that a person or organisation matters by listing where they have been mentioned or how many followers they have, with nothing about what was said.

**Detect.** A run of outlet names, award names or follower counts with no content attached. A human read; no scanner check.

**Fix.** Pick the one mention that carries a claim and report the claim.

```text
Before: Her work has been featured in trade journals, national newspapers and podcasts, and she has a large following online.
After:  In a 2019 interview with a trade journal she argued that depots should publish their late-delivery rates.
```

### 3. Trailing -ing commentary

A sentence ends with a participle phrase that interprets the fact it follows: it "highlights", "reflects", "signals" or "ensures" something. The phrase adds the appearance of analysis and no information.

**Detect.** A comma, then a present participle that comments on the main clause. Scanner: S03.

**Fix.** Delete the phrase, or turn it into a sentence with a source and a subject who did the interpreting.

```text
Before: The new rota moves night shifts to a four-week cycle, reflecting the team's dedication to wellbeing and signalling a cultural shift.
After:  The new rota moves night shifts to a four-week cycle. The union asked for it after two years of complaints about short turnarounds.
```

### 4. Promotional wording

Description slides into advertising: places are `nestled`, views `breathtaking`, heritage `rich`, products `cutting-edge`. Text about towns, buildings, products and cultural subjects is the most exposed.

**Detect.** Adjectives that sell. Scanner: S04 for the common ones.

**Fix.** Replace each with the fact it was standing in for, or delete it.

```text
Before: Nestled in the heart of the valley, Tollbridge is a charming market town boasting stunning views and a vibrant cultural scene.
After:  Tollbridge is a market town in the valley floor. It holds a Saturday market and a folk festival every summer.
```

### 5. Vague attribution

An opinion is credited to "experts", "observers", "critics" or "industry reports" with no name, so the reader cannot check it and cannot tell whether it is one person's view or a consensus.

**Detect.** A plural, unnamed authority as the subject of a reporting verb. Scanner: S05.

**Fix.** Name the source from the documents. Where there is none, the claim is the writer's: say so, or remove it.

```text
Before: Experts believe the bypass will transform traffic in the town.
After:  The county's 2018 traffic model predicts the bypass will cut peak-hour queues on the high street by about a fifth.
```

### 6. The formulaic challenges section

The piece closes with a passage that grants the subject some difficulties ("despite its success, it faces challenges") and then dismisses them in the next breath ("despite these challenges, it continues to thrive"). Both halves are generic.

**Detect.** `Despite ... faces challenges`, `Despite these challenges`, a heading such as `Challenges and outlook`. Scanner: S06.

**Fix.** Name each difficulty with its evidence, or drop the passage. Never close on the dismissal.

```text
Before: Despite its growth, the cooperative faces several challenges, including funding and staffing. Despite these challenges, it remains a beloved part of the community.
After:  The cooperative lost its council grant in 2017 and has run on member fees since. It has had no paid manager for three years.
```

## Language patterns

### 7. Overused machine vocabulary

A small set of words turns up far more often in machine text than in human text, and they tend to arrive together. The giveaway is density and clustering; one of them alone proves nothing.

**Detect.** Words such as `delve`, `tapestry`, `testament`, `pivotal`, `crucial`, `intricate`, `interplay`, `foster`, `garner`, `showcase`, `underscore`, `vibrant`, `robust`, `seamless`, `leverage`, `holistic`, `realm`, `myriad`, and `landscape` used for anything other than land. `Anchored to` in the sense of "based on" belongs here too; a literal anchor or a term of art does not. Scanner: S07.

**Fix.** The plain word: look at, mix, proof, key, important, detailed, help, gain, show, stress, lively, solid, smooth, use, whole, field, many. Often the sentence is better with the word deleted.

```text
Before: This report delves into the intricate interplay of factors that underscore the pivotal role of training.
After:  This report looks at why training made the most difference.
```

### 8. Avoiding "is" and "has"

Plain copulas are swapped for grander verbs: a room "serves as" an office, a building "boasts" three floors, a policy "represents a" change.

**Detect.** `serves as`, `stands as`, `functions as`, `boasts`, `features a`, `represents a`. Scanner: S08.

**Fix.** Use is, are, has, have.

```text
Before: The annexe serves as the archive and boasts climate-controlled storage across two floors.
After:  The annexe is the archive. It has climate-controlled storage on two floors.
```

### 9. Negative parallelism and the corrective antithesis

The text knocks down a claim nobody made so that it can put up the real one: "it is not just X, it is Y", "not only X but also Y", "X, not Y", "it's not X, it's Y". Clipped tails such as "no guessing" or "no surprises" tacked on after a comma belong here too.

**This is a hard constraint.** The final rewrite contains no corrective antithesis in the writer's own words. That covers the comma form, the not-but form, `not just`, `not merely`, `not only`, the softer `rather than` and `instead of` when they pin a claim against a foil, an either/or set up for rhythm, and the two-sentence form (`X is not A. It is B.`). It also covers titles, where `The problem with X is not that ...` makes the reader invent the objection and then guess the answer.

**Detect.** Scanner: S09 in all its forms, including the two-sentence form a comma-only search misses.

**Fix.** State the positive claim. If the excluded alternative really carries information, give it a sentence of its own.

```text
Before: The audit is not a box-ticking exercise, it is a conversation. It is not about blame but about learning.
After:  The audit is a conversation between the team and the reviewer. Its findings are used to change the process, and nobody is named in them.
```

```text
Before: The labels come from the parcel record, no guessing.
After:  The labels come from the parcel record, so the driver never has to guess.
```

**Not this.** A single contrast that rules out something the reader would otherwise assume, written as a full clause, can be precise. The scanner still reports it; judge it, and keep it only when the excluded reading is one the reader would really make.

### 10. Reflexive groups of three

Items arrive in threes because three sounds complete: three adjectives, three nouns, three clauses that restate one idea.

**Detect.** Three comma-joined clauses or terms where the facts support one or two. Scanner: S10 for the three-clause form.

**Fix.** Keep the items the facts support. Let a list be as long as it is.

```text
Before: The workshop offers inspiration, insight and innovation for attendees seeking growth, learning and connection.
After:  The workshop has two talks and an hour of open questions.
```

**Not this.** Anaphora, a repeated opening that carries three different ideas, is a device a writer chose. Each clause adds something the others do not. Leave it.

```text
We will not wait for the review, because the review is a year away. We will not wait for the budget, because the budget follows the review. We will not wait at all.
```

A set of four or more rendered one member per sentence on one frame is §39.

### 11. Synonym cycling

One thing is called by three names in three sentences (the depot, the facility, the site, the hub) to avoid repeating a word. The reader wonders whether there are four places.

**Detect.** A human read: two different nouns for one referent in neighbouring sentences.

**Fix.** Pick one name and keep it. Inside a run of parallel sentences, cycled verbs (rose, climbed, jumped) are evidence for §39: fix the run first, because swapping the verbs back leaves the run intact.

```text
Before: The depot opened in 2011. The facility employs 200 people. The site runs three shifts. The hub plans to expand.
After:  The depot opened in 2011. It employs 200 people on three shifts and plans to add a fourth loading bay.
```

### 12. False ranges

"From X to Y" where X and Y are not two ends of any scale, often doubled: "from the smallest startup to the largest bank, from code to culture". The reader looks for the scale and finds none.

**Detect.** The shape `from ... to ..., from ...`, which the scanner reports as S12.

**Fix.** List what is covered.

```text
Before: The guide takes you from first principles to field practice, from the warehouse floor to the boardroom.
After:  The guide covers stock rotation, loading order and the monthly report to the board.
```

### 13. Hidden actors and subjectless fragments

"No set-up needed." "Results are saved automatically." The reader cannot tell who does what, and a fragment without a subject reads like a slogan.

**Detect.** A human read. Passive voice is common in good prose, so a scanner flag would cost more than it finds.

**Fix.** Put the actor back where it helps the reader.

```text
Before: No account required. Data is synced in the background.
After:  You do not need an account. The app copies your data to the server while you work.
```

## Style patterns

### 14. Dashes

The final rewrite contains no em dash, en dash or spaced double hyphen in the text the skill writes. A dash inside a quotation is the source's punctuation and stays exactly as the source set it; restoring one an earlier pass removed is a repair.

**This is house style and it is no evidence of a machine.** Most published human essays use dashes, some heavily, and a few use none. So the rule binds the rewrite and is never offered as a reason to think someone else's text was generated.

**Detect.** Scanner: S14, over the text with quoted spans masked. The full set of dash characters counts: U+2010 to U+2015, U+2212, and ` -- `. A hit inside a quotation means the scan ran on unmasked text. Where a report gives a dash count, it says how many sit inside quotations.

**Fix.** In rough order of preference: a full stop, a comma, a colon, brackets, or a rebuilt sentence.

```text
Before: The new rota — agreed without a ballot — starts next month. The changes -- overdue, say the drivers -- cover nights only.
After:  The new rota, agreed without a ballot, starts next month. The changes cover nights only, and the drivers say they are overdue.
```

### 15. Bold scattered through prose

Phrases inside sentences are set in bold for no reason a reader can find: every acronym, every product, every second noun.

**Detect.** More than six bold spans in a paragraph is the scanner's line (S15). Fewer can still be too many.

**Fix.** Remove the bold. Keep it for a term a reader must find again, or for the one sentence a skimming reader should take away.

```text
Before: The plan combines **service levels**, **cost targets** and tools such as the **route planner** and the **load calculator**.
After:  The plan combines service levels, cost targets and two tools, the route planner and the load calculator.
```

### 16. Lists led by bold labels

Each item opens with a bold label and a colon, then restates the label in a sentence: "**Speed:** Speed has improved."

**Detect.** Three or more consecutive items that open with a bold label ending in a colon. Scanner: S16.

**Fix.** Write the paragraph. Keep a list only when the items are parallel and the reader will scan them.

```text
Before:
- **Speed:** Speed has improved with the new scanner.
- **Accuracy:** Accuracy has improved through better labels.
- **Safety:** Safety has been strengthened with guards.
After:  The new scanner is faster, the new labels cut misreads, and the conveyor now has guards.
```

### 17. Title Case in headings

Every main word of a heading is capitalised when the rest of the document uses sentence case.

**Detect.** Scanner: S17 (four or more words, nearly all capitalised).

**Fix.** Match the document's own heading style; with none, use sentence case.

```text
Before: ## Planning The Winter Rota And Leave Requests
After:  ## Planning the winter rota and leave requests
```

### 18. Emoji as decoration

Emoji at the start of headings or list items, used as bullets or mood.

**Detect.** Scanner: S18.

**Fix.** Remove them. Where one carried meaning (a warning, a done mark), say it in words.

```text
Before: 🚚 **Next run:** Thursday   ✅ **Done:** labels printed
After:  The next run is on Thursday. The labels are printed.
```

### 19. Curly quotation marks

**This is no longer a check.** Word processors and publishing systems curl quotes by default, so curly marks turn up in most human writing and the check produced more false hits than any other.

What remains is consistency. The scanner's voice readout counts straight and curly marks and says when a piece carries both. Settle on one in the text the skill writes. Inside a quotation the source's marks stay.

## Communication patterns

### 20. Chat residue

Words addressed to the person who asked for the text survive into the text: "Here is an overview", "I hope this helps", "Let me know if you want more", "Certainly!", "Would you like me to...".

**Detect.** Scanner: S20.

**Fix.** Delete them. A document does not talk to the person who commissioned it.

```text
Before: Certainly! Here is a short overview of the new returns policy. I hope this helps, and let me know if you need more detail.
After:  Customers can return an item within 30 days if it is unused and in its packaging.
```

### 21. Cutoff disclaimers and guessed filler

Two related habits. One is a disclaimer about what the writer could not find ("as of my last update", "details are limited"). The other is what follows it: plausible filler to cover the gap. For a private person the filler is nearly always the same ("keeps a low profile", "likely grew up in"), and none of it has a source.

**Detect.** Scanner: S21.

**Fix.** Say what is not known, in one line, or cut the sentence. Never present a guess as a fact.

```text
Before: Little is publicly known about his early career, suggesting he prefers to stay out of the spotlight. He likely studied engineering before joining the firm.
After:  The documents say nothing about his career before he joined the firm in 2009.
```

### 22. Flattery of the reader

"Great question!", "You're absolutely right", "That's an excellent point". The text praises its reader before it answers.

**Detect.** Scanner: S22.

**Fix.** Delete the praise and keep the answer.

```text
Before: Excellent point! You're absolutely right that the deadline matters here.
After:  The deadline matters here because the contract lapses on the last day of the month.
```

## Filler and hedging

### 23. Filler phrases

Long phrases standing where one short word would do the same work.

**Detect.** Scanner: S23 for the common ones.

**Fix.**

| Filler | Plain |
|---|---|
| `in order to` | to |
| `due to the fact that` | because |
| `at this point in time` | now |
| `in the event that` | if |
| `has the ability to` | can |
| `it is worth noting that` | (delete; start with the point) |
| `a wide range of` | many, or the number |

### 24. Stacked hedges

One claim carries several qualifiers: "could potentially", "might possibly", "it could perhaps be argued".

**Detect.** Scanner: S24.

**Fix.** Keep the one hedge the evidence calls for, or none.

```text
Before: The change could potentially lead to a possible reduction in some delays.
After:  The change may reduce delays.
```

### 25. Upbeat empty endings

The piece ends on a cheerful generality: `the future looks bright`, `exciting times lie ahead`, `a step in the right direction`.

**Detect.** Scanner: S25.

**Fix.** End on the last concrete fact, or on what happens next and when.

```text
Before: With these changes in place, the future looks bright for the depot and exciting times lie ahead.
After:  The fourth loading bay opens next spring, and the depot will then take overnight freight.
```

## Further patterns

### 26. Hyphenated pairs in predicate position

Compound modifiers are hyphenated everywhere, including after the noun: "the report is high-quality". Most writers hyphenate before the noun (a high-quality report) and drop it after.

**Detect.** Scanner: S26 for common pairs after a linking verb.

**Fix.** Keep the hyphen before the noun; drop it after.

```text
Before: The team is cross-functional and the data is real-time.
After:  The team is cross functional and the data is real time.
```

### 27. Authority tropes

Phrases that claim to cut through to a deeper truth (`the real question is`, `at its core`, `what really matters`, `fundamentally,`, `the heart of the matter`), followed by an ordinary point.

**Detect.** Scanner: S27.

**Fix.** Make the point without the ceremony.

```text
Before: The real question is whether the depot can grow. At its core, what really matters is space.
After:  Whether the depot can grow depends on space. The site has room for one more bay.
```

### 28. Signposting and announcements

The text announces what it is about to do (`let's dive in`, `here's what you need to know`, `let's break this down`, `without further ado`) or promises a simplification it should simply deliver (`in plain English`, `put simply`, `in a nutshell`). Never use the latter in a title.

**Detect.** Scanner: S28.

**Fix.** Do what the announcement promised.

```text
Before: Let's dive into how the returns process works. Here's what you need to know.
After:  A return starts when the customer prints a label from the order page.
```

### 29. Fragmented headers

A heading is followed by a one-line paragraph that restates it before the content starts.

**Detect.** A heading, then a paragraph of fewer than ten words. Scanner: S29.

**Fix.** Delete the warm-up line.

```text
Before:
## Late deliveries

Lateness matters.

Most late parcels miss the first sort.
After:
## Late deliveries

Most late parcels miss the first sort.
```

### 30. Diff-anchored writing

Documentation describes a change ("this function was added to replace the old loop") where it should describe the code as it now is. Outside changelogs, release notes and migration guides, a reader should not need to know what changed last.

**Detect.** Scanner: S30 for common phrasings.

**Fix.** Describe the current behaviour and, where it helps, why.

```text
Before: This lookup was added to replace the previous approach of scanning every row, which was slow.
After:  This lookup uses an index, so it reads one row whatever the table's size.
```

### 31. Manufactured punchlines and staccato

Sentences are shaped to land like closing lines, and short fragments are stacked to build drama. One short sentence for emphasis is fine. A run sounds engineered.

**Detect.** Three or more consecutive sentences under eleven words, reported once per run. Scanner: S31. A pair is not reported, because people write pairs all the time. Read a pair anyway for what it does: two short sentences that deny one thing and assert another are §9 whatever their length.

**Fix.** Join the fragments into a sentence that carries the reasoning, and keep one short sentence where the point lands.

```text
Before: Then the new planner arrived. It had no habits. No favourite routes. No loyalty to the old map. Everything changed.
After:  The new planner ignored the routes drivers had always used, so several old assumptions about the map stopped holding.
```

### 32. Aphorism formulas

An ordinary claim is turned into a maxim (`X is the language of Y`, `X becomes a trap`, `X is not a tool but a mirror`). It sounds wise and says less than the plain version.

**Detect.** Scanner: S32 for the common frames.

**Fix.** State the concrete claim the formula gestures at.

```text
Before: Punctuality is the currency of trust. Efficiency becomes a trap when routes ignore drivers.
After:  Customers who get late parcels order less often. Routes planned without drivers' input tend to miss loading-bay queues.
```

### 33. Fake-candid openers

A theatrical pause before an ordinary answer: `Honestly?`, `Look,`, `Here's the thing`, `Real talk`.

**Detect.** Scanner: S33, at the start of a line.

**Fix.** Say the answer.

```text
Before: Is the upgrade worth it? Honestly? It depends on volume.
After:  Whether the upgrade pays depends on how many parcels you handle.
```

### 34. Self-referential summary closers

A last line that restates the thesis with a note of finality and adds nothing: `that is the whole point`, `nothing more and nothing less`, `and that is what makes it work`, `at the end of the day`. It is often a one-sentence paragraph and often quiet, which is why it passes the checks for upbeat endings (§25) and staccato (§31).

**Detect.** Scanner: S34.

**Fix.** Delete it and let the last substantive sentence end the piece. Keep a line of this shape only when it adds a real qualification. A causal link (`that is why <reason>`) or a concrete pointer (`the full list is in the appendix`) is content.

### 35. Folksy idiom filler

Worn figures that sound plain-spoken and stand in for a specific claim: `earns its keep`, `low-hanging fruit`, `moves the needle`, `the sweet spot`, `no silver bullet`, `boils down to`.

**Detect.** Scanner: S35.

**Fix.** Say what the effort buys or what the trade-off is. Leave an idiom the author's own voice would use; remove the reflexive one.

```text
Before: The extra check earns its keep, and fixing the labels is low-hanging fruit that moves the needle.
After:  The extra check catches about one misrouted parcel a day, and the label fix costs an hour and removes most misreads.
```

### 36. Contentless structural headings

A heading that would fit above any document: a count or a category label (`The three pieces`, `Key components`, `Important considerations`). It tells the reader a quantity and nothing about the subject.

**Detect.** Scanner: S36 for the commonest labels. A number in a heading is a strong sign.

**Fix.** Name the subject the section covers. Conventional navigation headings (Installation, Requirements, Licence, Troubleshooting) carry an established meaning and stay.

```text
Before: ## The three pieces
After:  ## Scanner, sorter and loading bay
```

### 37. Question-shaped and copula headings

Headings built as questions or dangling clauses (`What a rota is`, `How it works`, `Why it matters`). A heading names its topic.

**Detect.** Scanner: S37 for headings ending in a question mark.

**Fix.** Use a noun phrase, often a gerund, in sentence case.

```text
Before: ## What a rota is
After:  ## Building a rota
```

### 38. False time-stakes

A day, an hour or a slice of leisure is borrowed to make a benefit feel concrete: something to use `on Monday`, a fix `at 2 a.m.`, `an afternoon` saved. Nothing in the claim depends on the time. Swap one weekday for another and the sentence means the same, which proves the reference was decoration.

**Detect.** Scanner: S38 for weekdays, clock times, `overnight`, `this quarter` and similar.

**Fix.** State the claim the time was standing in for: what the reader can do, how long it takes, when a constraint binds. Keep every real date, deadline, measured duration and incident time.

```text
Before: Read the checklist once and you will have something to use on Monday, and it will save you a weekend of rework.
After:  The checklist covers the five checks that caught most loading errors last year, so you can apply it to your next shift plan.
```

### 39. Uniform enumeration

A paragraph works through a set and gives each member its own sentence built on one template. It is a list with the bullets removed, and no single sentence in it is wrong.

**Detect.** Look for a run of three or more consecutive sentences that meets three conditions. None is short (each runs over about fifteen words). Each carries one member of a set, and one template with slots would generate all of them. The third condition decides it. Scanner: S39 finds runs of long sentences; whether they share a frame is a read. Check consecutive spans, never the paragraph as a whole: a paragraph whose short sentences all sit before the run passes a paragraph-level test.

**The trap in the repair.** Changing the verb does not change the frame. Write out each sentence's skeleton with the content words removed (`[subject] fell from [A] to [B]`) and check that the skeletons differ.

**Fix.** Group the set into the two or three things it is saying, give each group a short sentence that names it, and vary the construction across the members. Every item stays.

```text
Before: Late deliveries fell from 9 per cent in 2019 to 4 per cent in 2023. Over the same period, damaged parcels rose from 0.8 per cent to 1.3 per cent. Misrouted parcels climbed from 120 a month in 2020 to 210. Returns processed within a week dropped from 88 per cent to 71 per cent.
After:  Speed improved and care slipped. Late deliveries are down to 4 per cent, from 9 in 2019. Damaged parcels were 0.8 per cent then and are 1.3 now, and misrouted parcels have nearly doubled to 210 a month. Returns suffered most: 71 per cent are processed within a week, against 88 per cent four years ago.
```

**Not this.** Anaphora (§10). A parallel comparison where the reader compares members on one axis and the shared frame makes that easier. A bulleted list, which is allowed to be uniform.

### 40. A description that mirrors its paragraph

A caption, alt text or figure description recites the paragraph beside it in the same order and the same phrasing.

**Detect.** Same order of items and same phrasing per item, together. A human read.

**Fix.** Say first what the picture is and how to read it (the kind of chart, what the marks mean), then the values. Where the picture's labels differ from the body's wording, report the difference. Never drop a value to look less repetitive: a reader who cannot see the picture needs all of them.

```text
Before: Chart. Late deliveries: 9% in 2019, 4% in 2023. Damaged parcels: 0.8% in 2019, 1.3% in 2023.
After:  Paired dot chart, one row per measure, each on its own scale. A hollow dot marks 2019 and a filled dot 2023. Late deliveries: 9% then 4%. Damaged parcels: 0.8% then 1.3%.
```

### 41. Conclusions with their joints removed

A passage reports what was established and deletes the reasoning between findings. Every sentence is a result. Nobody observes, expects, calculates or infers, and a figure arrives with nothing to compare it against, which quietly turns hypotheses into facts.

**Detect.** For a run of three or more sentences, name the job each does (observation, expectation, finding, inference, consequence). Flag the run when every answer is "finding". Two signs confirm it: no counterfactual for a statistic, and no verb of inference.

**Fix.** Put back the observation, the expectation it departs from and the verb of whoever drew the inference. Restate a probability or rate in a form the reader can picture. This adds words and is not padding.

```text
Before: The 2022 audit covered six depots. Night-shift errors cluster in the last two hours. The chance of that by accident is under 1 per cent. Fatigue is the cause.
After:  In 2022 the auditors looked at errors across six depots and expected them to spread evenly over the night shift. They found most in the last two hours, and put the chance of that pattern arising by accident at under 1 in 100. Their explanation was fatigue, which they proposed and did not test.
```

**Not this.** A closing run that collects reasoning given earlier. Notes, digests and reference rows, which are meant to be conclusions. A single short conclusion after a long sentence.

### 42. The staged imperative

A short command puts the reader in a scene so the next sentence can spring a reveal: `Open your rota.` `Picture a loading bay.` The next sentence points back with *it*, *that* or *there*.

**Detect.** A sentence-initial bare verb under fifteen words, followed by a sentence that opens by pointing back at its object. Scanner: S42. Then the deletion test: strike the command and make its object the subject of the next sentence. If nothing is lost, the command was staging. The one-sentence form (`Start with the rota, because it is...`) has no second sentence for the scanner; the deletion test still applies.

**Fix.** Make the reader's object the subject of a statement. The second person can stay (`your rota`).

```text
Before: Open your rota. Every gap in it is a shift somebody agreed to cover without asking.
After:  Every gap in your rota is a shift somebody agreed to cover without asking.
```

**Not this.** A reader's tool (a checklist, a procedure, a recommended control). A closing call to action. The narration of a declared fictional frame.

### 43. The unmasking formula

The sentence declares the reader's category a disguise and swaps in a better one: `a staffing problem wearing a technology costume`, `a cost cut dressed up as a strategy`, `X by another name`. The costume carries no information; strike it and the bare claim is the whole assertion.

**Detect.** Scanner: S43.

**Fix.** State the reclassification plainly, then earn it in the next sentence with the evidence.

```text
Before: The delay is a staffing problem wearing a software costume.
After:  The delay is a staffing problem: the new system works, and there is nobody on the night shift trained to use it.
```

**Not this.** An analogy that is declared, mapped and bounded.

### 44. The unclaimed void

A sweeping negative about a field, unsourced and usually unfalsifiable (`the industry has no answer`, `nobody is talking about this`, `there is no framework for`). It clears ground for whatever the writer says next. A negative universal about a population is also an unsourced claim about that population.

**Detect.** Scanner: S44.

**Fix.** Replace the universal with the narrower observation underneath: what was searched, what came back.

```text
Before: The logistics sector has no answer to this.
After:  The three trade guides I read all deal with warehouse safety; none covers drivers' working hours.
```

**Not this.** A sourced statement that a gap exists.

### 45. The unnamed referent

A description stands where a name would do: `the part that...`, `the thing you...`, `the piece nobody...`, often with a verdict on the evidence (`is the clearest sign that...`). The reader has to resolve the referent before the sentence means anything.

**Detect.** Ask of each noun phrase: is there a name for this, and do I know it? Two yeses in one sentence is the pattern. Scanner: S45 for the emptiest placeholders (`thing`, `part`, `piece`, `bit`), the superlative-evidence frame and `not yours to`. The broad form produced four false hits for every true one, so it stays a read.

**Fix.** Name each referent, then state the claim. Where an evaluative frame survives, put it before a colon.

```text
Before: The part you can check without asking anyone is the clearest evidence that the thing behind the label is not yours to control.
After:  The carrier's own service notices show it: a delivery promise can change without notice, and you cannot stop it changing.
```

**Not this.** A referent withheld deliberately and named within a sentence or two. A category with no shorter name. An abstraction the argument is about.

### 46. The assigned memory

Recognition is asserted as the reader's history: `You have sat in the meeting where...`, `You've watched...`, `We have all seen...`, `Everyone has...`. It tells the reader what their past holds, and the definite article sends them looking for one particular meeting.

**Detect.** Scanner: S46, on a capitalised `You have` / `You've` / `You will have` plus a past participle, `You know the meeting`, `We have all`, `Everyone has`. Silent when a hedge follows (`probably`, `likely`) and when `you have` sits inside a sentence.

**Fix.** Offer the recognition: a condition (`If you have ever...`), a modal (`you may have seen...`) or a reader scoped in the same sentence. Use an indefinite article for the scene and give the event a person as its actor. Vary the repair between pieces, or it becomes the next template.

```text
Before: You have sat in the planning meeting where "the system says so" ended the argument.
After:  If you have ever sat in a planning meeting, you may have seen an argument end once somebody said the planning system had already decided.
```

**Not this.** A hedged appeal. A clause inside a sentence (`after you have seen the data`). Present possession (`you have a rota`). A declared fictional frame.

### 47. The descriptive epithet

A party the piece can name is replaced by a description built from other names in the piece and joined by a verb: `the firm Kestrel bought its scanners from` where the supplier was named one sentence earlier. The reader must solve it, and the verb asserts a relation nobody sourced, inside a noun phrase where no citation check looks.

**Detect.** Scanner: S47, for a role noun plus a capitalised name plus a past-tense verb, a creator noun `of the` abstraction (`the inventor of the method`), `the company behind X`, and `The <role> whose <X> a <Y> would <verb>`. Then ask of every noun phrase a rewrite put where a name was: what is the name, and did anybody say this relation?

**Fix.** Use the name. Cut the relation unless a source gives it, and then give it its own clause and its source.

```text
Before: On a quick reading, the firm Kestrel bought its scanners from says the fault is in the labels.
After:  On a quick reading, Tamsin Optics says the fault is in the labels.
```

**Not this:** a description added to a name already given; a party with no name in any source; a naming construction (`the practice drivers call double-backing`); a first introduction the reader needs.

### 48. The stand-in character

A claim about what a system does to people is told as the story of one invented representative: `The new driver who questions the route, and is overruled twice, stops asking.` Two companions travel with it: a comparison without its baseline (`than before`, `than ever`) and a reason given as a figure (`because the system has spoken`).

**Detect.** Scanner: S48, for a type-person whose story sits before the verb, `than before` / `than ever` / `than it used to`, and a short list of verdict idioms with a thing as subject. Ask of every type-person: is this sentence a claim, and where is its source? Ask of every *because*: what actually happens, and who does it?

**Fix.** State the claim about the type in one clause, give the mechanism plainly, name the comparison or drop it, and use the first person when the claim is the writer's argument.

```text
Before: The new driver who doubts a route, and watches it pass every check, has less say than before, because the planner has already spoken.
After:  A new driver who doubts a route has no way to stop it. By the time they object, the planner has approved it, and I expect that approval to outweigh them.
```

**Not this.** A person a source describes. Recognition offered to the reader (§46). A type in one clause (`a reviewer who approves everything learns nothing`). A comparison whose baseline is in view.

### 49. The elliptical punchline

A short line (a subtitle, heading or teaser) deletes words to fit and leaves its conclusion unsaid: `the limit on how often counts late parcels, and a lost parcel has none`. The reader must restore the missing clause, carry a noun across to a different verb, and then draw the conclusion.

**Detect.** Scanner: S49, for `how often` / `how frequently` / `how soon` with the clause cut, and a joined clause ending on `none`, `nothing` or `zero` with a different verb from the one its noun came with. A human read covers the rest: the riddle split over two sentences, `how much` cut short, a verb phrase with its middle removed, a closing `one` standing for a noun several words back.

**Fix.** Put the deleted words back and state the consequence in the verb.

```text
Before: The depot halts rather than risk bad scans. Its limit on how often counts late parcels, and a lost parcel has none.
After:  The depot halts when it cannot trust its scans, and its limit on how often it may halt counts late parcels and ignores lost ones.
```

**Not this.** Parallel ellipsis on the same verb (`team A has three bugs, and team B has none`). A quantifier its clause completes. A *nothing* that is the claim.

### 50. A title and subtitle that carry the argument

A title of two or three full sentences sets out claim, counter-claim and verdict; a subtitle states the mechanism and then names the reader and the benefit. A reader taking in the title at a glance has to weigh an argument before knowing whether the piece is for them.

**Detect.** Scanner: S50, on a document's title and subtitle when it has them (front matter, a labelled field, the first level-1 heading, an italic standfirst under it). It fires above 75 characters or two sentences for a title and 120 characters or two sentences for a subtitle. These ceilings are house judgement.

**Fix.** Give each line one job. The title names the subject and states one claim; the subtitle adds the one piece of context the title lacks, or names the reader. Cut whole clauses, never words inside a clause (that produces §49).

```text
Before: Kestrel Says Its Robots Need Rest. Corvid Says Robots Never Tire. Neither Has Measured It.
        What a vendor says about its machines comes from its own tests. That matters to anyone buying a fleet.
After:  Kestrel Says Its Robots Need Rest
        Corvid says the opposite, and neither vendor has published a test.
```

**Not this.** Two short sentences that make one move. A title that has to carry a long official name.

### 51. Literature-review order

A section opens on its evidence (who published what, and when) and reaches its point later, or never states it. The order is the order the writer worked in.

**Detect.** Scanner: S51, on a section's first sentence whose first six words are attribution-led (`According to`, a date, a year, a study or author as subject). It does not catch a vague lead followed by the study; that is a read.

**Fix.** Put the point first, then why it holds, then who showed it. The evidence stays, in the same words.

```text
Before: In 2018 Ines Marlow and colleagues found that drivers who plan their own routes deliver faster. They compared 40 depots over a year.
After:  Letting drivers plan their own routes speeds up deliveries. In 2018 Ines Marlow and colleagues compared 40 depots over a year and found the self-planned routes faster.
```

**Not this.** A point that needs one sentence of setting first. A takeaway carrying its own source marker. A chronology the argument is about.

### 52. The empty announcement

A sentence promises that something matters and leaves the content to the next sentence: `The figures show what that change is worth.` `This is where it gets interesting.` `That paragraph is worth pausing on.` Its cousin is an instruction that counts unnamed objects: `check two documents.`

**Detect.** Scanner: S52 for six recurring forms. Any other wording is a read: does this sentence carry the claim, or only promise one?

**Fix.** Put the claim in the sentence that announces it.

```text
Before: The figures show what the new rota is worth. Late parcels fell by a third.
After:  The new rota cut late parcels by a third.
```

**Not this.** A colon that promises a shape and delivers it in the same sentence. A transition that carries a fact. A short sentence that is the answer.

### 53. The bare aphorism

A short sentence of two unpossessed abstractions, `An X is not a Y`, stopping there: `A forecast is not a plan.` It reads as a maxim and leaves the reader to supply whose, of what, and against what.

**Detect.** Scanner: S53, on sentences of twelve words or fewer of that exact shape.

**Fix.** Give the abstraction an owner and an object.

```text
Before: A forecast is not a commitment.
After:  The depot's volume forecast does not commit the carrier to any number of vans.
```

**Not this:** a definition the piece has just earned; a concrete subject; a contrast worked out in the same sentence.

### 54. The orphaned reference

A count of five or three after a demonstrative (`those five answers`, `these three checks`) points at a set the reader was never given nearby, often because a repair deleted the sentence that named it.

**Detect.** Scanner: S54, which looks for the noun or number in the same and the previous paragraph. A demonstrative without a count (`that setting`) can be orphaned just as easily, and only a read finds it.

**Fix.** Name the set where you point at it, in as few words as the sentence can carry.

```text
Before: The gap between those four quotes is a pricing choice.
After:  Of the four carriers I asked, one quoted per parcel and three per van, and that gap is a pricing choice.
```

### 55. The nominalised claim

A verb becomes a noun that needs a *why*, *what* or *how* clause to prop it up: `the board's understanding of what went wrong`, `her account of how the fault spread`. The subject runs seven or eight words before its verb.

**Detect.** Scanner: S55, for a dozen such nouns followed by a wh-word. More widely, any subject that runs past six words before its verb.

**Fix.** Give the noun back its verb and let the actor do it.

```text
Before: The board's understanding of what went wrong arrived after the audit.
After:  The board understood what had gone wrong only after the audit.
```

### 56. The audit-trail sentence

Every clause was added by a different rule (a date for accuracy, an interval for momentum, a role for legibility, a gloss for a technical term, a clause about the document for sourcing) and nobody reread the result as a sentence. Each insertion resolves; together they tire the reader.

**Detect.** Scanner: S56, in four forms: (a) the time ladder, a date, then an interval, then a second date before the subject; (b) the gloss in the gap, an appositive wedged between an elided verb's object and its quoted complement; (c) the custody run, two or more quotations in one paragraph each handed over by a document as subject; (d) the opening stack, an occasion and a date, then a role and a name, before the verb. Otherwise count the insertions between subject and verb and ask which rule put each one there.

A computed detail whose meaning the sentence never states has usually outlived the point it was computed for. Ask what the reader should conclude from it; if nothing nearby says, cut it.

**Fix.** One job per sentence and the point first. Give an event its date and nothing else before the subject. Give a gloss a clause of its own. Let the source marker carry the custody.

```text
Before: On 16 January 2019, nineteen days after filing its annual report on 28 December, Kestrel's chief executive, Ana Ruiz, opened the depot.
After:  Ana Ruiz, Kestrel's chief executive, opened the depot on 16 January 2019.
```

### 57. The quoted label

A source's figure of speech is quoted as if it were evidence: the chief executive called the planner the "heartbeat" and the depot the "crown jewels". The quotation says only that the speaker likes what it describes.

**Detect.** Scanner: S57, for (a) two or more naming verbs in a paragraph each followed by a quotation of four words or fewer, (b) a gloss joined by *and* to such a label, and (c) a label that the next sentence decodes by defining its last word.

**Fix.** Say what the speaker claimed, in plain words, and mark the paraphrase. Quote only words that are themselves evidence: an admission, a commitment, a figure, a definition the argument turns on. Give a gloss its own sentence. If a figure needs explaining, the explanation is the sentence and the figure goes.

```text
Before: The planner is Kestrel's routing software, and Ruiz called it the "heartbeat" of the company.
After:  Ruiz credited the routing software with most of the company's growth.
```

**Not this:** a term of art in quotation marks; a label the piece goes on to dispute; a drawing's printed labels.

### 58. The compliance clause

An audience definition read out as prose: a generic person handed a role, then an abstract object defined by who depends on it (`anyone who runs a service other people depend on`). Both ends are placeholders, and nobody talks like that to another person.

**Detect.** Scanner: S58, for a generic head, a role verb, an abstract object and a depend/rely/count-on ending in one sentence.

**Fix.** Give the dependency clause its own subject, or name the concrete case.

```text
Before: It is worth rehearsing for anyone who operates a system that others rely on.
After:  It is worth rehearsing if other people rely on what you run, such as a depot that feeds every shop in a town.
```

**Not this:** a working scope note nobody publishes; a reader addressed by name or role; a real dependency between two named things.

### 59. The private code word

A vivid image from the opening returns later, unglossed, as a label for what it first illustrated. The first use is a joke the reader follows. Every later use is a key they must look up, so the close, which should be the plainest sentence, becomes the most coded. The family includes headings that are figures and a case study whose lesson arrives as a metaphor.

**Detect.** Scanner: S59 lists words that sit in the opening paragraph, the last two paragraphs and the body between, appear in no heading, are not proper nouns and occur ten times or fewer. It cannot tell a figure from a technical noun, so ask of each: is this word standing for something else? Then read the headings alone as a reader's scan path.

**Fix.** Say the plain thing the first time and every time. Keep one image if it earns its place, glossed where it stands, and never reuse it as a label.

```text
Before: Treat the small alerts as burnt toast. Each team adds toast to the dashboard until nobody can see the fire. Somebody still has to tell the toast from the fire.
After:  Most alerts report faults that fix themselves. Each team adds more of them until the dashboard hides the few that need a person. Somebody still has to pick out those few.
```

**Not this.** A figure used once and glossed where it stands. A technical term of the subject that recurs and appears in headings. A source's own image, quoted once.

## Telling the patterns apart

Several patterns sit close together. The distinctions that matter when you name one in a report:

| Pair | The difference |
|---|---|
| §9 and §53 | §9 sets a claim against a foil; §53 states a bare maxim with no foil and no owner. |
| §28, §33 and §42 | §28 is the writer announcing what the writer will do; §33 is a fake-candid hook; §42 orders the reader into a scene. |
| §45 and §47 | §45 hides a thing behind a placeholder; §47 hides a named party behind a description that asserts a relation. |
| §46 and §48 | §46 tells the reader what their past holds; §48 invents a third person and gives them a story. |
| §49 and §50 | §49 cut words until the line became a riddle; §50 is the line that was never cut. |
| §52, §53 and §55 | §52 promises a claim and states none; §53 states a claim with its actor and object removed; §55 keeps the actor and buries it behind a noun. |
| §39 and §41 | §39 repeats one frame across a set; §41 removes the reasoning between findings, whatever the frames. |
| §32, §43 and §59 | §32 and §43 are one-sentence formulas; §59 is a figure the piece creates and keeps reusing. |

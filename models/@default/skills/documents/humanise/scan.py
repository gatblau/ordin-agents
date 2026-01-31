#!/usr/bin/env python3
"""humanise-scan - the mechanical half of the humanise catalogue.

Runs every pattern in the catalogue that a machine can test, in every FORM the
catalogue names for it, with quoted spans masked first. Prints what it checked,
what it found, and - the part that matters - what it did not check and why.

It exists because a regex tests the form it was written for. Several patterns
have more than one form (the corrective antithesis has a comma form and a
two-sentence form, "X is not A. It is B."), and a hand-written scan that tests
one form passes every instance of the others.

Every run also prints a voice readout: six figures about the writer's presence,
beside the range measured across a set of published human essays. It is
information and never a hit.

And a structure profile: seventeen patterns that show in a whole piece's
structure and rhythm rather than in a sentence, counted per 2,000 words, graded,
quoted, and set beside the same human essays. Per piece, never per unit, so it
raises no hit and enters no log; the humanise report carries it.

Usage:  python3 scan.py <file.md> [--quiet] [--profile]   (--profile: every instance)
        python3 scan.py --selftest
        python3 scan.py --check-log <file.md>
        python3 scan.py --log <file.md> --lines A-B|--all --note 'read: <findings>'
        python3 scan.py --baseline <file.md> --note 'baseline: <why>'
The log commands read and write humanise-log.json in the folder that holds <file.md>.
Standard library only. Exit: 0 clean, 1 hits found, 2 bad usage.
"""
import re
import sys
import os

# The dash and curly-quote characters the checks look for, kept in one place.
DASHES = "‐‑‒–—―−"
CURLY = "‘’“”"
LQUOTE, RQUOTE = "“", "”"


# ---------------------------------------------------------------------------
# Masking. The catalogue's precedence rule: no pattern applies inside a direct
# quotation, a fenced code block, a URL, or a markdown link target.
# ---------------------------------------------------------------------------
def mask(text):
    """Replace protected spans with same-length filler so offsets survive. Newlines
    are kept, so a masked code block or comment never merges the paragraphs around it."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    t = re.sub(r"```.*?```", blank, text, flags=re.S)      # fenced code
    t = re.sub(r"`[^`\n]*`", blank, t)                     # inline code
    t = re.sub(r"\]\([^)]*\)", blank, t)                   # link targets incl. URLs
    t = re.sub(r"https?://\S+", blank, t)                  # bare URLs
    t = re.sub(r"<!--.*?-->", blank, t, flags=re.S)        # html comments
    t = re.sub(r'"[^"\n]*"', blank, t)                     # straight-quoted spans
    t = re.sub(LQUOTE + r"[^" + RQUOTE + r"\n]*" + RQUOTE, blank, t)  # curly-quoted
    return t


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def region_map(raw):
    """Label each line with the top-level region it sits in, so a hit can be
    judged fast. The catalogue does not reach every region equally: the body is
    prose a person reads, and a references or sources list is a set of citations."""
    regions, cur = [], "body"
    for line in raw.split("\n"):
        h = line.strip().lower()
        if re.match(r"^#{1,3}\s*(references|sources?|bibliography|works cited)\b", h):
            cur = "references"
        elif re.match(r"^#{1,2}\s", h):
            cur = "body"
        regions.append(cur)
    return regions


def region_at(regions, ln):
    return regions[min(ln, len(regions)) - 1] if regions else "body"


def ctx(text, pos, before=55, after=70):
    a, b = max(0, pos - before), min(len(text), pos + after)
    return re.sub(r"\s+", " ", text[a:b]).strip()


# Vocabulary for S47, the descriptive epithet. ROLE is the kind of noun that stands
# in for a named party; PAST is the verb that joins it to another name; NAMING verbs
# supply the name rather than withholding it, so they never fire.
EPITHET_ROLE = (r"(?:company|firm|manufacturer|maker|carmaker|automaker|vendor|supplier"
                r"|startup|lab|laboratory|agency|regulator|court|plant|factory|team|group"
                r"|union|organisation|organization|institution|university|publisher|paper"
                r"|study|report|book|article|researchers|authors|engineers|economist"
                r"|analyst|official|executive|founder|man|woman|person|country|government"
                r"|bank|fund|investor|client|customer|partner|rival|competitor)")
EPITHET_PAST = (r"(?:\w+ed|made|built|took|gave|sold|bought|wrote|ran|brought|taught|put"
                r"|set|got|lent|sent|found|held|kept|left|lost|paid|saw|told|won|chose|drew"
                r"|grew|knew|threw|began|drove|spoke)")
NAMING = r"(?:called|named|termed|dubbed|labelled|labeled|nicknamed|titled|renamed)"
# Form (d) reaches roles a regulated industry uses for a party: operator, provider, body.
EPITHET_ROLE_WIDE = r"(?:operator|provider|body|party|side|service|" + EPITHET_ROLE[3:]

# S58 - the compliance clause. A generic, indefinite person (anyone, those, a
# reader) handed a role by a verb (runs, manages, operates), then handed a second,
# abstract object (something, a service, a system) defined only by who depends on
# it. Both ends are placeholders, which is the tell: nobody pictures "anyone who
# runs a service other people depend on", because it reads as an audience
# definition copied into prose rather than something said to somebody. A named
# operator and its real system is ordinary prose ("Kestrel Freight, which runs the
# depot network, restarted the routing system").
GENERIC_HEAD = r"(?:anyone|those|someone|people|a\s+reader)"
GENERIC_OBJ = (r"(?:something|anything|a\s+service|a\s+system|an\s+organisation"
               r"|an\s+organization|infrastructure)")
RUN_VERB = r"(?:runs?|manages?|operates?|owns?|(?:is|are)\s+responsible\s+for)"
DEPEND_ON = r"(?:depend(?:s)?\s+on|rel(?:y|ies)\s+on|count(?:s)?\s+on)"

# Degree words that make "not that" an intensifier rather than a denied foil.
DEGREE = (r"(?:simple|simply|hard|easy|different|much|many|far|long|bad|big|good|important"
          r"|unusual|surprising|new|old|clear|straightforward|obvious|rare|common|interesting"
          r"|useful|great|large|small|high|low|strong|weak|sure)")

# Past participles for S46: every regular -ed form plus the irregulars that turn
# up in "you have sat / seen / run / met" constructions.
PARTICIPLE = (r"(?:\w+ed|sat|seen|been|run|read|met|heard|written|built|made|had|done"
              r"|taken|given|left|sent|spent|stood|found|known|lost|paid|put|said|told"
              r"|thought|brought|bought|caught|fought|taught|kept|felt|held|led|shut|won"
              r"|drawn|driven|shown|spoken|chosen|broken|forgotten|begun|sworn)\b")


# ---------------------------------------------------------------------------
# Regex checks: (section, name, pattern, flags)
# Each section lists EVERY form the catalogue names for it.
# ---------------------------------------------------------------------------
REGEX_CHECKS = [
    # An en dash between two capitals is a proper name or a range of letters, which
    # the catalogue's quoted-material rule protects. Everything else is reported.
    # Most published human essays use dashes, some heavily, so a dash is no evidence
    # of a machine. The ban is house style, and the name says so.
    ("S14", "em/en dash and double hyphen (house style, not a machine tell)",
     r"(?<![A-Z])[" + DASHES + r"](?![A-Z])|(?<=\s)--(?=\s)", 0),
    ("S09", "antithesis: comma form (X, not Y)",
     r",\s+not\s+(?!only\b)", 0),
    ("S09", "antithesis: not-but form",
     r"\bnot\s+(?:a|an|the)?\s*\w[\w\s]{0,30}?\s+but\s+(?:a|an|the|rather)\b", re.I),
    ("S09", "antithesis: not just / not merely / not only",
     r"\bnot\s+(?:just|merely|only|simply)\b", re.I),
    ("S09", "antithesis: 'rather than' pinning a claim",
     r"\brather than\b", re.I),
    ("S09", "antithesis: 'instead of' pinning a claim",
     r"\binstead of\b", re.I),
    # "The Problem With X Is Not That It's Rude": the foil is denied and the claim
    # withheld, so the reader invents the objection and then guesses the answer.
    # A degree word after "that" ("not that simple") is not the form.
    ("S09", "antithesis: 'X is not that Y' (a denied foil, the claim withheld)",
     r"\b(?:is|are|was|were)\s+not\s+that\b(?!\s+" + DEGREE + r"\b)"
     r"|\b(?:is|are|was|were)n(?:'|’)t\s+that\b(?!\s+" + DEGREE + r"\b)"
     r"|\b\w+(?:'|’)s\s+not\s+that\b(?!\s+" + DEGREE + r"\b)", re.I),
    # HT - house style for titles. A literal carrying its own colon (a git trailer,
    # a header name) reads in a headline as the title's break, and many destinations
    # print backticks literally, so nothing marks it as one string: "The Problem With
    # Reviewed-By: Bot Is Not That It's Rude" parses first as "...Reviewed-By" /
    # "Bot Is Not That It's Rude". Read on a level-1 heading, a front-matter title,
    # and a labelled Title field.
    ("HT", "title: a literal's own colon reads as the title's break (it parses twice)",
     r"^(?:# |title:[ \t]+|(?:[-*][ \t]+)?\*\*(?:Title|Search title)[^*\n]*\*\*[ \t]*"
     r"|(?:Title|Search title):[ \t]+)[^\n]*?\b[A-Za-z]+(?:-[A-Za-z]+)+:[ \t]",
     re.M),
    ("S09", "tailing negation fragment",
     r"[,;]\s*no\s+\w+ing\b|[,;]\s*no\s+(?:guessing|wasted|surprises)\b", re.I),
    # S19 (curly quotation marks) is not a check. Run over published human essays it
    # made about half of all hits, because most editors curl quotes without being
    # asked. The voice readout reports both counts so a piece that mixes the two
    # styles can still be seen.
    ("S18", "emoji", "[\U0001F300-\U0001FAFF☀-➿]", 0),
    ("S07", "AI vocabulary",
     r"\b(delve|crucial|pivotal|tapestry|testament|underscore[sd]?|underscoring"
     r"|showcas(?:e|es|ed|ing)|vibrant|intricate|intricacies|interplay"
     r"|garner(?:ed|s)?|foster(?:ed|s|ing)?|enduring|enhance[sd]?|myriad|realm"
     r"|landscape of|navigate the|robust(?:ness)?|leverage[sd]?|holistic"
     r"|seamless(?:ly)?)\b", re.I),
    ("S01", "significance inflation",
     r"\b(stands as|serves as|is a testament|is a reminder|marking a"
     r"|underscor\w+ (?:its|the) (?:importance|significance)|reflects broader"
     r"|setting the stage|indelible mark|deeply rooted|key turning point"
     r"|evolving landscape)\b", re.I),
    ("S03", "superficial -ing analysis",
     r",\s+(highlighting|underscoring|emphasi[sz]ing|ensuring|reflecting"
     r"|symboli[sz]ing|contributing to|cultivating|fostering|encompassing"
     r"|showcasing)\b", re.I),
    ("S04", "promotional language",
     r"\b(boasts a|nestled|in the heart of|breathtaking|must-visit|stunning"
     r"|renowned|groundbreaking|rich (?:cultural|history|tapestry))\b", re.I),
    ("S05", "vague attribution",
     r"\b(experts (?:say|argue|believe)|studies show|research shows"
     r"|observers have|industry reports|some critics argue|it is widely believed"
     r"|many believe)\b", re.I),
    ("S06", "challenges-and-prospects framing",
     r"\b(faces several challenges|despite these challenges"
     r"|challenges and (?:legacy|opportunities)|future outlook"
     r"|future prospects)\b", re.I),
    ("S08", "copula avoidance",
     r"\b(serves as a|stands as a|represents a|boasts \w+|features a)\b", re.I),
    ("S12", "false range",
     r"\bfrom\s+(?:the\s+)?\w[\w\s]{0,25}\s+to\s+(?:the\s+)?\w[\w\s]{0,25},\s+from\b",
     re.I),
    ("S20", "chat artefact",
     r"\b(I hope this helps|Of course!|Certainly!|You're absolutely right"
     r"|Would you like|Want me to|let me know if"
     r"|here is a (?:brief|short) overview)\b", re.I),
    ("S21", "knowledge-cutoff / speculative gap-filling",
     r"\b(as of my last|up to my last training|while specific details"
     r"|based on available information|maintains a low profile"
     r"|keeps personal details private|it is believed that"
     r"|likely (?:grew up|studied|began))\b", re.I),
    ("S22", "sycophancy",
     r"\b(great question|excellent point|that's a great)\b", re.I),
    ("S23", "filler phrase",
     r"\b(in order to|due to the fact that|at this point in time"
     r"|in the event that|has the ability to|it is important to note that"
     r"|it is worth noting that|needless to say)\b", re.I),
    ("S24", "excessive hedging",
     r"\b(could potentially|might possibly|may potentially"
     r"|it could be argued that|somewhat of a|arguably one of)\b", re.I),
    ("S25", "generic positive conclusion",
     r"\b(the future looks bright|exciting times|a step in the right direction"
     r"|only time will tell|the possibilities are endless)\b", re.I),
    ("S26", "hyphenated pair in predicate position",
     r"\b(?:is|are|was|were|seems?|remains?|feels?)\s+(?:very\s+|quite\s+)?"
     r"(third-party|cross-functional|client-facing|data-driven|high-quality"
     r"|real-time|long-term|end-to-end|well-known)\b", re.I),
    ("S27", "persuasive authority trope",
     r"\b(the real question is|at its core|in reality,|what really matters"
     r"|fundamentally,|the deeper issue|the heart of the matter)\b", re.I),
    ("S28", "signposting / announcement",
     r"\b(let'?s (?:dive|explore|break|take a look)"
     r"|here'?s what you need to know|without further ado|in a nutshell"
     r"|simply put|put simply|to put it simply|in plain English|in plain terms"
     r"|as we (?:will|shall) see|it is worth pausing)\b", re.I),
    ("S30", "diff-anchored writing",
     r"\b(this (?:function|section|change) was added to replace"
     r"|previously,? (?:this|the) (?:code|function)"
     r"|the old (?:approach|version) (?:was|used))\b", re.I),
    ("S32", "aphorism formula",
     r"\b(is the (?:language|currency|architecture|grammar) of|becomes a trap"
     r"|is not a tool but)\b", re.I),
    ("S33", "conversational rhetorical opener",
     r"(?:^|\n)\s*(Honestly\?|Look,|Here'?s the thing|The thing is,"
     r"|Let'?s be honest|Real talk)", re.I),
    ("S34", "self-referential summary closer",
     r"\b(that is the whole (?:point|job|story)|and that is all it does"
     r"|nothing more and nothing less|that is exactly the point"
     r"|that is the beauty of it|at the end of the day"
     r"|and that is what makes it work)\b", re.I),
    ("S35", "folksy idiom",
     r"\b(earns? its keep|pulls? (?:its|their) weight"
     r"|punch(?:es)? above its weight|more than pays for itself|the sweet spot"
     r"|moves? the needle|bang for (?:your|the) buck"
     r"|when the rubber meets the road|the name of the game"
     r"|double-edged sword|no silver bullet|low-hanging fruit|boils down to"
     r"|par for the course|your mileage may vary)\b", re.I),
    # S38 covers every form the catalogue section names, not the literal phrases
    # it happens to quote. The weekday and hour forms were previously encoded as
    # "on Monday", "by Tuesday", "at 2 a.m." and "at 3 a.m." only, so "on a
    # Tuesday" and "at 4am" passed silently; "this quarter" was absent. A hit is
    # still a candidate: a genuine date or a measured hour is evidence and stays.
    ("S38", "false time-stakes",
     r"\b((?:on|by|that|since|until) (?:a |an |that |the |last |next )?"
     r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
     r"|saves? you a weekend|over the weekend|in an afternoon|this afternoon"
     r"|at \d{1,2}(?::\d{2})? ?[ap]\.? ?m\.?"
     r"|before your next standup|by the time your coffee"
     r"|overnight|worth an evening|this quarter|in the next sprint)\b", re.I),
    # S43 - the unmasking formula. Strike the disguise and read what is left; the
    # bare claim is the whole assertion and the costume was the flourish.
    ("S43", "unmasking formula (disguise aphorism)",
     r"\b(wearing (?:a|an|the) [\w\s-]{0,20}?(?:costume|mask|disguise|suit|clothing)"
     r"|in [\w'’]{1,15} clothing|dressed up as|wearing the mask of"
     r"|by another name|really just (?:a|an|the)|with a new label"
     r"|with (?:a|an) [\w\s-]{0,15} sticker on it"
     r"|strip away the|underneath it all)\b", re.I),
    # S44 - the unclaimed void. A negative universal about a field, unsourced and
    # unfalsifiable, clearing ground for the piece that follows. This is an accuracy
    # fault as much as a prose one: there is no figure in it for a sourcing check to
    # catch, which is exactly why it passes one.
    ("S44", "unclaimed void (sweeping negative about a field)",
     r"\b((?:your|our|the|this) (?:industry|field|profession|sector|discipline) "
     r"(?:has no|have no|has not|hasn't)"
     r"|nobody has (?:solved|answered|written|asked|noticed)"
     r"|no one has (?:solved|answered|written|asked|noticed)"
     r"|no ?one is (?:talking about|asking|writing about)"
     r"|nobody is (?:talking about|asking|writing about)"
     r"|there is no vocabulary for|has not caught up|has yet to catch up"
     r"|have no framework for|the literature is silent"
     r"|everyone is missing|everybody is missing)\b", re.I),
    # S45 - the unnamed referent. DELIBERATELY NARROW. The broad form of this check
    # (any placeholder noun plus a relative clause) was tested against three finished
    # articles and returned four false positives for every true one: "the way it is
    # rolled back", "the feature you approved longest ago", "the one that should go
    # back to the board" and "the half that comes after launch" are all genuine
    # descriptions or plain anaphora. A check that cries wolf four times out of five
    # trains its reader to skip it. So only the emptiest placeholders are encoded,
    # plus the two frames that travel with them; everything wider is declared below
    # as a human read.
    ("S45", "unnamed referent (placeholder subject; name the thing)",
     # "the thing" fires alone: in professional prose it is almost never a real
     # referent, and requiring a relative clause after it missed "stop the thing
     # once it holds credentials" in a finished article. part/piece/bit keep the
     # relative-clause guard, because those have honest uses ("each part").
     r"\bthe things?\b"
     r"|\bthe (?:part|piece|bit)s? (?:you|that|which|an?\s+\w+|nobody|anybody)\b"
     r"|\bthe (?:clearest|strongest|surest|plainest|best|most telling|most obvious) "
     r"(?:evidence|sign|indication|illustration|proof|demonstration)\b"
     r"|\bnot (?:yours|ours|theirs) to \w+", re.I),
    # S46 - the assigned memory. Recognition stated as the reader's history: "You
    # have sat in the review where...". Case-SENSITIVE on purpose: a capital "You"
    # outside a title only starts a sentence, so the check reaches the declaration
    # and leaves the clause alone ("after you have seen the data", "the feature you
    # have approved", "for anyone who has run a team, you have watched..."). A hedge
    # straight after the verb is the offer this section asks for, so it is silent.
    ("S46", "assigned memory (the reader's past stated as fact; offer it instead)",
     r"(?<![\w'\u2019])(?:(?:And|But|So|Yet)\s+you|You)"
     r"(?:(?:'|\u2019)ve|\s+have|\s+will\s+have|(?:'|\u2019)ll\s+have)\s+"
     r"(?!(?:probably|likely|possibly|perhaps|almost|maybe|to|got)\b)"
     r"(?:(?:already|often|once|all|certainly|surely)\s+)?" + PARTICIPLE +
     r"|(?<![\w'\u2019])You\s+know\s+the\s+(?:meeting|review|call|moment|feeling|one"
     r"|kind|type|conversation|room|standup|slide|email|ticket|incident)\b"
     r"|(?<![\w'\u2019])We(?:(?:'|\u2019)ve|\s+have)\s+all\s+" + PARTICIPLE +
     r"|(?<![\w'\u2019])(?:Every|Any)(?:one|body)\s+has\s+" + PARTICIPLE, 0),
    # S47 - the descriptive epithet. A party the piece can name, replaced by a
    # description assembled from OTHER names in the piece and joined by a verb that
    # nobody sourced: "the company Kestrel borrowed the method from" for a firm named
    # one sentence earlier. Two harms in one noun phrase: the reader has to resolve
    # who it is, and the verb asserts a relation no source made, where no citation
    # check looks for a claim. Three forms: role noun + Name + past verb; creator
    # noun "of the" abstraction; "the company behind X". Case-SENSITIVE, so the name
    # must be capitalised. Naming verbs (called, dubbed) are the repair and stay
    # silent; "one of the organisations Kestrel contracted" follows a name already
    # given and is excluded by the "of " guard.
    ("S47", "descriptive epithet (a name swapped for a description that asserts a relation; use the name)",
     r"(?<!of )\b[Tt]he " + EPITHET_ROLE + r"s? (?:that |which |who |whom )?"
     r"(?!" + NAMING + r"\b)(?:[A-Z][\w\u2019'&.-]*)(?: [A-Z][\w\u2019'&.-]*)* "
     r"(?!" + NAMING + r"\b)" + EPITHET_PAST + r"\b"
     r"|\b[Tt]he (?:manufacturer|maker|inventor|architect|originator|creator|owner|keeper"
     r"|home|birthplace|father|mother|custodian|guardian|champion|author|source|designer"
     r"|founder)s? of (?:the|this|that|its) (?:philosophy|idea|method|practice|approach"
     r"|movement|concept|framework|discipline|doctrine|principle|theory|thinking"
     r"|technique|habit|model)\b"
     r"|\b[Tt]he (?:company|firm|team|lab|startup|people|researchers|group|engineers|man"
     r"|woman|person|organisation|organization|agency|minds?|brains?) behind "
     r"(?:the |a |an )?[A-Z]", 0),
    # S47 (d) - the same epithet with no capitalised name in it, which the forms above
    # cannot see: a role noun as the subject, then "whose", then a clause with its own
    # subject and a modal, so a hypothetical relation stands where the name should be
    # and the reader has to turn the clause round to see who does what ("The operator
    # whose failures a cancellation count would record argued against keeping one",
    # with the operator named two sentences earlier). Case-SENSITIVE on the article,
    # so it starts a sentence. An indirect question ("about whose name a log should
    # carry") has no role noun in front and stays silent.
    ("S47", "descriptive epithet, lowercase: 'The <role> whose <X> a <Y> would <verb>' (use the name)",
     r"\b(?:The|A|An)\s+(?:[\w-]+\s+)?" + EPITHET_ROLE_WIDE + r"s?\s+whose\s+[\w-]+\s+"
     r"(?:a|an|the|this|that|any|every|no|its|their)\s+(?:[\w-]+\s+){0,3}"
     r"(?:would|could|will|might|may|can|should|must)\s+\w+", 0),
    # S48 - the stand-in character. A claim about what a system does to people, told
    # as the story of one invented representative: "The junior engineer who believes a
    # change is wrong, and watches it clear every gate, has less standing than before,
    # because the gates have already spoken." Three riddles travel together, and each
    # is a form: (a) a type-person whose story sits between the subject and its verb;
    # (b) a comparison whose baseline is left for the reader ("than before" - before
    # what?); (c) a reason given as a figure, a thing performing a verdict ("the gates
    # have spoken"). The broad form of (c) - any inanimate subject with any human
    # verb - returned one false positive per true hit and is declared below instead.
    ("S48", "stand-in character: a type-person's story before the verb (state the claim)",
     r"(?:^|(?<=[.!?)\]])\s+)(?:The|A|An|Every|Any)\s+(?:[a-z-]+\s+){0,2}"
     r"(?:engineer|developer|manager|reviewer|lead|architect|operator|worker|analyst"
     r"|designer|founder|user|customer|hire|intern|person|employee|tester|maintainer"
     r"|executive|leader|programmer|contributor|owner|buyer|auditor|clinician|nurse"
     r"|pilot|driver)s?\s+who\s+[^.!?]{3,120}?,\s+(?:\w+\s+){0,2}"
     r"(?:has|have|is|are|was|were|will|can|cannot|gets?|loses?|learns?|finds?"
     r"|becomes?|ends?|stops?|keeps?|now)\b", re.M),
    ("S48", "stand-in character: comparison with its baseline left out (than before / than ever)",
     r"\b(?:more|less|fewer|better|worse|\w{3,}er)\b[\w\s']{0,30}?\bthan (?:before|ever"
     r"|it used to|they used to|it did|they did|it was|they were)(?=\s*[,.;:)]|\s*\[\[)",
     re.I),
    ("S48", "stand-in character: a thing delivering a verdict (the gates have spoken)",
     r"\b(?:the|its|their|this|that|these|those|every|your)\s+(?:[\w-]+\s+)?"
     r"(?:gates?|checks?|tests?|pipelines?|process(?:es)?|system|data|numbers|metrics?"
     r"|dashboards?|market|benchmarks?|model|algorithm|tools?|reviews?|scores?|evidence"
     r"|results?|record|build|policy|rules?|machine|scanner|linter|report|audit|queue)\s+"
     r"(?:(?:has|have|had)\s+(?:already\s+)?spoken|(?:has|have|had)\s+(?:already\s+)?"
     r"(?:delivered|passed|returned|handed down)\s+(?:its|their|a|the)\s+"
     r"(?:verdict|judgement|judgment)|(?:has|have|had)\s+the\s+(?:final|last)\s+(?:word|say)"
     r"|(?:has|have|had)\s+made\s+up\s+(?:its|their)\s+mind)\b", re.I),
    # S49 - the elliptical punchline. Words deleted to make a line short, left for the
    # reader to put back, and the conclusion left for the reader to draw: "The written
    # limit on how often counts late parcels, and a lost parcel has none." How often
    # WHAT? None of WHAT, and so what? Form (a) is here: "how often / how frequently /
    # how soon" with its clause cut, so the next word is the sentence's main verb.
    # "How much" and "how many" are left out because they can be subjects ("how much
    # is enough"), and "how often is too often" is an idiom. Form (b), the bare
    # closing quantifier, is structural.
    # S52 - the empty announcement. A lead-in that promises the reader something
    # significant is coming and states none of it, leaving the claim to the sentences
    # after it: "The five answers show what that setting is worth." It passes every
    # other check because nothing in it is wrong; it just says nothing. The forms
    # below are the ones that recur; the general case is a read.
    # S55 - the nominalised claim. A verb turned into a noun and then given a wh-clause
    # to carry: "a model's account of why it answered", "their understanding of what
    # went wrong". The reader unpacks two levels before the sentence's verb arrives.
    # The plain form uses the verb: "a model can explain its answer and be wrong
    # about why".
    # S56 - the audit-trail sentence. Every clause in it was added by a different
    # checking rule (a date for accuracy, an interval for momentum, a role for
    # legibility, a gloss for a technical term, provenance for sourcing), and nobody
    # reread the result as a sentence. Two of its forms are mechanical.
    # (a) The time ladder: a sentence opening on a date, then the writer's own
    # interval to a second dated event, before the subject arrives ("On 16 January
    # 2019, nineteen days after filing the report on 28 December, the chief
    # executive..."). (b) The gloss in the gap: a pair whose second verb is elided
    # ("calling A the 'x', and B the 'y'") with an appositive gloss wedged between B
    # and its complement, so the reader loses which verb governs 'the y'.
    # "In January 2014, a little over five years in, the maintainers moved the
    # deadline" stays silent: one date, and an interval from a start the section
    # has already given.
    ("S56", "time ladder: a date, then an interval to a second date, before the subject "
     "(say what the interval means, or cut it)",
     r"(?:^|(?<=[.!?] ))(?:On|In|By) [^,.\n]{0,25}(?:19|20)\d\d, [^,.]{0,40}?(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty[\w-]*|thirty|forty|fifty|sixty|a|an) "
     r"(?:days?|weeks?|months?|years?)[^,.]{0,50}?\b(?:on|in) (?:\d{1,2} [A-Z][a-z]+"
     r"|[A-Z][a-z]+ \d{1,2}|(?:19|20)\d\d)", re.M),
    ("S56", "gloss in the gap: an appositive between an elided verb's object and its "
     "quoted complement (give the gloss its own clause)",
     r", and (?:the )?[A-Z][\w-]*[^,.\n]{0,30}, [^,.\n]{3,70}, the (?:\*|\s{3,}|\"|\u201c)", 0),
    ("S55", "nominalised claim: '<noun> of why/what/how' (use the verb)",
     r"\b(?:account|explanation|description|characteri[sz]ation|statement|report"
     r"|understanding|assessment|sense|picture|narrative|telling)\s+of\s+"
     r"(?:why|what|how|whether)\b", re.I),
    ("S52", "empty announcement: 'shows what X is worth' (say what it shows)",
     r"\b(?:shows?|reveals?|tells? (?:you|us)|says?)\s+(?:what|how much|just how)\s+"
     r"[^.!?]{0,60}?\b(?:is|are|was|were)\s+(?:worth|really worth|actually worth)\b", re.I),
    ("S52", "empty announcement: 'the useful/interesting part' (name it)",
     r"\bis\s+(?:the|what makes it)\s+(?:useful|interesting|important|telling|striking"
     r"|revealing)\s+(?:part|bit|thing)\b", re.I),
    ("S52", "empty announcement: 'where it gets interesting' (say what happens there)",
     r"\b(?:this|that|here)\s+is\s+where\s+(?:it|this|things?)\s+(?:gets?|becomes?)\s+"
     r"(?:interesting|strange|difficult|tricky|awkward|complicated)\b", re.I),
    ("S52", "empty announcement: 'worth pausing/dwelling on' (state the point instead)",
     r"\b(?:is|are)\s+worth\s+(?:pausing|dwelling|lingering|sitting)\s+(?:on|over|with)\b",
     re.I),
    ("S52", "withheld object: an instruction counting things it does not name (name them here)",
     r"(?:^|(?<=[.;:!?])\s+|,\s+)(?:read|search|check|open|consult|examine|review)\s+"
     r"(?:two|three|four|five|six)\s+(?:documents?|sources?|files?|places?|things?"
     r"|questions?|fields?|reports?|pages?)\b(?![^.!?]*[:,])", re.I),
    ("S52", "empty announcement: 'says something important' (say the something)",
     r"\b(?:says?|tells? (?:you|us)|suggests?)\s+something\s+"
     r"(?:important|interesting|useful|telling|revealing|worrying)\b", re.I),
    ("S49", "elliptical punchline: 'how often' with its clause cut (how often WHAT?)",
     r"\b(?:on|about|of|over|for|to|and|or)\s+how\s+(?:often|frequently|soon)\s+"
     r"(?!is\s+too\b)(?:counts?|is|are|was|were|has|have|had|matters?|depends|varies"
     r"|gets?|sets?|uses?|measures?|decides?|determines?|falls?|rises?)\b", re.I),
    # S58 - the compliance clause: a generic head (anyone/those/a reader) handed a
    # role, then a second, abstract object defined only by who depends on it
    # ("anyone who runs a service other people depend on"). Requiring the object to
    # be a placeholder noun, not a named thing, keeps this off "Kestrel runs the
    # routing system that couriers depend on", where both ends are real.
    ("S58", "compliance clause: a generic head defined by who depends on it (flip "
     "it: 'if other people depend on what you run')",
     r"\b" + GENERIC_HEAD + r"\b[^.\n]{0,15}?\b(?:who|that)\b[^.\n]{0,20}?\b" + RUN_VERB
     + r"\b[^.\n]{0,15}?\b" + GENERIC_OBJ + r"\b[^.\n]{0,30}?\b" + DEPEND_ON + r"\b", re.I),
]


# Two-sided self-test: every FIRE case must hit and every SILENT case must not.
# Run with --selftest. The cases were written for the checks, so a pass shows that
# each check does what it says on these sentences and nothing more. Names in them
# are invented.
SELFTEST = {
    "S56": {
        "fire": [
            "On 16 January 2019, nineteen days after filing the report on 28 December, Kestrel's "
            "chief executive, Ana Ruiz, opened the depot.",
            "In January 2025, three weeks after the audit closed on 12 December, the board approved "
            "the plan.",
            "The keynote called Tern the *\"flywheel\"*, and the Harbour libraries, Kestrel's "
            "ready-made code for common tasks, the *\"crown jewels\"*.",
        ],
        "silent": [
            "In January 2014, a little over five years in, the maintainers moved the deadline.",
            "On 16 January 2019 Ana Ruiz opened the depot.",
            "Version 3.0 was released on 3 January 2008.",
            "She called Tern the *\"flywheel\"* and the Harbour libraries the *\"crown jewels\"*.",
            "The Harbour libraries are Kestrel's ready-made code for common tasks, and she called "
            "them the *\"crown jewels\"*.",
            "The filing names Alder, Brightwater, and Copperfield Foods, a food company, as "
            "customers.",
        ],
    },
    "S55": {
        "fire": [
            "A model's account of why it answered is not always what drove the answer.",
            "The board's understanding of what went wrong arrived late.",
            "Her description of how the outage spread was the useful part of the report.",
        ],
        "silent": [
            "A model can explain its answer and be wrong about why.",
            "The board did not understand what had gone wrong until the audit.",
            "Products lean on what a model says about itself: how sure it is, and why it answered.",
        ],
    },
    "S52": {
        "fire": [
            "The five answers show what that setting is worth.",
            "That invented explanation is the useful part.",
            "This is where it gets interesting.",
            "The filing tells you something important about the timing.",
            "That paragraph is worth pausing on.",
            "Before you treat anything as a measurement, search two documents.",
        ],
        "silent": [
            "The differences between those five answers are product decisions.",
            "The invented explanation is what a planted answer catches.",
            "The filing shows the board knew before the audit.",
            "This is where the denial was graded.",
            "The report says the outage lasted forty minutes.",
            "Read two documents: the vendor's governing document and your system prompt.",
            "Check three things before you ship: the version, the owner and the rollback.",
        ],
    },
    "S09": {
        "fire": [
            "The Problem With Reviewed-By: Bot Is Not That It's Rude",
            "The point is not that collapse is secretly fine; it is that recovery takes a "
            "generation.",
            "The trouble with the tag isn't that it is rude.",
        ],
        "silent": [
            "It is not that simple.",
            "The fix is not that hard once the field is named.",
            "They agreed that the tag was not needed.",
            "A commit message holds three kinds of field.",
        ],
    },
    "HT": {
        "fire": [
            "# The Problem With Reviewed-By: Bot Is Not That It's Rude",
            "- **Search title (43 characters).** Why Reviewed-By: Bot Is the Wrong Tag",
            "- **Title.** Why Signed-off-by: Means More Than a Name",
            "title: Why Reviewed-By: Bot Is the Wrong Tag",
            "Title: Why Signed-off-by: Means More Than a Name",
        ],
        "silent": [
            "# Three Fields, One Machine: Where an Agent Belongs in Your Commit Message",
            "# Your Coding Agent Did Not Write That Commit",
            "- **Subtitle.** The tag read Reviewed-by: Bot, and the maintainers removed it.",
            "The trailer reads Reviewed-By: Bot in the body text.",
        ],
    },
    "S48": {
        "fire": [
            "The junior engineer who believes a change is wrong, and watches it clear every "
            "gate, has less standing than before, because the gates have already spoken.",
            "The on-call engineer who spots the leak, and files it twice, gets nowhere.",
            "A new hire who questions the design, and is overruled once, stops asking.",
            "Every reviewer who approves in bulk, whatever the diff, learns nothing.",
            "Teams ship faster than ever.",
            "Review takes longer than it used to.",
            "Once the benchmark has the final word, nobody reopens the question.",
            "By Friday the metrics had delivered their verdict.",
            "The approval process has made up its mind.",
        ],
        "silent": [
            "A junior engineer who thinks a change is wrong gains no power to stop it.",
            "By the time they object, an agent has already approved the change, and I would "
            "expect that approval to count against them.",
            "The engineer who wrote the patch, Mara Lind, said it had been reviewed twice.",
            "Absenteeism was lower than before the depot opened.",
            "Latency is lower than it was in 2024.",
            "The reviewer who has spoken to the vendor confirmed the date.",
            "The people have spoken, the minister said.",
            "The gate has already passed the change.",
            "Anyone who maintains a long-lived repository may recognise that list.",
            "The line could never stop.",
        ],
    },
    "S47": {
        "fire": [
            "The operator whose failures a cancellation count would record argued against "
            "keeping one.",
            "The vendor whose outages a status page would reveal declined to publish one.",
            "A regulator whose rulings an appeal could overturn said nothing.",
        ],
        "silent": [
            "The second is about whose name a permanent log should carry.",
            "The company whose shares fell 12% said it would appeal.",
            "Kestrel Freight, whose failures strand parcels, cautioned against adding a measure "
            "of lost parcels.",
            "The engineer whose patch the reviewer approved left the team.",
            "Kestrel's failures strand parcels, and Kestrel cautioned against adding a measure "
            "of lost parcels.",
        ],
    },
    "S49": {
        "fire": [
            "The depot halts rather than risk bad scans. Kestrel's written limit on how often "
            "counts late parcels, and a lost parcel has none.",
            "The rule on how often counts only full outages.",
            "A cap on how frequently is set by the vendor, not the customer.",
        ],
        "silent": [
            "Kestrel's limit on how often the depot may halt counts late parcels.",
            "They asked how often.",
            "The argument about how much is enough never ended.",
            "The question of how often is too often never came up.",
            "Nobody knows how soon the report will land.",
        ],
    },
    "S58": {
        "fire": [
            "So it is worth rehearsing for anyone who runs a service other people depend on.",
            "For anyone who runs something a country depends on, the window matters.",
            "A reader who runs something a country depends on finishes able to say why.",
            "This matters for anyone who manages a system that other people rely on.",
            "It falls to those who operate an organisation the public counts on.",
        ],
        "silent": [
            "Kestrel Freight, which runs the depot network in the north, restarted the routing "
            "system.",
            "Kestrel runs the routing system that couriers depend on for scheduling.",
            "The grid depends on generators that can start without power from the grid.",
            "If you have ever sat in a review where the estimate was agreed before anyone "
            "opened the ticket, you already know which number the plan was built on.",
            "A reader who has never seen anything else you have published can tell, from "
            "this piece, who it is for.",
            "The system depends on manual checks when telemetry is down.",
            "So it is worth rehearsing if other people depend on what you run.",
            "Anyone who has read the report knows the cause was technical.",
            "An operator of essential services, or an organisation that depends on one, "
            "should rehearse the restart.",
        ],
    },
}


# Structural cases: the true form each check exists for, and the near misses that
# must stay silent. (section, text, should it fire)
STRUCT_SELFTEST = [
    # S56 (c), the custody run, then the one-custody-sentence and pronoun-only shapes
    # that must stay silent.
    ("S56", 'In January 2014 the maintainers moved the deadline. The release schedule says the '
            'date *"now falls three years later than first planned"*. [[5]](u) The decision was '
            'made *"to give packagers time"*. [[5]](u) The same paragraph says the extension '
            'should *"settle the question"*. [[5]](u)', True),
    ("S56", 'The filing puts the network first. It says that *"our depot network"* matters, '
            'and the 2024 filing says *"couriers strengthen our network"*. [[1]](u)', False),
    ("S56", 'The 2024 filing says why the count matters: *"the growing number of couriers"*. '
            '[[1]](u) It also says Kestrel has invested over $76.7 million.', False),
    ("S56", 'They pushed the date *"three years later than first planned"*. [[5]](u) They added '
            'that it should *"settle the question"*. [[5]](u)', False),
    # S57, the quoted label: a paragraph with every form, each form alone, and the near
    # misses that must stay silent.
    ("S57", 'Ana Ruiz marked the anniversary on 16 January 2019 and called Tern the '
            '*"flywheel"* driving the depot network. [[6]](u) The Harbour libraries are '
            'Kestrel\'s ready-made code for common tasks, and she called them the *"crown '
            'jewels"* of the company. [[6]](u)', True),
    ("S57", 'She called Tern the *"flywheel"*. [[6]](u) Later she described the libraries as '
            'the *"crown jewels"*. [[6]](u)', True),
    ("S57", 'The Harbour libraries are Kestrel\'s ready-made code for common tasks, and she '
            'called them the *"crown jewels"*. [[6]](u)', True),
    ("S57", 'Ruiz described Tern as the *"flywheel"* driving the depot network: each new '
            'route brings couriers, and each courier makes the next route worth '
            'running. [[6]](u)', False),
    ("S57", 'A dashed box labelled "the reason given" sits above a box labelled "cannot '
            'change".', False),
    ("S57", 'That is the circle Okafor objects to, and he states it sharply: "the words '
            'cannot count as testimony". [[3]](u)', False),
    # S57 (c) the decoded label and S56 (d) the opening stack, each with the repaired
    # shape that must stay silent.
    ("S57", 'Ruiz described Tern as the *"flywheel"* driving the depot network. [[6]](u) '
            'A flywheel keeps itself turning, and the filing states one half of that loop.', True),
    ("S57", 'Kestrel\'s chief executive credited Tern with driving the growth of the depot '
            'network. [[6]](u) A flywheel is not mentioned here.', False),
    ("S56", 'At the company\'s customer conference on 16 January 2019, its chief executive, Ana '
            'Ruiz, marked the depot\'s twentieth anniversary.', True),
    ("S56", 'Kestrel\'s chief executive, Ana Ruiz, used her keynote in January 2019 to mark '
            'twenty years of the depot.', False),
    ("S56", 'In January 2024 the analysis firm Corvid Metrics, after five months of testing, '
            'found the software lacking.', False),
    ("S31", "So the tag was never rude. It was unpayable.", False),
    ("S31", "Each kind of rota works well alone. Trouble starts when two of them meet.", False),
    ("S31", "It had no preference for symmetry. No aesthetic prior. No nostalgia for human "
            "taste.", True),
    ("S31", "The tag was never rude. It was unpayable. Nobody could settle it. The argument "
            "that follows runs a good deal longer than any of those three did.", True),
    ("S31", "That becomes visible wherever somebody checks the field. The U.K. registry "
            "tells applicants plainly that nobody should list a machine as an author.",
     False),
    ("S31", 'Then the policy closes the loop in two sentences. "Agents MUST NOT approve their '
            'own changes. Only a named person can sign the release."', False),
    ("S31", 'She called it Tavi. You pronounce it "tah-vee", like the river. It means harbour.',
     True),
    ("S31", 'She called it Tavi. You pronounce it "tah-vee", like the river.', False),
    ("S31", "**Figure 3. Three fields, one machine.** The order is the point, and authority "
            "runs downward from the signature to the disclosure.", False),
    ("S09", "A commit message is not a credit list. It is three kinds of field.", True),
    ("S09", "The name is not the artefact. It is a pointer to one.", True),
    ("S09", "Your agent did not write that commit. It did not sign it either.", False),
    ("S09", "The chain above does not reach you. That is true, and it leaves you worse off.",
     False),
    ("S09", "The maintainers do not require it.\n\n## What it asks for\n\nIt is a disclosure.",
     False),
    ("S49", "Kestrel's written limit on how often counts late parcels, and a lost parcel has "
            "none.", True),
    ("S49", "## The limit counts minutes, and a cancelled evening has none", True),
    ("S49", "The written limit on depot failures counts minutes of delay, and a lost parcel "
            "adds none.", True),
    ("S49", "The dashboard tracks latency, and an outage that never started records nothing.",
     True),
    ("S49", "Team A has three open bugs, and team B has none.", False),
    ("S49", "The first release adds four endpoints, and the second adds none.", False),
    ("S49", "A control loop needs a measured error signal, and review has none for "
            "understanding.", False),
    ("S49", "A number that only rises is a counter, and a counter measures nothing.", False),
    ("S49", "A small team has about a quarter, and two thirds of the time has nothing at all.",
     False),
    ("S49", "## The limit counts minutes of delay and leaves out lost parcels", False),
    # S50: a title and a subtitle that each carry the argument, in every place the check
    # reads them, and fields that fit.
    ("S50", "- **Title.** Kestrel Says Its Robots Might Be Bored. Corvid Says Its Robots Are "
            "Not. Neither Answer Is Evidence.", True),
    ("S50", "- **Title.** Kestrel Wrote Its Robots' Doubt About Their Own Work. Corvid's Draft "
            "Writes the Opposite.", True),
    ("S50", "- **Subtitle.** What a model says about its own mind comes from the document that "
            "trained it. That matters to anyone who trusts a model's account of itself.", True),
    ("S50", "- **Subtitle.** Kestrel's own test caught a model noticing a planted thought "
            "about 20% of the time, and Corvid's draft is open for six weeks. Three checks "
            "before your product trusts what a model says about itself.", True),
    ("S50", "---\ntitle: Kestrel Says Its Robots Might Be Bored. Corvid Says They Are Not. "
            "Neither Is Evidence.\n---\n\nBody text.", True),
    ("S50", "# A Short Title\n\n*A standfirst that runs on and on past the ceiling because it "
            "tries to say the mechanism, the audience and the benefit all at once, in one "
            "breath.*\n\nBody text.", True),
    ("S50", "# A Short Title\n\n*One plain line of context.*\n\nBody text.", False),
    ("S50", "- **Title.** Your Coding Agent Did Not Write That Commit", False),
    # S54: a counted set with nothing to count, and two that were named first.
    ("S54", "## Section\n\nThe study reordered the options.\n\nThe differences between those "
            "five answers are product decisions.", True),
    ("S54", "## Section\n\nI asked five models the same question. One was unsure and four "
            "denied it.\n\nThe differences between those five answers are product decisions.",
     False),
    ("S54", "## Section\n\nThe three checks below take an afternoon. These three checks are "
            "the cheapest ones I know.", False),
    # S53: the bare aphorism, and three sentences that name what they are about.
    ("S53", "And an explanation is not always the reason.", True),
    ("S53", "A score is not a measurement.", True),
    ("S53", "A model's explanation is not always the reason it answered.", False),
    ("S53", "An explanation is not always the reason a model gave that answer.", False),
    ("S53", "The denial was not evidence.", False),
    # S51: a section opening on its evidence, and two that open on their point.
    ("S51", "## What this means\n\nIn 2023 Ines Marlow and colleagues showed that a model's "
            "step-by-step explanation can misrepresent the true reason for its answer.", True),
    ("S51", "## What this means\n\nAccording to Marlow and colleagues, a model's explanation "
            "can misrepresent the reason for its answer.", True),
    ("S51", "## What this means\n\nA 2023 study says so. [[6]](https://example.org/a)", True),
    ("S51", "## What this means\n\nSearch two documents before you trust a self-report. In 2023 "
            "Ines Marlow showed why.", False),
    ("S51", "## What this means\n\nA model's explanation is not always its reason, and the "
            "evidence for that is a 2023 study. [[6]](https://example.org/a)", False),
    ("S50", "- **Title.** You Can Stockpile Gallium. You Can't Stockpile Judgement.", False),
    ("S50", "- **Title.** How Two Labs Can Call for a Slowdown and Keep Shipping", False),
    ("S50", "- **Subtitle.** A chip maker is reportedly in talks to buy a model hub. Four steps "
            "for anyone whose pipeline uses them.", False),
    ("S50", "- **Subtitle.** Two labs ran 200 million exchanges through a rival's model. One "
            "team used it as an engineering crew.", False),
    ("S50", "The first sentence of a body paragraph can run well past a hundred and twenty "
            "characters without being a title field, and the check must leave it alone.",
     False),
    # S59: a word from the opening that returns as a label, and openings that share only
    # the title's words.
    ("S59", "# Shipping safely\n\nOne engineer likened the pager to a smoke alarm, and every alert "
            "wants its toast checked before anything else.\n\n## Why alerts multiply\n\nEach team "
            "adds toasts to the dashboard until nobody can see the fire.\n\n## What to remove\n\n"
            "Delete the toast alerts first, because nobody reads them anyway.\n\nSomebody still "
            "has to tell the toast from the fire when the pager goes.\n\n## References\n", True),
    ("S59", "# How Teams Review Changes\n\nA reviewer opens the change and reads the diff before "
            "anything else happens.\n\n## The review\n\nThe reviewer reads every file in turn and "
            "writes a comment on each.\n\n## The close\n\nReview every change with the same care.\n\n"
            "Then merge it when the comments are answered.\n\n## References\n", False),
    ("S59", "# Shipping safely\n\nOne engineer likened the pager to a smoke alarm, and every alert "
            "wants its toast checked before anything else.\n\n## Why alerts multiply\n\nEach team "
            "adds checks to the dashboard until nobody can see the fire.\n\n## What to remove\n\n"
            "Delete the first alerts, because nobody reads them anyway.\n\nSomebody still "
            "has to tell the toast from the fire when the pager goes.\n\n## References\n", False),
    # An example inside a code fence is never the writer's prose.
    ("S16", "- **Speed:** faster.\n- **Accuracy:** better.\n- **Safety:** guarded.", True),
    ("S16", "```text\n- **Speed:** faster.\n- **Accuracy:** better.\n- **Safety:** guarded.\n```", False),
    ("S31", "```text\nIt stopped. Nobody knew. Then it started.\n\nAgain.\n```", False),
]


def selftest():
    failures = 0
    for sec, text, want in STRUCT_SELFTEST:
        got = any(h[0] == sec for h in structural(text, mask(text)))
        ok = got == want
        failures += not ok
        print("  %s  %-6s %-6s %s" % ("ok " if ok else "BAD", sec, "fire" if want else "silent",
                                     text.replace("\n", " ")[:78]))
    for sec, cases in SELFTEST.items():
        checks = [(n, p, f) for s, n, p, f in REGEX_CHECKS if s == sec]
        for want, texts in (("fire", cases["fire"]), ("silent", cases["silent"])):
            for t in texts:
                got = [n for n, p, f in checks if re.search(p, mask(t), f)]
                ok = bool(got) == (want == "fire")
                failures += not ok
                print("  %s  %-6s %-6s %s%s" % ("ok " if ok else "BAD", sec, want, t[:78],
                                               "" if ok or not got else "  <- " + got[0]))
    print("\nself-test: %s" % ("PASS" if not failures else "%d FAILURE(S)" % failures))
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# Structural checks that no single regex can carry.
# ---------------------------------------------------------------------------
# A full stop inside an abbreviation is not a sentence end. Splitting on it cut
# "The U.S." off as a two-word sentence and reported it as staccato. Initialisms
# (U.S., D.C., U.K.), Latin short forms and titles are protected; "etc." is not,
# because it usually does end the sentence it is in.
ABBREV = re.compile(r"\b(?:[A-Z]\.){2,}|\b(?:e\.g|i\.e|vs|cf|al|Dr|Mr|Mrs|Ms|St|Jr|Sr|Inc"
                    r"|Ltd|Fig|Vol)\.|\bNo\.(?=\s*\d)|\b(?:Figure|Table)\s+\d+\.")
HOLD = "․"   # one-dot leader, standing in for a protected full stop


def split_sentences(t):
    t = re.sub(r"\[\[\d+\]\]\([^)]*\)", "", t)
    t = ABBREV.sub(lambda m: m.group(0).replace(".", HOLD), t)
    return [x.strip().replace(HOLD, ".")
            for x in re.split(r"(?<=[.!?])\s+", t.strip()) if x.strip()]


def blocks(masked):
    """Paragraph-sized blocks of the masked text, heading lines removed, so no
    sentence pair is ever read across a heading or a paragraph break."""
    for b in re.split(r"\n\s*\n", masked):
        lines = [ln for ln in b.split("\n") if not ln.lstrip().startswith("#")]
        if "".join(lines).strip():
            yield "\n".join(lines)


def strip_fences(text):
    """Fenced code blanked to spaces with its newlines kept, so no structural check
    reads an example inside a code fence as the writer's prose."""
    return re.sub(r"```.*?```", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)


def prose_paragraphs(raw):
    out, head = [], None
    for para in strip_fences(raw).split("\n\n"):
        p = para.strip()
        if not p:
            continue
        if p.startswith("#"):
            head = p.lstrip("# ").strip()
            continue
        if p.startswith(("![", "<!--", ">", "|", "---", "```")):
            continue
        if re.match(r"^\d+\.\s", p) or p.startswith("- "):
            continue
        out.append((head, p))
    return out




VERB = (r"\b(is|are|was|were|has|have|had|does|do|did|can|will|would|point|tilt"
        r"|came|went|ran|built|found|sits?|carries|makes?|gets?|turns?|holds?"
        r"|shows?|says?|leaves?|takes?|gives?|costs?)\b")


def pline(raw, para):
    """First line of a paragraph taken from the raw text, or 0 when it cannot be
    found. Structural hits carry it so check-log can tell which unit a hit is in."""
    at = raw.find(para)
    return lineno(raw, at) if at >= 0 else 0


def structural(raw, masked):
    hits = []

    # S09 - the two-sentence corrective antithesis, the form a comma-only scan misses.
    # Pairs are read within one block only: reading the whole file as one run joined a
    # heading to the paragraph under it. The second sentence must be the positive
    # replacement: "It did not sign it either" is a second negative, and "That is true"
    # after a negative is a concession.
    per_block = [split_sentences(b) for b in blocks(masked)]
    sents = [s for blk in per_block for s in blk]
    for blk in per_block:
        for i in range(len(blk) - 1):
            a, b = blk[i], blk[i + 1]
            if re.search(r"\b(is|are|was|were|does|do|did|has|have)\s+not\b", a) and \
               re.match(r"^(It|They|That|This|What|These|Those)\s+"
                        r"(is|are|was|were|does|do|did|has|have)\b(?!\s+(?:not|never)\b)", b) and \
               not re.match(r"^That\s+is\s+(?:true|right|fair|correct|so)\b", b):
                at = masked.find(a)
                hits.append(("S09", "antithesis: two-sentence form (X is not A. It is B.)",
                             lineno(masked, at) if at >= 0 else 0, a[:70] + " / " + b[:60]))

    # S31 - staccato: THREE OR MORE consecutive sentences all under 11 words, reported
    # once per run. A pair is not enough: two short sentences in a row turn up in
    # nearly every published human essay, at about three times the rate of machine
    # drafts, so a pair check removes a rhythm people write. The catalogue's wording
    # is "a single short sentence for emphasis is fine; a run of them starts to sound
    # engineered", and a run starts at three. A sentence the split cut out of a
    # quotation is skipped: its words are the source's, which the quoted-material
    # rule puts out of scope, and it was never a sentence of the writer's. The sign is
    # an unbalanced quotation mark. A sentence that merely CONTAINS a whole quotation
    # ('You pronounce it "tah-vee"') is the writer's and stays.
    def cut_from_quote(s):
        return s.count('"') % 2 == 1 or s.count(LQUOTE) != s.count(RQUOTE)
    for head, p in prose_paragraphs(raw):
        S = split_sentences(p)
        L = [len(x.split()) for x in S]
        short = [L[i] < 11 and not cut_from_quote(S[i]) for i in range(len(L))]
        i = 0
        while i < len(L):
            j = i
            while j < len(L) and short[j]:
                j += 1
            if j - i >= 3:
                hits.append(("S31", "three or more consecutive short sentences", pline(raw, p),
                             "[%s] %s: %s" % (head, "+".join("%dw" % v for v in L[i:j]),
                                              " / ".join(S[i:j]))))
            i = max(j, i + 1)

    # S39 - run of 3+ consecutive sentences all over 15 words in one paragraph
    for head, p in prose_paragraphs(raw):
        L = [len(x.split()) for x in split_sentences(p)]
        if len(L) >= 3 and any(all(v > 15 for v in L[j:j + 3]) for j in range(len(L) - 2)):
            hits.append(("S39", "run of 3+ long sentences (check for one shared frame)",
                         pline(raw, p), "[%s] lengths %s" % (head, L)))

    # S10 - rule of three: three comma-joined clauses each carrying a finite verb
    for s in sents:
        parts = [c.strip() for c in re.split(r",\s*(?:and\s+)?", s) if c.strip()]
        if len(parts) == 3 and sum(1 for c in parts if re.search(VERB, c)) == 3:
            at = masked.find(s)
            hits.append(("S10", "three-beat (verify each clause carries a different idea)",
                         lineno(masked, at) if at >= 0 else 0, s[:120]))

    # S17 / S36 / S37 - heading forms
    nocode = strip_fences(raw)
    for m in re.finditer(r"^(#{2,4})\s+(.+)$", nocode, re.M):
        h = m.group(2).strip()
        if h.endswith("?"):
            hits.append(("S37", "question heading (name the topic instead)",
                         lineno(raw, m.start()), h))
        words = re.findall(r"[A-Za-z][a-z']+", h)
        if len(words) >= 4 and sum(1 for w in words if w[0].isupper()) >= len(words) - 1:
            hits.append(("S17", "title case heading", lineno(raw, m.start()), h))
        if re.match(r"^(Background|Analysis|Discussion|Implications"
                    r"|Other considerations|Key components|Main features"
                    r"|Core concepts)$", h, re.I):
            hits.append(("S36", "contentless structural heading",
                         lineno(raw, m.start()), h))

    # S29 - fragmented header: heading, then a one-line paragraph under 10 words
    for m in re.finditer(r"^#{2,4}\s+.+\n\n([^\n#!<>|].{0,120})\n\n", nocode, re.M):
        line = m.group(1).strip()
        if re.fullmatch(r"[*_].+[*_]", line):
            continue
        if len(line.split()) < 10:
            hits.append(("S29", "fragmented header (one-line warm-up under a heading)",
                         lineno(raw, m.start()), m.group(1)))

    # S15 - boldface overuse: more than six bold spans in one paragraph
    for head, p in prose_paragraphs(raw):
        n = len(re.findall(r"\*\*[^*]+\*\*", p))
        if n > 6:
            hits.append(("S15", "boldface overuse (%d spans in one paragraph)" % n,
                         pline(raw, p), "[%s] %s" % (head, p[:80])))

    # S16 - inline-header vertical list: 3+ consecutive items opening "**Label:**"
    runs, cur = [], 0
    for line in nocode.split("\n"):
        if re.match(r"^\s*[-*]\s+\*\*[^*]+:\*\*", line):
            cur += 1
        else:
            if cur >= 3:
                runs.append(cur)
            cur = 0
    if cur >= 3:
        runs.append(cur)
    for n in runs:
        hits.append(("S16", "inline-header vertical list (%d items)" % n, 0,
                     "bolded label plus colon opening consecutive items"))

    # S42 - the staged imperative. A short command that puts the reader in a scene,
    # followed by a sentence that opens by pointing back at the staged object.
    # Both halves are required, and the length guard is what separates staging from
    # an instruction: a reader's tool carries its detail in the imperative sentence
    # itself and runs long, while a stage direction is short by construction. The
    # deletion test - strike the command, promote its object into the next sentence's
    # subject, see whether anything is lost - is a human read and is declared below.
    STAGE = (r"^\**(?:Now|Then|First|Next)?\s*\**\s*"
             r"(Open|Picture|Imagine|Look|Find|Take|Consider|Think|Watch|Read|Start"
             r"|Notice|Listen|Count|Compare|Pick|Choose|Follow|Try|Walk|Go|Ask|Say)\b")
    ANAPH = r"\b(it|its|that|this|these|those|there|they|them|one|each one)\b"
    for head, p in prose_paragraphs(raw):
        S = split_sentences(p)
        for i in range(len(S) - 1):
            a, b = S[i], S[i + 1]
            if len(a.split()) > 14:
                continue
            # Case-insensitive: after a leading "Now"/"Then"/"First" the verb is
            # lowercase, and a case-sensitive match silently missed "Now find the
            # line ... / There isn't one." - one of this section's own examples.
            if not re.match(STAGE, a.strip(), re.I):
                continue
            if re.search(ANAPH, " ".join(b.split()[:5]), re.I):
                hits.append(("S42", "staged imperative (run the deletion test)", pline(raw, p),
                             "[%s] %s / %s" % (head, a[:70], b[:60])))

    # S49 (b) - the bare closing quantifier. A clause joined by and/but/yet/while/whereas
    # that ENDS on none / nothing / zero, on a verb that is not the one its noun came
    # from: "counts late parcels, and a lost parcel has none". The reader carries "late
    # parcels" across to a different verb, then works out the consequence the line
    # leaves unsaid (so lost parcels are not counted). The same verb on both sides
    # ("Team A has three bugs, and team B has none") is ordinary ellipsis and stays
    # silent, and so does a quantifier the clause goes on to complete ("has none for
    # understanding"). Read line by line, so headings, captions and titles are reached.
    CLOSE_V = (r"(?:has|have|had|adds?|added|carries|carry|carried|gets?|got|earns?|earned"
               r"|registers?|registered|contributes?|shows?|showed|leaves?|left|scores?|scored"
               r"|counts?|counted|records?|recorded|holds?|held|gains?|gained)")

    def verb_family(v):
        v = v.lower()
        if v in ("has", "have", "had"):
            return r"has|have|had"
        if v in ("got", "left", "held"):
            return {"got": r"gets?|got", "left": r"leaves?|left", "held": r"holds?|held"}[v]
        if v.endswith(("ies", "ied")):
            return re.escape(v[:-3]) + r"(?:y|ies|ied)"
        return re.escape(re.sub(r"(?:es|s|ed)$", "", v)) + r"\w*"

    for mln, line in enumerate(masked.split("\n"), 1):
        text = re.sub(r"^\s*(?:#{1,6}\s+|[-*]\s+|\d+\.\s+)", "", line)
        for sent in split_sentences(text):
            m = re.search(r"^(?P<pre>.+),\s+(?:and|but|yet|while|whereas)\s+"
                          r"(?:[\w'\u2019-]+\s+){1,6}?(?P<v>" + CLOSE_V + r")\s+"
                          r"(?:none|nothing|zero)\s*[.!?]?\s*$", sent, re.I)
            if not m:
                continue
            if re.search(r"\b(?:" + verb_family(m.group("v")) + r")\b", m.group("pre"), re.I):
                continue
            hits.append(("S49", "elliptical punchline: a closing none/nothing on a different "
                                "verb (none of WHAT, and so what?)", mln, sent.strip()[:120]))

    # S50 - a title or subtitle that tries to carry the whole argument. Read from a
    # front-matter title or subtitle, a labelled Title or Subtitle field, the first
    # level-1 heading, and an italic standfirst line straight under that heading.
    # The ceilings are house judgement, not findings.
    fields, lines50, fm_end = [], raw.split("\n"), 0
    if lines50 and lines50[0].strip() == "---":
        for j in range(1, len(lines50)):
            if lines50[j].strip() == "---":
                fm_end = j + 1
                break
        for j in range(1, max(fm_end - 1, 1)):
            m = re.match(r"^(title|subtitle):[ \t]*(.+)$", lines50[j], re.I)
            if m:
                fields.append((m.group(1).capitalize(), j + 1, m.group(2).strip().strip("'\"")))
    seen_h1 = False
    for j in range(fm_end, len(lines50)):
        line = lines50[j]
        m = re.match(r"^(?:[-*][ \t]+)?(?:\*\*(Title|Subtitle)[.:]?\*\*[.:]?|(Title|Subtitle):)"
                     r"[ \t]+(.+)$", line)
        if m:
            fields.append((m.group(1) or m.group(2), j + 1, m.group(3)))
            continue
        if not seen_h1 and re.match(r"^#[ \t]+\S", line):
            seen_h1 = True
            fields.append(("Title", j + 1, line[1:].strip()))
            k = j + 1
            while k < len(lines50) and not lines50[k].strip():
                k += 1
            if k < len(lines50) and re.fullmatch(r"\s*([*_])[^*_\s].*[^*_\s]\1\s*", lines50[k]):
                fields.append(("Subtitle", k + 1, lines50[k].strip()))
    for field, ln, text in fields:
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"[*_`]", "", text).strip()
        n, sents = len(text), len(split_sentences(text))
        limit, most = (TITLE_MAX, 2) if field == "Title" else (SUBTITLE_MAX, 2)
        if n > limit or sents > most:
            hits.append(("S50", "%s carries an essay: %d characters, %d sentence(s); ceiling "
                         "%d characters and %d sentences" % (field.lower(), n, sents, limit, most),
                         ln, text[:120]))

    # S51 - the section that opens on its evidence instead of its point. The order
    # that works is takeaway, explanation, evidence, qualification, implication, and a
    # section can pass every sentence-level check while opening "In 2023 Ines Marlow
    # and colleagues showed...". A first sentence that carries a citation marker,
    # opens on a date, or opens with "According to" is reporting a source before the
    # reader has been told why it matters.
    seen = set()
    for head, para in prose_paragraphs(raw):
        if head is None or head in seen:
            continue
        seen.add(head)
        if re.match(r"(references|sources?|bibliography|works cited|notes)\b", head, re.I):
            continue
        plain = re.sub(r"[*_`]", "", para).lstrip("> ").strip()
        first = split_sentences(plain)
        if not first:
            continue
        sent = first[0].strip()
        # What fires is attribution in the opening words: the sentence's subject is a
        # source rather than the section's point. A takeaway that carries its own
        # marker at the end is the correct shape and stays silent.
        head6 = " ".join(re.sub(r"\[\[\d+\]\]\([^)]*\)", "", sent).split()[:6])
        why = None
        if re.match(r"^According to\b", head6, re.I):
            why = '"According to"'
        elif re.match(r"^(In|On)\s+((19|20)\d\d|\d{1,2}\s+[A-Z][a-z]+)\b", head6):
            why = "a date"
        elif re.search(r"\b(19|20)\d\d\b", head6):
            why = "a year"
        elif re.search(r"\b(study|paper|report|researchers|survey|analysis)\b", head6, re.I):
            why = "a source as its subject"
        elif re.search(r"\b[A-Z][a-z]+\s+(?:and colleagues|et al\.)", head6):
            why = "an author as its subject"
        if why:
            hits.append(("S51", "section opens on its evidence (%s in the first six words), "
                         "not on its point" % why, lineno(raw, raw.find(para)),
                         re.sub(r"\[\[(\d+)\]\]\([^)]*\)", r"[\1]", sent)[:120]))

    # S53 - the bare aphorism. Two unpossessed abstract nouns in a short "X is not Y"
    # sentence, stating a general truth with the actor, the object and the mechanism
    # all deleted: "And an explanation is not always the reason." The claim
    # underneath names whose explanation, of what, and what actually drove it.
    BARE = re.compile(r"^(?:And|But|Yet)?\s*(?:An?|The)\s+([a-z]{4,})\s+(?:is|was|are|were)\s+"
                      r"(?:not|never|rarely)\s+(?:always\s+|necessarily\s+|simply\s+)?"
                      r"(?:an?|the)\s+([a-z]{4,})\s*[.!?]$", re.I)
    for head, para in prose_paragraphs(raw):
        plain = re.sub(r"[*_`]", "", para).strip()
        for sent in split_sentences(plain):
            sent = sent.strip()
            if len(sent.split()) > 12:
                continue
            m = BARE.match(sent)
            if m:
                hits.append(("S53", "bare aphorism: '%s'/'%s' with no owner, object or actor "
                             "(say whose, and of what)" % (m.group(1).lower(), m.group(2).lower()),
                             lineno(raw, raw.find(para)), sent[:110]))

    # S54 - the counted demonstrative with nothing to count. "The differences between
    # those five answers are product decisions" points at a set the reader cannot find,
    # typically because the sentence naming the five was deleted while repairing a
    # different defect. A repair can orphan a reference, and this check watches for it.
    NUMS = r"two|three|four|five|six|seven|eight|nine|ten|\d+"
    DEM = re.compile(r"\b(?:those|these)\s+(" + NUMS + r")\s+([a-z]{3,}s)\b", re.I)
    paras = [re.sub(r"[*_`]", "", p).strip() for _, p in prose_paragraphs(raw)]
    for i, para in enumerate(paras):
        for m in DEM.finditer(para):
            num, noun = m.group(1).lower(), m.group(2).lower()
            window = (paras[i - 1] if i else "") + " " + para[:m.start()]
            window = window.lower()
            if noun in window or (num + " ") in window:
                continue
            hits.append(("S54", "counted demonstrative with no antecedent nearby: '%s %s' "
                         "(name the set here, or drop the count)" % (num, noun),
                         lineno(raw, raw.find(para)), m.group(0)))

    # S56 (c) - the custody run. Two or more sentences in one paragraph whose subject
    # is a document and whose verb hands over a quotation: "The release schedule says
    # *"..."*. [5] ... The same paragraph says *"..."*. [5]". The marker already says
    # where the words came from; the clause about the document repeats it, and a run
    # of them puts the paper in the subject where the people who wrote it belong. The
    # regex checks run on masked text, where a quotation is blanked and "The release
    # schedule says" is a four-word stub no length check reaches, so this one reads
    # the raw paragraph: the quotation must be present for the sentence to count. A
    # single custody sentence is ordinary sourcing and stays silent; so does "It says"
    # with no document-subject sentence beside it.
    DOCN = (r"(?:filing|report|release|schedule|paragraph|document|page|section|PEP(?: \d+)?"
            r"|blog|post|statement|announcement|letter|paper|study|survey|guidance|policy"
            r"|notice|account|transcript|minutes|record|summary|notes?|changelog|FAQ"
            r"|disclosure|prospectus|submission|judgment|judgement|ruling|order|brief"
            r"|complaint|memo|email|website|README|documentation|docs|specification|spec"
            r"|standard|RFC|charter|agreement|contract|licen[cs]e|terms|readout|keynote"
            r"|press release|release notes|risk factors?|proposal|entry|article|thread)")
    RVERB = (r"(?:says?|said|states?|stated|reads?|notes?|noted|adds?|added|puts? it"
             r"|describes?|described|calls?|called|lists?|listed|explains?|explained"
             r"|records?|recorded|writes?|wrote|warns?|warned|concludes?|concluded"
             r"|continues?|goes on|argues?|argued|claims?|claimed|sets? out|spells? out"
             r"|admits?|acknowledges?|gives?|quotes?|quoted|promises?|promised"
             r"|describes? it as|has (?:him|her|them|it) (?:saying|calling))")
    CUSTODY = re.compile(r"^(?:The|This|That|Its|Their|His|Her|Our|Your|Each|Every|A|An"
                         r"|[A-Z][\w.&-]*(?:'s|’s))(?:\s+[\w'’.-]+){0,4}?\s+"
                         + DOCN + r"s?(?:'s|’s)?\b(?:\s+[\w,'’-]+){0,4}?\s+"
                         + RVERB + r"\b", re.I)
    PRON = re.compile(r"^(?:It|They|This|That)\s+(?:also\s+|then\s+|further\s+)?" + RVERB + r"\b")
    QMARK = re.compile(r'"|' + LQUOTE)
    for head, p in prose_paragraphs(raw):
        doc_led, pron_led, first = 0, 0, None
        for sent in split_sentences(p):
            plain = re.sub(r"[*_`]", "", sent).strip()
            m = CUSTODY.match(plain) or PRON.match(plain)
            if not m or not QMARK.search(plain[m.end():]):
                continue
            if CUSTODY.match(plain):
                doc_led += 1
            else:
                pron_led += 1
            first = first or plain
        if doc_led >= 1 and doc_led + pron_led >= 2:
            hits.append(("S56", "custody run: %d quotations each handed over by the document "
                         "as subject (let the marker carry the source; put the people in the "
                         "subject)" % (doc_led + pron_led), pline(raw, p),
                         "[%s] %s" % (head, first[:100])))

    # S57 - the quoted label. A source's figure of speech ("flywheel", "crown jewels")
    # quoted as if it were evidence. It says only that the speaker likes the thing,
    # which the sentence before usually said already, and the piece never states what
    # the figure means. Every regex check runs on masked text, where the label is
    # blanked, so this one reads the raw paragraph.
    # (a) Two or more labels in one paragraph: a naming verb (call, describe as,
    #     dub) with a quotation of four words or fewer.
    # (b) A gloss welded to a label by "and": "The X are <what they are>, and he
    #     called them the 'y'". A definition and an event share one sentence, and the
    #     reader gets the handle and the praise in one breath.
    # Leaving out "labelled" keeps (a) off a drawing's printed labels; requiring the
    # naming verb after "and" keeps (b) off ordinary "X is Y, and he states it".
    LABEL = re.compile(r"\b(?:call(?:s|ed|ing)?|describ(?:es|ed|ing)\s+(?:\w+\s+){0,3}?as"
                       r"|dubb(?:ed|s|ing))\b[^.\n]{0,70}?[\"" + LQUOTE + r"]([^\"" + RQUOTE
                       + r"\n]{1,40})[\"" + RQUOTE + "]", re.I)
    WELD = re.compile(r"^[A-Z][^,.]{2,60}?\b(?:is|are)\b[^,.]{3,90}, and (?:he|she|they|it|we"
                      r"|[A-Z][\w'’]+)\s+(?:call(?:s|ed)?|describ(?:es|ed)|dubb(?:s|ed)|named?s?)"
                      r"\s+(?:them|it|him|her)\b[^.]{0,20}?[\"" + LQUOTE + "]")
    # (c) The decoded label: a short quotation, then the next sentence opens by
    #     defining its last word ('... the "flywheel" driving the network. A flywheel
    #     keeps itself turning, and ...'). The writer imported the speaker's figure and
    #     now has to explain it, and the explanation is usually a second figure.
    # (d) is in S56 below: the opening stack.
    SHORTQ = re.compile(r"[\"" + LQUOTE + r"]([^\"" + RQUOTE + r"\n]{1,40})[\"" + RQUOTE + "]")
    for head, p in prose_paragraphs(raw):
        labels, welds = [], []
        S = [re.sub(r"[*_`]", "", x).strip() for x in split_sentences(p)]
        for i in range(len(S) - 1):
            for m in SHORTQ.finditer(S[i]):
                w = m.group(1).split()
                if not 1 <= len(w) <= 4:
                    continue
                last = re.escape(w[-1].strip(".,;:!?").lower())
                if last and re.match(r"^(?:A|An|The)\s+(?:[\w-]+\s+)?" + last + r"s?\b", S[i + 1], re.I):
                    hits.append(("S57", "decoded label: a quoted figure of speech, then a sentence "
                                 "explaining it (say what the speaker claimed, in plain words)",
                                 pline(raw, p), "[%s] %s / %s" % (head, S[i][-50:], S[i + 1][:60])))
                    break
        for sent in split_sentences(p):
            plain = re.sub(r"[*_`]", "", sent).strip()
            if any(len(m.group(1).split()) <= 4 for m in LABEL.finditer(plain)):
                labels.append(plain)
            if WELD.match(plain):
                welds.append(plain)
        if len(labels) >= 2:
            hits.append(("S57", "quoted labels: %d praise-words quoted as evidence in one "
                         "paragraph (keep one and say what it means, or paraphrase)"
                         % len(labels), pline(raw, p), "[%s] %s" % (head, labels[0][:100])))
        for w in welds:
            hits.append(("S57", "gloss welded to a label by 'and' (give the gloss and the "
                         "quotation separate sentences, or drop the label)", pline(raw, p),
                         "[%s] %s" % (head, w[:100])))

    # S56 (d) - the opening stack. A sentence that opens on an occasion and a date,
    # then a subject carrying its role and its name between commas, so four insertions
    # arrive before the verb: "At the company's customer conference on 16 January
    # 2019, its chief executive, Ana Ruiz, marked...". It is the usual result of
    # repairing a time ladder by cutting the interval and moving the date forward.
    STACK = re.compile(r"^(?:At|In|On|During|Speaking at)\b[^.]{5,90}?\b(?:19|20)\d\d, "
                       r"(?:its|the|his|her|their|[A-Z][\w&.-]*(?:'s|\u2019s))\s[^,]{2,40}, "
                       r"[A-Z][\w.'\u2019-]+(?: [A-Z][\w.'\u2019-]+)+,")
    for head, p in prose_paragraphs(raw):
        for sent in split_sentences(p):
            plain = re.sub(r"[*_`]", "", sent).strip()
            if STACK.match(plain):
                hits.append(("S56", "opening stack: an occasion and a date, then a role and a name, "
                             "before the verb (name the person first and let them act)",
                             pline(raw, p), "[%s] %s" % (head, plain[:100])))

    # S59 - the private code word. A figure of speech introduced in the opening and then
    # reused as a label until it stands for a claim: a toast is a trivial alert, a fire
    # is a real one, and the close tells the reader to "tell the toast from the fire".
    # The reader must decode it once, then keep the key in mind for the whole piece.
    # The mechanical proxy is a ring: a word that is in the opening paragraph, in the
    # last two paragraphs, and in the body between, that is not in the title or any
    # heading, and that is rare enough (ten uses or fewer) not to be the subject. It
    # lists candidates and the reader judges them, as S39 does; a plain recurring term
    # of the subject is not a hit once it is in a heading or is common. Proper nouns
    # are skipped. It cannot tell a figure from a technical noun, so a hit asks one
    # question: is this word standing for something else?
    body59 = re.split(r"\n#{1,3} (?:References|Sources|Bibliography|Works cited|Notes)\b",
                      raw)[0]
    def stem59(w):
        w = w.lower()
        if len(w) > 5 and w.endswith("es"):
            return w[:-2] if w[:-2].endswith(("x", "ch", "sh", "ss")) else w[:-1]
        if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
            return w[:-1]
        return w
    STOP59 = set("""that with from have this their which would there about other these those than then when what
        will more most much many also only into over same such each both even ever just like make made does were been
        being them they your some very still here where after before again because while until against between
        without under through whether could should every never first second third three doing going goes gets
        takes took came come says said used uses want wants need needs work works working know known knows
        something nothing anything everything someone somebody anyone nobody people person thing things way ways
        part parts time times year years week weeks day days case cases piece point points kind sort real whole
        another already always often rather really quite later early once twice back down away around along
        behind beside beyond within across toward among whose whom does done doesn""".split())
    paras59 = []
    for blk in re.split(r"\n\s*\n", body59):
        b = blk.strip()
        if not b or b.startswith(("#", "!", "<!--", ">", "-", "1.")):
            continue
        b = re.sub(r"\[\[\d+\]\]\([^)]*\)", "", b)
        if len(b.split()) >= 8:
            paras59.append(b)
    if len(paras59) >= 4:
        heads59 = set()
        for ln in body59.split("\n"):
            if ln.startswith("#"):
                heads59 |= {stem59(w) for w in re.findall(r"[A-Za-z]{4,}", ln)}
        caps59 = {stem59(w) for w in re.findall(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{3,}", body59)}
        def words59(t):
            return [stem59(w) for w in re.findall(r"[A-Za-z]{4,}", t)
                    if stem59(w) not in STOP59 and w.lower() not in STOP59]
        opening59 = set(words59(paras59[0]))
        closing59 = set(words59(" ".join(paras59[-2:])))
        middle59 = words59(" ".join(paras59[1:-2]))
        everything59 = words59(" ".join(paras59))
        rings = sorted(w for w in opening59 & closing59
                       if w in middle59 and w not in heads59 and w not in caps59
                       and everything59.count(w) <= 10)
        if rings:
            hits.append(("S59", "private code word: a word from the opening that comes back as a "
                         "label (is it a figure of speech standing for a claim?)",
                         pline(raw, paras59[0]), ", ".join(rings)))

    return hits


TITLE_MAX = 75
SUBTITLE_MAX = 120


# ---------------------------------------------------------------------------
# What this scanner does NOT check, and why. Printed every run.
# ---------------------------------------------------------------------------
NOT_CHECKED = [
    ("S02", "undue emphasis on notability",
     "needs judgement about whether a source list has context around it"),
    ("S11", "elegant variation / synonym cycling",
     "needs to know that two different words mean the same thing here"),
    ("S13", "passive voice and subjectless fragments",
     "detectable, and the false-positive rate on deliberate fragments makes a flag "
     "worse than a read"),
    ("S39", "whether a flagged run shares ONE FRAME",
     "the scanner finds the run; only a reader sees whether one template generates it"),
    ("S40", "description mirroring its own paragraph",
     "needs each caption and alt text read against the prose beside it, in order "
     "and phrasing"),
    ("S41", "conclusions with their joints removed",
     "needs each sentence's job named (observation, expectation, finding, inference); "
     "a run where every answer is 'finding' is the pattern"),
    ("S45", "whether a described thing HAS A NAME the writer knows",
     "the scanner encodes only the emptiest placeholders (thing, part, piece, bit) "
     "because the broad form returned four false positives for every true one. Ask it "
     "of every noun phrase by hand: is there a name for this, and do I know it?"),
    ("S42", "whether a flagged imperative survives the DELETION TEST",
     "the scanner finds the two-sentence shape; only a reader can strike the command, "
     "promote its object into the next sentence's subject, and see whether anything "
     "was lost. An imperative carrying content stays"),
    ("S46", "whether the REWRITES have converged on a new template",
     "the scanner finds each assigned memory; only a read across pieces sees every "
     "repaired opening becoming 'If you have ever sat in...'. It also cannot see the "
     "compressed actor in the scene ('where \"independently evaluated\" ended the "
     "discussion'): a phrase ended nothing, somebody said it"),
    ("S47", "whether the RELATION an epithet asserts is in a source, and every epithet "
     "the forms miss",
     "the scanner finds three shapes of description standing where a name should be. "
     "It cannot tell whether 'borrowed from', 'hired by' or 'built for' was read in a "
     "source. Of descriptions with no capitalised name in them it finds only 'The <role> "
     "whose <X> a <Y> would <verb>'; 'the company that taught the method' still passes. "
     "Ask of every noun phrase a rewrite put where a name was: what is the name, and "
     "did anybody say this relation?"),
    ("S48", "whether a BECAUSE-CLAUSE gives a mechanism or a figure, and every stand-in the "
     "forms miss",
     "the scanner finds a type-person with a story before the verb, 'than before' and "
     "'than ever', and a short list of verdict idioms (has spoken, the final word). It "
     "cannot tell a mechanism from a personification in general: the broad form, any "
     "thing doing any human act, fired on 'the person building the model wants' as often "
     "as on the real case. Ask of every 'because' in a verdict: what actually happens, "
     "and who does it? And of every type-person: is this a claim, and where is its source?"),
    ("HT", "whether a SUBTITLE does one job, and a title that denies a foil in any other form",
     "S50 checks length (title 75 characters, subtitle 120, two sentences each) as house "
     "judgement; it cannot see whether a short line still argues the whole piece. Read "
     "the subtitle for the context the title left out, with the plot and the argument "
     "left to the opening. A title denying a complaint nobody made is caught only in its "
     "'is not that' form"),
    ("S55", "a HEAVY SUBJECT the nominalisation list does not name",
     "S55 carries a dozen nouns followed by a wh-clause. The family is wider: any "
     "sentence whose subject runs past six words before its verb makes the reader hold "
     "a phrase they cannot yet use. Read each sentence to its first verb, and if the "
     "subject is still arriving, find the actor and let them act. Ask it hardest of a "
     "sentence written to repair another defect, which is where this shape most often "
     "appears"),
    ("S54", "a DEMONSTRATIVE with no count, pointing at something the reader cannot find",
     "S54 needs the number: 'those five answers' is checkable, 'that setting' and 'this "
     "pattern' are not, and they orphan just as easily. Of every 'this/that/those + "
     "noun', ask whether the thing it points at is on the same screen. Ask it "
     "especially after a repair: removing a fact can leave a later sentence pointing "
     "at nothing, and neither sentence looks wrong by itself."),
    ("S53", "an ABSTRACTION PAIR the shape does not catch",
     "S53 wants the sentence to end at the second noun, so 'An explanation is rarely "
     "the whole reason for an answer' passes it while asking the reader for the same "
     "three things. Of every short declarative made of abstract nouns, ask: whose, of "
     "what, and against what? If the piece has just named all three, the line is a "
     "summary; if it has not, the reader is doing the writer's work."),
    ("S52", "an ANNOUNCEMENT with no content, in wording the six forms miss",
     "the forms are literal: 'shows what X is worth', 'the useful part', 'where it gets "
     "interesting', 'worth pausing on', 'says something important', and an imperative "
     "counting unnamed objects. A lead-in can be empty in any wording - 'the numbers "
     "here repay a second look', 'what follows is the heart of it' - and no list "
     "catches that. Read every bolded lead-in and every short sentence before a "
     "paragraph of detail, and ask: does this sentence carry the claim, or only "
     "promise one?"),
    ("S51", "whether each section OPENS ON ITS POINT, which is the general case S51 misses",
     "S51 fires only where the first sentence is attribution-led: a date, a year, "
     "'According to', or a study or author as its subject. It stays silent on a vague "
     "lead ('The same problem arrives at a smaller scale') followed by the study, which "
     "reads as a literature review and passes every form here. So read each section's "
     "first sentence in order and ask of each: is this the section's point, or the "
     "material behind it? The order that works is takeaway, explanation, evidence, "
     "qualification, implication, and it applies to the opening too"),
    ("S49", "every ELLIPSIS the two forms miss, and the conclusion a compressed line leaves "
     "unsaid",
     "the scanner finds 'how often' with its clause cut and a clause ending on none or "
     "nothing on a different verb. It misses the same riddle split across two sentences "
     "('Late parcels count against the limit. A lost parcel has none.'), 'how much' and "
     "'how many' cut short, a verb phrase with its middle deleted ('halts rather than "
     "risk bad scans': risk passing on bad scans), and a closing 'one' standing for a "
     "noun several words back ('argued against keeping one'). A check for a sentence "
     "ending on a verb and 'one' also fired on 'whether you have one' and 'Medical device "
     "regulators have one', two of its three hits wrong, so that one is a read. Ask of "
     "every short line, and of every title above all: which words did I delete, and "
     "what does the reader have to conclude that I did not say?"),
    ("S56", "every AUDIT-TRAIL sentence the forms miss",
     "the scanner finds a date-interval-date ladder, a gloss wedged into an elided "
     "pair, an opening stack, and a custody run (two or more quotations in one paragraph "
     "each handed over by a document as subject, read from the raw text because masking "
     "blanks the quotation). A run led only by 'It says' or by a verb outside its list "
     "('reports', 'The decision was made') is not seen. It misses the general case: a "
     "name, its role, a gloss and a clause about the source's custody stacked between "
     "one subject and its verb, and a computed detail whose meaning the paragraph never "
     "states. Count the insertions before the verb, and ask of each which rule put it "
     "there and whether the reader needs it here."),
    ("S57", "a QUOTED LABEL the forms miss, and whether a kept label is CASHED",
     "the scanner finds two short quoted labels in one paragraph, a gloss welded to a "
     "label by 'and', and a label decoded by the next sentence. It misses a single label "
     "left uncashed, and a label reached by a verb outside its list ('hailed it as', "
     "'his word for it was'). Of every quotation of four words or fewer, ask: what does "
     "it tell the reader that the sentence around it did not, and is it evidence or "
     "only praise?"),
    ("S58", "a COMPLIANCE CLAUSE the one form misses, and whether the reader was defined "
     "rather than addressed",
     "the scanner needs a generic head from a short list, a verb from a short list, an "
     "abstract object from a short list, and a depend/rely/count-on ending, all in one "
     "sentence. It misses the same clause with 'which' for 'that', a verb outside the "
     "list ('is in charge of', 'keeps ... running'), a dependency worded another way "
     "('cannot do without', 'needs'), or the definition spread over two sentences. It "
     "also cannot tell a working audience note (a brief's 'target reader' line, never "
     "published) from the same words dropped into the document's own voice. Of every "
     "sentence naming who the piece is for, ask: would a person say this to another "
     "person, or was it assembled from a scope field? If the second, flip it: give the "
     "dependency clause its own subject ('if other people depend on what you run') or "
     "name the concrete case and let it stand for the class."),
    ("--", "whether a promise in the title, subtitle or summary is kept by the body",
     "no catalogue pattern detects it; read those lines against the body by hand"),
    ("S59", "whether a word that comes back from the opening is a FIGURE OF SPEECH, and every "
     "code word the ring misses",
     "the scanner lists words that sit in the opening, the close and the body between, and are "
     "not in a heading. It cannot tell a metaphor from a technical noun, and it misses a "
     "code word that never reaches the close, one that is also a heading word, one used more "
     "than ten times, and a figure that is never repeated but still has to be decoded once. "
     "Of every hit, and of every metaphor in the piece, ask: if I struck the figure out and "
     "wrote what it stands for, would the sentence lose anything the reader needs? If not, "
     "write the plain thing."),
]


# ---------------------------------------------------------------------------
# The humanise log. Nothing above can tell a paragraph that was read from one
# that was not: a skipped pass leaves no trace in the text. So a pass can leave a
# record: a fingerprint of every reader-facing unit it covered, written to
# humanise-log.json in the folder that holds the scanned file, and a compare mode
# that lists every unit whose text is not in the log. The log proves the pass was
# RECORDED, not that the reading happened; an entry is only accepted with the
# reading's findings stated ("read: 0 findings" counts), so a skip becomes a false
# statement rather than a silence. It is optional, for a long document that is
# edited over several passes.
# ---------------------------------------------------------------------------
import json
import hashlib
import datetime

LOG_NAME = "humanise-log.json"
# Sections whose content is not prose a reader reads: citations and notes.
SKIP_SECTIONS = re.compile(r"^(references|sources?|bibliography|works cited|notes)\b", re.I)


def units(raw):
    """Reader-facing units, each (line, text, last line): body paragraphs, headings and
    list items. Front matter, rules, comments, fenced code, tables, the references and
    the notes are left out."""
    out, section = [], ""
    lines = raw.split("\n")
    i, n = 0, len(lines)
    if lines and lines[0].strip() == "---":            # YAML front matter
        i = 1
        while i < n and lines[i].strip() != "---":
            i += 1
        i += 1
    block, start = [], None

    def flush():
        if not block:
            return
        text = " ".join(l.strip() for l in block).strip()
        if text and not text.startswith(("<!--", "```", "|")) and text != "---":
            out.append((start, text, start + len(block) - 1))

    in_code = in_comment = False
    while i < n:
        line, ln = lines[i], i + 1
        st = line.strip()
        if st.startswith("```"):
            flush(); block, start = [], None
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
        if st.startswith("<!--") and "-->" not in st:
            in_comment = True
        if in_comment:
            if "-->" in st:
                in_comment = False
            i += 1
            continue
        if re.match(r"^#{1,6}\s", st):
            flush(); block, start = [], None
            name = st.lstrip("#").strip()
            if st.startswith("## ") or st.startswith("# "):
                section = name
            if not SKIP_SECTIONS.match(section):
                out.append((ln, name, ln))              # a heading the reader sees
            i += 1
            continue
        if SKIP_SECTIONS.match(section):
            i += 1
            continue
        if not st or st == "---":
            flush(); block, start = [], None
        elif st.startswith("- ") or re.match(r"^\d+\.\s", st):
            flush(); block, start = [st], ln           # a list item is its own unit
            flush(); block, start = [], None
        else:
            if start is None:
                start = ln
            block.append(line)
        i += 1
    flush()
    return out


def fingerprint(text):
    return hashlib.sha256(re.sub(r"\s+", " ", text).strip().encode("utf-8")).hexdigest()[:16]


def log_path(path):
    return os.path.join(os.path.dirname(os.path.abspath(path)), LOG_NAME)


def read_log(path):
    lp = log_path(path)
    if not os.path.exists(lp):
        return None
    return json.load(open(lp, encoding="utf-8"))


def write_log(path, log):
    with open(log_path(path), "w", encoding="utf-8") as f:
        json.dump(log, f, indent=1, ensure_ascii=True)
        f.write("\n")


def hit_list(raw):
    """(line, section) for every scanner hit that has a line."""
    masked = mask(raw)
    out = []
    for sec, nm, pat, fl in REGEX_CHECKS:
        for m in re.finditer(pat, masked, fl):
            out.append((lineno(raw, m.start()), sec))
    out += [(h[2], h[0]) for h in structural(raw, masked) if h[2]]
    return out


def hit_lines(raw):
    """The line of every scanner hit that has one."""
    return [ln for ln, _ in hit_list(raw)]


def unit_hits(hits, ln, end):
    """The sections that fire inside one unit's lines."""
    return sorted(set(sec for h, sec in hits if ln <= h <= end))


def latest_read(entries, h):
    reads = [e for e in entries if e["hash"] == h and e["kind"] == "read"]
    return reads[-1] if reads else None


def unjudged(entry, secs):
    """The sections firing in a unit that its logged read never saw. A read records
    the sections it judged ("hits"). The unit's text is unchanged, so a section it
    did not record can only come from a check added after the read. An entry written
    without a "hits" field judged an unknown set, so any hit in it counts."""
    if entry is None or not secs:
        return []
    if "hits" not in entry:
        return list(secs)
    return [x for x in secs if x not in entry["hits"]]


def log_units(path, kind, note, lo=None, hi=None, today=None):
    """Record the units whose first line falls in lo..hi (all when None)."""
    raw = open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    log = read_log(path) or {"entries": []}
    if kind == "baseline":
        if any(e["file"] == name and e["kind"] == "baseline" for e in log["entries"]):
            return "refused: %s already has a baseline; it is allowed once" % name, 1
    elif not re.match(r"^read:\s*\S", note or ""):
        return "refused: the note must state what the reading found, starting 'read:' " \
               "(e.g. 'read: 0 findings' or 'read: 2 findings, echo repaired')", 1
    hits = hit_list(raw)
    mine = [e for e in log["entries"] if e["file"] == name]
    # A read supersedes a baseline: the baseline attests no read, so a unit resting on
    # it can still be read and logged. A read supersedes an earlier read only where a
    # check fires that the earlier read did not see; otherwise it is a repeat.
    known = set(e["hash"] for e in mine if kind == "baseline" or e["kind"] == "read")
    day = today or datetime.date.today().isoformat()
    added = 0
    for ln, text, end in units(raw):
        if lo is not None and not (lo <= ln <= hi):
            continue
        h = fingerprint(text)
        secs = unit_hits(hits, ln, end)
        if h in known and not (kind == "read" and unjudged(latest_read(mine, h), secs)):
            continue
        log["entries"].append({"file": name, "hash": h, "line": ln,
                               "first": " ".join(text.split()[:8]), "logged": day,
                               "kind": kind, "note": note,
                               "scan_hits_in_range": sum(1 for x, _ in hits
                                                         if lo is None or lo <= x <= hi),
                               "hits": secs})
        known.add(h)
        added += 1
    write_log(path, log)
    return "logged %d unit(s) of %s as %s" % (added, name, kind), 0


def check_log(path):
    """Every reader-facing unit must match a logged fingerprint."""
    raw = open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    log = read_log(path)
    if log is None or not any(e["file"] == name for e in log["entries"]):
        return ["no humanise log for %s: nothing has been recorded as humanised" % name], 2, 0
    entries = [e for e in log["entries"] if e["file"] == name]
    by_hash = {}
    for e in entries:                                   # a read outranks a baseline
        if e["kind"] == "read" or e["hash"] not in by_hash:
            by_hash[e["hash"]] = e
    hits = hit_list(raw)
    missing, baseline = [], 0
    for ln, text, end in units(raw):
        e = by_hash.get(fingerprint(text))
        if e is not None and e["kind"] == "read":
            new = unjudged(latest_read(entries, e["hash"]), unit_hits(hits, ln, end))
            if new:
                missing.append("line %d: UNJUDGED - %s fire(s) here and the logged read did not "
                               "record judging %s: %s" % (ln, ", ".join(new),
                               "it" if len(new) == 1 else "them", " ".join(text.split()[:10])))
            continue
        if e is None:
            missing.append("line %d: %s" % (ln, " ".join(text.split()[:12])))
        elif e["kind"] == "baseline":
            # A baseline attests that nobody has read the unit since the log began.
            # With no scanner hit in it that is a fair record of old prose; with a
            # hit it is an unjudged candidate that every later pass could wave
            # through as "predates this pass".
            n = sum(1 for h, _ in hits if ln <= h <= end)
            if n:
                missing.append("line %d: UNJUDGED - %d scanner hit(s) in a unit resting on the "
                               "baseline, never read: %s" % (ln, n, " ".join(text.split()[:10])))
            else:
                baseline += 1
    return missing, (1 if missing else 0), baseline


def log_selftest():
    import tempfile
    failures = 0
    d = tempfile.mkdtemp()
    p = os.path.join(d, "article.md")
    # Paragraphs long enough that no scanner check fires on the fixture itself: a
    # baseline unit carrying a hit fails the check.
    base = ("## title\n\nA title paragraph that runs long enough that no warm-up check fires.\n\n## body\n\nFirst paragraph here, which runs long enough that "
            "no warm-up check fires.\n\nSecond paragraph here.\n\n### A heading\n\nThird paragraph, "
            "which also runs long enough that no warm-up check fires.\n\n## references\n\n1. A row."
            "\n\n## notes\n\n1. AI\n")
    open(p, "w").write(base)

    def expect(label, got, want):
        nonlocal failures
        ok = got == want
        failures += not ok
        print("  %s  LOG    %-40s %s" % ("ok " if ok else "BAD", label, "" if ok else "got %r" % (got,)))

    expect("no log -> exit 2", check_log(p)[1], 2)
    expect("baseline logs", log_units(p, "baseline", "baseline: test")[1], 0)
    expect("baseline twice refused", log_units(p, "baseline", "baseline: again")[1], 1)
    expect("clean after baseline", check_log(p)[1], 0)
    open(p, "w").write(base.replace("Second paragraph here.", "Second paragraph, edited."))
    m, code, _ = check_log(p)
    expect("one edit -> one unit flagged", (code, len(m)), (1, 1))
    expect("note without 'read:' refused", log_units(p, "read", "done")[1], 1)
    expect("read note accepted", log_units(p, "read", "read: 0 findings", 9, 9)[1], 0)
    expect("clean after the read is logged", check_log(p)[1], 0)
    open(p, "w").write(base.replace("Second paragraph here.", "Second paragraph, edited.")
                       .replace("First paragraph here,", "First   paragraph\nhere,"))
    expect("whitespace-only change not flagged", check_log(p)[1], 0)
    open(p, "w").write(base.replace("1. A row.", "1. A changed row.").replace("1. AI", "1. ML")
                       .replace("Second paragraph here.", "Second paragraph, edited."))
    expect("references and notes not tracked", check_log(p)[1], 0)
    open(p, "w").write(base.replace("### A heading", "### A new heading")
                       .replace("Second paragraph here.", "Second paragraph, edited."))
    expect("a changed heading is flagged", check_log(p)[1], 1)
    # A baseline unit carrying a scanner hit is unjudged, and a read clears it.
    d2 = tempfile.mkdtemp()
    q = os.path.join(d2, "article.md")
    hit = ("## body\n\nA clean opening paragraph that says one thing and stops there.\n\n"
           "Version 3.0 was released in 2008. Support stopped in 2020. That is eleven years.\n")
    open(q, "w").write(hit)
    log_units(q, "baseline", "baseline: test")
    m, code, _ = check_log(q)
    expect("baseline unit with a hit -> unjudged", (code, len(m), "UNJUDGED" in (m or [""])[0]),
           (1, 1, True))
    expect("read over a baseline accepted", log_units(q, "read", "read: 1 finding, kept", 5, 5)[1], 0)
    expect("clean after the hit is judged", check_log(q)[1], 0)
    open(q, "w").write(hit.replace("That is eleven years.", "That is eleven years and a month."))
    expect("baseline without a hit stays clean", check_log(q)[:2] == (["line 5: Version 3.0 was "
           "released in 2008. Support stopped in 2020. That is"], 1), True)
    # A read records what it judged; a check that fires later is unjudged.
    log = read_log(q)
    for e in log["entries"]:
        if e["kind"] == "read":
            e["hits"] = []                  # as if the S31 check had not existed at the read
    write_log(q, log)
    open(q, "w").write(hit)
    m, code, _ = check_log(q)
    expect("a check added after the read -> unjudged", (code, "S31" in (m or [""])[0]), (1, True))
    expect("re-read over the stale read accepted", log_units(q, "read", "read: S31 kept", 5, 5)[1], 0)
    expect("clean once the new hit is judged", check_log(q)[1], 0)
    expect("a repeat read adds nothing", log_units(q, "read", "read: again", 5, 5)[0].startswith("logged 0"), True)
    log = read_log(q)
    for e in log["entries"]:
        e.pop("hits", None)                 # an entry written before hits were recorded
    write_log(q, log)
    expect("legacy read with a hit -> unjudged", check_log(q)[1], 1)
    return failures


# ---------------------------------------------------------------------------
# Voice readout. Information, never a hit: it changes no exit code and enters no
# log. Measured against a set of published human essays, machine drafts matched
# them on sentence length, its spread and reading ease, and differed on the six
# figures below. Nothing in the catalogue asks for any of them: every pattern in
# it is a prohibition, and a draft can clear all of them and still have nobody in
# it. The ranges are the median and the lowest and highest of the human essays,
# measured by this function.
# ---------------------------------------------------------------------------
# (label, unit, human median, human low, human high)
VOICE_RANGES = [
    ("sentences opening on And, But or So", "% of sentences", 9.3, 2.4, 20.3),
    ("first person singular (I, me, my)", "per 1,000 words", 11.1, 0.0, 25.2),
    ("contractions", "per 1,000 words", 21.2, 2.2, 55.2),
    ("figures", "per 1,000 words", 4.3, 0.5, 19.0),
    ("parentheses", "per 1,000 words", 2.4, 0.4, 7.7),
    ("questions", "per 1,000 words", 1.8, 0.0, 4.0),
]
VOICE_MIN_WORDS = 300
APOS = "['" + CURLY[1] + "]"


def voice(raw):
    """The six figures, over the writer's own body prose: quoted spans, code, links,
    headings and the references are left out.
    Returns None under VOICE_MIN_WORDS, where a rate per 1,000 words means little."""
    regions = region_map(raw)
    body = "\n".join(ln for ln, r in zip(raw.split("\n"), regions) if r == "body")
    body = re.sub(r"(?s)\A---\n.*?\n---\n", "", body)           # frontmatter
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)            # images
    body = re.sub(r"\[\[?\d+\]?\]\([^)]*\)", "", body)          # citation markers
    t = mask(body)
    t = re.sub(r"^\s*(?:#.*|[-*_]{3,}\s*)$", "", t, flags=re.M)   # headings, rules
    words = re.findall(r"[A-Za-z][A-Za-z" + CURLY[1] + r"'-]*", t)
    if len(words) < VOICE_MIN_WORDS:
        return None
    k = 1000.0 / len(words)
    sents = []
    for b in re.split(r"\n\s*\n", t):
        sents += split_sentences(re.sub(r"\s+", " ", b))
    opens = sum(1 for x in sents if re.match(r"[(*_]*(?:And|But|So)\b", x))
    return {
        "words": len(words),
        "values": [
            100.0 * opens / max(len(sents), 1),
            k * len(re.findall(r"\b(?:I|me|my|mine|myself)\b|\bI" + APOS + r"(?:m|ve|d|ll)\b", t)),
            k * len(re.findall(r"\b[A-Za-z]+" + APOS + r"(?:t|s|re|ve|ll|d|m)\b", t)),
            k * len(re.findall(r"(?<![\w.,])\d[\d,.]*%?", t)),
            k * t.count("("),
            k * t.count("?"),
        ],
        "straight": body.count('"'),
        "curly": body.count(LQUOTE) + body.count(RQUOTE),
    }


def print_voice(raw):
    v = voice(raw)
    print("VOICE READOUT - information only. Not a hit, not a score, and never a target.")
    if v is None:
        print("  under %d words of body prose: too short for a rate to mean anything.\n"
              % VOICE_MIN_WORDS)
        return
    print("  %d words of the writer's own body prose. Beside each figure: the median and"
          % v["words"])
    print("  the range measured across a set of published human essays.")
    for (label, unit, med, lo, hi), val in zip(VOICE_RANGES, v["values"]):
        where = "below every sample" if val < lo else "above every sample" if val > hi else ""
        print("    %5.1f   %-38s %-16s human %4.1f [%.1f to %.1f]  %s"
              % (val, label, unit, med, lo, hi, where))
    q = "straight %d, curly %d" % (v["straight"], v["curly"])
    if v["straight"] and v["curly"]:
        q += "  <- both styles in one piece; settle on one outside quotations"
    print("    quotation marks: " + q)
    print("  A figure outside the range is a question to ask of the draft: is anybody in it?")
    print("  It is never an instruction. Adding 'And' or 'I' to move a number makes a")
    print("  template, which is the defect this catalogue exists to remove. One of the human")
    print("  samples has no first person and almost no contractions, and it is as human as")
    print("  the rest.\n")


def voice_selftest():
    failures = 0
    def expect(name, got, want):
        nonlocal failures
        ok = got == want
        failures += not ok
        print("  %s  VOICE  %-40s %s" % ("ok " if ok else "BAD", name, "" if ok else "got %r" % (got,)))
    unit = ("I checked the figure twice. But it didn't move (not once). So what changed? "
            "The filing lists 40 sites. ")
    pad = "The plan holds as written and the team keeps to its dates. " * 30
    v = voice(unit + pad)
    n = v["words"]
    expect("short text returns nothing", voice("I think so. But why?"), None)
    expect("opening conjunctions counted", round(v["values"][0] * 35 / 100), 2)
    expect("first person counted", round(v["values"][1] * n / 1000), 1)
    expect("contractions counted", round(v["values"][2] * n / 1000), 1)
    expect("figures counted", round(v["values"][3] * n / 1000), 1)
    expect("parentheses counted", round(v["values"][4] * n / 1000), 1)
    expect("questions counted", round(v["values"][5] * n / 1000), 1)
    quoted = voice('He said "I didn\'t know, and I won\'t ask (ever)?" twice. ' + pad)
    expect("a source's words are not the writer's", [round(x) for x in quoted["values"][1:3]], [0, 0])
    refs = voice(pad + "\n\n## References\n\n1. I don't count (at all)? 1999.\n")
    expect("references are left out", [round(x) for x in refs["values"]], [0, 0, 0, 0, 0, 0])
    expect("readout raises no hit", [h for h in structural(unit + pad, mask(unit + pad))
                                     if h[0] in ("S19", "VOICE")], [])
    expect("curly quotes raise no hit",
           [n for s2, n, p2, f in REGEX_CHECKS if re.search(p2, CURLY[1] + " " + LQUOTE, f)], [])
    return failures



# ---------------------------------------------------------------------------
# STRUCTURE PROFILE. Seventeen patterns that live in the structure and rhythm of a
# whole piece rather than in any one sentence. Edited drafts no longer carry
# "delve"; they carry a "So" at the head of every conclusion, a five-word recap at
# the foot of every paragraph, and a "such as" after every abstract claim. No
# single instance is a tell. The count is.
#
# So the profile is per piece, never per unit. It counts, normalises to 2,000 words
# of the writer's own body prose, grades each pattern, and quotes every instance.
# It raises no hit, changes no exit code and enters no log: a rate is a property of
# the piece, and a unit-level read cannot judge it. The humanise report carries the
# table and a verdict (references/detection.md, The structure profile).
# ---------------------------------------------------------------------------
PROFILE_WINDOW = 2000      # words; the unit every rate is given in
PROFILE_MIN_WORDS = 800    # below this a rate per 2,000 words is two instances

PROFILE_NAMES = [
    (1, "'So' paragraph openers"),
    (2, "short recap closers (<10 words, ends a paragraph)"),
    (3, "three-part signposting (Start with / Then / Last)"),
    (4, "roadmap sentences (parallel parts listed ahead)"),
    (5, "second-person hooks (If you run / You may have)"),
    (6, "balanced contrast pairs (now/later, more/fewer)"),
    (7, "colon reveals (short label, then colon)"),
    (8, "repeated example phrase ('such as' every time)"),
    (9, "uniform source tags (Name, a <description>, verb)"),
    (10, "stacked institutional citations"),
    (11, "repeated key phrase across sections"),
    (12, "declarative headings (a claim, not a topic)"),
    (13, "built-in limits section / admitted inference"),
    (14, "templated list items (label. one-line reading.)"),
    (15, "escalating case walk-throughs (the harder case)"),
    (16, "unpunctuated image descriptions"),
    (17, "imperative close (orders in the last section)"),
]
# Measured over a set of twelve published human essays: median and highest count
# per 2,000 words, and how many of the twelve the grading calls strong. Where
# humans reach "strong", the pattern does not separate a person from a machine on
# its own and weighs only in a cluster.
# Pattern 10 counts organisations named as the source of a survey, report or
# study, and its figures were measured for that form over the same set.
PROFILE_HUMAN = {1: (0.0, 1.5, 0), 2: (2.8, 8.2, 6), 3: (0.0, 0.0, 0), 4: (0.0, 0.0, 0),
                 5: (0.5, 7.1, 1), 6: (0.3, 1.8, 0), 7: (0.5, 3.8, 1), 8: (0.5, 4.4, 1),
                 9: (0.0, 0.5, 0), 10: (0.0, 0.5, 0), 11: (0.0, 1.5, 1), 12: (0.0, 2.2, 1),
                 13: (0.0, 0.0, 0), 14: (0.0, 0.0, 0), 15: (0.0, 0.7, 0), 16: (0.0, 0.0, 0),
                 17: (0.9, 3.6, 3)}
# Patterns that weigh most when they appear together.
PROFILE_CORE = (1, 2, 6, 8)

PROFILE_END = re.compile(r"^#{1,3}\s*(references|sources?|bibliography|works cited|notes)\b",
                         re.I)
SEQ_MARK = re.compile(r"^(?:\*\*)?(Start with|Begin with|First(?:ly)?,|Second(?:ly)?,|Third(?:ly)?,"
                      r"|Then\b|Next,?|Last(?:ly)?,|Finally,|After that,)", re.I)
# Pattern 10: an organisation named as the source of a survey, report, study or
# estimate. Counted by distinct name, never by citation, so one source cited many
# times counts once.
FIRM_CITE = re.compile(r"\b([A-Z][\w&.-]*(?:\s+(?:&\s+)?[A-Z][\w&.-]*){0,3})(?:'s|’s)?\s+"
                       r"(?:(?:19|20)\d\d\s+|annual\s+|latest\s+|recent\s+|new\s+|global\s+)*"
                       r"(?:survey|report|study|analysis|estimate|forecast|benchmark|index|poll)s?\b")
FIRM_SKIP = {"The", "A", "An", "This", "That", "These", "Those", "Its", "Our", "Their", "His",
             "Her", "My", "Your", "One", "Each", "Every", "Another", "In", "On", "At", "For",
             "By", "From", "Some", "Any", "No", "Most", "Both", "If", "When", "Which", "What",
             "Whose", "And", "But", "So", "Yet", "Or", "Same", "First", "Second", "Last",
             "Next", "Earlier", "Later", "Recent", "New", "Annual", "Latest", "Global", "I",
             "Read", "See", "Take", "Every", "Such", "Many", "Several", "Two", "Three"}
CONTRAST_PAIRS = [
    (r"now|today|this year|this quarter|short[- ]term", r"later|tomorrow|next year|future|long[- ]term|eventually"),
    (r"more", r"fewer|less"), (r"faster|quicker", r"slower"), (r"higher|rises?", r"lower|falls?"),
    (r"saves?|gains?|wins?", r"costs?|loses?|pays?|trains fewer"),
    (r"cheaper", r"dearer|costlier|more expensive"), (r"keeps?", r"loses?|gives? up"),
]
REPORT_VERB = (r"(?:found|finds|said|says|told|tells|wrote|writes|reported|reports|estimated"
               r"|estimates|expects|expected|argued|argues|calls|called|puts|put|noted|notes"
               r"|warned|warns|claimed|claims|showed|shows|concluded|concludes|described"
               r"|describes|predicts|predicted|counted|counts|measured|measures)")
AUX = {"is", "are", "was", "were", "be", "been", "can", "can't", "cannot", "could", "will",
       "won't", "would", "doesn't", "don't", "does", "do", "did", "has", "have", "had", "must",
       "should", "never", "not", "isn't", "aren't", "wasn't"}
STOP = {"the", "a", "an", "of", "to", "in", "on", "and", "or", "for", "with", "that", "this",
        "it", "its", "by", "as", "at", "from", "be", "is", "are", "was", "were", "who", "what",
        "which", "they", "their", "them", "he", "she", "his", "her", "we", "you", "your", "i",
        "my", "our", "not", "no", "so", "but", "if", "then", "than", "there", "these", "those",
        "can", "can't", "will", "has", "have", "had", "do", "does", "did", "one", "each", "all"}
IMPERATIVE = (r"(?:List|Put|Mark|Check|Start|Ask|Find|Name|Write|Make|Pick|Choose|Look|Read"
              r"|Give|Set|Keep|Stop|Track|Measure|Map|Run|Build|Count|Decide|Draw|Agree"
              r"|Assign|Review|Test|Use|Try|Take|Tell|Add|Cut|Move|Open|Plan|Record|Remove"
              r"|Replace|Show|Sort|Treat|Watch|Begin|Audit|Identify|Define|Document|Hold|Get"
              r"|Do|Don't|Never|Always|Let|Consider|Avoid|Ensure|Require|Search|Compare|Note"
              r"|Go|Fix|Publish|Demand|Insist|Budget|Hire|Train|Rotate|Separate|Route)")
LIMITS_HEAD = re.compile(r"(limit|limitation|caveat|where (this|it|the \w+) (breaks|fails|falls|stops)"
                         r"|what (this|it|the \w+) (does not|doesn't|can't|cannot|won't)"
                         r"|what i (can't|cannot|don't|do not)|weak (points?|spots?)|open questions"
                         r"|what could (be wrong|go wrong)|what would change|blind spots?)", re.I)
INFERENCE = re.compile(r"\b(?:is|are|remains?) (?:my|an|our) (?:inference|guess|assumption|extrapolation)\b"
                       r"|\bI(?:'m| am) (?:inferring|extrapolating|guessing)\b|\bI infer\b"
                       r"|\bmy (?:own )?inference\b", re.I)


def profile_body(raw):
    """The writer's own body prose, cut at the references or the notes, front matter
    and comments removed. Returns (lines, start_line) so instances keep a line."""
    lines = raw.split("\n")
    i = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                i = j + 1
                break
    out = []
    for k in range(i, len(lines)):
        if PROFILE_END.match(lines[k].strip()):
            break
        out.append((k + 1, lines[k]))
    return out


def profile_units(body):
    """Paragraphs, headings and list runs, each with the line it starts on and the
    section heading above it."""
    paras, heads, lists, section = [], [], [], None
    buf, start, kind = [], 0, None

    def flush():
        nonlocal buf, kind
        if buf:
            text = "\n".join(x for _, x in buf)
            if kind == "list":
                lists.append((start, section, [x for _, x in buf]))
            else:
                paras.append((start, section, re.sub(r"\s+", " ", text).strip()))
        buf, kind = [], None

    in_code = False
    for ln, line in body:
        s = line.strip()
        if s.startswith("```"):          # fenced code is never the writer's prose
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        if not s:
            flush()
            continue
        if s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            section = s.lstrip("# ").strip()
            heads.append((ln, level, section))
            continue
        if s.startswith(("<!--", "|", "```", "---")) or s.startswith(">"):
            flush()
            continue
        is_item = bool(re.match(r"^(?:[-*+]|\d+\.)\s+", s))
        this = "list" if is_item else ("list" if kind == "list" and not is_item and buf and line.startswith(" ") else "para")
        if kind and this != kind:
            flush()
        if not buf:
            start, kind = ln, this
        buf.append((ln, s))
    flush()
    return paras, heads, lists


def strip_marks(s):
    s = re.sub(r"\[\[\d+\]\]\([^)]*\)", "", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return s


def profile(raw):
    body = profile_body(raw)
    paras, heads, lists = profile_units(body)
    title = heads[0][2] if heads and heads[0][1] == 1 else ""
    sec_heads = [h for h in heads if h[1] >= 2 and h[2].lower() != "content"]
    prose = [(ln, sec, p) for ln, sec, p in paras if not p.startswith("![")]
    images = [(ln, sec, p) for ln, sec, p in paras if p.startswith("![")]

    words_text = mask(" ".join(strip_marks(p) for _, _, p in prose) + " " +
                      " ".join(strip_marks(" ".join(it)) for _, _, it in lists))
    nwords = len(re.findall(r"[A-Za-z][A-Za-z'" + CURLY[1] + "-]*", words_text))
    found = {n: [] for n, _ in PROFILE_NAMES}

    def add(n, ln, quote):
        found[n].append((ln, re.sub(r"\s+", " ", quote).strip()[:110]))

    sent_cache = []
    for ln, sec, p in prose:
        m = mask(strip_marks(p))
        sent_cache.append((ln, sec, p, m, split_sentences(m)))

    # 1. So openers: the paragraph's first word is So.
    for ln, sec, p, m, S in sent_cache:
        if S and re.match(r"^[*_]*So\b[ ,]", S[0]):
            add(1, ln, S[0])

    # 2. Short recap closers: a paragraph of three or more sentences ending on one
    # under ten words. Two-sentence paragraphs are left alone: a short second
    # sentence there is the long-then-short cadence people write.
    for ln, sec, p, m, S in sent_cache:
        if len(S) >= 3:
            last = S[-1]
            n = len(last.split())
            if 0 < n < 10 and not last.rstrip().endswith("?") and not last.count(":"):
                add(2, ln, last)

    # 3. Three-part signposting: a heading naming three items, or two or more
    # consecutive paragraphs in one section opening on a sequence marker.
    for ln, level, h in sec_heads:
        if re.search(r"\w[\w\s'-]*,\s*[\w\s'-]+,?\s+(?:and|or)\s+\w", h) and h.count(",") >= 1:
            add(3, ln, "heading: " + h)
    run = []
    for ln, sec, p, m, S in sent_cache + [(0, None, "", "", [])]:
        hit = bool(S) and bool(SEQ_MARK.match(S[0]))
        if hit and (not run or run[-1][1] == sec):
            run.append((ln, sec, S[0]))
            continue
        if len(run) >= 2:
            for r in run:
                add(3, r[0], r[2])
        run = [(ln, sec, S[0])] if hit else []

    # 4. Roadmap sentences: three or more parallel parts, each opening on the same
    # word, listed in one sentence. Weighted to the opening, where it is a parts list.
    for idx, (ln, sec, p, m, S) in enumerate(sent_cache):
        for s in S:
            mm = re.search(r"\b(who|what|how|where|why|when|which|whether)\b[^,.;:]{3,70},\s+"
                           r"\1\b[^,.;:]{3,70},\s+(?:and\s+|or\s+)?\1\b", s, re.I)
            if mm:
                add(4, ln, ("[opening] " if idx < 2 else "") + s)

    # 5. Second-person hooks: a sentence opening by addressing the reader's role or
    # past. The repair S46 asks for (If you have ever...) is still this frame, and a
    # piece that uses it more than once has made it a habit.
    for idx, (ln, sec, p, m, S) in enumerate(sent_cache):
        for s in S:
            if re.match(r"^[*_]*(?:If|When|Whether|As) you(?:'re| are| run| lead| manage| work| have"
                        r"| own| build| hire| sit| use)\b|^[*_]*You(?:'ve| have| may have| might have"
                        r"| probably| already)\b|^[*_]*(?:For anyone|Anyone) who\b", s):
                add(5, ln, ("[opening] " if idx == 0 else "") + s)

    # 6. Balanced contrast pairs: both poles of one opposition in one sentence, or a
    # clause that affirms and a mirrored clause that denies by ellipsis.
    for ln, sec, p, m, S in sent_cache:
        for s in S:
            hit = False
            for a, b in CONTRAST_PAIRS:
                ma = re.search(r"\b(?:%s)\b" % a, s, re.I)
                mb = re.search(r"\b(?:%s)\b" % b, s, re.I)
                if ma and mb and abs(ma.start() - mb.start()) > 12:
                    hit = True
                    break
            if not hit and re.search(r"\b\w+s\b[^.;]{3,60}\b(?:and|but|while)\s+the\s+[^.;]{3,40}"
                                     r"\b(?:doesn't|does not|don't|do not|isn't|won't|can't|didn't)\s*[.,;]?$", s):
                hit = True
            if hit:
                add(6, ln, s)

    # 7. Colon reveals: a label of four words or fewer opens the sentence and a colon
    # hands over the point.
    for ln, sec, p, m, S in sent_cache:
        for s in S:
            mm = re.match(r"^[*_]*([A-Z][\w'" + CURLY[1] + r"-]*(?:\s+[\w'" + CURLY[1] + r"-]+){0,3})[*_]*:\s+\S", s)
            if mm and not re.search(r"\d", mm.group(1)):
                add(7, ln, s)

    # 8. Repeated example phrase: one introducer doing every example. Counted for the
    # most-used introducer, which is 'such as' in practice.
    intro = {}
    for ln, sec, p, m, S in sent_cache:
        for s in S:
            for k in re.findall(r"\b(such as|for example|for instance|e\.g\.|say,)\s", s, re.I):
                intro.setdefault(k.lower(), []).append((ln, s))
    for ln, sec, items in lists:
        for it in items:
            for k in re.findall(r"\b(such as|for example|for instance)\s", mask(it), re.I):
                intro.setdefault(k.lower(), []).append((ln, it))
    if intro:
        top = max(intro, key=lambda k: len(intro[k]))
        for ln, s in intro[top]:
            add(8, ln, s)

    # 9. Uniform source tags: Name, <description>, reporting verb.
    for ln, sec, p, m, S in sent_cache:
        for s in S:
            for mm in re.finditer(r"([A-Z][\w.&'-]*(?:\s+(?:of\s+)?[A-Z][\w.&'-]*){0,4}),\s+"
                                  r"(?:(?:a|an|the|its|his|her|their)\s+)?[a-z*][^,;.]{2,70},\s+"
                                  r"(?:\w+\s+){0,2}?" + REPORT_VERB + r"\b", s):
                add(9, ln, mm.group(0))

    # 10. Stacked institutional citations: distinct organisations named as the source
    # of a survey, report, study or estimate.
    firms = {}
    for ln, sec, p, m, S in sent_cache:
        for mm in FIRM_CITE.finditer(m):
            words = mm.group(1).split()
            while words and words[0] in FIRM_SKIP:
                words = words[1:]
            if words:
                firms.setdefault(" ".join(words), ln)
    for name, ln in sorted(firms.items(), key=lambda x: x[1]):
        add(10, ln, name)

    # 11. Repeated key phrase: a three-word phrase carrying a verb, returning in four
    # or more sections. A recurring noun term (the chief architect) is vocabulary;
    # a recurring predicate (can't be undone) is a slogan.
    grams = {}
    for ln, sec, p, m, S in sent_cache:
        toks = re.findall(r"[a-z][a-z'" + CURLY[1] + r"]*", m.lower().replace(CURLY[1], "'"))
        for i in range(len(toks) - 2):
            g = tuple(toks[i:i + 3])
            if not any(t in AUX for t in g):
                continue
            if not any(t not in STOP and len(t) > 3 for t in g):
                continue
            grams.setdefault(g, {}).setdefault(sec, ln)
    seen = []
    for g, secs in sorted(grams.items(), key=lambda x: -len(x[1])):
        if len(secs) < 3:
            break
        if any(len(set(g) & set(s)) >= 2 for s in seen):
            continue
        seen.append(g)
        add(11, min(secs.values()), "'%s' in %d sections" % (" ".join(g), len(secs)))

    # 12. Declarative headings: a heading that states a claim. A finite verb after a
    # one- or two-word subject; wh-headings and noun phrases are topics.
    for ln, level, h in sec_heads:
        w = re.findall(r"[A-Za-z'" + CURLY[1] + r"-]+", h)
        if len(w) < 3 or w[0].lower() in ("who", "what", "how", "where", "why", "when", "which",
                                          "whether", "if", "in", "on", "at", "for", "from"):
            continue
        det = w[0].lower() in ("the", "a", "an", "your", "every", "each", "most", "some", "no")
        vs = lambda t: bool(re.match(r"^[a-z]+(?<![su])s$", t))   # removes, hits; not class, status
        if w[1].lower() in AUX or (not det and vs(w[1]) and len(w) > 2) or \
           (det and (w[2].lower() in AUX or (vs(w[2]) and len(w) > 3))):
            add(12, ln, h)

    # 13. Built-in limits: a section that lists the piece's own weak points, counted
    # by its items, plus every inference the prose admits to.
    for ln, level, h in sec_heads:
        if LIMITS_HEAD.search(h):
            items = [x for x in paras if x[1] == h] + [(l2, s2, i) for l2, s2, its in lists
                                                      if s2 == h for i in its]
            add(13, ln, "section: %s (%d items)" % (h, len(items)))
            for x in items[1:]:
                add(13, x[0], x[2] if isinstance(x[2], str) else str(x[2]))
    for ln, sec, p, m, S in sent_cache:
        for s in S:
            if INFERENCE.search(s):
                add(13, ln, s)

    # 14. Templated list items: three or more items in a run, each a short label
    # sentence then a one-line reading. Bold-led paragraph runs count the same way.
    def labelled(t):
        t = re.sub(r"^(?:[-*+]|\d+\.)\s+", "", t.strip())
        mm = re.match(r"^(\*\*)?([^.!?:]{2,90}?[.!?:])(\*\*)?\s+\S", t)
        return bool(mm) and len(mm.group(2).split()) <= 12
    for ln, sec, items in lists:
        flags = [labelled(i) for i in items]
        if len(items) >= 3 and sum(flags) >= max(3, int(0.8 * len(items) + 0.5)):
            for i, f in zip(items, flags):
                if f:
                    add(14, ln, i)
    bold_run = []
    for ln, sec, p in prose + [(0, None, "")]:
        if p.startswith("**") and labelled(p):
            if bold_run and bold_run[-1][1] != sec:
                bold_run = []
            bold_run.append((ln, sec, p))
            continue
        if len(bold_run) >= 3:
            for b in bold_run:
                add(14, b[0], b[2])
        bold_run = []

    # 15. Escalating case walk-throughs: the text flags its step up.
    for ln, sec, p, m, S in sent_cache:
        for s in S:
            if re.search(r"\b(?:the|a|an)\s+(?:harder|hardest|tougher|toughest|trickier|trickiest"
                         r"|more difficult|most difficult|messier|easier|easiest|simplest|simpler"
                         r"|subtler)\s+(?:case|one|example|scenario|version|question|kind)\b"
                         r"|\b(?:harder|worse|trickier) still\b|\bit gets (?:harder|worse|trickier)\b", s, re.I):
                add(15, ln, s)

    # 16. Unpunctuated image descriptions: a long alt text, caption or accessible
    # reading that runs on without sentence ends.
    descs = []
    for ln, sec, p in images:
        mm = re.match(r"!\[([^\]]*)\]", p)
        if mm:
            descs.append((ln, mm.group(1)))
    for ln, line in body:
        mm = re.match(r"^\s*(?:[-*]\s+)?\*\*(?:caption|accessible reading|alt text)\.?\*\*:?\s*(.+)$", line, re.I)
        if mm:
            descs.append((ln, mm.group(1)))
    for ln, d in descs:
        w = len(d.split())
        ends = len(re.findall(r"[.!?](?=\s|$)", d))
        if w >= 35 and w / max(ends, 1) > 30:
            add(16, ln, "%d words, %d sentence end(s): %s" % (w, ends, d))

    # 17. Imperative close: orders in the last body section.
    if sent_cache:
        last_sec = sent_cache[-1][1]
        tail = [x for x in sent_cache if x[1] == last_sec]
        tail_lists = [(ln, it) for ln, s2, its in lists if s2 == last_sec for it in its]
        sents = [(ln, s) for ln, sec, p, m, S in tail for s in S] + \
                [(ln, re.sub(r"^(?:[-*+]|\d+\.)\s+[*_]*", "", mask(it))) for ln, it in tail_lists]
        for ln, s in sents:
            core = re.sub(r"^[*_]*(?:Then|And|Next|First|Finally|Now|So),?\s+", "", s)
            if re.match(r"^[*_]*" + IMPERATIVE + r"\b", core, re.I) and \
               not re.match(r"^[*_]*\w+\s+(?:is|are|was|were|has|have|of)\b", core):
                add(17, ln, s)

    return {"words": nwords, "found": found, "headings": len(sec_heads), "firms": firms}


def profile_human_signals(raw):
    """What points the other way: asides, questions, the writer present in the
    reasoning, and an uneven cadence. Quoted, so the verdict can cite them."""
    paras, heads, lists = profile_units(profile_body(raw))
    asides, quest, first, lens = [], [], [], []
    for ln, sec, p in paras:
        if p.startswith("!["):
            continue
        m = mask(strip_marks(p))
        for x in re.finditer(r"\(([^()]{8,160})\)", m):
            asides.append((ln, "(" + x.group(1) + ")"))
        for sn in split_sentences(m):
            lens.append(len(sn.split()))
            if sn.rstrip("*_ ").endswith("?"):
                quest.append((ln, sn))
            if re.search(r"\bI\b|\bI'(?:m|d|ve|ll)\b|\bmy\b", sn):
                first.append((ln, sn))
    spread = []
    if len(lens) > 5:
        mean = sum(lens) / len(lens)
        sd = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5
        spread = [(0, "sentence length %.0f +/- %.0f words, %d to %d" % (mean, sd, min(lens), max(lens)))]
    return [("parenthetical asides", asides), ("questions", quest),
            ("first person in the reasoning", first), ("cadence", spread)]


def profile_selftest():
    """Each pattern on the form it names, and silent on a near miss."""
    failures = 0
    filler = ("The team reviewed the plan at the spring meeting and kept most of it, though the "
              "budget line moved twice before anyone signed it off at the end of the quarter. ") * 60
    cases = [
        (1, "So the team has to choose. It waited a week.\n\nSo the vendor called again. Nobody answered.", True),
        (1, "The team has to choose, so it waited.\n\nThe vendor called again.", False),
        (3, "## Compression hits tasks, roles and seniority\n\nStart with tasks. One.\n\nThen roles. Two.", True),
        (6, "A CTO who cuts back saves money now and trains fewer specialists later.\n\nA CTO who "
            "cuts back saves money now and pays for it later.", True),
        (6, "The CTO cut the budget at the spring meeting.\n\nThe board agreed a month later.", False),
        (7, "My rule: whoever signs does not ship.\n\nThe short version: nobody owns it.", True),
        (7, "On 3 May: the release went out.\n\nThe board met.", False),
        (9, "Corvid Metrics, a software analytics firm, found more merges. Dana Whitlow, author of a "
            "book on release engineering, told Harrow Partners the same.", True),
        (10, "Corvid's 2024 survey found more merges. A Harrow Partners report said the same. The "
             "Tamsin Research study agreed.", True),
        (10, "The 2024 survey found more merges. Our report said the same.", False),
        (13, "## Where this breaks down\n\n**Checks miss judgement.** One.\n\n**Gates see one change.** "
             "Two.\n\nThat AI does the same is my inference.", True),
        (14, "- **Designs sent.** Each one waits.\n- **Exceptions granted.** Each one counts.\n"
             "- **Owners missing.** Each one is a gap.", True),
        (14, "- the design note\n- the infrastructure code\n- the application code", False),
        (15, "The harder case is a refusal. The hardest case is a reversal.", True),
        (17, "## Where to start\n\nList the decisions. Then mark the ones that need a signature. "
             "Check that no signer reports to the team.", True),
    ]
    for n, text, want in cases:
        raw = "# Title\n\n" + filler + "\n\n" + text + "\n"
        got = len(profile(raw)["found"][n]) >= 2
        ok = got == want
        failures += not ok
        print("  %s  P%-4d %-6s %s" % ("ok " if ok else "BAD", n, "fire" if want else "silent",
                                      text.replace("\n", " ")[:72]))
    short = profile("# T\n\nSo it goes. So it went.\n")
    ok = short["words"] < PROFILE_MIN_WORDS
    failures += not ok
    print("  %s  P-    short text is not graded" % ("ok " if ok else "BAD"))
    return failures


def profile_grade(n, items, words, headings):
    """Strength for one pattern. Never on one instance (the first rule of the profile)."""
    c = len(items)
    if n == 11 and items:   # sections the top phrase returns in, whatever the item count
        top = max(int(re.search(r"in (\d+) sections", q).group(1)) for _, q in items)
        return "strong" if top >= 4 else "moderate"
    if n == 4 and any(q.startswith("[opening]") for _, q in items):
        return "opening"    # a parts list in the opening is already a defect
    if c < 2:
        return "-"
    if n == 10:   # distinct firms
        return "strong" if c >= 3 else "weak"
    if n == 12:
        share = c / max(headings, 1)
        return "strong" if c >= 3 and share >= 0.5 else "moderate" if share >= 0.34 else "weak"
    if n in (16, 17):
        return "strong" if c >= 3 else "moderate"
    rate = c * PROFILE_WINDOW / max(words, 1)
    return "strong" if rate >= 3 else "moderate" if rate >= 2 else "weak"


def profile_rows(raw):
    p = profile(raw)
    rows = []
    for n, name in PROFILE_NAMES:
        items = p["found"][n]
        rows.append((n, name, len(items), profile_grade(n, items, p["words"], p["headings"]), items))
    return p, rows


def print_profile(raw, every=False):
    p, rows = profile_rows(raw)
    print("STRUCTURE PROFILE - per piece, never per unit. Not a hit, not a score.")
    if p["words"] < PROFILE_MIN_WORDS:
        print("  %d words of body prose: under %d, too few instances for a pattern to show.\n"
              % (p["words"], PROFILE_MIN_WORDS))
        return
    print("  %d words of body prose. Rate per 2,000 words; one instance is never graded."
          % p["words"])
    print("  %-3s %-50s %5s %6s  %-9s %s" % ("#", "pattern", "count", "/2000", "strength",
                                               "human med/max, strong in"))
    for n, name, c, g, items in rows:
        rate = c * PROFILE_WINDOW / max(p["words"], 1)
        med, hi, k = PROFILE_HUMAN[n]
        flag = "  <- above every human sample" if c >= 2 and rate > hi else ""
        print("  %-3d %-50s %5d %6.1f  %-9s %3.1f/%3.1f, %d of 12%s"
              % (n, name[:50], c, rate, g, med, hi, k, flag))
    core = [n for n, _, _, g, _ in rows if n in PROFILE_CORE and g in ("moderate", "strong")]
    print("  core cluster (1, 2, 6, 8 at moderate or above): %d of 4%s"
          % (len(core), "  <- the combination that weighs most" if len(core) >= 3 else ""))
    strong = [n for n, _, _, g, _ in rows if g == "strong"]
    beyond = [n for n, _, c, g, _ in rows
              if c >= 2 and c * PROFILE_WINDOW / max(p["words"], 1) > PROFILE_HUMAN[n][1]]
    print("  strong: %s" % (", ".join(str(n) for n in strong) or "none"))
    print("  above every human sample: %s" % (", ".join(str(n) for n in beyond) or "none"))
    print("")
    for n, name, c, g, items in rows:
        if c < 2 and not every:
            continue
        if g == "-" and not every:
            continue
        print("  %d. %s  [%s]" % (n, name, g))
        for ln, q in (items if every or g == "strong" else items[:3]):
            print("      line %d: %s" % (ln, q))
        if not (every or g == "strong") and len(items) > 3:
            print("      ... and %d more (--profile prints every instance)" % (len(items) - 3))
    print("")
    sig = profile_human_signals(raw)
    print("  HUMAN SIGNALS (quoted; the counterweight to the patterns):")
    for label, qs in sig:
        print("    %-34s %d" % (label, len(qs)))
        for ln, q in qs[:2]:
            print("        line %d: %s" % (ln, q))
    print("")
    print("  Calibration (references/detection.md, The structure profile): several of these")
    print("  fire on published human essays too. The weight is in the cluster and in a")
    print("  device that has become the piece's habit, never in a count on its own.\n")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    if sys.argv[1] == "--selftest":
        r = selftest()
        lf = log_selftest()
        print("log self-test: %s" % ("PASS" if not lf else "%d FAILURE(S)" % lf))
        vf = voice_selftest()
        print("voice self-test: %s" % ("PASS" if not vf else "%d FAILURE(S)" % vf))
        pf = profile_selftest()
        print("profile self-test: %s" % ("PASS" if not pf else "%d FAILURE(S)" % pf))
        return 1 if (r or lf or vf or pf) else 0
    if sys.argv[1] in ("--log", "--baseline", "--check-log"):
        if len(sys.argv) < 3 or not os.path.exists(sys.argv[2]):
            print("usage: scan.py --check-log <file.md>\n"
                  "       scan.py --log <file.md> --lines A-B --note 'read: <what the reading found>'\n"
                  "       scan.py --log <file.md> --all --note 'read: ...'\n"
                  "       scan.py --baseline <file.md> --note 'baseline: <why>'")
            return 2
        path = sys.argv[2]
        if sys.argv[1] == "--check-log":
            missing, code, baseline = check_log(path)
            if code == 2:
                print(missing[0])
            elif missing:
                print("NOT HUMANISED: %d unit(s) changed or added since their last logged pass,"
                      " or carrying a scanner hit nobody has judged:" % len(missing))
                for m in missing:
                    print("  " + m)
            else:
                print("humanise log: every reader-facing unit is logged"
                      + (" (%d by the one-time baseline, not by a read)" % baseline if baseline else ""))
            return code
        note = sys.argv[sys.argv.index("--note") + 1] if "--note" in sys.argv else ""
        lo = hi = None
        if sys.argv[1] == "--log":
            if "--lines" in sys.argv:
                lo, hi = [int(x) for x in sys.argv[sys.argv.index("--lines") + 1].split("-")]
            elif "--all" not in sys.argv:
                print("say which units were read: --lines A-B, or --all")
                return 2
        msg, code = log_units(path, "baseline" if sys.argv[1] == "--baseline" else "read",
                              note, lo, hi)
        print(msg)
        return code
    path = sys.argv[1]
    quiet = "--quiet" in sys.argv
    if not os.path.exists(path):
        print("no such file: " + path)
        return 2
    raw = open(path, encoding="utf-8").read()
    masked = mask(raw)

    regions = region_map(raw)
    hits = []
    for sec, name, pat, flags in REGEX_CHECKS:
        for m in re.finditer(pat, masked, flags):
            ln = lineno(raw, m.start())
            hits.append((sec, name, ln, "[" + region_at(regions, ln) + "] " + ctx(raw, m.start())))
    hits += structural(raw, masked)

    sections = sorted(set(s for s, _, _, _ in REGEX_CHECKS))
    print("humanise-scan  ::  " + path)
    print("%d regex checks over %d catalogue sections, plus the structural checks."
          % (len(REGEX_CHECKS), len(sections)))
    print("Quoted spans, code, URLs and link targets masked before scanning.\n")

    if not hits:
        print("NO HITS.\n")
    else:
        by = {}
        for sec, name, ln, c in hits:
            by.setdefault((sec, name), []).append((ln, c))
        print("%d HIT(S):\n" % len(hits))
        for (sec, name), items in sorted(by.items()):
            print("  %s  %s  (%d)" % (sec, name, len(items)))
            for ln, c in items[:6]:
                print("      line %d: %s" % (ln, c) if ln else "      " + c)
            if len(items) > 6:
                print("      ... and %d more" % (len(items) - 6))
            print()

    print_voice(raw)
    print_profile(raw, every="--profile" in sys.argv)

    if not quiet:
        print("NOT CHECKED MECHANICALLY - these need a human read:")
        for sec, name, why in NOT_CHECKED:
            print("  %-5s %s" % (sec, name))
            print("        " + why)
        print("\nA hit is a candidate, never a verdict. S10 and S31 in particular fire on")
        print("deliberate devices: anaphora carrying three different ideas, and a run of")
        print("short sentences somebody meant. Judge each one.")
        print("")
        print("WHAT A LOW COUNT DOES NOT MEAN. Over a small set of published articles, the")
        print("two densest files by hits per 1,000 words were among the most read, and the")
        print("least read sat between them. This scanner has NO demonstrated power to")
        print("separate a piece that will be read from one that will not. It measures")
        print("conformance to a prose catalogue. Treating a low count as evidence of")
        print("quality inverts the only evidence there is.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())

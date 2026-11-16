# Structure: outline, scan layer, scope

Character and section counts here are this skill's defaults, not rules of any platform (`sources.md`). Length is judged against the thesis, never counted against a target.

## Thesis
- One sentence, a claim: "Rerunning a load is safe when the table has a natural key and the insert is an UPSERT."
- Not a topic ("UPSERT in SQLite"), not a promise ("everything about UPSERT"), not two claims joined by "and".
- Test: could a reader with experience disagree, or do something differently tomorrow? No → sharpen it.

## Outline per post type
Every type: summary paragraph first, `Takeaways` last, a limits section before the takeaways.

| Type | Sections, in order | Evidence each needs |
|---|---|---|
| Tutorial | problem in one concrete case · what you need (versions) · steps, one result each · check that it worked · limits · takeaways | code that runs top to bottom; output after each step |
| Explainer | the question · the model in one figure · how it works, part by part · where the model breaks · takeaways | figure; small experiment or source per part |
| Lessons learned | what was built, in 3 lines · what went wrong (symptom, cause) · what changed · result with numbers · what still hurts · takeaways | numbers with setup; before/after code or config |
| Comparison | the decision and who faces it · criteria and why these · A and B per criterion (table) · when A, when B · what was not tested · takeaways | same test for both sides; versions of both |

- 3-6 `##` sections between summary and takeaways. More → the thesis is too wide.
- One point per section. Order: the order the reader needs it, not the order it was discovered.
- `###` only inside a section with 3 or more parallel parts (steps, options).
- Prerequisites as a list with versions, not a paragraph.
- Limits section: versions tested, cases not covered, when to do something else. Missing limits read as overclaiming.

## Scan layer
A reader who reads only title, summary, headings, figure captions and takeaways gets the thesis and the steps.

| Element | Rule |
|---|---|
| Title | States the outcome or the claim in the reader's words, or opens with an accurate hook that the post keeps ("Run it twice, get the same rows"), never a riddle or a question the post does not answer; 70 characters or fewer; the main term early; sentence case. Matches what the post proves - no wider. Patterns: "Make X do Y with Z" · "Why X fails when Y" · "X or Y for Z: what we measured". No "ultimate", "complete guide", "you need to know", no unkept numbers, no clickbait question. |
| Description | 70-160 characters; the case and the result; not a copy of the title; no keyword list. |
| Summary paragraph | Directly under the title. Its first sentence is the thesis (the lede); then the problem and what the post shows, nothing else. The answer is in it - no teaser. |
| Headings | Sentence case; state the point ("Give the table a natural key"), not the kind of content ("Background", "Implementation", "Overview"); no end punctuation; unique; no skipped levels; code font for code terms. |
| Lists | Numbered for steps in sequence, bullets for parallel items, table for comparison on the same attributes. |
| Takeaways | 3-5 bullets. Each a rule with its condition ("Use X when Y"), not a recap of sections ("We looked at X"). Nothing new that the post did not show. No sign-off, no call to subscribe. |

Title check: write 3 candidates, pick the one that is true if the reader stops after it.

## Scope
| Scope | Fits |
|---|---|
| Focused | one technique, one example |
| Standard | a tutorial of a few steps, an explainer of one mechanism |
| Deep | a comparison with measurements, lessons learned with history |

- The post is as long as the thesis needs within its scope: every section earns its place, nothing is padded. The script shows the reading time; it is information, not a target.
- Too long for the thesis → cut sections, not sentences everywhere. Too short → the thesis needs less, say so; never pad.
- Code share: a tutorial shows every line the reader must type; other types show only the lines the point is about and link the rest (`_code/<slug>/`).

## Openings and endings
- Open with the thesis, the concrete problem or the result: "A load job that runs twice inserts every row twice." Not with history, a definition, a trend or a question. A hook belongs in the title, never in place of the first sentence's point.
- No "what we will cover" paragraph when the headings already say it.
- End with `Takeaways`. No conclusion paragraph that repeats the summary.

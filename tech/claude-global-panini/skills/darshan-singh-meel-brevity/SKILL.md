---
name: darshan-singh-meel-brevity
description: Shared base for writing that gives the reader the most value in the least time, short but never shallow - a plain title that states the point, a one-sentence lede (verdict, answer, decision or result), why it matters to this reader, then detail in layers so skimmers stop early and deep readers continue. Sets format rules (short paragraphs, bullets, bold only on the point, active verbs, plain words, a diagram where it replaces text), where the lede goes per output kind, the first-line test and the cut test, plus a heuristic checker for .md and .html. Load alongside any skill that writes docs, reports, reviews, briefs, tech summaries, blog posts, SME answers, notebook notes, prototype notes, knowledge-graph answers, chat replies or school material. Triggers - "smart brevity", "lead with the point", "too long", "make it shorter", "get to the point", "bottom line first", "kürzer", "auf den Punkt", "zu lang", "kürzer fassen", "das Wichtigste zuerst".
---

# Brevity (base)

Every text Claude produces opens with its point and carries only words the reader needs. Other skills load this one alongside and keep one pointer line to it; they never copy its text.

## When to use
- Anything textual: docs (v1, v2, v3, tech summary), code reviews and review-v2, architecture reviews, requirements briefs, blog posts and articles, SME answers, notebook notes, prototype `NOTES.md`, knowledge-graph answers, chat replies, school material and its reviews.
- Before writing: name the reader and the one thing they take away. That thing becomes the lede.

## The four parts
1. **Title** - plain, says the point or the subject exactly. No clickbait, no puns, no riddles. Exception: a tech blog post or article may open with a hook, as long as the hook is accurate.
2. **Lede** - a single sentence first (a shape, not a length limit): what the reader must remember if they read nothing else. A verdict, an answer, a decision or a result, never a description of the document. A one-line metadata subtitle (stack · schedule · source → outputs) may sit between the title and the lede, as the docs-v2 and v3 builders render it.
3. **Why it matters** - right after the lede, briefly: why this reader should care, what changes for them. Leave it out when the lede already makes that obvious.
4. **Go deeper** - the detail in layers below: sections, per-file detail, `path:line`, links to local files. Each layer works on its own; a reader can stop after any of them.

## Format
- Short paragraphs of a few sentences, then bullets.
- Bold only the phrase that carries the point, not whole sentences, not labels.
- Active verbs, plain words. Explain a term once, where it first appears.
- A diagram where it explains better than a paragraph (built with `darshan-singh-meel-diagrams`). Few diagrams, each to the point.
- Signpost labels ("Why it matters", "Go deeper", "Bottom line") only when the text after them carries a fact. Never as boilerplate headings.
- Length is judged, never counted. No rule, template or reply sets a word, line, sentence or paragraph length for our own prose; builders may keep internal caps for a WARN whose text names the long passage, never the number.
- Not length rules, so they stay: "one sentence" as the shape of a lede; counts of items (findings, steps, examples); code snippet and diagram fit; character limits an outside system sets (search-result titles); text sizes and sentence lengths that a curriculum, an exam format or a learner level sets for school and DaF material.

## Where the lede goes, per output kind
| Output | Lede (first line under the title) | Go deeper |
|---|---|---|
| Doc - Overview | what the system does and for whom | parts, main flow diagram, where to start |
| Doc - Technical | how it works in one sentence: the main mechanism | components, flows, data model, config, deploy, ops, tests - full depth |
| Doc - User guide | what the reader can do with it and the first step | tasks step by step, errors and fixes |
| Runbook | what this fixes and the first action to take | numbered steps, checks, rollback, escalation - nothing cut |
| KT | what the receiver will own and the riskiest part | areas, contacts, open work, history |
| Code review / review-v2 report | verdict plus the finding that decides it | Must / Should lists, per-file detail with `path:line` |
| Architecture review | the recommended target and its main gain | current state, problems with evidence, target, impact, migration |
| Requirements brief | what is asked, in one sentence, and the biggest gap | data, flows, gaps, options, work items |
| Tech summary | what it is and the main risk or strength | components, flows, data model, stack, deploy, risks |
| Blog post / article | an accurate hook, then the claim the post proves | argument, code, diagrams, caveats |
| SME answer (Snowflake, Databricks, dbt) | the answer or the number, with its unit | query, how to read the result, pitfalls |
| Knowledge-graph answer | the direct answer | path through the graph, `path:line`, sources used |
| Notebook note | what this cell checks and what result means trouble | the query, its output, the reading |
| Prototype `NOTES.md` | the answer to the design question | what was tried, results, limits, next step |
| Chat reply | the result or answer | only the details needed to act; then the global end-of-reply sections |
| School lesson plan | the lesson goal (what students can do afterwards) | phases, material, differentiation |
| School worksheet | task text stays a task; the teacher note opens with the goal | tasks, hints, solution |
| School solution / Erwartungshorizont | the expected core result per task | steps, scoring, accepted variants |
| School material review | verdict plus the deciding finding | Must / Should / Other |

## Two tests before finishing
- **First-line test** - read only the title and the first sentence. Does the reader know the point? No → rewrite the lede.
- **Cut test** - remove each sentence in turn. Does the reader lose a fact or an instruction? No → cut it. Yes → keep it, however long the text gets.

## What not to do
- Clickbait, cryptic or jokey titles (a tech blog hook is fine when accurate).
- Openings that describe the text: "This document describes", "In this report", "Introduction", "Overview of".
- Burying the point after background, history or method.
- Filler: "it is important to note", "basically", "in order to", "as mentioned above", "grundsätzlich", "im Folgenden", "es ist wichtig zu erwähnen".
- Repeating the lede as a closing summary or a second "Summary" block. In a chat reply the opening result is the summary the global end-of-reply order asks for; the end adds only what changed after it.
- Word, line or sentence length targets for our own prose.
- **Shallow cuts** - removing depth the reader needs. Runbooks, Technical docs, KT and architecture evidence keep every step, value and `path:line`; brevity shortens each sentence and the top layer, never the content.
- Overriding the global rules: author voice, no chat in output, the end-of-reply order (summary, Self-check, Other findings, `Skills:` line) stay and win.

## Checker
- `python scripts/check_brevity.py <file-or-folder> [--strict]` - heuristic advice for `.md` and `.html`: missing lede, a lede of only history or method above a verdict (buried point), filler phrases (EN and DE, one line per block), very long paragraphs, duplicated summary blocks.
- Prints `BREVITY <file> | <issue> | <text>`; exit 0 unless `--strict` and something was found. It is advice: the writer decides.
- Reviewers use `references/checks.md` for what to check and how severe it is.
- Before/after pairs: `references/examples/`.
- Tests: `python tests/run.py`.

# Brevity checks for reviewers

Review skills apply these to the material they review. Each finding goes in the review's Must / Should / Other list as what · why · fix.

## What to check
| Check | Look for | Severity |
|---|---|---|
| Lede says the point | The first sentence under the title gives the verdict, answer, decision or result; a one-line metadata subtitle (stack · schedule · source → outputs) between title and lede is fine, as the docs-v2 and v3 builders render it | Missing or buried lede in a doc or report: **Should** |
| Lede is true | The lede matches the body: same verdict, same number, same recommendation | Misleading lede (contradicts or overstates the body): **Must** |
| Title | Plain and exact; a tech blog hook only if accurate | Clickbait or a misleading title: **Must**; vague title: **Should** |
| Why it matters | Present where the reader cannot see the consequence from the lede alone | Missing where needed: **Should**; present as empty boilerplate: **Other** |
| Top layer works alone | Title, lede and the first section let a skimmer act without reading further | Skimmer cannot act: **Should** |
| Buried point | The key fact sits after background, history or method | **Should** |
| Wall of text | A long paragraph that should be bullets, a table or a diagram | **Should** in docs and reports; **Other** elsewhere |
| Filler phrases | Words that carry no fact or instruction (cut test) | **Other**; **Should** when frequent enough to slow reading |
| Duplicate summaries | The lede repeated as a closing summary, or two summary blocks | **Other** |
| Diagram missing | A paragraph that describes a flow, structure or comparison a diagram would show faster | **Should** when the paragraph is hard to follow; **Other** otherwise |
| Signpost boilerplate | "Why it matters" / "Go deeper" labels with nothing factual after them | **Other** |
| Word counts | A template, rule or text that sets a word, line, sentence or paragraph length for our own prose. Not a finding: "one sentence" as the lede's shape, item counts, code and diagram fit, outside character limits, and text sizes a curriculum, exam format or learner level sets | **Should** |
| Shallow cut | Steps, values, evidence or `path:line` removed for shortness where the reader needs them | **Must** in runbooks and architecture evidence; **Should** elsewhere |

## How to check
- Run `python scripts/check_brevity.py <path>` first; treat each line as a lead to judge, not a finding.
- Do the first-line test and the cut test on the opening and on each section's first paragraph.
- Never flag task text in a school worksheet for a missing lede; the lede rule applies to teacher-facing parts.
- Never flag a missing lede in data files, code, or generated tables.

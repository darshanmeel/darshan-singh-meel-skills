# Review checklist for a technical blog post

Used by `darshan-singh-meel-tech-blog-review` (all columns) and by step 10 of the writer's process (Must column). Judge against the brief comment in the post: reader, goal, thesis, type, words.

| # | Area | Check | Must when |
|---|---|---|---|
| 1 | Code runs | every block rerun from the post's own text in a clean folder; exit code 0; quoted output equals real output; versions in the post equal the versions that ran; a reader following the steps top to bottom gets the result | a block fails, or prints something else than the post shows; a step is missing so the tutorial cannot be followed; a not-run block is presented as tested |
| 2 | Code quality | smallest example that shows the point; no secrets, real names or real data; no unsafe pattern shown as normal (SQL built by string concatenation, disabled TLS checks, `chmod 777`, broad IAM); no deprecated API without a note; errors the reader will hit are mentioned | a secret or real personal data; an unsafe pattern the reader would copy |
| 3 | Claims | every checkable statement listed and read on the official page: versions, dates, defaults, limits, syntax, behaviour, "faster/cheaper"; link goes to the page that says it; version scope stated; numbers carry their setup | a claim is wrong; a number has no source and no measurement; a benchmark without setup; a link that does not support the sentence |
| 4 | Thesis and scope | one thesis; every section supports it; the post proves it within its own limits section; no second topic | the post does not prove its thesis; conclusions wider than the evidence |
| 5 | Title honesty | title, description and summary promise exactly what the post delivers: same scope, same tool and version, same strength ("faster" needs the number; "how to" needs working steps; "why" needs the cause) | the title promises something the post does not deliver |
| 6 | Structure | summary gives the answer; headings state points and work as an outline alone; order follows the reader's need; one point per section; prerequisites with versions; limits section; `Takeaways` are rules, with nothing new | no summary or no takeaways; a reader cannot find the steps; sections in an order that breaks understanding |
| 7 | Clarity for the reader | terms defined for the reader in the brief and used consistently; no step assumes unstated knowledge; no ambiguous "this/it"; each code block introduced and its output explained; nothing explained that this reader already knows at length | the stated reader cannot follow a required step |
| 8 | Style and slop | `style.md`: active voice, second person, present tense; no hype, filler, scene-setting, announcing, false contrasts, recap endings; adjectives backed by facts; sentence and paragraph length; no exclamation marks, emoji, em-dash chains; author's voice: no trace of the drafting chat ("as discussed", "as you requested", "the user", "Claude", open points addressed to a requester), open points stated as facts ("not tested on PostgreSQL yet") | hype or filler in title, summary or takeaways; a `BANNED` phrase anywhere |
| 9 | Length fit | word count within the brief's range; each section's length matches its weight for the thesis; nothing padded, nothing essential missing; code share fits the type | more than 25 % outside the range without a reason |
| 10 | Figures | each figure explains something prose could not do shorter; referred to in the text; same names as text and code; renders; readable; alt text or a caption sentence states the content; no fact only in the figure | a figure shows something false or contradicts the text; a figure does not render |
| 11 | Links and form | front matter and brief complete; slug rule; descriptive link text; no dead local targets; fence languages; code wrapped at 80; no placeholders; no machine paths; HTML (if any) self-contained and equal to the Markdown | placeholder left; dead local target; HTML differs from the Markdown |
| 12 | Originality and privacy | no copied passages, code or figures beyond a short quoted line with a link; no employer, client, colleague or internal system names; synthetic examples | copied protected content; private or confidential information, including content from the drafting chat |

## Severity
| Level | Meaning |
|---|---|
| Must | wrong, not reproducible, misleading, unsafe, or breaks a "Must when" above - fix before publishing |
| Should | correct but weakens the post: unclear, padded, off-style, weak structure, a trace of the drafting chat (Must when it misstates a fact or exposes private chat content) |
| Other | optional polish; at most 5, only if worth knowing |

- Every finding: place (line or heading, quoted words) · what · why · fix (the rewritten sentence, the corrected value, the missing step).
- No finding without evidence: the failing command and its output, the official page and what it says, the quoted phrase.
- A `?` line of the script is a finding only after reading it in context.
- No praise section, no summary of the post, no taste-only remarks.

## Verdict
| Verdict | When |
|---|---|
| Publish | no Must |
| Publish after Must fixes | 1-3 Must, each fixable without changing the thesis or the outline |
| Rework | more than 3 Must, or a Must in area 1, 3, 4 or 5 that changes what the post can claim |

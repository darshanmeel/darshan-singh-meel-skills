---
name: darshan-singh-meel-tech-blog-review
description: Reviewer for English technical blog posts (software, data engineering, cloud, AI) - reruns every code block from the post's own text, re-reads every claim and version on the official page, and checks thesis, title honesty, structure, clarity for the stated reader, AI slop and style, length fit, figures and links; writes reviews/tech-blog-review-<date>.md with a verdict and Must / Should / Other findings (what, why, fix). Reviews, does not rewrite. Use when asked to review, check, fact-check or proofread a technical blog post or article, or after darshan-singh-meel-tech-blog wrote one. Triggers - "review my blog post", "check this article", "fact-check the post", "is this post ready to publish", "does the code in my post run", "is this post AI slop"; "Blogartikel prüfen", "Blogbeitrag reviewen", "Artikel gegenlesen". Not for code review (darshan-singh-meel-review) and not for writing the post (darshan-singh-meel-tech-blog).
context: fork
argument-hint: [blog/<slug>.md]
---

# Technical blog post review

Find what would embarrass the author after publishing: code that does not run, facts that are wrong, a title the post does not keep, text nobody needs. Global rules in CLAUDE.md apply. Loads `darshan-singh-meel-tech-blog` for its checklist, style list and script; `<blog skill dir>` below is that skill's folder.

## Rules
- **Independent.** `context: fork` runs this skill in a subagent that gets this file and the arguments, not the session that wrote the post. Trust nothing the post or its `_code/` folder says about itself: rerun, re-read.
- **Run the code from the post's text**, not from `_code/`: readers copy from the post.
- **Official pages only** for facts (CLAUDE.md network rule): the product's docs, release notes, the standard, the paper. Nothing private in a request - search for the feature, never paste the post's text.
- **Evidence per finding:** the command and its output, the page and what it says, or the quoted words. No evidence → a question under "Not checked", not a finding.
- **Review, not rewrite.** Fixes are proposed in the report; files change only when the user asks (arguments say "fix", or a later request). Then: fix, rerun steps 2-3, add a "Fixed" line per finding.
- **Never execute** anything that touches real systems, real data, paid services or the network beyond package indexes the user approved; mark as not run with the reason.
- **Brief, not gentle.** No praise section, no summary of the post, no taste-only findings.

## Process (fixed)
1. **Scope** - the post in the arguments (`$ARGUMENTS`), else the newest `blog/*.md`. Read its brief comment (reader, goal, thesis, type, words). No brief → one AskUserQuestion prompt: reader · intended length; recommended first. Cannot ask (forked run) → reader = practitioner who uses the tool daily, length = as written; say so in the report.
2. **Script** - `python <blog skill dir>/scripts/blog_post.py blog/<slug>.md --run`. Every `FAIL` is a Must candidate; every `?` is read in context.
3. **Rerun the code** - `python <blog skill dir>/scripts/blog_post.py blog/<slug>.md --extract <temp dir>/<slug>`, then in that folder:
   - assemble the blocks the way a reader would (same file when the post says so, in order) and run them with the versions the post names; record command, version, exit code;
   - compare real output with every quoted output block, character by character where the post shows it verbatim (line endings aside: redirected output on Windows ends lines with CRLF);
   - tutorial: follow the steps top to bottom using nothing but the post;
   - `not-run` blocks: check the syntax against the official reference and that the prose admits it was not run.
4. **Claims** - list every checkable statement (`references/format.md`, claim table). Open the linked page: does it say this, for this version? No link → find the official page. Mark each `confirmed` · `wrong` · `not supported by the link` · `unsourced` · `not checked`.
5. **Read as the reader** in the brief, once, top to bottom, only title + summary + headings + takeaways first: is the thesis there, is the title kept? Then the full text.
6. **Checklist** - walk areas 1-12 of `<blog skill dir>/references/review.md`; style against `references/style.md` of that skill.
7. **Figures and HTML** - render or open every figure; compare `blog/<slug>.html` (if present) with the Markdown: rebuild with `--html` into a copy and diff.
8. **Report** - `reviews/tech-blog-review-<YYYY-MM-DD-HHMM>.md` from `references/format.md`; add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, the Must lines, report path.

## Specific checks beyond the checklist
- **Title test:** state in one sentence what the title promises; find the paragraph that delivers it. Not found, or delivered for a narrower case → Must (area 5).
- **Thesis test:** delete each section in turn - does the thesis still stand? Yes → the section is a Should (cut).
- **Number test:** every number in the prose traced to an output file, a measurement with setup, or a linked page. Derived numbers (differences, ratios, counts, percentages): recompute from the values shown.
- **Version test:** versions named in the post = versions that ran in step 3 = versions the cited pages describe.
- **Copy-paste test:** blocks contain no prompts, no line numbers, no smart quotes, no tabs mixed with spaces; a block that depends on an earlier one says so.
- **Slop test:** read the first sentence of every paragraph and the last sentence of every section; cut candidates are openers that set a scene and closers that state a moral.
- **Voice test:** the post reads as the author's; any trace of the drafting chat ("as discussed", "the user", "Claude", open points addressed to a requester) → Should (area 8); Must when it misstates a fact or exposes private chat content (area 12).
- **Safety test:** would a reader who copies this into production be harmed (injection, leaked secret, data loss without a warning, cost surprise)? → Must (area 2).

## References
| File | Read when |
|---|---|
| `<blog skill dir>/references/review.md` | always: checklist, severity, verdict |
| `<blog skill dir>/references/style.md`, `structure.md`, `evidence.md`, `diagrams.md` | the areas the post touches |
| `references/format.md` | step 4 and step 8: claim table, report format |

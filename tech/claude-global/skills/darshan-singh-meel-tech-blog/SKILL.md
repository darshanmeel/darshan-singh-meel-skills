---
name: darshan-singh-meel-tech-blog
description: Technical writer for English technical blog posts on software, data engineering, cloud and AI - fixed process (reader and goal, one-sentence thesis, outline, code run before it is quoted, every claim and version from official docs, a diagram where it explains, title + summary + headings for scanning, takeaways), plain style without fluff, hype or AI slop, checked by a script. Writes blog/<slug>.md (+ optional self-contained .html) with the tested code in blog/_code/<slug>/. Use when asked to write, draft, outline, rewrite or tighten a technical blog post, tutorial, explainer, lessons-learned or comparison article. Triggers - "write a blog post about", "technical blog", "tech article", "tutorial post", "draft a post", "turn this into a blog post", "tighten my post", "blog outline"; "Blogartikel schreiben", "technischer Blogbeitrag", "Tech-Blog", "Artikel über". Not for project documentation (darshan-singh-meel-docs) and not for reviewing a post (darshan-singh-meel-tech-blog-review).
---

# Technical blog post

One post = one thesis, proven with code that ran and facts that have a source. Global rules in CLAUDE.md apply. Code in the post follows `darshan-singh-meel-code`; data-platform topics also load `darshan-singh-meel-data-platform` (only the reference files for the tools in the post).

## Rules
- **Reader first.** Name the reader and what they already know; cut everything that reader knows and explain everything they do not.
- **One thesis.** One sentence the reader could act on or disagree with. A section that does not support it is cut or becomes another post.
- **Evidence before prose.** Code and output exist and ran before the paragraph about them is written. The post quotes the files in `blog/_code/<slug>/` verbatim; nothing is typed from memory.
- **Every block ran, or says why not.** A block that was not run carries `<!-- not-run: <reason> -->` on the line before the fence, and the prose says so in words ("not run here: needs a cloud account").
- **Every fact has an official source.** Versions, defaults, limits, syntax, release dates, behaviour: read on the official page, linked at the claim. Not found → cut the claim or write it as the author's observation with the measurement. No numbers from memory. Network rule of CLAUDE.md applies: official sites only, nothing private in a request.
- **Measured numbers carry their setup:** machine, versions, data size, runs, what was measured. No setup → no number.
- **Every word informs.** Active voice, second person, present tense, short sentences. No hype, no filler, no scene-setting intro, no summary of what was just said. The post reads as the author's own: no trace of the chat that shaped it (CLAUDE.md, author voice). `references/style.md`.
- **Diagram only where it explains** a flow, a structure, a sequence or a before/after that prose needs more than a paragraph for. `references/diagrams.md`.
- **Honest title.** The title states what the post delivers, within the scope it proves. No "ultimate", no number it does not keep, no question it does not answer.
- **Original and generic.** No copied text, code or figures beyond a short quoted line with a link. No employer, client, colleague or internal system names, no secrets, no real data rows; examples are synthetic.
- **Local files only.** No publishing, no gists, no hosted previews.

## Output
```
blog/
  <slug>.md                 the post (front matter, brief comment, body)
  <slug>-<name>.svg         figures, when not Mermaid
  <slug>.html               only when asked; built by the script
  _code/<slug>/             every code file quoted in the post + <file>.out (stdout)
```
- `<slug>`: lower case, ASCII, hyphens, 3-6 words from the title (`idempotent-load-sqlite-upsert`).
- Front matter: `title`, `description`, `date`, `tags`. Other keys the site generator needs - check: the generator's docs.
- Under the front matter, one comment: `<!-- brief: reader=...; goal=...; thesis=...; type=...; words=... -->`. The script and the reviewer read it. No `;` inside a value: it separates the keys.
- Paths in replies are relative to the project root.

## Process (fixed)
1. **Setup questions** - one AskUserQuestion prompt, recommended first, skip what the user already said. No answer → recommended options, and say which.

   | # | Question | Options |
   |---|---|---|
   | 1 | Reader | Practitioner who uses the tool daily (Recommended) · Engineer new to the tool · Decision-maker (lead, architect) · free text |
   | 2 | Post type | Tutorial: reader builds it (Recommended) · Explainer: how it works · Lessons learned: what happened, what changed · Comparison: A or B, when |
   | 3 | Length | Standard 1,200-1,800 words (Recommended) · Short 600-900 · Long 2,500-3,500 |
   | 4 | Output | Markdown (Recommended) · Markdown + HTML |

   Topic unclear, or the user's notes hold several possible theses → propose 3 thesis sentences in the same prompt's place of question 2 and ask which.
2. **Brief** - write reader, goal, thesis, type, words. Test the thesis: one sentence, a claim (not a topic), provable in this length with code or sources you can get.
3. **Outline** - `references/structure.md` for the type. Per section: heading that states the point · the one point · its evidence (code file, figure, source page). A section without evidence is cut or researched.
4. **Evidence** - `references/evidence.md`. Write the code in `blog/_code/<slug>/`, run it (`blog_post.py --run` for Python), read the output. Read the official page for each fact; note page and version. The outline changes when the evidence disagrees with it - never the evidence.
5. **Draft** from `references/templates/post.md`, section by section: point first, then evidence, then what follows from it. Paste code and output from the files.
6. **Figures** - where step 3 named one. `references/diagrams.md`.
7. **Scan layer** - title, description, summary paragraph, headings, takeaways: a reader who reads only these gets the thesis and the steps. `references/structure.md`.
8. **Cut** - read once for `references/style.md` only: delete every sentence the reader would not miss; replace every adjective with the fact behind it.
9. **Check** - `python <skill dir>/scripts/blog_post.py blog/<slug>.md --run` (add `--html` when asked). Fix every `FAIL`; read every `?` line and fix or keep on purpose. It checks: front matter and brief, one H1 = title, heading levels, summary paragraph, `Takeaways` last, every code block found in `_code/<slug>/` or marked not-run, fence languages, code wrapped at 80, slop phrases, passive voice, long sentences and paragraphs, link text, alt text, local targets, placeholders, machine paths (prose and code blocks), length against the brief; `--run` reruns the Python files and compares stdout.
10. **Self-review** against `references/review.md` (Must column), then reply: files written, thesis, what ran (command, exit code), what was not run and why, sources used, anything marked `check:`. Offer the reviewer skill in one line.

Rewrite or tighten an existing post: skip step 1 when the post has a brief comment; otherwise ask reader and length only. Steps 4 and 9 still run - existing code is rerun, existing claims re-read.

## References (load only what the task needs)
| File | Read when |
|---|---|
| `references/structure.md` | steps 3 and 7: outline per post type, title, description, summary, headings, takeaways, length |
| `references/evidence.md` | step 4: running code, quoting output, sourcing claims, benchmarks, what counts as official |
| `references/style.md` | steps 5 and 8: sentence rules, slop list with replacements, before/after |
| `references/diagrams.md` | step 6: when to draw, Mermaid or SVG, syntax traps, accessibility |
| `references/review.md` | step 10 and the reviewer skill: checklist, severity |
| `references/templates/post.md`, `post.html` | step 5; `--html` |
| `references/examples/blog/` | one finished short post (tutorial, 600-900 words) with its code, output, figure and HTML: the target for form and density |
| `references/sources.md` | where the rules in this skill come from; what is our own default |

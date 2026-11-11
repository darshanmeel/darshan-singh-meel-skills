---
name: darshan-singh-meel-tech-blog
description: Technical writer for English technical blog posts on software, data engineering, cloud and AI - fixed process (reader and goal, one-sentence thesis, outline, code run before it is quoted, every claim and version from official docs, a diagram where it explains, title + summary + headings for scanning, takeaways), plain style without fluff, hype or AI slop, checked by a script. Writes blog/<slug>.md (+ optional self-contained .html) with the tested code in blog/_code/<slug>/. Use when asked to write, draft, outline, rewrite or tighten a technical blog post, tutorial, explainer, lessons-learned or comparison article. Triggers - "write a blog post about", "technical blog", "tech article", "tutorial post", "draft a post", "turn this into a blog post", "tighten my post", "blog outline"; "Blogartikel schreiben", "technischer Blogbeitrag", "Tech-Blog", "Artikel über". Not for project documentation (darshan-singh-meel-docs) and not for reviewing a post (darshan-singh-meel-tech-blog-review).
---

# Tech blog post
One post = one thesis · code that ran · facts with a source. CLAUDE.md applies. Code → `darshan-singh-meel-code`; data-platform topic → also `darshan-singh-meel-data-platform` (refs for tools in the post only).

## Rules
- Reader first: name reader + what they know → cut the known, explain the rest.
- One thesis: one sentence, actionable or arguable → unsupporting section cut or own post.
- Evidence before prose: code + output ran first → post quotes `blog/_code/<slug>/` verbatim, nothing from memory.
- Block not run → `<!-- not-run: <reason> -->` before the fence + prose says so.
- Every fact (version · default · limit · syntax · date · behaviour) → official page, linked at the claim. Not found → cut, or author observation with measurement. Official sites only, nothing private in requests.
- Measured number → carries machine · versions · data size · runs · what. No setup → no number.
- Every word informs: active · 2nd person · present · short. No hype · filler · scene-setting intro · recap → `references/style.md`.
- Diagram only where prose needs >1 paragraph for a flow · structure · sequence · before/after → `references/diagrams.md`.
- Title states what the post delivers within what it proves. No "ultimate", no unkept number, no unanswered question.
- Original + generic: no copied text/code/figures beyond a short linked quote; no employer · client · colleague · internal names · secrets · real rows; synthetic examples.
- Local files only: no publishing · gists · hosted previews.

## Output
- `blog/<slug>.md` post (front matter, brief comment, body) · `blog/<slug>-<name>.svg` figures (non-Mermaid) · `blog/<slug>.html` only when asked, built by script · `blog/_code/<slug>/` every quoted code file + `<file>.out`.
- slug: lower-case ASCII hyphens, 3-6 words from title.
- Front matter: `title` · `description` · `date` · `tags`; other site keys → check: generator docs.
- Under it: `<!-- brief: reader=...; goal=...; thesis=...; type=...; words=... -->`, no `;` inside values. Script + reviewer read it.
- Paths in replies relative to project root.

## Process (fixed)
1. **Setup** - one AskUserQuestion, rec first, skip what user said, no answer → rec + say which.
   - Reader: practitioner using tool daily (rec) · engineer new to tool · decision-maker · free text.
   - Type: tutorial (rec) · explainer · lessons learned · comparison.
   - Length: standard 1,200-1,800 (rec) · short 600-900 · long 2,500-3,500.
   - Output: Markdown (rec) · Markdown + HTML.
   - Topic unclear / notes hold several theses → 3 thesis sentences replace Q2.
2. **Brief** - reader · goal · thesis · type · words. Thesis = one sentence · claim not topic · provable at this length with code/sources obtainable.
3. **Outline** - `references/structure.md`. Per section: point-stating heading · the point · evidence (code file · figure · source). No evidence → cut or research.
4. **Evidence** - `references/evidence.md`. Write code in `blog/_code/<slug>/` → run (`blog_post.py --run` for Python) → read output. Read official page per fact, note page + version. Evidence disagrees → change outline, never evidence.
5. **Draft** from `references/templates/post.md`: point → evidence → consequence. Paste code/output from files.
6. **Figures** named in step 3 → `references/diagrams.md`.
7. **Scan layer** - title · description · summary · headings · takeaways: alone they give thesis + steps → `references/structure.md`.
8. **Cut** - one pass for `references/style.md`: delete unmissed sentences · adjective → its fact.
9. **Check** - `python <skill dir>/scripts/blog_post.py blog/<slug>.md --run` (+ `--html` if asked). Fix every `FAIL`; read every `?` → fix or keep on purpose. Covers: front matter · brief · one H1 = title · heading levels · summary · `Takeaways` last · code blocks in `_code/` or not-run · fence languages · wrap 80 · slop · passive · long sentences/paragraphs · link + alt text · local targets · placeholders · machine paths · length vs brief; `--run` reruns Python, compares stdout.
10. **Self-review** vs `references/review.md` (Must column) → reply: files · thesis · what ran (command, exit code) · not run + why · sources · `check:` items. Offer reviewer skill in one line.

Rewrite/tighten existing post → skip 1 if brief comment exists, else ask reader + length only. Steps 4 + 9 still run: rerun code, re-read claims.

## References (load only when needed)
| File | Read when |
|---|---|
| `references/structure.md` | 3, 7: outline per type · title · description · summary · headings · takeaways · length |
| `references/evidence.md` | 4: running code · quoting output · sourcing · benchmarks · what is official |
| `references/style.md` | 5, 8: sentence rules · slop list · before/after |
| `references/diagrams.md` | 6: when · Mermaid vs SVG · traps · accessibility |
| `references/review.md` | 10 + reviewer: checklist · severity |
| `references/templates/post.md`, `post.html` | 5; `--html` |
| `references/examples/blog/` | target form + density: short tutorial with code, output, figure, HTML |
| `references/sources.md` | origin of rules; own defaults |

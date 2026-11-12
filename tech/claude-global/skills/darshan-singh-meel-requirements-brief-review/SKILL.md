---
name: darshan-singh-meel-requirements-brief-review
description: Reviewer for a requirements brief built by darshan-singh-meel-requirements-brief - re-reads every input independently, rebuilds the traceability (every input requirement and data point to where it appears), recomputes the data-findings numbers with the profile script, checks that the confirmed stack is used as given and tech facts follow the loaded skills and official pages, diagrams against tables, the 12 fixed sections and whether their content fits this input or is template filler, voice and wording; writes reviews/requirements-brief-<date>.md with a verdict and Must / Should / Other findings (what, why, fix). Reviews, does not rewrite. Use when asked to review, check or verify a requirements brief, or after the brief skill built one. Triggers - "review the requirements brief", "check the brief against the requirements", "is every requirement in the brief", "are the tech options right". Not for code review (darshan-singh-meel-review) or writing the brief.
context: fork
argument-hint: [generated-docs/requirements-brief-<slug>.html]
---

# Requirements brief review

Find what would mislead the reader: a requirement missing or misread, a data point lost, a number not from the profile, a product fact the official page does not support, a given platform re-litigated, a diagram that disagrees with its table, a block that is template filler, a trace of the chat, personal data. Global rules in CLAUDE.md apply. Loads `darshan-singh-meel-requirements-brief` for its spec, catalogue, style and scripts; `<brief skill>` below is that skill's folder.

## Rules
- **Independent.** `context: fork` runs this skill in a subagent with this file and the arguments, not the session that wrote the brief. Trust nothing the spec says about the inputs: re-read the inputs, rerun the scripts.
- **Official pages only** for product facts (CLAUDE.md network rule); nothing from the brief or the inputs goes into a search.
- **Evidence per finding:** the input line or id, the script output, the page and what it says, or the quoted words. No evidence → a question under "Not checked", not a finding.
- **Review, not rewrite.** Fixes are proposed in the report; files change only when the user asks ("fix" in the arguments or a later request). Then: fix the spec, rebuild, rerun steps 2–5, add a "Fixed" line per finding.
- **Never open secret files, never read data rows:** the profile script is the only way to look at data. `generated-docs/_spec/inputs/` and `_spec/text/` hold raw requirements and may contain personal data by nature: read them for the review, quote ids and field names only, never a person's name, e-mail or phone, and check that both folders are git-ignored (missing from `.gitignore` → Must, Privacy).
- **Brief, not gentle.** No praise section, no summary of the brief, no taste-only findings.

## Process (fixed)
1. **Scope** — the HTML in the arguments (`$ARGUMENTS`), else the newest `generated-docs/requirements-brief-*.html`; its spec in `generated-docs/_spec/`; the inputs the spec names (`inputs[]`, `generated-docs/_spec/inputs/`, the data files behind `profile.json`); the spec's `stack` and the skills it names. An input the spec names but that is not there → Must (Traceability).
2. **Rebuild** — `python <brief skill>/references/templates/build.py <spec> <temp>/brief.html`: every ERROR is a Must, every WARN a Should candidate; diff the page with the one under review (a stale page → Must).
3. **Inputs again** — `inputs.py` on the same files into a temp folder; read the plain text top to bottom and list every requirement (id or sentence), every source, every data point, every consumer, every constraint (cadence, retention, access, data protection), every named platform. This list is yours, made before opening section 3 of the brief.
4. **Traceability** — one row per item of step 3: where it appears in the brief (section, row id) and whether the status (clear · gap · conflict) and the wording hold. Missing requirement or data point → Must. A status that hides a conflict or gap in the input → Must. A requirement the brief invented → Must.
5. **Numbers** — `profile.py` on the same data files with the same keys into a temp folder; every number in Data findings (rows, columns, null %, distinct, overlaps) and every derived number in the text ("17 of 20", "25%") compared with the fresh output. Differs → Must. No data files but numbers in section 8 → Must.
6. **Stack and tech facts** — every platform the input names or the spec's `stack` lists is a given row (chip, no alternatives, `why` = how it fits) and appears in the work items; a given platform with alternatives or swapped → Must (Given); a platform made given that neither the input nor the stack names → Must. Other rows: pick + 2–3 alternatives present; every product fact (connector exists, feature, limit, version) read on the page named in `source` or found on the official site, and against the loaded skills' rules when the spec names them: `confirmed` · `wrong` (Must) · `not supported by the page` (Must) · `against the skill's rule` (Must, quote the rule) · `unsourced` (Should; Must for a limit or a price) · `not checked`. A `check:` left in the page → Should with the answer when the page gives it.
7. **Diagrams vs tables** — context boxes of kind source = sources rows; consumers in the diagram = consumers in needs; links entities and keys = identifiers in the sources' data points; timeline times = cadence in sources and requirements. Mismatch → Must.
8. **Fixed sections and fit** — the 12 sections present in order (the build enforces it); inside each, every block says something only this input has: per source, per flow, per conflict. A subsection with a wrapper title that fits any brief ("Overview", "Per need", "Work items") or content that could stand in any brief (generic best practice, restated definitions, a diagram that repeats a table) → Should (Fit); a one-line section where the input holds material for it → Should; a section filled with material the input does not contain, or an example row that survived from the skill's example → Must.
9. **Voice and words** — `<brief skill>/references/style.md`: chat voice ("you said", "as requested", "the requester", "the user", notes on what was skipped) → Should, Must when it misstates a fact or exposes private content; a fact said in two sections → Should; a string over 40 words, filler, a request to the reader → Should.
10. **Data handling** — any data row, real value of a sensitive-looking column, person's name, e-mail, phone, secret value or absolute path in the page, the spec, `profile.json` or the report → Must (Privacy). For `_spec/inputs/` and `_spec/text/` only two checks: both git-ignored, and nothing personal from them quoted anywhere else.
11. **Report** — `reviews/requirements-brief-<YYYY-MM-DD-HHMM>.md` from `references/format.md`; add `/reviews/` to `.gitignore` when the folder is first created. Reply: verdict, counts, the Must lines, report path.
12. **Self-check** - the reply ends with the CLAUDE.md Self-check (confidence · main risk · went well), logged with `python ~/.claude/hooks/log-work.py --skill darshan-singh-meel-requirements-brief-review …`; this skill runs as a fork, so it logs its own entry.

## Specific tests
- **Reader test:** read At a glance and the context diagram only: can the reader say what is asked, from where, how often, for whom? A missing piece → Must (Clarity).
- **Gap test:** every needs row without a source or marked partial, and every `gap`/`conflict` requirement, has a work item (decide or clarify) with an owner; missing → Should.
- **Dependency test:** work items that build on a decide/clarify item list it in `depends`; a build item that can start without its gap resolved → Should.
- **Print test:** render the page with playwright (`python -m playwright install chromium` once; screenshots at 1280 and 390 px, full page and each `.dg`): cut box text, overflowing tables, a diagram wider than the page without scroll, a line through a box → Should (Layout). Playwright truly missing → inspect the HTML and SVG coordinates (box rects vs polyline points) and say so under "Not checked".

## References
| File | Read when |
|---|---|
| `<brief skill>/references/spec.md` | steps 2, 7, 8: fixed sections, blocks, checks |
| `<brief skill>/references/tech-options.md`, `sources.md` | step 6: rules for picks, documentation homes |
| `<brief skill>/references/style.md` | step 9 |
| `references/format.md` | step 11: report format, traceability, numbers and claims tables |

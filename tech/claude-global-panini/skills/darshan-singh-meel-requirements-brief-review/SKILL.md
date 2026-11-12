---
name: darshan-singh-meel-requirements-brief-review
description: Reviewer for a requirements brief built by darshan-singh-meel-requirements-brief - re-reads every input independently, rebuilds the traceability (every input requirement and data point to where it appears), recomputes the data-findings numbers with the profile script, checks that the confirmed stack is used as given and tech facts follow the loaded skills and official pages, diagrams against tables, the 12 fixed sections and whether their content fits this input or is template filler, voice and wording; writes reviews/requirements-brief-<date>.md with a verdict and Must / Should / Other findings (what, why, fix). Reviews, does not rewrite. Use when asked to review, check or verify a requirements brief, or after the brief skill built one. Triggers - "review the requirements brief", "check the brief against the requirements", "is every requirement in the brief", "are the tech options right". Not for code review (darshan-singh-meel-review) or writing the brief.
context: fork
argument-hint: [generated-docs/requirements-brief-<slug>.html]
---

# Requirements brief review
Find what would mislead the reader: requirement missing/misread · data point lost · number not from profile · product fact the official page does not support · given platform re-litigated · diagram disagreeing with its table · template-filler block · trace of chat · personal data. CLAUDE.md applies. Loads `darshan-singh-meel-requirements-brief` for spec, catalogue, style, scripts; `<brief skill>` = its folder.

## Rules
- Independent: `context: fork` → subagent with this file + arguments, not the session that wrote the brief. Trust nothing the spec says about inputs: re-read inputs, rerun scripts.
- Official pages only for product facts (CLAUDE.md network rule); nothing from brief or inputs goes into a search.
- Evidence per finding: input line/id · script output · page + what it says · quoted words. No evidence → question under "Not checked", not a finding.
- Review, not rewrite: fixes proposed in report; files change only when user asks ("fix" in arguments or later request). Then: fix spec → rebuild → rerun 2–5 → "Fixed" line per finding.
- Never open secret files, never read data rows: profile script is the only look at data. `generated-docs/_spec/inputs/` + `_spec/text/` hold raw requirements, may contain personal data by nature: read for review, quote ids + field names only, never a person's name/e-mail/phone; both folders must be git-ignored (missing from `.gitignore` → Must, Privacy).
- Brief, not gentle: no praise section, no summary of the brief, no taste-only findings.

## Process (fixed)
1. Scope: HTML in arguments (`$ARGUMENTS`), else newest `generated-docs/requirements-brief-*.html`; its spec in `generated-docs/_spec/`; inputs the spec names (`inputs[]`, `generated-docs/_spec/inputs/`, data files behind `profile.json`); spec's `stack` + skills it names. Input named by spec but absent → Must (Traceability).
2. Rebuild: `python <brief skill>/references/templates/build.py <spec> <temp>/brief.html`: every ERROR = Must, every WARN = Should candidate; diff with page under review (stale page → Must).
3. Inputs again: `inputs.py` on same files into temp folder; read plain text top to bottom; list every requirement (id or sentence) · source · data point · consumer · constraint (cadence, retention, access, data protection) · named platform. Your list, made before opening section 3 of the brief.
4. Traceability: one row per step-3 item: where in brief (section, row id), status (clear · gap · conflict) + wording hold? Missing requirement/data point → Must. Status hiding a conflict/gap of the input → Must. Requirement the brief invented → Must.
5. Numbers: `profile.py` on same data files, same keys, into temp folder; every number in Data findings (rows · columns · null % · distinct · overlaps) + every derived number in text ("17 of 20", "25%") vs fresh output. Differs → Must. No data files but numbers in section 8 → Must.
6. Stack + tech facts: every platform the input names or spec's `stack` lists = a given row (chip, no alternatives, `why` = how it fits) + appears in work items; given platform with alternatives or swapped → Must (Given); platform made given that neither input nor stack names → Must. Other rows: pick + 2–3 alternatives present; every product fact (connector exists · feature · limit · version) read on page named in `source` or on the official site, and against loaded skills' rules when spec names them → `confirmed` · `wrong` (Must) · `not supported by the page` (Must) · `against the skill's rule` (Must, quote rule) · `unsourced` (Should; Must for a limit or price) · `not checked`. `check:` left in page → Should, with the answer when page gives it.
7. Diagrams vs tables: context boxes of kind source = sources rows; diagram consumers = consumers in needs; links entities + keys = identifiers in sources' data points; timeline times = cadence in sources + requirements. Mismatch → Must.
8. Fixed sections + fit: 12 sections present in order (build enforces); inside each, every block says something only this input has (per source · flow · conflict). Subsection with wrapper title fitting any brief ("Overview", "Per need", "Work items") or content fitting any brief (generic best practice · restated definitions · diagram repeating a table) → Should (Fit); one-line section where input holds material → Should; section filled with material the input lacks, or example row surviving from the skill's example → Must.
9. Voice + words (`<brief skill>/references/style.md`): chat voice ("you said", "as requested", "the requester", "the user", notes on what was skipped) → Should, Must when it misstates a fact or exposes private content; fact said in two sections → Should; string over 40 words · filler · request to reader → Should.
10. Data handling: any data row · real value of sensitive-looking column · person's name/e-mail/phone · secret value · absolute path in page, spec, `profile.json` or report → Must (Privacy). `_spec/inputs/` + `_spec/text/`: only two checks — git-ignored; nothing personal from them quoted elsewhere.
11. Report: `reviews/requirements-brief-<YYYY-MM-DD-HHMM>.md` per `references/format.md`; add `/reviews/` to `.gitignore` when folder first created. Reply: verdict · counts · Must lines · report path.

## Specific tests
- Reader test: read At a glance + context diagram only → can reader say what is asked, from where, how often, for whom? Missing piece → Must (Clarity).
- Gap test: every needs row without source or marked partial, every `gap`/`conflict` requirement → has a work item (decide/clarify) with owner; missing → Should.
- Dependency test: work items building on a decide/clarify item list it in `depends`; build item startable without its gap resolved → Should.
- Print test: render with playwright (`python -m playwright install chromium` once; shots at 1280 + 390 px, full page + each `.dg`): cut box text · overflowing tables · diagram wider than page without scroll · line through a box → Should (Layout). Playwright truly missing → inspect HTML + SVG coordinates (box rects vs polyline points), say so under "Not checked".

## References
- `<brief skill>/references/spec.md` → steps 2, 7, 8: fixed sections, blocks, checks.
- `<brief skill>/references/tech-options.md`, `sources.md` → step 6: pick rules, docs homes.
- `<brief skill>/references/style.md` → step 9.
- `references/format.md` → step 11: report format; traceability, numbers, claims tables.

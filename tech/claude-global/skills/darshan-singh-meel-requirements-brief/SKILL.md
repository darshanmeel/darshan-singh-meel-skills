---
name: darshan-singh-meel-requirements-brief
description: Turns pasted or attached requirements (text, epics and stories with ticket ids, source and data-point tables, notes, Jira exports, docx/pdf/xlsx/csv, sample data) into one self-contained HTML brief with inline SVG in generated-docs/. Infers the tech stack, confirms it, finds and loads the installed skills that cover it. 12 fixed sections, content per input; at a glance, context diagram, traceable requirements (own ids, clear/gap/conflict), per-source data points, linking diagram, flows, use case to source map, data findings (structure only), tech options per need (confirmed stack as given; one pick + 2-3 alternatives, official docs), what needs to be done (build/configure/decide/clarify, owner), gaps and risks, glossary. Triggers - "turn these requirements into a brief", "diagram these requirements", "what tech can we use for this use case", "explain this requirement", "solution brief". Not for documenting code (darshan-singh-meel-docs) or an architecture review (darshan-singh-meel-architecture).
---

# Requirements brief

One page that lets a reader understand a requirement and the shape of a solution fast: what is asked, what data is involved, how it flows and links, what is unclear, which tech fits each need, what has to be done. Not an architecture review: no current-vs-target, no migration, no cost model, no repo or graph needed. Global CLAUDE.md rules apply (local files only, relative paths, never open secret files, never read data rows, author voice).

- **Output:** `generated-docs/requirements-brief-<slug>.html` from `generated-docs/_spec/requirements-brief-<slug>.json`. Raw inputs go to `generated-docs/_spec/inputs/`, text extracts to `generated-docs/_spec/text/`, the profile to `generated-docs/_spec/profile.json`. The two input folders are git-ignored on first creation (`inputs.py` adds them): requirements are confidential, the brief is not. One brief per run; a new run on the same inputs overwrites it.
- **Fixed top level, free inside.** Every brief has the same 12 sections in the same order (`references/spec.md`); the build refuses a missing or extra one. Inside, blocks sit directly in the section; a subsection only when a named group needs its own heading, named from the input ("B. Telematics provider", "FLT-4 vs FLT-2"), never a wrapper title that fits any brief ("Overview", "Per need": the build warns). A section with nothing to say is one line.
- `<skill>` = this folder. Fields and checks: `references/spec.md`. Tech catalogue: `references/tech-options.md`. Voice and wording: `references/style.md`.

## Step 0 — ask first
Before any question: inventory (process step 1) and infer the stack from the inputs: named platforms, connectors, cadence ("Snowflake Data Share" → Snowflake; "daily batch" → an orchestrator is needed; "dashboard" → a BI or app tool). Then one AskUserQuestion prompt, recommended first; skip what the user already said in their own words. No answer → recommended options, said in the reply.

| # | Header | Question | Options |
|---|---|---|---|
| 1 | Stack | Which stack is given? (always asked, even when inferred) | the inferred stack (Recommended) · 2–3 typical combinations that fit the input, e.g. Databricks + Airflow + dbt · ADF + Snowflake + dbt · Other (free text) |
| 2 | Reader | Who reads the brief? | Engineers and business together (Recommended) · Engineers · Business and product |
| 3 | Inputs | Which inputs are in scope? (only when several pieces were given) | All of them (Recommended) · named subset (multi) |
| 4 | Data | Profile the supplied data files? (only when data came with the requirements) | Yes, structure only: columns, types, counts, nulls, key overlap (Recommended) · No |

Second prompt, right after, once the stack is confirmed: `python <skill>/references/templates/skills.py <confirmed techs>` lists the installed skills (`~/.claude/skills`, `./.claude/skills`) whose name or description covers a confirmed tech, by reading their frontmatter only; ranked by techs matched, process skills (review, docs, graph, prototype, …) left out; `offer:` names the top 3.
- **Skills** (multiSelect): the top 3 as options, best first and recommended, plus Other (free text for any other listed skill). Load the chosen ones and follow their version and feature rules in the tech rows and work items. No answer → the top-ranked one only.
- A tech with no matching skill (`no skill:` line) → one line to the user; its facts come from the official docs.

## Process (fixed)
| # | Step | Model | Output |
|---|---|---|---|
| 1 | Inventory: copy or save the inputs to `generated-docs/_spec/inputs/` (pastes as `paste-<n>.md`), then `python <skill>/references/templates/inputs.py generated-docs/_spec/inputs --text generated-docs/_spec/text` → kinds, sizes, requirement ids, plain text. Secret-looking files are listed, never opened; Jira exports keep key, summary, description, type and epic only; JSON/YAML record files give keys only; standards, quarters and the like (ISO-8601, UTF-8, Q1-2025, COVID-19) are not ids, and EPIC 12 = EPIC-12. Rerun-safe: the text folder is skipped | script | `inputs` list for the spec |
| 2 | Step 0 questions; load the chosen skills | - | stack, reader, scope, data, skills |
| 3 | Read the plain text (judgment: what is asked, objective, cadence, sources, consumers, constraints). Every requirement keeps the input's id; none → `R1…`, marked ours. Status per item: `clear` buildable as written · `gap` information missing · `conflict` two items disagree | Opus | requirement rows |
| 4 | Data (Q4 = yes): `python <skill>/references/templates/profile.py <data files> --out generated-docs/_spec/profile.json [--key <col>]` → structure only; sensitive-looking columns have values withheld. Data dictionaries are read as text. No data → section 8 is one line: "Data not yet profiled." | script | `profile.json` |
| 5 | Tech: one row per need the input raises (`references/tech-options.md`): every confirmed tech as `given` (no alternatives; `why` = how it carries the need); else one pick that fits this brief + 2–3 alternatives with the condition that would make them the pick; product facts per the loaded skills and the official page named in `source`; unsure → `check: <page>` | Opus | `options` rows, `stack` |
| 6 | Work items: per source and need, what has to be built, configured, decided or clarified on the confirmed stack; owner role, `depends`, `ref` (requirement or source ids). Decide/clarify items first, build items that depend on them after | Opus | `work` rows |
| 7 | Spec: copy `references/examples/requirements-brief-example.json`, replace every section from steps 3–6 (nothing of the example survives: not a row, not a title); diagrams: context (always), links (≥ 2 sources join), timeline (only when timing explains); each with `key`. Sources not yet defined get `planned: true`, no invented connector | Opus | spec |
| 8 | Build: `mkdir -p generated-docs/_spec` → `python <skill>/references/templates/build.py <spec> <html>` → fix every ERROR and WARN; the build rescans `generated-docs/_spec/inputs` for ids and computes the At a glance status counts itself | Sonnet | page |
| 9 | Read as the reader from Q2, top to bottom: every block says something only this input has; a block that could stand in any brief is cut. Open the HTML with playwright (`python -m playwright`, chromium; screenshots at 1280 and 390 px): boxes not cut, tables readable, diagrams match the tables | Haiku | checked page |

- Reply: files written, the build's summary line, every `check:` left in the page, skills loaded and techs without one, decisions made where no answer came. One line: "Review it with darshan-singh-meel-requirements-brief-review?"
- First time `generated-docs/` is created: ask once whether to commit it (default: committed; the `_spec/inputs/` and `_spec/text/` folders stay ignored either way).
- No subagents unless asked; tell the user in one line which model to switch to per phase.

## Rules
- **Every requirement traceable:** the input's ids appear in the Requirements rows (the build rescans the inputs and fails otherwise), and again in needs, work items and risks where they apply.
- **Every source has a row and a box:** a `source` box in the context diagram needs a `sources` row with the same id; a row without a box is a WARN.
- **Use cases without a source are shown**, not hidden: an empty `sources` list renders "no source", a `missing` field renders "partial"; both get a work item.
- **Confirmed stack = given.** Shown as given with how it fits, used in the work items, never re-litigated; a real misfit is a risk in section 11, not a swap. The build fails when a confirmed tech has no given row.
- **Numbers only from the profile script.** Counts, null %, overlaps are read from `profile.json`; the status counts are computed by the build. No data rows, no values of sensitive-looking columns, no personal data (the build fails on an e-mail address or phone number); examples in text are synthetic.
- **Author voice** (`references/style.md`): "We load all sources daily", "Owner to decide: …", "Data not yet profiled." Never "you said", "as requested", "the requester", "the user", what was skipped.
- **Minimal words:** tables and one-line bullets; a fact lives in one section and is referenced from the others.
- **Generic:** any domain, any platform; nothing from the input beyond what the requirement itself names.
- **No user to ask** (subagent or batch run): Step 0 recommended options (inferred stack, all found skills), said in the reply.

## Updating
- "Update the brief" with new or changed inputs: rerun steps 1 and 4 (ids and profile first), then change only the rows and blocks those inputs touch; rebuild; the reply lists which sections changed.
- "Use <alternative> instead" on a tech row: the alternative becomes `rec`, the old pick an alternative with its trade-off, `why` rewritten for this brief; work items naming the old pick follow. A given row is not swapped: the stack changes first (Step 0, question 1).

## References (load only what the step needs)
| File | Read when |
|---|---|
| `references/spec.md` | step 7: fixed sections, blocks, fields, ERROR/WARN list |
| `references/tech-options.md` | step 5: rules for picks, catalogue by need with official docs homes |
| `references/style.md` | steps 7 and 9: voice, wording, diagram rules, data rules |
| `references/examples/` | step 7: a built brief (fleet maintenance, synthetic): `inputs/`, spec, `profile.json`, HTML |
| `references/sources.md` | where the catalogue's documentation homes and our own defaults come from |

---
name: darshan-singh-meel-requirements-brief
description: Turns pasted or attached requirements (text, epics and stories with ticket ids, source and data-point tables, notes, Jira exports, docx/pdf/xlsx/csv, sample data) into one self-contained HTML brief with inline SVG in generated-docs/. Infers the tech stack, confirms it, finds and loads the installed skills that cover it. 12 fixed sections, content per input; at a glance, context diagram, traceable requirements (own ids, clear/gap/conflict), per-source data points, linking diagram, flows, use case to source map, data findings (structure only), tech options per need (confirmed stack as given; one pick + 2-3 alternatives, official docs), what needs to be done (build/configure/decide/clarify, owner), gaps and risks, glossary. Triggers - "turn these requirements into a brief", "diagram these requirements", "what tech can we use for this use case", "explain this requirement", "solution brief". Not for documenting code (darshan-singh-meel-docs) or an architecture review (darshan-singh-meel-architecture).
---

# Requirements brief
One page: what is asked · data · flow + links · unclear · tech per need · to do. Not an architecture review: no current-vs-target, migration, cost model, repo, graph. CLAUDE.md applies (local only · relative paths · no secret files · no data rows · author voice).
- Output: `generated-docs/requirements-brief-<slug>.html` ← spec `generated-docs/_spec/requirements-brief-<slug>.json`. Raw inputs → `_spec/inputs/`, text → `_spec/text/`, profile → `_spec/profile.json`. Both input folders git-ignored on first creation (`inputs.py` adds them): requirements confidential, brief not. One brief per run; rerun on same inputs overwrites.
- Top level fixed, inside free. Same 12 sections, same order (`references/spec.md`); build refuses a missing/extra one. Blocks sit directly in section; subsection only for a named group, named from input ("B. Telematics provider", "FLT-4 vs FLT-2"), never a wrapper title fitting any brief ("Overview", "Per need": WARN). Empty section = one line.
- `<skill>` = this folder. Fields, checks → `references/spec.md`. Tech catalogue → `references/tech-options.md`. Voice → `references/style.md`.

## Step 0 — ask first
Before any question: inventory (step 1) + infer stack from inputs: named platforms, connectors, cadence ("Snowflake Data Share" → Snowflake; "daily batch" → orchestrator; "dashboard" → BI/app tool). Then one AskUserQuestion prompt, recommended first; skip what user said in own words. No answer → recommended, say so.
- Q1 Stack (always, even if inferred): which stack is given? Inferred stack (Rec) · 2–3 typical combos that fit, e.g. Databricks + Airflow + dbt · ADF + Snowflake + dbt · Other (free text).
- Q2 Reader: Engineers and business together (Rec) · Engineers · Business and product.
- Q3 Inputs (only if several pieces): All (Rec) · named subset (multi).
- Q4 Data (only if data came with requirements): profile data files? Yes, structure only: columns, types, counts, nulls, key overlap (Rec) · No.

Second prompt right after, stack confirmed: `python <skill>/references/templates/skills.py <confirmed techs>` → installed skills (`~/.claude/skills`, `./.claude/skills`) whose name/description covers a confirmed tech (frontmatter only); ranked by techs matched; process skills (review, docs, graph, prototype, …) left out; `offer:` = top 3.
- Skills (multiSelect): top 3 as options, best first + Rec, plus Other (free text, any listed skill). Load chosen; follow their version/feature rules in tech rows + work items. No answer → top one only.
- Tech without skill (`no skill:` line) → one line to user; facts from official docs.

## Process (fixed)
1. Inventory (script): copy/save inputs → `generated-docs/_spec/inputs/` (pastes `paste-<n>.md`); `python <skill>/references/templates/inputs.py generated-docs/_spec/inputs --text generated-docs/_spec/text` → kinds, sizes, requirement ids, plain text. Secret-looking files listed, never opened; Jira exports keep key · summary · description · type · epic only; JSON/YAML record files = keys only; standards, quarters etc. (ISO-8601, UTF-8, Q1-2025, COVID-19) are not ids; EPIC 12 = EPIC-12. Rerun-safe (text folder skipped). → `inputs` list.
2. Step 0 questions; load chosen skills → stack · reader · scope · data · skills.
3. Requirement rows (Opus): read plain text (judgment: asked, objective, cadence, sources, consumers, constraints). Each requirement keeps input's id; none → `R1…`, marked ours. Status per item: `clear` buildable as written · `gap` information missing · `conflict` two items disagree.
4. Data (script; Q4 yes): `python <skill>/references/templates/profile.py <data files> --out generated-docs/_spec/profile.json [--key <col>]` → structure only; sensitive-looking columns values withheld. Data dictionaries read as text. No data → section 8 = one line "Data not yet profiled." → `profile.json`.
5. Tech (Opus): one row per need the input raises (`references/tech-options.md`). Every confirmed tech = `given` (no alternatives; `why` = how it carries the need); else one pick fitting this brief + 2–3 alternatives, each with the condition making it the pick. Product facts per loaded skills + official page in `source`; unsure → `check: <page>`. → `options` rows, `stack`.
6. Work items (Opus): per source + need, what to build · configure · decide · clarify on confirmed stack; owner role, `depends`, `ref` (requirement/source ids). Decide/clarify first, dependent build items after. → `work` rows.
7. Spec (Opus): copy `references/examples/requirements-brief-example.json`, replace every section from steps 3–6 (nothing of example survives: no row, no title). Diagrams: context (always) · links (≥ 2 sources join) · timeline (only when timing explains); each with `key`. Undefined sources → `planned: true`, no invented connector.
8. Build (Sonnet): `mkdir -p generated-docs/_spec` → `python <skill>/references/templates/build.py <spec> <html>` → fix every ERROR + WARN. Build rescans `generated-docs/_spec/inputs` for ids, computes At a glance status counts itself.
9. Check (Haiku): read as Q2's reader, top to bottom: every block says something only this input has; a block fitting any brief → cut. Open HTML with playwright (`python -m playwright`, chromium; shots at 1280 + 390 px): boxes not cut · tables readable · diagrams match tables.

- Reply: files written · build summary line · every `check:` left in page · skills loaded + techs without one · decisions made where no answer. One line: "Review it with darshan-singh-meel-requirements-brief-review?"
- First time `generated-docs/` is created: ask once whether to commit (default committed; `_spec/inputs/` + `_spec/text/` stay ignored either way).
- No subagents unless asked; tell user in one line which model to switch to per phase.

## Rules
- Every requirement traceable: input's ids in Requirements rows (build rescans inputs, fails otherwise), again in needs · work items · risks where they apply.
- Every source has a row + a box: `source` box in context diagram needs a `sources` row with same id; row without box = WARN.
- Use cases without source are shown: empty `sources` → "no source"; `missing` field → "partial"; both get a work item.
- Confirmed stack = given: shown as given + how it fits, used in work items, never re-litigated; real misfit = risk in section 11, not a swap. Build fails when a confirmed tech has no given row.
- Numbers only from profile script: counts, null %, overlaps from `profile.json`; status counts computed by build. No data rows · no values of sensitive-looking columns · no personal data (build fails on e-mail or phone); text examples synthetic.
- Author voice (`references/style.md`): "We load all sources daily", "Owner to decide: …", "Data not yet profiled." Never "you said", "as requested", "the requester", "the user", what was skipped.
- Minimal words: tables + one-line bullets; a fact lives in one section, referenced from others.
- Generic: any domain, any platform; nothing from input beyond what the requirement names.
- No user to ask (subagent/batch) → Step 0 recommended (inferred stack, all found skills), say so.

## Updating
- "Update the brief" with new/changed inputs: rerun 1 + 4 (ids, profile first), change only rows/blocks those inputs touch; rebuild; reply lists changed sections.
- "Use <alternative> instead" on a tech row: alternative → `rec`, old pick → alternative with its trade-off, `why` rewritten for this brief; work items naming old pick follow. Given row not swapped: stack changes first (Step 0 Q1).

## References (load only what the step needs)
- `references/spec.md` → step 7: fixed sections, blocks, fields, ERROR/WARN.
- `references/tech-options.md` → step 5: pick rules, catalogue by need + official docs homes.
- `references/style.md` → steps 7, 9: voice, wording, diagram + data rules.
- `references/examples/` → step 7: built brief (fleet maintenance, synthetic): `inputs/`, spec, `profile.json`, HTML.
- `references/sources.md` → origin of catalogue docs homes + our defaults.

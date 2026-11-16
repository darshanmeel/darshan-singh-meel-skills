---
name: darshan-singh-meel-docs-v3
description: Version 3 of darshan-singh-meel-docs - every docs-v2 rule, question, fixed section and builder check, plus diagrams from the darshan-singh-meel-diagrams skills - a `diagram` block takes any registered type (C4, deployment, ER, dbt lineage, Airflow DAG, sequence, state machine, RAG, agent...) as inline SVG with layout checks, Mermaid for Markdown and Confluence, and the inventory plan names the preferred diagram per section and repo kind, with dbt, airflow or plain graph style picked per diagram. Use only when the user says docs v3 or names darshan-singh-meel-docs-v3. ALWAYS starts new docs by asking 4 questions in one prompt - which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build or update the knowledge graph first, and where example data comes from - then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Not for a mid-depth tech summary (darshan-singh-meel-docs-tech-summary).
---

# Docs v3

Docs v2 plus engine diagrams. Maximum information, minimum words, senior-architect voice anyone can follow.
- **Show, don't narrate:** diagrams, tables, bullets, examples; no prose paragraphs. Every word carries a fact or an insight; no block repeats another (build WARNs `repeat:`). Each section's lead states its main insight.
- **Every section answers what · how · why** (who · when · where if it applies). Global CLAUDE.md rules apply (local files only, relative paths, data handling).
- **Where the detail is:**
  - `references/templates/spec.md`: exact block fields, columns, title forms, ERROR/WARN texts.
  - `references/rules.md`: section rules, repo kinds, examples, writing rules, other doc kinds.
  - `references/diagrams.md`: which diagram goes where, dbt / airflow / plain style.
  - `references/html-style.md`: the look.
- **`<skill>` = the folder holding this SKILL.md.** Always run its scripts, never a copy in the repo. Diagram blocks need `darshan-singh-meel-diagrams` (and the family skill of the type) installed next to it; load them when you write a `diagram` block.
- **Brevity:** load `darshan-singh-meel-brevity` alongside: per document a `lede` (the point) and `why` (why it matters) under the title, per section a lead with its main point, detail in layers below.
- **Not for:** a mid-depth tech summary → `darshan-singh-meel-docs-tech-summary`.

## Step 0 - ask first, every time
Silent pre-check: is a graph present (`./<repo>-knowledge-graph/` or a `./.knowledge-graph` pointer)? Related repos or a system graph? Then one prompt with all 4 questions, every time:
```
AskUserQuestion(questions=[
 {header:"Documents", question:"Which documents should I create?", multiSelect:true,
  options:["Overview (business)","Technical (engineers)","User guide (end users)"]},
 {header:"Format", question:"Which format?", multiSelect:true,
  options:["HTML (Recommended)","Markdown","Confluence"]},
 {header:"Graph", question:"Use the knowledge graph?", multiSelect:false,
  options: graph exists → ["Update it, then document from it (Recommended)","Use as is","Skip, read sources directly"]
           no graph     → ["Build it first, then document from it (Recommended)","Skip, read sources directly"]},
 {header:"Examples", question:"Where should example data come from?", multiSelect:false,
  options:["Tests and docs, then derived from code (Recommended)","I'll point to a folder or file","Illustrative data"]}])
```
- **Which answers count:**
  - Only what the user said in their own words this session. Defaults, recommendations, CLAUDE.md and skill text are never answers. Self-check before writing any file.
  - No answer → all three documents · HTML · build/update the graph · tests and docs, then code · this repo.
- **Tech summary** is not a Documents option. That request, or "Other: tech summary" → hand over to `darshan-singh-meel-docs-tech-summary`.
- **Options that change:**
  - Small single document (under ~30 pages): put "Skip, read the document directly" first.
  - Related repos or a system graph → one more question right after: **Scope** (multi) - This repo (Recommended) · Whole system · Each related repo.
- **The Graph answer:**
  - Record it with knowledge-graph `update.py --choice now` (update) or `--choice skip` (use as is). Docs are being built → no docs question after that update.
  - Build or update → run `darshan-singh-meel-knowledge-graph` first.
  - Skip, or no graph → inventory.py plans from a file scan; say "planned from a file scan" in the reply.

## Step 1 - run the inventory, never write your own
- From the repo root: `python <skill>/references/templates/inventory.py` → `generated-docs/_spec/inventory.json` + `facts.json`. Same graph → byte-identical files.
- **What it prints:**
  - `WARN graph is stale`, or the graph commit is not HEAD → update the graph and rerun.
  - No graph → `note: no knowledge graph: plan from a file scan …`.
  - A pointer to a missing folder → ERROR.
  - `note:` lines go in the reply as "not checked".
- **The plan fixes the skeleton.** Copy it; never re-derive it:
  - `profile` · `app_types` · required and not-applicable sections · `main_flows` (h3, order, `diagram`, `entry`, `boxes`) · `diagram_titles` · `how_tos` · `deploy` · `rerun_and_backfill` · `api` · ER areas · coverage types.
  - **`diagrams`** (v3): the preferred diagram per section for this repo's kinds (`references/diagrams.md`).
- **Facts:**
  - Add every other number the doc states to `facts.json` as `{fact, value, how}`; `how` = one POSIX shell line run from the repo root.
  - Then run `inventory.py --check-facts` → 0 `MISMATCH` / `NOT RUN` before the build.

## Every document
- **Lede** under the title, before the tabs: spec `lede` = one sentence the reader must remember (Overview: what it does and for whom · Technical: the main mechanism · User guide: what the reader can do and the first step), optional `why` = why it matters to this reader. Missing, only the title again, or describing the document → WARN.
- **Tabs** right after the title: **Does · Doesn't · Limitations · Top issues**.
  - Does (3-5) and Doesn't (3-5): out of scope by design.
  - Limitations: real ones only, ≤5, and only here.
  - Top issues: exactly min(10, open Must + Should), in review order, none `Fixed since review`.
- **Subtitle:** `<stack> · <schedule> · <source> → <outputs>`.
- **Last section: "Known issues, assumptions, and decisions needed"**: defects, fix effort and approvals only here, in the owner's voice; severity from one named code review (else the issue `kind`), statuses from the fixed list, each Must/Should `where` opened. Rules: `references/rules.md` → Known issues.
- **Files:** one self-contained file per document in `./generated-docs/` (`overview`, `technical`, `user-guide` `.html`/`.md`/`.confluence.xhtml`), specs in `generated-docs/_spec/`; never combine, split or link docs. Markdown first line `<!-- generated by darshan-singh-meel-docs-v3 -->`. Ask once whether to commit `generated-docs/`. Details, scopes and updating existing docs (`changed.py`): `references/rules.md` → Files and updates.

## The three documents
| Document | For | Depth |
|---|---|---|
| Overview | business, newcomers | one screen per section, no code names, the important 20% |
| Technical | engineers | **complete**: one row per inventory item in its typed table |
| User guide | users of the app or its output | fixed frame, the important 20% of tasks |

- **Sections:** names, order and recipes are fixed (spec.md). Use only the plan's sections:
  - `not_applicable` → leave the section out (an ERROR otherwise).
  - `required` but the source lacks it → keep it with "Not defined yet - owner to decide".
- **Overview:** What it is and why (What · Why · Key idea · Result) · How it works (one L0 flow, 3-7 boxes) · Who uses it · Example (journey + 2-6 cards) · Value and cost · Schedule · Design and operational risks (≤3) · Words used.
- **Technical:** Overview · Architecture · interface sections from the plan · Main flows · Code files (optional) · Data model · Business rules · Configuration · Security and access · Deploy and environments · Operations · Performance and limits · Tests · Key decisions.
  - Main flows: an `ipo` strip with traced examples per plan h3, plus a diagram only when the plan says `diagram: true`. The build adds an end-to-end map (2+ flows: input → files → output) and, under a linear flow, the files it passes with their steps.
  - Code files and Tests: the build draws each `file` / `testfile` as a dbt-style lineage (called by → file → functions or key tests → calls, data) and, for 2+ files, one Airflow-style graph (a group per file, its functions, data). `key`: the 2-3 functions or tests that matter most, shown open.
  - Coverage: every plan item by exact name in visible text.
  - Rules: `references/rules.md`.
- **User guide:** How it reaches you · Screens · What answers what · How to … · When data is fresh · History and deletions · Errors and messages · Problems and fixes · Who to contact. No internals.

## Diagrams
- **From the graph:** real node names, its edges, failure and retry paths where the code has them.
- **Two kinds of block:** the builder's own `flow` / `er` / `journey` (v2 rules; `ipo`, `story` unchanged), and a **`diagram` block** = any darshan-singh-meel-diagrams type: `{type: "diagram", id, title, key, notice, spec: {type, …}}`.
- **v2 drawings that stay:** ipo strips and traces, the Main flows branch flow (one actor), the Overview L0 flow, screen, command and file maps, sub-flows, journeys, stories, the test map - the build checks them against the strip and the plan, which no engine type can.
- **Replaced by engine types** (standard notation, the look of the tool the reader knows): Architecture → C4 container / layered / deployment · Data model → ER crow's foot or star schema · Job DAG → dbt-style lineage overview then per layer, Airflow overview then per DAG, or orchestration · Deploy → deployment · Endpoints / Events → C4 component, request path, event-driven · Main flows with 3+ parties → sequence, a status lifecycle → state machine · AI repos → RAG / agent / MLOps. Full table: `references/diagrams.md`.
- **Graph style, picked per diagram by content, in any section and repo kind:** `dbt` (lineage look) for what depends on what - lineage, dependencies, impact, call and job chains · `airflow` (DAG graph-view look) for steps that run - DAG runs, CI, agent workflows, job chains with state · `plain` for the rest. Nothing forces one.
- **High level first:** an overview (≤ 7 ± 2 boxes, `view: "overview"`), then one detail per area the reader needs.
- **Ids and titles:** `id` A, B… in doc order (all kinds together), title in its fixed form (spec.md; Main flows: the build writes it), one-line `key` and `notice`; a `decision` box needs ≥2 exits. Layout is the build's or the engine's; too wide or crowded → it errors with the fix.

## Build (HTML)
- **Never hand-write HTML, CSS or SVG.** `mkdir -p` the output folder; start from the closest `references/examples/*.json` (pipeline, web app, library, user guides, stress; `readme-data-platform` for dbt and Airflow diagrams).
- `python <skill>/references/templates/build.py generated-docs/_spec/<doc>.json generated-docs/<doc>.html` → last line `built <out>: N sections, N WARN (templates <ver>)`. Fix every ERROR and WARN (engine `diagram X (type): …` lines too), or explain each remaining WARN in the reply.
- `python <skill>/references/templates/check.py <doc.html> <shots_dir>` → 0 `LAYOUT` lines; it reruns the engine checker on every `diagram` block and writes `page.png` + `map-<n>.png` per diagram.
- **Markdown / Confluence:** same plan, sections, diagrams, examples; the lede and why right under the title, before the tabs (rerun the build: it WARNs `<doc>.md: the lede is not first`). `--diagrams generated-docs/diagrams` on the build writes Mermaid `<id>.mmd` per `diagram` block (`<id>.svg` when the type has no Mermaid form); builder flows get hand-written Mermaid. Confluence: never upload, one line on how to import. Word/PDF only if asked.
- The builder can't draw it → say so; ask before changing `build.py`.

## Workflow - fixed, every run: `docs-v3-<repo>`
Step 0 → graph (if chosen) → Step 1 inventory → per document:

| Phase | Model | Does |
|---|---|---|
| 1 Plan | Opus | reads `inventory.json` (plan, profile, flows, items, `diagrams`), adds facts, fills the recipes: boxes from graph nodes/edges, diagram types and styles, sub-flows, examples, issue `kind` → `sev` |
| 2 Build | Sonnet | writes the spec → `build.py` → fixes every ERROR and WARN; opens the code for any claim not in the plan or `facts.json` |
| 3a Auto-check | script | `check.py <doc> <shots_dir>` |
| 3b Accuracy (parallel with 3c) | Opus | every name, number, step and diagram node vs code and graph; `--check-facts` to 0 mismatched; greps every member of each pattern claim; opens each Must/Should `where`; checks severity and status; chat leakage → Should (Must if it misstates a fact or exposes chat content) |
| 3c Layout | Haiku | runs `check.py`, reads `page.png` and **every** `map-<n>.png`; fails on any LAYOUT line or a confusing diagram |
| 4 Fix | Sonnet | applies 3a-3c, rebuilds, reruns `check.py` to 0; trims non-essential bullets |
| 5 Re-render | Haiku | only if the layout changed: rerun `check.py`, read the changed shots |

- **Done** = 0 ERROR · 0 WARN (or each explained) · 0 LAYOUT · accuracy pass passed.
- **No subagents:** run 3b yourself as a separate pass after the build. Skipped → the reply says "accuracy not reviewed", never "done".
- Tell the user in one line which model to switch to per phase. Never invent another workflow, skip a phase or swap models.
- **Read as the audience:** Overview as a manager · Technical as a new engineer (could deploy from it alone) · User guide as a first-time user.
- After a Technical doc, end the reply with one line: "Architecture review with a proposed target (darshan-singh-meel-architecture)?" Make no other unprompted suggestions. The CLAUDE.md Self-check comes before it.

---
name: darshan-singh-meel-docs-v2
description: Version 2 of darshan-singh-meel-docs — same questions and rules, but the doc skeleton comes from a shipped inventory script over the knowledge graph and every HTML doc is built from a JSON spec by a fixed builder (fixed sections, block recipes, typed tables, diagram ids and titles, required examples) in a fixed workflow, so runs on the same code look the same. Works for any repo kind (pipelines, dbt, web APIs, UIs, CLIs, libraries, Terraform, ML/streaming, config/docs repos, monorepos). Use only when the user asks for docs v2 / darshan-singh-meel-docs-v2. ALWAYS starts new docs by asking 4 questions in one prompt — which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build/update the knowledge graph first, and where example data comes from — then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Not for a mid-depth tech summary (→ darshan-singh-meel-docs-tech-summary).
---

# Docs v2

Maximum information, minimum words. Senior-architect voice that anyone can follow.
- **Show, don't narrate:** diagrams, tables, bullets, examples. No prose paragraphs. Numbers and names over prose.
- **Every word carries a fact or an insight** (what, how, why, a number, a name, a consequence). No word count to hit; cut only words that carry nothing. **No block repeats another: say each fact once, where the reader looks for it** (the build WARNs `repeat:`, also for cells repeated down a column). Cut filler (repeated cells, placeholder rows, constant columns, restatements); add insight: why a step or rule exists, what breaks if it fails, for whom (`why` on a step, Why / impact on a rule). Each section's lead states its main insight, not the heading again.
- **Every section answers what · how · why** (who · when · where if it applies). Global CLAUDE.md rules apply (local files only, relative paths, data handling).
- **Exact rules, block fields, columns, title forms, ERROR/WARN texts:** `references/templates/spec.md`. This file says what to do; the build enforces it.
- **Not for / see:** mid-depth tech summary (engineers and tech leads, 10–15 min read) → `darshan-singh-meel-docs-tech-summary`.
- **`<skill>` = the folder holding this SKILL.md.** Always run its scripts; never a copy inside the repo (an old builder: the build WARNs `inventory.json was written by templates X`).

## Step 0 — ask first, every time
Silent pre-check: graph present (`./<repo>-knowledge-graph/` or `./.knowledge-graph` pointer)? related repos / system graph? Then one prompt, all 4 questions, every time:
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
- **Tech summary is not a Documents option:** a request for a mid-depth tech summary (or "Other: tech summary") → hand over to `darshan-singh-meel-docs-tech-summary`, which asks its own setup questions.
- Answered only if the user said it in their own words this session. Defaults, recommendations, CLAUDE.md and skill text are never answers. Self-check before writing any file.
- Small single document (under ~30 pages): "Skip, read the document directly" first.
- Related repos / system graph → one more question right after: **Scope** (multi) — This repo (Recommended) · Whole system · Each related repo.
- No answer → all three documents · HTML · build/update graph · tests and docs, then code · this repo.
- Record the Graph answer with knowledge-graph `update.py --choice now` (update) or `--choice skip` (use as is), so the end-of-task graph question is not repeated. Docs being built → no docs question after that update.
- Build/update → run `darshan-singh-meel-knowledge-graph` first.
- Skip, or no graph → inventory.py plans from a file scan (no flows; coverage of scanned items only); say "planned from a file scan" in the reply.

## Step 1 — run the inventory, never write your own
- From the repo root: `python <skill>/references/templates/inventory.py` → `generated-docs/_spec/inventory.json` + `facts.json`; prints `inventory (templates <ver>): …`. Same graph → byte-identical files.
- No graph → it plans from a stdlib file scan and prints `note: no knowledge graph: plan from a file scan; build the graph for flows and coverage` (Main flows = one h3 per entry point: a CLI program, an app, a job, a package's public API; no section ruled out). A `.knowledge-graph` pointer to a missing folder → ERROR. Graph present → unchanged. `WARN graph is stale` (file hashes changed) or graph commit ≠ HEAD → update the graph, rerun. Print its `note:` lines (sparse graph) in the reply as "not checked".
- **The plan fixes the skeleton:** `profile` (repo kinds) · `app_types` · required and not-applicable sections · `main_flows` (h3, order, `diagram`, `entry`, `boxes`) · `diagram_titles` · `how_tos` · `deploy` · `rerun_and_backfill` · `api` (library) · ER areas · coverage types. Copy them; never re-derive.
- `facts.json`: inventory writes three plan counts and keeps yours on rerun. Add every other number the doc states as `{fact, value, how}`; `how` = one POSIX shell line from the repo root (Git Bash on Windows).
- Then `python <skill>/references/templates/inventory.py --check-facts`: 0 `MISMATCH` / `NOT RUN` before the build.

## Every document opens with four tabs
- Right after the title: **Does · Doesn't · Limitations · Top issues**.
  - **Does** (3–5): outcomes (Overview) · what components handle (Technical) · tasks users can do (User guide).
  - **Doesn't** (3–5): out of scope by design.
  - **Limitations** (real ones, ≤5): constraints inside the scope ("refreshed daily 06:00", "uploads ≤50 MB"). Only here.
  - **Top issues:** exactly min(10, open Must + Should), review order, one line + status; none `Fixed since review`. None → leave empty; the build names the other items.
- **Subtitle:** `<stack> · <schedule> · <source> → <outputs>` (two `·`, one `→`; no schedule → "on demand").
- Markdown / Confluence: four short headed lists, same order.

## Last section of every document: "Known issues, assumptions, and decisions needed"
- The body describes intended, current behaviour. Defects, fix effort and approvals only here. Owner's voice (global Author voice): open points as facts ("Not yet tested in production", "Owner to decide: retention"); build WARNs `chat voice`.
- Sources: **one code review**, named in `review` (any `reviews/` folder; several and unclear → ask) · failing tests · graph `possible_issue` (Not verified) · code vs docs conflicts · assumptions made.
- **Severity** (`sev`): from the review, its order kept; Critical/High → Must, Medium → Should, rest → Other; its questions → Question. No review → each issue's `kind` fixes `sev` (rubric: `spec.md`).
- **Status:** one of the fixed list (`spec.md` → Statuses). Confirm only what a review, test (`test` = `path::name` or command) or the cited code proves; a made-up excerpt → `Not verified`.
- **The accuracy reviewer opens each Must/Should `where`:** fixed in code → `Fixed since review`, out of Top issues. Never copy a fixed issue as Confirmed. `review X is older than the last code change` → do this for every item.
- Overview: every top issue in plain words, what it means for the reader; no paths. Technical: `Issue | Where (path:line) | Impact | Status | Suggested fix`, optional `unused`. User guide: only issues a user can hit, "If you see X — do Y".
- Names the issue says are missing → its `absent: [names]` (skips the name check).
- Optional typed tables: `assumptions`, `decisions` (only real ones). Nothing known → "No known issues".

## Files
- One self-contained file per document in `./generated-docs/` (or the user's folder): `overview.html`, `technical.html`, `user-guide.html` (+ `.md` / `.confluence.xhtml`). Never combine, split, or link docs.
- Specs in `generated-docs/_spec/<doc>.json`. The build adds the generator tag (templates version), version stamp (repo commit, graph commit or date + stale count, review) and the `.generated-by-darshan-singh-meel-docs` marker. Markdown/Confluence only: first line `<!-- generated by darshan-singh-meel-docs-v2 -->` and create the marker yourself.
- First time `generated-docs/` is created in a repo, ask once: "Commit generated docs to git?" Committed (Recommended) · Git-ignored (→ `/generated-docs/` in `.gitignore`).
- Scope whole system → from `_combined` to `../<name>-graphs/_combined/generated-docs/`; each related repo → `../<name>-graphs/<repo>/generated-docs/`; copies into other repos need one yes.

## Updating existing docs
- On "Update now" (knowledge-graph docs question, after a graph update; background) or "update the docs"; no Step 0 questions. `python <skill>/references/templates/changed.py --save` before inventory.py, `changed.py` after → edit and accuracy-check only the sections it prints; after a good build `changed.py --done`, then knowledge-graph `update.py --docs done`.
- Rerun inventory.py, then edit only sections covering changed files. Keep diagram ids, box names and groups; a new item joins its existing group; h3s and ER areas follow the new plan.

## The three documents
| Document | For | Depth |
|---|---|---|
| Overview | business, newcomers | one screen per section, no code names, the important 20% |
| Technical | engineers | **complete**: one row per inventory item in its typed table |
| User guide | users of the app or its output | fixed frame, the important 20% of tasks |

- Section names, order and recipes are fixed (`spec.md`). Free: item counts above minimums, boxes, wording.
- **Which sections: only the plan.** `not_applicable` → leave out (including one is an ERROR); `required` the source lacks → keep with "Not defined yet — owner to decide".

**Overview:** What it is and why (`labels` What · Why · Key idea · Result) · How it works (one L0 flow, 3–7 boxes; no steps table) · Who uses it · Example (journey + 2–6 cards, one non-typical) · Value and cost · Schedule · Design and operational risks (≤3) · Words used. L0 boxes: input/actor → one box per entry group of each kind (table below) → output/store.

**Technical:** Overview · Architecture (L2 flow + `components`, one box per top-level module or folder; library: + `api` table, Call · Returns · Raises · Where, one row per `plan.api` name) · the interface sections the plan requires · Main flows · Data model · Business rules · Configuration · Security and access · Deploy and environments · Operations · Performance and limits · Tests · Key decisions.
- **Main flows:** per plan `main_flows` h3 (exact text, order): `h3 ipo flow* io?`. One `ipo` per h3 = Input → Process → Output, each step showing its output:
  - `input` (with its source) · `steps [{do ≤8 words, out, where path:line}]` covering the plan's ordered steps, **≤7**: merge plumbing (parse argv, dispatch, fetch) into the step that produces data, `graph: [k, …]` = the graph steps it covers · `output` (where it lands).
  - `out` names what the step produces with a name or number its `do` lacks ("HTTP request" after "fetch(…)" says nothing).
  - `why` (one clause, shown under `out`, from code, tests or docs, never invented): why the step exists or what breaks if it fails ("downstream joins need one row per key"). Every flow has at least one; required on a step that branches, drops, filters or writes data; never a restatement of its `out` or `branch` (WARN each).
  - `examples`: 2–3 traces through those steps `{case, title, expect, in, at, out, source}`; a = typical, ≥1 edge/rejected/failure. Each `at` cell is the example's value at that step (name, number, status), `"="` only for unchanged from the column before (never at step 1: ERROR), `null` (`–`) not reached or not touched by this example. A trace more than half `=` is a one-step example: put it in the rule's row (WARN). Never "skipped", "sent", "valid", "rows".
  - Flow diagram only if plan `diagram: true` (the flow branches): the diagram draws the branches, never the strip again (a straight chain → ERROR). Its title is the build's: `<h3>, N steps` (names the flow, never a box). Arrows that are strip steps carry `step: k` (shown as the strip's number), branch arrows a label only; the step the branch leaves gets `branch: "<other outcome>"` ("404, nothing stored") and the diagram must draw that branch at arrow k (ERROR). Linear flow = the ipo alone (a one-step alternative also goes in `branch`). `code`/`entry` boxes only plan `boxes` or entry points; sub-flows via `parent`. Field rules: `spec.md` → Blocks · Recipes.
  - Plan h3 wrong (graph mistake) → fix the graph; else `h3_override {plan_h3: {title, why}}`.
- **Coverage:** every item of a `plan.coverage` type (incl. storage locations, business rules, processes) by exact name in visible text — a box label, step or table row. Never in a hover `tip` (not counted); groups have no `tip`. Long names: full name in a table row. A name defined in several places: name each, or the count next to it (`` `var.region` (4 modules) ``). Leave out only via `coverage_skip {name: why}`. Items that say the same thing share one group row: "13 schema files: `a`, `b`, …", or a pattern row ending in `{"covers": [names]}` (counts for coverage; count and names are its hover title: no "(2 graph rules)" in a cell, WARN). Unused and marker files: one group row.
- **Data model** (only if the plan requires it: ≥2 tables/views/dbt models or any fk; else name the table in Architecture `components`): one `er` per plan area, title = the plan's `ER: <area>`, in order; `views` only if the graph has views.
- **Business rules:** one `rules` row per business_rule node: Rule (a phrase a reader understands, never an identifier alone (WARN); graph ids in Where or `covers`) · Example in → out (values) · Why / impact (why it exists, what breaks for whom without it; WARN when empty; never a citation, WARN) · Where (`basename:line`); no examples block. One rule over N entities = one row "… applies to: a, b, c". A rule a Main flows step already shows → `see step 5.1.3`; Where empty, or other lines than the step's. **Operations** (only if the plan requires it: pipeline, dbt, web API, streaming): one `tasks` table (Task · Command · When · Where), one heading row per task with its rows under it; Tasks only `Rerun and backfill` (plan `rerun_and_backfill`) or the plan's `how_tos` (process nodes + `Run the tests`), plan order: the exact text, or plain words with the how-to in Where or `covers`. A how-to that is a flow → point to its Main flows h3. A command Deploy or Commands gives → point there. **Deploy:** every `plan.deploy` unit and `deploys` source in a steps or environments row; one row per file kind (all Dockerfiles in one). **Configuration:** `Default (code) / deploy value`.
- **Repeats:** a repeated pattern → one group "Repeats for each …" + one sub-flow; every member named in a table row (fan-out frames: the build).

**User guide:** How it reaches you · Screens · What answers what · How to … (one per real task) · When data is fresh · History and deletions · Errors and messages · Problems and fixes · Who to contact. No internals; tasks from screens, routes, commands, consumer queries.

## By repo kind (profile in inventory.json)
What goes into the sections the plan picked:

| Kind | Interface section · table | Main flows h3 unit | Data model (if planned) | Diagrams from graph | Example io |
|---|---|---|---|---|---|
| pipeline (Airflow, Spark, jobs) | Job DAG and schedule · `schedule` | job / DAG pattern: source → written data | tables/views on `writes` | dag/job → tasks (`depends_on`, `triggers`, `schedules`) | rendered command or SQL + rows |
| dbt | Job DAG and schedule · `schedule` | layer chain: source → mart | `dbt_model` + `fk` (tables if present) | models by `ref`, lanes per layer | compiled SQL + rows |
| web API | Endpoints · `endpoints` | endpoint group: request → response | tables on handler `writes` | route → handler → store (`exposes`, `calls`, `writes`) | request + response |
| UI / frontend | Screens and navigation · `elements` | user action → screen | the backend's tables | `ui_screen` map + calls to endpoints; journey | action + what shows |
| CLI | Commands · `commands` | command group: command → output | tables it writes | command → functions → output (`calls`) | command + output |
| library | none: public modules in `components`, public calls in `api` | public call → return value | tables it owns | module map (`imports`, `calls`) | `Call` + result |
| infra / Terraform | none: roots in Architecture, `terraform_resource` in `components` | root → cloud resources | tables it defines | root → modules → resources (`deploys`, `depends_on`), lanes per account/env | plan excerpt `+ ~ -` (synthetic: provider behaviour Not verified) |
| ML / streaming | Events and messages · `events` (timers too) | event → score / train → model artefact | feature tables; topics in flows | producer → topic → consumer (`reads`, `writes`); train vs serve lanes | event payload + result |
| config / docs repo | none: folders in Architecture, keys in `config` | change → published / applied | — | `documents`, `configures` edges | config before → after |
| monorepo | union of its kinds | the plan's h3s; with no graph flows, one per entry group = one per kind | union | Architecture: one lane per kind | per kind |

- **Diagrams come from the graph:** boxes = graph nodes with real names (Overview/User guide may add business words in `sub`), arrows = its edges, steps = flow `part_of` steps in order. Show failure/retry paths where the graph or code has them.

## Diagrams
| Show | Use |
|---|---|
| Big picture | L0 flow, 3–7 boxes |
| Order, who does what | L1 flow with lanes, numbered |
| Architecture | L2 flow, lanes per platform/kind, `code` boxes |
| Inside one box | sub-flow (`parent`), max 2 levels, not in Overview |
| Data model | `er` only; views in a table |
| Input → steps → output, examples traced through each step | ipo (Main flows) |
| One record through stages | journey (not in Main flows) |

- Every flow, ER and journey: `id` (A, B… in doc order) + fixed title form (`spec.md` → Diagram ids and titles; Main flows: the build writes it). Steps or area per section: `plan.diagram_titles`.
- One-line `key` + `notice` on each. Boxes: `tag`, 1–3 `bullets`, `in`/`out`, `runs`, `see`. Technical: real names; Overview/User guide: business words. A `decision` box needs ≥2 outgoing arrows.
- Layout is the build's (`spec.md` → Layout). Too wide or crowded → it errors with the fix; follow it.

## Examples
- **Every main flow, rule and user task gets examples.** Source order: tests/fixtures → docs/README → derived from code (`derived from <path:line>`) → synthetic (`synthetic: true`). Cite each (`source`). Realistic, 2–5 rows, no real data, no PII.
- **Repo has tests:** example a of each main flow from a test; ≤⅓ of all examples synthetic (WARN).
- **Every example:** `case` (typical · edge · rejected · failure), `title`, `expect` (one line: what we want), `in`, `out`. The build adds the id (5.1a) — never in `tag`; naming a missing example → ERROR. Never invent a case the code lacks.
- **Where:** Main flows → ipo traces (above) · Business rules → in the rule row · Overview → 2–6 cards that add a case the journey does not show · User guide How to → cards or io for the result and the failure, not the steps again · else cards. Record changing → journey · query/request/command/call/UI action → io.
- Key example missing or data may be sensitive → ask once.

## Writing rules
- **No word target** (build WARNs; `spec.md` → Word budgets): words stay when they carry a fact or insight. Caps only catch prose: lead ≤2 sentences / 40 words · table cell or `why` ≤40 (over: split into fact + why) · ipo step `do` ≤8 · card, strip and trace value ≤12 · no lead that restates the next block.
- **Repeats** (build WARNs `repeat:`): one sentence (≥6 words) in two blocks, one `path:line` in two sections (not Known issues), one command in two sections, a column with one value in ≥70% of its rows, the same cell in 4+ rows. Keep it where the reader looks for it; point from the other ("see step 5.1.3", "Deploy: Run locally"). A column with one value in every row the build says once above the table ("All rows: …").
- One fact per bullet; tables for anything repeated (the build renders 1–2-row and one-column tables as lists). Diagram, then bullets, then example.
- **Fewer tables:** ≤3 tables per section (WARN); merge rows that say the same thing; adjacent tables of one shape render as one. A cell shows ≤6 names, then "+N more" (full list in its hover; still covered). A status in ≥ half the rows is said once ("… unless shown").
- Lead with the conclusion; concrete ("daily 06:00"); explain a needed term once; acronyms spelled out in Overview.
- Accurate: every name, number, command and box matches source; unsure → "unclear — verify". Counts only from `facts.json`: `<N> <fact name>` in the text = its value (WARN).
- Names in backticks, real and exact (never drop backticks to pass the name check); synthetic ones in `ids_skip`. Paths from the repo root; a path with spaces whole in backticks.
- Pattern claims hold for every member; name exceptions.
- State decisions, not deliberation. Only major risks (Overview ≤3, Technical 5–10).
- Banned: intros/outros, restating diagrams, marketing words, padding, emoji.

## Build (HTML)
- Never hand-write HTML, CSS or SVG. Output folder must exist (`mkdir -p` it). Spec → `python <skill>/references/templates/build.py generated-docs/_spec/<doc>.json generated-docs/<doc>.html`. Start from the closest `references/examples/*.json` (pipeline, web app, library, user guides, stress).
- Last line `built <out>: N sections, N WARN (templates <ver>)`. Fix every ERROR and WARN, or explain each remaining WARN in the reply (never in the doc).
- `python <skill>/references/templates/check.py <doc.html> <shots_dir>` → 0 `LAYOUT` lines (`LAYOUT <section> | diagram <id> (map-<n>) | <problem> | <text>`); writes `page.png` + `map-<n>.png` per diagram.
- Builder can't draw it → say so; ask before changing `build.py`.
- Markdown/Confluence: same plan, sections, diagrams (Mermaid / images), examples. Confluence: never upload; one line on how to import. Word/PDF only if asked.

## Other document kinds (`type: "custom"`, same blocks)
- **Code explanation:** what · flow · `Name | Does | Example` · one traced example · top 3 gotchas · "to change X, edit `file:function`".
- **README:** purpose · architecture diagram · quick start with output · 2–3 usage examples · settings table · folder tree · dev commands · `Problem | Fix`.
- **Design doc:** goal + non-goals · current → proposed · components · main flow + example · ER if schemas change · decisions · risks · rollout.
- **Runbook:** what/when/owner + flow · healthy run output · top 5 `Symptom | Cause | Fix` · rerun/backfill commands.
- **From PDF/Word/slides:** what · overview diagram · grouped key points · worked example · requirements table · top 3 gaps.
- **Ported or rewritten code:** `references/html-style.md` → Ported or rewritten code.

## Workflow — fixed, every run: `docs-v2-<repo>`
Step 0 → graph (if chosen) → Step 1 inventory → per document:

| Phase | Model | Does |
|---|---|---|
| 1 Plan | Opus | reads `inventory.json` (plan, profile, flows, items), adds facts, fills the recipes: boxes from graph nodes/edges, sub-flows, examples, issue `kind` → `sev` |
| 2 Build | Sonnet | writes the spec → `build.py` → fixes every ERROR and WARN; opens the code for any claim not in the plan or `facts.json` |
| 3a Auto-check | script | `check.py <doc> <shots_dir>` |
| 3b Accuracy (parallel with 3c) | Opus | every name, number, step vs code and graph; `inventory.py --check-facts` to 0 mismatched; greps every member of each pattern claim; opens each Must/Should `where`; checks each severity and status; author voice: chat leakage → Should (Must if it misstates a fact or exposes chat content) |
| 3c Layout | Haiku | runs `check.py`, reads `page.png` and **every** `map-<n>.png`; fails on any LAYOUT line (crossing near a label, label near a foreign line, arrow on no box, decision with <2 arrows, name broken mid-word, …) or confusing diagram |
| 4 Fix | Sonnet | applies 3a–3c, rebuilds, reruns `check.py` to 0; trims non-essential bullets |
| 5 Re-render | Haiku | only if layout changed: rerun `check.py`, read the changed shots |

- **Done** = 0 ERROR · 0 WARN (or each explained in the reply) · 0 LAYOUT · accuracy pass passed.
- **No subagents:** run 3b yourself as a separate pass after the build; skipped → the reply says "accuracy not reviewed", never "done". Tell the user in one line which model to switch to per phase.
- Never invent another workflow, skip a phase or swap models.
- Read as the audience: Overview as a manager · Technical as a new engineer (could deploy from it alone) · User guide as a first-time user.
- After a Technical doc is built, end the reply with one line: "Architecture review with a proposed target (darshan-singh-meel-architecture)?" — no other unprompted suggestions.

---
name: darshan-singh-meel-docs-v2
description: Docs v2 — darshan-singh-meel-docs on a fixed pipeline: shipped inventory script plans from the knowledge graph (inventory.json), fixed builder renders HTML from a JSON spec (fixed sections, typed tables, diagram ids/titles, required examples), fixed workflow → same code, same-looking docs. Any repo kind (pipelines, dbt, web APIs, UIs, CLIs, libraries, Terraform, ML/streaming, config/docs, monorepos). Only when the user asks for docs v2 / darshan-singh-meel-docs-v2: diagram-first READMEs, code/repo explanations, design docs, user guides, runbooks, KT, data docs, PDF/Word/slide summaries. New docs → ALWAYS 4 questions in one prompt (documents Overview/Technical/User guide · format HTML/Markdown/Confluence · graph first · example source) → one self-contained file per document in ./generated-docs/; refresh after a change → no questions.
---

# Docs v2
Max info, min words; senior architect, anyone follows.
- Show (diagrams · tables · bullets · examples), no prose; numbers + names over prose.
- Each word = fact or insight (what · how · why · number · name · consequence); no word target, cut only empty words. **Each fact once, where the reader looks** (build WARNs `repeat:`, cells down a column too). Cut filler (repeated cells · placeholder rows · constant columns · restatements); add insight: why a step/rule exists · what breaks if it fails · for whom (step `why`, rule Why / impact). Section lead = its main insight, never the heading again. Section → what · how · why (+ who · when · where). Global CLAUDE.md applies.
- Exact rules · fields · columns · titles · ERROR/WARN → `references/templates/spec.md`; build enforces.
- **`<skill>`** = this folder. Its scripts only, never a repo copy (WARN `inventory.json was written by templates X`).

## Step 0 — ask, always
Pre-check (silent): graph (`./<repo>-knowledge-graph/` or `./.knowledge-graph`)? related repos / system graph? → one prompt:
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
- Answer = user's words this session, never defaults · recs · CLAUDE.md · skill text; self-check before any file.
- Single doc <~30 pages → "Skip, read the document directly" first.
- Related repos → next: **Scope** (multi) This repo (rec) · Whole system · Each related repo.
- No answer → 3 docs · HTML · build/update graph · tests+docs, then code · this repo.
- Record Graph answer: graph `update.py --choice now` (update) · `--choice skip` (as is) → no repeat graph question. Docs being built → no docs question after that update.
- Build/update → `darshan-singh-meel-knowledge-graph` first. Skip / no graph → inventory plans from a file scan (no flows, scanned coverage only); reply "planned from a file scan".

## Step 1 — inventory, never own
- Repo root: `python <skill>/references/templates/inventory.py` → `generated-docs/_spec/inventory.json` + `facts.json`; prints `inventory (templates <ver>): …`. Same graph → same bytes.
- No graph → file-scan plan + `note: no knowledge graph: plan from a file scan; build the graph for flows and coverage` (h3 per entry point: CLI program · app · job · package API; nothing ruled out); `.knowledge-graph` → missing folder → ERROR; graph → unchanged. `WARN graph is stale` / graph commit ≠ HEAD → update, rerun. `note:` lines → reply "not checked".
- **Plan = skeleton:** `profile` · `app_types` · required / not_applicable · `main_flows` (h3, order, `diagram`, `entry`, `boxes`) · `diagram_titles` · `how_tos` · `deploy` · `rerun_and_backfill` · `api` (library) · ER areas · coverage. Copy, never re-derive.
- `facts.json`: 3 plan counts, yours kept. Other numbers → `{fact, value, how}`; `how` = one POSIX line, repo root (Git Bash).
- Then `python <skill>/references/templates/inventory.py --check-facts` → 0 `MISMATCH` / `NOT RUN` before build.

## Opening tabs
- After title: **Does · Doesn't · Limitations · Top issues**.
  - Does 3–5: outcomes (Overview) · components (Technical) · user tasks (User guide). Doesn't 3–5: out of scope by design. Limitations ≤5, real, in scope ("daily 06:00", "≤50 MB"), only here.
  - Top issues = min(10, open Must + Should), review order, line + status, no `Fixed since review`; none → empty (build names others).
- Subtitle `<stack> · <schedule> · <source> → <outputs>` (2 `·`, 1 `→`; none → "on demand").
- Md/Confluence: 4 headed lists.

## Last section: "Known issues, assumptions, and decisions needed"
- Defects · effort · approvals only here; body = intended current behaviour. Owner's voice (global Author voice): open points as facts ("Not yet tested in production", "Owner to decide: retention"); build WARN `chat voice`.
- Sources: **one review** in `review` (any `reviews/`; several + unclear → ask) · failing tests · graph `possible_issue` (Not verified) · code ≠ docs · assumptions.
- **`sev`:** review order; Critical/High → Must, Medium → Should, rest → Other, questions → Question. No review → `kind` fixes `sev` (rubric: `spec.md`).
- **Status:** fixed list (`spec.md` → Statuses); confirm only what review · test (`test` = `path::name`/command) · cited code proves; made-up excerpt → `Not verified`.
- Accuracy pass opens each Must/Should `where`: fixed → `Fixed since review`, out of Top issues, never Confirmed; `review X is older than the last code change` → every item.
- Overview: top issues in plain words + reader impact, no paths. Technical: `Issue | Where (path:line) | Impact | Status | Suggested fix` (+ `unused`). User guide: user-hit only, "If you see X — do Y".
- Names issue says missing → `absent: [names]` (no name check).
- Optional `assumptions`, `decisions` (real). Nothing → "No known issues".

## Files
- `./generated-docs/` (or user's): `overview.html` · `technical.html` · `user-guide.html` (+ `.md` / `.confluence.xhtml`), one self-contained file each; never combine, split, link.
- Specs `generated-docs/_spec/<doc>.json`. Build adds generator (templates ver) · stamp (repo commit, graph commit or date + stale count, review) · `.generated-by-darshan-singh-meel-docs`. Md/Confluence: first line `<!-- generated by darshan-singh-meel-docs-v2 -->` + marker yourself.
- First `generated-docs/` → ask once "Commit generated docs to git?" Committed (rec) · Git-ignored (`/generated-docs/` → `.gitignore`).
- Whole system: `_combined` → `../<name>-graphs/_combined/generated-docs/`; each repo → `../<name>-graphs/<repo>/generated-docs/`; other repos → one yes.

## Updating
- "Update now" (graph's docs question, background) / "update the docs" → no Step 0; `templates/changed.py --save` → rerun inventory → `changed.py` → edit + accuracy-check only its sections → good build → `changed.py --done` → graph `update.py --docs done`. Keep diagram ids · box names · groups; new item → its group; h3s + ER areas → new plan.

## Documents
- **Overview** (business, newcomers): screen per section, no code names, top 20%. **Technical** (engineers): **complete**, row per inventory item in its typed table. **User guide** (app/output users): fixed frame, top 20% of tasks.
- Names · order · recipes fixed (`spec.md`); free: counts above minimums · boxes · wording.
- **Sections = plan only.** `not_applicable` → out (else ERROR); `required`, no source → "Not defined yet — owner to decide".

**Overview:** What it is and why (`labels` What · Why · Key idea · Result) · How it works (one L0 flow, 3–7 boxes, no steps) · Who uses it · Example (journey + 2–6 cards, ≥1 non-typical) · Value and cost · Schedule · Design and operational risks (≤3) · Words used. L0: input/actor → box per entry group per kind → output/store.

**Technical:** Overview · Architecture (L2 flow + `components`, box per top-level module/folder; library + `api` table Call · Returns · Raises · Where, row per `plan.api`) · plan's interface sections · Main flows · Data model · Business rules · Configuration · Security and access · Deploy and environments · Operations · Performance and limits · Tests · Key decisions.
- **Main flows:** per `main_flows` h3 (exact, order): `h3 ipo flow* io?`. `ipo` = Input → Process → Output, output at each step: `input` (+ source) · `steps [{do ≤8 words, out, where path:line}]` covering plan steps, **≤7** (plumbing → merged, `graph: [k, …]`) · `output` (where it lands) · `examples` 2–3 traces `{case, title, expect, in, at, out, source}`; a = typical, ≥1 edge/rejected/failure.
- `out` = name/number not in `do`. `why` (one clause, under `out`; from code · tests · docs, never invented): why the step exists / what breaks if it fails. WARN: flow without any `why` · branch/drop/filter/write step without · `why` restating `out`/`branch`.
- `at` cell = example value (name · number · status) · `"="` only unchanged from the column before (step 1 → ERROR) · `null` (`–`) not reached / not touched by this example; row >½ `=` → one-step example → rule row (WARN); never skipped · sent · valid · rows.
- Flow only if `diagram: true` (branches): title by build `<h3>, N steps` (flow, never a box); diagram = branches, never the strip again (straight chain → ERROR); strip-step arrows `step: k` (shown as strip number k), branch arrows label only; strip = main path, branch step `branch: "<other outcome>"`, drawn at arrow k (ERROR otherwise). Linear → ipo alone (one-step alternative → `branch`). `code`/`entry` boxes = plan `boxes` or entry points; sub-flows `parent`. Fields → `spec.md`. Wrong h3 → fix graph; else `h3_override {plan_h3: {title, why}}`.
- **Coverage:** each `plan.coverage` item (incl. storage locations · business rules · processes), exact name, visible (box · step · row); `tip` uncounted; groups no `tip`. Long name → row. Several definitions → each, or count (`` `var.region` (4 modules) ``). Skip only `coverage_skip {name: why}`. Same-saying items → one group row: "13 schema files: `a`, `b`, …" or pattern + `{"covers": [names]}` (counted; count + names = hover title; "(2 graph rules)" in a cell → WARN). Unused/marker files → one group row.
- **Data model** (plan only: ≥2 tables/views/dbt models or any fk; else table in Architecture `components`): `er` per plan area, title `ER: <area>`, in order; `views` only if graph has views.
- **Rules:** `rules` row per business_rule: Rule (reader's phrase; identifier alone → WARN; graph ids → Where / `covers`) · Example in → out (values) · Why / impact (why it exists · what breaks, for whom; WARN empty; citation → WARN, goes in Where) · Where (`basename:line`); no examples block; one rule over N entities = one row "… applies to: a, b"; shown by a Main flows step → `see step 5.1.3`, Where empty or other lines than the step's. **Operations** (plan only: pipeline · dbt · web API · streaming): one `tasks` table (Task · Command · When · Where), heading row per task, its rows under it; Tasks only `Rerun and backfill` (`rerun_and_backfill`) · `how_tos` (processes + `Run the tests`), plan order: exact, or plain words + how-to in Where / `covers`; how-to that is a flow → point to its Main flows h3; Deploy/Commands command → point there. **Deploy:** each `plan.deploy` unit + `deploys` source in a steps/environments row; row per file kind (Dockerfiles one). **Configuration:** `Default (code) / deploy value`.
- **Repeats:** pattern → group "Repeats for each …" + one sub-flow; each member in a row (fan-out frame: build).

**User guide:** How it reaches you · Screens · What answers what · How to … (per real task) · When data is fresh · History and deletions · Errors and messages · Problems and fixes · Who to contact. No internals; tasks from screens · routes · commands · consumer queries.

## By `profile` kind
Interface section · table | h3 unit | data model | graph diagram | io:
- **pipeline** (Airflow, Spark, jobs): Job DAG and schedule · `schedule` | job/DAG pattern: source → written data | tables/views on `writes` | dag/job → tasks (`depends_on`, `triggers`, `schedules`) | rendered command/SQL + rows
- **dbt**: Job DAG and schedule · `schedule` | layer chain: source → mart | `dbt_model` + `fk` (+ tables) | models by `ref`, lane per layer | compiled SQL + rows
- **web API**: Endpoints · `endpoints` | endpoint group: request → response | handler `writes` tables | route → handler → store (`exposes`, `calls`, `writes`) | request + response
- **UI**: Screens and navigation · `elements` | user action → screen | backend tables | `ui_screen` map + endpoint calls; journey | action + what shows
- **CLI**: Commands · `commands` | command group → output | written tables | command → functions → output (`calls`) | command + output
- **library**: none, public modules in `components`, calls in `api` | public call → return | owned tables | module map (`imports`, `calls`) | `Call` + result
- **Terraform**: none, roots in Architecture, `terraform_resource` in `components` | root → cloud resources | defined tables | root → modules → resources (`deploys`, `depends_on`), lane per account/env | plan excerpt `+ ~ -` (synthetic: provider behaviour Not verified)
- **ML/streaming**: Events and messages · `events` (+ timers) | event → score / train → model artefact | feature tables; topics in flows | producer → topic → consumer (`reads`, `writes`); train vs serve lanes | event payload + result
- **config/docs**: none, folders in Architecture, keys in `config` | change → published/applied | — | `documents`, `configures` | config before → after
- **monorepo**: union | plan's h3s; no graph flows → one per entry group = per kind | union | lane per kind | per kind
- Boxes = graph nodes, real names (Overview/User guide: business words in `sub`) · arrows = edges · steps = `part_of` order · failure/retry paths where graph/code has them.

## Diagrams
- Big picture → L0, 3–7 boxes · order/who → L1, lanes, numbered · architecture → L2, lanes per platform/kind, `code` boxes · inside a box → sub-flow (`parent`), ≤2 levels, not Overview · data model → `er` only, views in table · input → steps → output + traced examples → ipo (Main flows) · one record through stages → journey (not Main flows).
- Flow · ER · journey: `id` (A, B… doc order) + title form (`spec.md`; Main flows: build). Steps/area: `plan.diagram_titles`.
- One-line `key` + `notice`. Boxes: `tag` · 1–3 `bullets` · `in`/`out` · `runs` · `see`. Technical real names; others business words. `decision` → ≥2 out-arrows.
- Layout = build's (`spec.md` → Layout); too wide/crowded → ERROR with fix; follow it.

## Examples
- **Every main flow · rule · user task.** Order: tests/fixtures → docs/README → code (`derived from <path:line>`) → `synthetic: true`. Cite `source`. Realistic, 2–5 rows, no real data/PII.
- Tests exist → example a per main flow from a test; ≤⅓ synthetic (WARN).
- **Each:** `case` (typical · edge · rejected · failure) · `title` · `expect` (one line, wanted) · `in` · `out`. Build adds id (5.1a), none in `tag`; missing example named → ERROR; no case code lacks.
- Main flows → ipo traces · rules → in the row · Overview 2–6 cards, a case the journey lacks · How to → result + failure, not the steps again · else cards. Record changing → journey · query/request/command/call/UI action → io.
- Key example missing / sensitive → ask once.

## Writing
- **No word target** (build WARNs, `spec.md`): words stay if fact or insight. Caps catch prose only: lead ≤2 sentences/40 words · cell / `why` ≤40 (over → split fact + why) · ipo `do` ≤8 · card/strip/trace value ≤12 · no lead restating next block.
- **Repeats** (WARN `repeat:`): sentence ≥6 words in 2 blocks · `path:line` in 2 sections (not Known issues) · command in 2 sections · column one value in ≥70% rows · same cell in 4+ rows → keep where read, point from the other / group. Column one value in all rows → build says it once ("All rows: …").
- One fact per bullet; repeats → tables (1–2 rows · one column → build lists); diagram → bullets → example.
- **Fewer tables:** ≤3 per section (WARN) · same-saying rows merged · adjacent same-shape tables → one (build) · cell ≤6 names, rest "+N more" in hover (still covered) · status in ≥½ rows → said once ("… unless shown"). Conclusion first, concrete ("daily 06:00"), term once, Overview spells acronyms.
- Names · numbers · commands · boxes match source; unsure → "unclear — verify". Counts only `facts.json`: `<N> <fact name>` = its value (WARN).
- Names in backticks, real, exact (keep backticks); synthetic → `ids_skip`. Paths from repo root; spaces → whole in backticks.
- Pattern claims hold for all; name exceptions. Decisions, not deliberation. Major risks only (Overview ≤3, Technical 5–10).
- Banned: intros/outros · restating diagrams · marketing · padding · emoji.

## Build (HTML)
- Never hand-write HTML/CSS/SVG. Output folder exists (`mkdir -p`). `python <skill>/references/templates/build.py generated-docs/_spec/<doc>.json generated-docs/<doc>.html`; start from closest `references/examples/*.json` (pipeline, web app, library, user guides, stress).
- Last line `built <out>: N sections, N WARN (templates <ver>)`. Fix each ERROR + WARN, or explain WARN in reply (never doc).
- `python <skill>/references/templates/check.py <doc.html> <shots_dir>` → 0 `LAYOUT` (`LAYOUT <section> | diagram <id> (map-<n>) | <problem> | <text>`); writes `page.png` + `map-<n>.png`.
- Can't draw → say so; ask before changing `build.py`.
- Md/Confluence: same plan · sections · diagrams (Mermaid/images) · examples. Confluence: never upload; one import line. Word/PDF only if asked.

## Other kinds (`type: "custom"`)
- **Code explanation:** what · flow · `Name | Does | Example` · traced example · top 3 gotchas · "to change X, edit `file:function`".
- **README:** purpose · architecture diagram · quick start + output · 2–3 usages · settings · folder tree · dev commands · `Problem | Fix`.
- **Design doc:** goal + non-goals · current → proposed · components · main flow + example · ER if schemas change · decisions · risks · rollout.
- **Runbook:** what/when/owner + flow · healthy output · top 5 `Symptom | Cause | Fix` · rerun/backfill commands.
- **PDF/Word/slides:** what · overview diagram · key points · worked example · requirements · top 3 gaps.
- **Ported/rewritten code:** `references/html-style.md`.

## Workflow — fixed: `docs-v2-<repo>`
Step 0 → graph (if chosen) → Step 1 → per doc:
1. **Plan** (Opus): `inventory.json` → facts · recipes (boxes from graph nodes/edges, sub-flows, examples, `kind` → `sev`).
2. **Build** (Sonnet): spec → `build.py` → fix all ERROR + WARN; claims outside plan/`facts.json` → open code.
3. a **Auto-check** (script): `check.py <doc> <shots_dir>`. b **Accuracy** (Opus, ∥ c): names · numbers · steps vs code + graph; `inventory.py --check-facts` to 0; grep each pattern member; open each Must/Should `where`; check severity + status; author voice: chat leakage → Should (Must: misstated fact · exposed chat content). c **Layout** (Haiku): `check.py`, read `page.png` + **every** `map-<n>.png`; fail on any LAYOUT (crossing near label, label near foreign line, arrow on no box, decision <2 arrows, name broken mid-word, …) or confusing diagram.
4. **Fix** (Sonnet): apply 3a–c, rebuild, `check.py` to 0; trim bullets.
5. **Re-render** (Haiku), layout changed only: `check.py`, read changed shots.
- **Done** = 0 ERROR · 0 WARN (or explained in reply) · 0 LAYOUT · accuracy passed.
- No subagents → 3b yourself, separate pass; skipped → "accuracy not reviewed", never "done". Tell user model per phase, one line.
- Never another workflow · skipped phase · swapped model. Read as manager · new engineer (could deploy from it alone) · first-time user.
- Technical doc built → reply ends with one line: "Architecture review with a proposed target (darshan-singh-meel-architecture)?" No other unprompted suggestion.

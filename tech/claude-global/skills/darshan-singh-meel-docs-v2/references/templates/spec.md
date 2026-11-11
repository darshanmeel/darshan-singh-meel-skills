# Doc spec — input to build.py
`<skill>` = the folder of the loaded skill (never a copy inside the repo: a copied builder is out of date). All commands run from the repo root.
First, once per run: `python <skill>/references/templates/inventory.py` → `generated-docs/_spec/inventory.json` + `facts.json` (never write your own inventory script; no graph → a plan from a stdlib file scan and `note: no knowledge graph: plan from a file scan; build the graph for flows and coverage`; a `.knowledge-graph` pointer to a missing folder → ERROR). It prints `inventory (templates <version>): …`, and `WARN graph is stale: N files changed since it was built (…)` when the graph's `meta.json` file hashes no longer match the repo: update the graph, then rerun.
Rerun every fact: `python <skill>/references/templates/inventory.py --check-facts` → `ok <fact> = <value>` or `MISMATCH <fact>: facts.json says X, how printed Y` per fact, exit 1 on any mismatch. A `how` without shell syntax runs directly (`python` = the running Python); one with pipes, globs or redirects runs in a POSIX `sh` (on Windows Git for Windows' own, never WSL's `bash`; none → `NOT RUN`).
Build: `python <skill>/references/templates/build.py generated-docs/_spec/<doc>.json generated-docs/<doc>.html` (reads `inventory.json` next to the spec; the output folder must exist, else `ERROR output folder X does not exist`).
Layout check after every build: `python <skill>/references/templates/check.py <doc.html> <shots_dir>` — opens every `details`, renders at 1280 px and at 390 px (phone: sideways scroll, the ipo strip, example traces and every table: rows stack as labelled blocks, nothing may scroll or be cut); must report 0 problems (overflow, overlaps, labels on boxes or frames, edges through boxes, frames or group labels, edges on top of each other or <20 px apart (lines leaving one point may share parts that start at one point: a branch), more than 3 line crossings in one diagram, a line crossing <12 px from a label or number, a label or number <6 px from a line that is not its own, an arrow that starts or ends on no box (a group frame border, empty space), a decision box with fewer than 2 outgoing arrows, a name broken mid-word in a box or table cell, arrow ends <12 px apart on one box side, lines crossing a group border <20 px apart, cut-off values, diagrams, journeys, tables or ipo strips wider than the page, sideways scroll, an example trace row hidden at 1280 px (`example 5.1b hidden (N of M example rows shown)`); at 390 px the problem says `at 390px`). It writes `page.png` and one `map-<n>.png` per diagram: the layout reviewer reads every one. Each line: `LAYOUT <section> | diagram <id> (map-<n>) | <problem> | <text>` (no diagram part outside diagrams).
Working specs + rendered results: `../examples/` (list at the end). Copy the closest one.

## inventory.json (written by inventory.py; same graph → byte-identical file)
| Field | Holds |
|---|---|
| `how`, `templates`, `graph`, `scan`, `graph_commit`, `graph_built`, `stale_files` | the command that wrote it · version of the templates that wrote it (build.py WARNs when its own differs) · graph folder (relative; outside the repo: its folder name only; `""` without a graph) · `true` = planned from a file scan (below) · graph `meta.json` commit (hex only) and build date · repo files changed since the graph was built |
| `counts` | `nodes`, `edges`, `by_type` |
| `profile` | `[{kind, evidence}]`, kinds from node types: pipeline (a dag outside CI, a job with tasks, or a `schedules` edge into a job, dag or task; an in-process timer is not one) · dbt · web_api · ui · cli · library · infra · streaming · ml · docs_config |
| `items` | `{node type: [{name, path, line, ci?}]}`, sorted by path, line, name; tests, fixtures, files, folders, columns and private modules left out (a process, flow or document is never a test: a test-tagged process stays); `ci: true` = CI or compose job or task (not covered; named in Deploy) |
| `flows` | flow and process nodes `[{name, path, line, id, type, ordered, branches, steps: [{name, type, text, evidence}]}]`; `ordered` = the graph gives one order (a numbered steps list, a step number on every `part_of` edge, or the one order the `calls`/`reads`/… edges between the steps allow); `branches` = a step is a `decision` (`branch`, `condition`) or leads to 2+ other steps of the flow; endpoint flows first, then job/dag, cli, ui, other |
| `entry_points` | `[{group, name, path, line}]`, group: job · endpoint · cli_command · ui_screen · terraform_root · public_module |
| `data_objects`, `fks` | tables, views, dbt models, storage locations `[{type, name, path, line, columns}]` · fk edges `[{from: child, to: parent}]` |
| `tests` | test files: test_case, file, function, module or class nodes on a test path (data fixtures, processes and flows left out) |
| `plan` | the fixed skeleton, below |
| `not_checked` | what a sparse graph could not give |

**No graph → file scan** (graph present: unchanged). Repo files (git tracked + untracked, else a walk; tool, graph and secret files left out) become graph-shaped items: entry points by convention (`dags/*.py` → job · `routes/`, `routers/`, `endpoints/`, `controllers/`, `views/*.py`, `app.py`, `server.*` → endpoint · `cli.py`, `__main__.py`, `main.py`, `manage.py`, `bin/*`, pyproject `[project.scripts]` → cli_command · `pages/`, `screens/`, `App.tsx` → ui_screen · `dbt_project.yml` + `models/**/*.sql` → dbt_model · folders with `*.tf` outside `modules/` → Terraform root), config files, CI files (Deploy units), test files, code modules and their top-level public functions and classes (Python `ast`). No flows, tables, fks or business rules. Plan: Main flows = one h3 per entry point `<name>: <group> → <output>`: a CLI program (its pyproject script, `cli.py` and `__main__.py` merged; named by the script), an app (its routes or screens, by top package), a job, a Terraform root, a package's public API (modules with a public function or class; CLI files and `_private` modules left out); `files` lists what each covers (no diagram, no step count) · no section ruled out (`not_applicable` empty: the scan cannot tell absent from unscanned) · coverage = the scanned types only. The build prints `note: inventory.json is from a file scan`.

**plan** — the build enforces it:
- `app_types` → the spec's `app_types` (WARN if they differ). `sections.<doc type>`: `required` (WARN if missing) and `not_applicable {section: reason}`.
- **Sections that don't apply: leave them out.** A section in `not_applicable` → ERROR. (No "not applicable" placeholder sections.)
- `main_flows [{h3, flow, steps, ordered, diagram, entry, boxes}]`: the technical Main flows h3 titles, exactly and in this order (ERROR otherwise). One per graph `flow` node; no flow nodes → one per entry-point group. h3 = the flow name if it has `→`, else `<name>: <a> → <z>` from its summary, else `<name> → <last step>` when the steps are ordered and the last is an output (table, view, dbt model, store, external system, screen), else the name alone. Never a step function name, never a made-up order. `diagram: true` (the flow `branches`) → the h3 needs a flow diagram showing the branches, and the strip shows the main path with the step the branch leaves marked (`branch`, WARN otherwise); `false` (linear: its ipo strip shows it) → no flow diagram (ERROR either way). `steps` = the ordered graph steps (`boxes`, in order): the ipo steps cover them in order, one each or a step with `graph: [k, …]` merging consecutive ones (plumbing such as parse argv, dispatch, fetch folds into the step that produces data); WARN otherwise. At most 7 ipo steps (WARN). `entry` = its first step; when that is over 40 chars or another diagram's entry too, the flow name up to its first `:` or `→` (still shared: the h3). `boxes` = the flow's step names: the only names for its `code` and `entry` boxes (besides entry points).
- A plan h3 is wrong (graph mistake)? Better: fix the graph. Else `"h3_override": {"<plan h3>": {"title": "<shown h3>", "why": "<what the graph gets wrong>"}}` → printed as a `note:`; without `title` and `why`, or a key that is no plan h3 → ERROR.
- `how_tos`: process node names, plus one `Run the tests` for all test-tagged processes (tag `test` or a test path) — every one a Task in the Operations `tasks` table (WARN if missing), the only tasks besides "Rerun and backfill". Empty when Operations does not apply. `rerun_and_backfill`: true for pipeline and dbt repos only.
- `deploy {units, deploys}`: CI and compose jobs and tasks (not CI action references `owner/action@v4`), and `deploys` edges (`a → b`, not from Terraform resources) from the graph. Deploy and environments names each unit and each edge's source as whole words (WARN otherwise); both empty → "Not defined in source — confirm with owner".
- `diagram_titles {doc: {section: steps|area}}`: title form of every top-level flow outside technical Main flows (ERROR otherwise): `steps` = numbered, `<entry>, N steps`; `area` = `numbered: false`, `<area> area`. Technical: Overview steps for a scheduled repo (pipeline, dbt or a Terraform scheduler), else area · Architecture, Screens and navigation, Endpoints, Commands, Events and messages area · Job DAG and schedule, Deploy and environments steps. Overview: How it works steps. User guide: How it reaches you, When data is fresh steps · Screens, What answers what area. Without a plan the same table from `app_types`.
- `api [{type, name, path, line}]` (library only): public functions and classes (public module, no name part starting `_`, dotted only as `Class.method`). Coverage type `api`: each name in the Call column of the Architecture `api` table (WARN if the table is missing).
- `er_areas [{name, title, tables}]`: the technical Data model ER titles (`ER: <area>`), exactly and in this order (ERROR otherwise). Area = one root table (no fk parent) plus all its descendants, inventory order; neighbouring areas merge while ≤9 tables; a bigger area is cut into parts of 9.
- `sections.technical.required`: Overview, Architecture, Main flows, Deploy and environments; + Business rules when the graph has business_rule nodes (not in a docs/config repo); + the per-kind sections. Operations: required for services and pipelines (pipeline, dbt, web_api, streaming), not applicable otherwise (name each process in Deploy or Tests). Data model: required with ≥2 tables, views or dbt models or any fk; one table and no fk → not applicable (name it in Architecture components). Job DAG and schedule: also for a Terraform-defined scheduler (`schedules` edge from a `terraform_resource`).
- `coverage`: node types whose every item (by exact name) must be in the technical doc's visible text: flow, config, test_file (= every path in `tests`); per kind job/dag/task, dbt_model, table/view, endpoint, ui_screen, cli_command, terraform_resource, module + api (library); storage_location, business_rule (not docs/config) and process when the graph has them.
- `inventory.json` from an older graph commit than the graph's `meta.json` → WARN: rerun inventory.py. Written by other templates → `WARN inventory.json was written by templates X, this build.py is Y: rerun … from the loaded skill's folder (never a copy inside the repo)`. Graph commit ≠ repo HEAD, or stale files → WARN: update the graph. A broken file → WARN `<what> not checked`.

```json
{"type": "overview | technical | user-guide | custom",
 "app_types": ["pipeline", "ui", "api", "cli", "events"],
 "title": "…", "subtitle": "<stack> · <schedule> · <source> → <outputs>",
 "review": "reviews/<file>",
 "ids_skip": ["synthetic_name"], "coverage_skip": {"<graph name>": "why it is left out"},
 "tabs": {"does": [], "doesnt": [], "limitations": [], "top_issues": [{"text": "…", "status": "<status>"}]},
 "h3_override": {"<plan h3>": {"title": "…", "why": "…"}},
 "sections": {"<section name>": [<block>, …]}}
```
- `app_types`: the plan's `app_types` (without an inventory: everything that applies). Drives the required sections below.
- `subtitle`: `<stack> · <schedule> · <source> → <outputs>` — two `·`, one `→` (WARN otherwise).
- `review`: the newest **code** review the known issues come from (several and unclear → ask the user). Shown under Known issues and in the stamp. Review files are found in every `reviews/` folder of the repo. WARN if one exists and none is named, if the named one is missing, or `review X is older than the last code change` (review date = its git commit, else a YYYY-MM-DD in its name or first 60 lines, else a `has no date` WARN; code date = newest commit outside `reviews/` and `generated-docs/`) → open each Must/Should `where`: fixed in code → status `Fixed since review`, out of Top issues.
- **Statuses** (issues and top issues), exactly one of (ERROR otherwise): `Confirmed (review)` = the review found it and it is still in the code · `Confirmed (test)` = a test or a run proved it: the issue's `test` names it (`tests/x.py::test_y` or the command; shown under the status; missing → ERROR) · `Confirmed (code)` = the cited code shows it (opened and read) · `Not verified` = nobody proved it · `Fixed since review` = fixed in code after the review. Without a named `review`, `Confirmed (review)` and `Fixed since review` → ERROR, and Known issues says "No code review: severity by the fixed rubric; Confirmed only where a test or the code proves it".
- **Severity** (`sev`): from a review: its own order, Critical/High → Must, Medium → Should, the rest → Other. **No review → `kind` fixes `sev`** (ERROR when `kind` is missing or `sev` differs):

| kind | sev | for |
|---|---|---|
| `security` · `data_loss` · `wrong_result` · `crash` | Must | a hole or leak · data lost or never written · a wrong value, count or row on any path · a crash or hang on valid input |
| `missing_handling` · `config` · `performance` · `cost` | Should | a missing check, retry, error handling (traceback or 500 on bad input) · a wrong or risky setting, image or deploy value · slow · wasted spend |
| `unclear_intent` · `docs_conflict` | Question | intent unclear from code and docs · code and docs disagree |
| `style` · `dead_code` · `docs` · `test_gap` | Other | naming, deprecated calls · unused code · docs only · a missing or weak test |

- **`absent`** (issue, optional): names the issue says do not exist (`"absent": ["retry_config"]`): not looked up by the name check; one that is in the repo → WARN.
- **Top issues** (every doc type): exactly min(10, open Must + Should) items, each also in the issues table, none `Fixed since review` (WARN otherwise). Empty → the tab says "No open Must or Should issue[ (not reviewed)]: N other items under Known issues" ("No known issues" only when none is listed).
- **Build output:** `ERROR` lines (wrong block, wrong order, wrong labels, wrong row length, bad citation, hand-shortened name, diagram ids or titles, example fields, plan mismatch, unknown type or block) stop the build. `WARN` lines (missing section, below a minimum, review, unknown name, coverage, top issues, subtitle, absolute paths, facts) → fix, or explain each in the doc. The last line counts them: `built <out>: N sections, N WARN`.
- **Word budgets** (WARN `words: <section>: N <what> over <max> words (longest K: '…')`; no word target: a short cell is not the aim, a cell with no fact is): lead `text` ≤2 sentences and ≤40 words · table cell (typed tables, `table`, `steps`, issues) and step `why` ≤40 words (over: it holds two facts, split it into fact + why) · ipo step `do` ≤8 words · card, ipo strip and trace value ≤12 words (each `[[k, v]]` value apart) · a lead whose backticked names (2+) are ≥60% in the next block only restates it (WARN). Keep the fact, names and numbers; cut the prose.
- **Say each fact once, where the reader looks for it** (WARN `repeat: …`): the same sentence (≥6 words; quoted UI text and paths left out) in two blocks · the same `path:line` in two sections (Known issues left out: an issue's `where` is its proof; a Business rule citing a Main flows step's lines → point to the step) · the same shell command (2+ words) in two sections → give it once, point to it from the other · table cells: see Columns said once (Typed tables). A linear Main flow is its ipo alone; a Main flows diagram only shows branches. `ipo` in a key, notice, lead or bullet → WARN (readers see "step").
- **facts.json** (next to the spec): `{"facts": [{fact, value, how}]}`; inventory.py writes three plan counts, each with a runnable `python -c "import json; d = json.load(open('generated-docs/_spec/inventory.json', encoding='utf-8')); print(…)"` how, and keeps every fact you added when it reruns. Add every other number the doc states, each with a `how`: one POSIX shell line that reruns from the repo root and prints the value last (`<skill>/…` allowed; rerun all with `inventory.py --check-facts`). The how is split as a shell does; only tokens with `/` and no backslash count as paths (a regex `a\.py` is none). Missing file, or a path outside the repo, absolute or missing → WARN. **Text vs facts:** a number followed by a fact's name in the visible text (`12 test files`; the fact name without its `(…)`, any case; headings and the contents list skipped) must be that fact's value, or the value of a fact whose name holds that name (a sub-count: `6 views` with a fact `views with deletion_time` = 6) → else WARN. Or say so: `10 of 11 endpoints`.
- **Checked against the repo** (run from the repo root; repo files = `git ls-files` tracked + untracked, else every file under the cwd; the output and `_spec/` folders, the graph, `reviews/`, `analysis/` and secret files are never searched):
  - **Citations:** every path in `source`, issues `where` (not `fix`), a typed table's `Where` column, and any `` `path[:line]` `` in text; a path with spaces counts only in backticks, whole (`` `My Folder/app.py:12` ``). Path not in the repo, absolute, or with `..` → ERROR (with "did you mean" for a path not from the root). Line or range end past the end of the file → ERROR. A bare file name matching 0 or 2+ files → WARN "use the repo path". **Paths are always from the repo root.** A path inside the graph folder (`data/model.json`) is accepted. In `rules`, `issues` and `unused` rows the cited lines must hold at least one of the row's backticked names → else WARN. Any absolute or machine path in any spec string (`C:\`, `/Users/`, `/home/`, `~/`) → WARN.
  - **Names:** every backticked token with `_`, 8+ chars, no space, `/`, `<`, `{` or `*` (`f(x)` → `f`) must occur in the repo as a whole word, same case (`module.func`, `schema.table`: each part may stand alone; a file name, a repo path suffix or a folder (`frontend/src/pages`) counts; `METHOD /path` matches its path words; ALL_CAPS names and external system names match in any case, e.g. `Postgres`; any inventory item, flow or entry point name counts, e.g. a graph command `npm run dev`; every other name keeps its case) → else WARN. In technical docs the label of every `code`, `data` and `entry` box too: use the real name. Intended synthetic names go in `ids_skip`; names an issue says are missing go in its `absent`. Secret files and folders are never read.
  - **Coverage (technical only):** every inventory item of a `plan.coverage` type must appear **by its exact name in visible text** (text, tables, steps, box labels — hover tips do not count, so a long name shortened in a box also goes in a table row; names a capped cell moves to its hover title do count), or in a group row's `covers` (Typed tables) → else one WARN per type listing the missing names. Unused or marker files that say the same thing: one group row, not one row each. Names with fewer than 2 letters or digits are skipped. A name defined in several places (`(N definitions)` in the WARN) needs each definition named, or the count within 40 chars of it (`` `var.region` (4 modules) ``) → else WARN. Leave one out on purpose: `coverage_skip {name: why}`. No inventory → WARN `coverage not checked: <why>` (no graph: inventory.py still writes a file-scan inventory) (other doc types: `plan not checked: <why>`); never silent.
  - **Examples:** with test files in the repo, example a of a Main flows h3 synthetic → WARN; more than a third of all examples (cards and traces) synthetic → WARN (take cases from tests and fixtures first). Text naming an "Example 5.1x" the doc does not have → ERROR.
  - No repo files under the cwd (e.g. an example built in an empty folder) → a `note:` line; these checks are skipped. build.py run from a copy inside the documented repo → `note:`.
- **Added by the build, never in the spec:** version stamp under the title (repo commit from `git rev-parse --short HEAD` with `+dirty` for uncommitted changes outside the output folder, or "repo not in git" · "graph <commit>" or "graph built <date>", plus "(stale: N files changed since)" · review file), generator `darshan-singh-meel-docs-v2 <templates version>` in the HTML meta, and an empty `.generated-by-darshan-singh-meel-docs` marker next to the HTML (the graph skill skips folders holding it). Specs are read as UTF-8; the HTML is written as pure ASCII (every other character as an entity).

## Sections — fixed names and order (build sorts them; others refused)
| Document | Sections (kept only if the code has it) | Always required | Required by app type |
|---|---|---|---|
| overview | What it is and why · How it works · Who uses it · Example · Value and cost · Schedule · Design and operational risks · Words used | What it is and why, How it works, Example | — |
| technical | Overview · Architecture · Job DAG and schedule · Screens and navigation · Endpoints · Commands · Events and messages · Main flows · Data model · Business rules · Configuration · Security and access · Deploy and environments · Operations · Performance and limits · Tests · Key decisions | Overview, Architecture, Main flows, Deploy and environments (+ Business rules, Operations: per plan) | from the plan; without one: Operations · pipeline: Job DAG and schedule, Data model · ui: Screens and navigation · api: Endpoints · cli: Commands · events: Events and messages |
| user-guide | How it reaches you · Screens · What answers what · **How to …** (one per task, any name starting "How to ") · When data is fresh · History and deletions · Errors and messages · Problems and fixes · Who to contact | How it reaches you, How to … (≥1), Problems and fixes, Who to contact | pipeline: What answers what, When data is fresh · ui: Screens · api: What answers what |

`custom` (README, runbook, design doc, code explanation, summary of a PDF): section names free, kept in written order, no recipes; same blocks and look.
Every document ends with **Known issues, assumptions, and decisions needed**. Sections are numbered by the build (all document types).
**Technical = complete:** every inventory item in its typed table (test file, config key, component, endpoint, command, view…); items that say the same thing share one **group row** ("13 schema files: `a`, `b`, …" or a pattern plus `{"covers": [names]}`): no row repeats another. "Cover the important 20%" applies to Overview and User guide only.
**Every word a fact or an insight; no word target.** Cut filler (a cell repeated down a column, placeholder rows, a constant column, a lead that restates its heading); add insight (why a step or rule exists, what breaks if it fails, for whom). Each section's lead states its main insight ("3 of 5 jobs write the same table: the last one wins"), never the heading again.
A required section the source doesn't cover → keep it with one bullet: "Not defined in source — confirm with owner." (a recipe minimum still WARNs; say so in the doc).

## Recipes — the blocks of each section, in order
A recipe is a regex over block types: `x` exactly one · `x?` optional · `x*` any number · `x+` one or more · `(a b)+` repeat the group · `(a|b)` either. Blocks inside `details` count in place. Free inside a recipe: how many items, which boxes, steps, examples, sub-flows, wording.
Wrong block or order → ERROR with the recipe and the actual sequence. Only a required block missing → WARN.

**Overview** (business words)
| Section | Recipe | Also |
|---|---|---|
| What it is and why | `labels` | first 4 labels exactly What · Why · Key idea · Result |
| How it works | `flow` | L0: one row of boxes (3–7), person boxes in row 1, no lanes, sub-flows or `box_w`, ≤2 bullets per box. Box width and gaps are set by the build from the box count and the longest arrow label (min 100 px a box): 7 boxes fit only without arrow labels, 6 with 1–2 short words, 5 with ≤3 words; too many → ERROR naming how many fit |
| Who uses it | `people` | |
| Example | `text? journey examples bullets?` | journey 3–5 stages × 3–8 rows · 2–6 cards, at least one `edge`, `rejected` or `failure` (WARN otherwise) |
| Value and cost | `labels` | each label Value or Cost |
| Schedule | `schedule bullets?` | |
| Design and operational risks | `bullets` | aim for ≤3 (guidance, not checked) |
| Words used | `terms` | |
| Known issues… | `text? issues assumptions? decisions?` | every top issue listed · WARN above ~12 |

**Technical** (complete)
| Section | Recipe |
|---|---|
| Overview | `text? flow` |
| Architecture | `flow components api? bullets?` — `api` = the library's public calls (plan `api`) |
| Job DAG and schedule | `flow+ schedule bullets?` (A plus sub-flows B, C…); each job pattern gets its examples as an `h3` in Main flows |
| Screens and navigation | `flow+ elements bullets?` |
| Endpoints | `flow+ endpoints bullets?` |
| Commands | `flow+ commands bullets?` |
| Events and messages | `flow+ events bullets?` |
| Main flows | `(h3 ipo flow* io?)+` — h3 = the plan's titles in order (without a plan: `<input> → <output>`, no `→` → ERROR); one `ipo` per h3: its steps cover the plan's ordered steps (one each, or merged with `graph`; WARN otherwise), ≤7; its examples are the traces (2–3, a `typical`, at least one edge/rejected/failure); a flow only where the plan says `diagram: true` (the flow branches; ERROR otherwise): it draws what the strip cannot, the branches. Its arrows that are strip steps carry `step: k` and show the strip's number k; branch arrows carry a label only; title = the h3 (the flow, never a box) + N = the strip steps it draws (no arrow with `step`, a `step` past the strip → ERROR). A step with `branch` links to it: the diagram must draw that branch at arrow k (a fail or decision box, or a second arrow from the box arrow k leaves; ERROR otherwise); one straight chain only redraws the strip (ERROR). The strip shows the main path and marks the branch step (`branch` → "else … ▸ Diagram X"); more flows under one h3 only as sub-flows (`parent`, ERROR otherwise); `code`/`entry` boxes are plan `boxes` or entry points (WARN otherwise; an added step is a plain box) |
| Data model | `text? er+ views? bullets?` (no views in the graph → no `views`) |
| Business rules | `rules` — one row per rule (Rule · Example in → out · Why / impact · Where), its example in the row (`Example in → out`: values on both sides, WARN otherwise), its why in the row (WARN when empty); no examples block; one rule over N entities = one row ("applies to: …"). A rule a Main flows step already shows → `see step 5.1.3` in the example cell; Where empty (the step cites it), or other lines that hold the rule (the step's own lines again → WARN; a missing step → ERROR); the row's empty cells join the example cell. Why / impact never holds a citation (a `path:line` there → WARN: it goes in Where). Rule named as a phrase a reader understands (`newest event wins per key`; an identifier alone, `` `task_dependency_order` ``, → WARN). The same rule twice → ERROR |
| Configuration | `config bullets?` |
| Security and access | `(access bullets?\|bullets)` |
| Deploy and environments | `flow? steps io* environments? bullets?` — what the plan's `deploy` says for this repo kind; one row per file kind (all Dockerfiles in one row, all requirements files in one) |
| Operations | `io* symptoms tasks? io*` — services and pipelines only (plan); one `tasks` table (Task · Command · When · Where): each Task is "Rerun and backfill" (only when `plan.rerun_and_backfill`) or one of `plan.how_tos`: its exact text, or a task in plain words with the how-to in its Where cell or `covers` (ERROR otherwise); a how-to that is a flow → one row pointing to its Main flows h3; an empty Task cell continues the task above (first row → ERROR; a task started twice → WARN); every how-to has a row (WARN). A command Deploy or Commands already gives → name the section there, not the command |
| Performance and limits | `bullets` |
| Tests | `tests io* bullets?` |
| Key decisions | `choices` |
| Known issues… | `text? issues unused? assumptions? decisions?` |

**User guide**
| Section | Recipe |
|---|---|
| How it reaches you | `flow bullets? examples?` |
| Screens | `flow+ elements` |
| What answers what | `text? flow* table (h3 bullets)?` — the h3 starts "Columns every" |
| How to … | `steps (io\|examples\|journey)+ bullets?` |
| When data is fresh | `flow? (schedule\|table) io? bullets?` |
| History and deletions | `text? journey bullets? io?` |
| Errors and messages | `messages` |
| Problems and fixes | `problems` |
| Who to contact | `bullets` |
| Known issues… | `text? issues assumptions? decisions?` |

**Steps columns are fixed per section** (leave out `cols`; any other `cols` → ERROR; each row has exactly that many cells):
| Section | Columns |
|---|---|
| technical Deploy and environments | Step · Command · Where it runs |
| user-guide How to … | Step · You see |

## Blocks
Text fields accept `` `code` ``, `**bold**`, `[synthetic]`. Any block takes `"source": "tests/x.py:42"` → cited under it. Paths are from the repo root and checked (above).
**Never shorten a name by hand** (`ab…yz`, `x_..._y`, `` `…_suffix` ``): an ellipsis touching a name in a box label/sub/in/out, ER entity or column, table cell, example or tab → ERROR. Give the full name (the build shortens it and keeps it in the hover tip), or a pattern with `*`. A plain word ending in an ellipsis is UI text and allowed (`` `Loading...` ``, `Saving…`).
Any table cell (typed tables, `table`, issues) starting "Confirmed", "Not verified" or "Fixed since review" renders as a status badge; other values stay plain.

| type | fields |
|---|---|
| text | text — one lead line: the section's main insight, not its heading again |
| h3 | text — sub-heading (one per flow, task, or job pattern) |
| bullets | items |
| labels | items `[[label, text]]` → bullets with a bold label |
| table | cols, rows — only where a recipe says `table`; one column → a plain list |
| *typed table* | rows — headers are fixed by the build (below); each row must have exactly that many cells; 1–2 rows → one line per row (first cell bold, the others after their column name), no table |
| steps | rows, cols? (default Step · In · Out) — numbered |
| terms | items `[[term, meaning]]` |
| flow | nodes, edges, id, title, parent?, lanes?, groups?, numbered? (true), box_w? (fixes the width; default 180 narrowed to 140 if arrow labels need room; not in overview), key?, notice? |
| er | entities `[{id, name, schema?, grain?, cols [[name, "PK FK"]]}]`, rels `[{from, from_col, to, to_col, label?, logical? (true, default = dashed)}]`, id, title (`ER: <area>`), box_w? (table width, default 260, narrowed to fit 1020 px), key? |
| journey | stages `[{title, sub?, changed?, what?, rows}]`; row = `[field, value]` or `{field, sub?, value, old?, changed?, calc?}`; `null` → NULL; id, title |
| io | label (SQL · Request · Command · Call · Action), title?, input, lang (sql · json · shell · text; any other, e.g. python, shows plain), result (`{cols, rows, synthetic: [row idx]}` or text), result_lang? (for a text result; default text), result_title |
| ipo | `input`, `steps [{do, out, why?, where?, branch?, graph?}]`, `output`, `examples [{case, title, expect, in, at, out, tag?, source?, synthetic?}]` — Main flows. `input`/`output`: what comes in (with its source) and what comes out (where it lands), text or `[[k, v]]`. Step `do` ≤8 words; `out` = what the step produces, with a name or number its `do` does not hold (WARN otherwise: "HTTP request" after "fetch(…)" says nothing); `why` = one clause, from code, tests or docs (never invented): why the step exists or what breaks when it fails ("downstream joins need one row per key"; shown as one muted line under `out`); WARN: a flow with no `why` at all, a step that branches, drops, filters or writes data (`branch`, or drop · filter · skip · dedup · delete · remove · reject · exclude · discard · write · insert · upsert · merge · overwrite · truncate · append · persist · publish in `do`/`out`) without one, a `why` whose words are mostly its step's `do`, `out` or `branch` (restates it); `where` = `path:line` (a citation); `branch` = the other outcome of this step ("404, nothing stored"); `graph` = graph step numbers a merged step covers. `at` = the example's value after each step, one per step (wrong count → ERROR): an example value (a name, number, status; a cell of plain lower-case words → WARN), `"="` or `""` = unchanged from the column before (only that; never at step 1, where it only repeats In → ERROR; a trace row more than half `=` → WARN; an example of one step is a rule example, its Business rules row), `null` or `"-"` = not reached, or a step this example does not touch (shown `–`, grey); other placeholder words (skipped, not run, not called, n/a, none, same) → WARN. Rendered as one strip Input ▸ 1 do → out (else branch ▸ Diagram X) `file.py:12` ▸ … ▸ Output (wraps; a column under 720 px; full path in the hover title and once in "Sources:" under it), then the trace grid: a row per example (id, case badge, title, EXPECT) × In · 1 · 2 … · Out; examples after the first two in a `<details>`; one legend line for the tokens used, once per section; sources under it. Under 720 px each row stacks, each value labelled with its step's `do`; `=` and `–` cells hidden; traces after the first behind one "More examples" toggle; strip steps compact |
| examples | items `[{case: typical/edge/rejected/failure, title, expect, in, out, tag?, source?, synthetic?}]`; in/out = text or `[[k, v]]`; `expect` = one line: what this case proves or what we want. A missing case, title, expect, in or out, or an unknown case → ERROR. `tag` only replaces the case word shown; never an id (a digit → ERROR). Not in Business rules (the rule row holds its example) |
| issues | items `[{sev: Must/Should/Question/Other, kind, issue, where, impact, status, test?, absent?, fix, see, do}]` — columns chosen per document; `kind` from the rubric (no review: required, fixes `sev`); `test` with `Confirmed (test)`; any other `sev` is listed under Other; `status` from the fixed list (above); `Fixed since review` = fixed in code after the review (green badge, not open). A plan, config or deploy excerpt made up for an example is synthetic: its issue stays `Not verified` |
| details | summary, blocks, open? — collapsible |

**Typed tables** — `{"type": "<name>", "rows": [[…], …]}`. A row may end with `{"covers": [names]}`: the inventory items a group row stands for (they count for coverage, shown as the row's hover title `covers N: a, b`; a name that is no inventory item → WARN). Graph bookkeeping in a cell ("(2 graph rules)", "(3 rules)") → WARN: the reader sees the rule, the count is in the hover title. A first cell "N <kind>: a, b, c" must list N names (WARN). **A cell naming more than 6 names** (backticked; paths in a Where cell) shows the first 6, then "+N more"; the full cell is its hover title, and the hidden names still count for coverage.
**Fewer tables (build):** adjacent tables of one shape (one typed table type, or `table` blocks with the same `cols`) render as one table; a typed table of 1–2 rows renders as a list; a section showing more than 3 tables → WARN (merge rows that say the same thing, give a small table as a line).
**Columns said once (build):** in a table of 3+ rows a column with one value in every row leaves the table and becomes one line above it, `All rows: <col> = <value>` (an empty column just goes); a review-status column with one status in ≥ half of its rows shows only the others (`… unless shown`; issues too). WARN `repeat:` for a column with one value in ≥70% of its 4+ rows (not all), and for the same cell (2+ words) in 4+ rows of one column: merge them into a group row or say it once.
| type | columns |
|---|---|
| people | Who · What they get |
| schedule | Environment · Runs · Notes |
| components | Component · Responsibility · Where |
| api | Call · Returns · Raises · Where — one row per public function and class (`` `parse(text, fmt)` ``) |
| rules | Rule · Example in → out · Why / impact · Where — one row per rule, named as a phrase in plain words (graph ids in Where or `covers`); Why / impact = why it exists or what breaks, for whom, without it (WARN when empty; a `see step` row may use its step's `why`; no citation); one rule over N entities = one row "… applies to: a, b, c"; `see step 5.1.3` for a rule a Main flows step shows (Where empty or other lines); Where as `basename:line`, full paths once under the table; Why / impact keeps a minimum width |
| tasks | Task · Command · When · Where — Operations; an empty Task continues the task above; rendered as one heading row per task with its rows numbered under it; Task in plain words, the plan how-to (graph name) exact in Where or `covers`; Where as `basename:line`; always a table |
| config | Setting · Default (code) / deploy value · Where · Purpose — the code default, then the value a deploy file sets (`3 / 5 (prod)`) |
| access | Who · Access · How |
| environments | Environment · Where · How deployed |
| symptoms | Symptom · Cause · Fix |
| tests | Test · Covers |
| choices | Decision · Why |
| elements | Element · What it does |
| endpoints | Endpoint · Does · Example |
| commands | Command · Does · Example |
| events | Event · From → to · Payload |
| messages | Message · Means · Do |
| problems | Problem · What to do |
| views | View · Built from · Rows |
| unused | File · Why it looks unused · Status — adds h3 "Unused files" (Known issues) |
| assumptions | Assumption · Why it matters — adds h3 "Assumptions" |
| decisions | Decision · Options · Recommendation · If it waits — adds h3 "Decisions needed" |

**Flow nodes:** `{id, label, col 0–3, row, kind?, tag?, sub?, bullets?, in?, out?, runs?, tip?, see?}`
- kind: blank = step/system · person · entry · code · data · shape (data changes shape) · decision · fail · confirm (outside repo / inferred).
- `bullets` 1–3 short lines · `in`/`out` short values · `runs` "runs as 10 steps" · `tip` hover note · `see: "B"` → "▸ Diagram B".
**Edges:** `{from, to, label?, dashed? (data moves), fail? (red)}`.
**Groups:** `[{label: "Repeats for each …", nodes: [ids]}]` — dashed purple frame. Groups must not overlap or enclose a box that isn't in them (ERROR).
**Sub-flow:** give the parent flow `id: "A"`; the box that opens it gets `see: "B"`; the child flow gets `id: "B"`, `title`, `parent: ["A", "<box label>"]` and goes right after A.
**Diagram ids and titles:** every flow, ER and journey needs an `id` and a `title` (ERROR otherwise). Ids share one letter sequence, A, B, C… in document order. The build writes "Diagram X ·" before the title, so a title starting "Diagram" → ERROR. `see`/`parent` must name an id in the doc. Title forms (ERROR otherwise):

| Diagram | Title |
|---|---|
| flow (technical Main flows) | written by the build: `<h3>, <N> steps` (the flow it belongs to, never a box), N = the strip steps it draws (its arrows with `step`; a title in the spec → ERROR) |
| flow (other) | the plan's form for its section (`diagram_titles`): `<entry>, <N> steps`, numbered (N = its numbered arrows, after a fan-out frame merges them; no arrows → `<area> area`), or `<area> area` with `numbered: false` |
| sub-flow (has `parent`) | `inside <box>` (the parent box label) |
| journey | `<entry>, <N> stages` |
| er | `ER: <area>` (technical: the plan's `er_areas` titles, in order) |

Every diagram title is unique in the doc (ERROR otherwise). A flow with arrows: every box needs an arrow (WARN). A decision box with fewer than 2 outgoing arrows (WARN). A box text part with no break point longer than one line breaks mid-word (WARN): shorten it, or use a name that breaks at `_ / . -` or CamelCase.
**Example ids:** added by the build only — never in the spec, never in `tag`. Every example (card, table row, ipo trace) is numbered `<section>.<h3 index><letter>` (5.1a, 5.1b; `4a` before any h3) and shown on it ("EXAMPLE 5.1a" on a card, `5.1a` in a trace; anchor `#ex-5.1a`), so text can say "see Example 5.1b". Each card: EXPECT, IN, OUT; each trace: EXPECT, In, the value after each step, Out. **Step ids** `<section>.<h3>.<step>` (5.1.3, anchor `#st-5.1.3`) on every strip step: "see step 5.1.3" links to it; one the doc does not have → ERROR.

**Layout (done by the build — never in the spec):**
- Long names break after `_` and `/`, after `.` and `-` (never between digits: `4.0.0`, `:38-63` and dates stay whole), and at CamelCase (`Order|Line|Job`); in a box never leaving a 1–2 char head or a ≤3 char tail after `. _ -` (`ci.yml`, `get_db` stay whole) unless the word is over 14 chars; table cells break only there, never mid-word. Box heights follow the wrapped lines; one height per row. A name needing more than 3 lines (sub, in/out: 2) is shortened in the middle (`ab…yz`), full name in the hover tip.
- Arrows run orthogonally through the gaps between rows and columns, never through a box. Parallel lines stay ≥20 px apart: each line along a row or column centre, and each line in a gap, gets its own offset. Two or more arrow ends on one box side are spread 40 px apart (rows grow; in a column as far as the narrowest box allows, never under 20 px). A fan-out (2+ arrows leaving one box side) is a tree: the arrows leave from one point, share their first part and their track in a gap, and branch off to their targets (separate lines only when no tree layout keeps labels ≥7 px from other lines).
- A box with more than 4 outgoing arrows: its targets go into one frame ("12 children") reached by one arrow, no per-child arrows or numbers. To name the frame, add a group with exactly those boxes.
- Each arrow label sits above its line, right of its number; if that doesn't fit, above its number, then on two lines; never on a box, a line, the arrowhead, a number or another label, and ≥7 px from any other line (2 px if nothing else fits). In each gap the build tries three line orders and keeps the one with the fewest crossings. Still no room after widening the gaps → ERROR: a label over 3 words → shorten it; otherwise too many lines crowd that gap → move boxes apart, drop labels the text already says, or use a sub-flow.
- Diagram wider than 1020 px → ERROR naming the diagram and the columns and boxes that don't fit: move them into a sub-flow behind one box.
- ER without relations: tables in a grid, 3 per row. ER: parents one column left of their children, so lines only join neighbouring columns; a key to a table further away shows as `FK → table` in the row; one key to several tables branches from one point; labels sit near the many end. More than 9 tables, or too many levels for 1020 px (~4), → ERROR: one ER per plan area (`er+`).
- Journey: values wrap, stages ≥240 px, 3 per row; the next row starts with "continues: stage 4". Cards ≥260 px, wrap to the next row, top-aligned, each value under its label.

## Which diagram for what
| Show | Block |
|---|---|
| L0 big picture (3–7 boxes) | flow, no lanes |
| L1 order of steps, who does what | flow with lanes |
| L2 architecture | flow with lanes per platform, `code` boxes |
| Input → steps → output, examples traced through each step | ipo (Main flows) |
| L3 inside one step / job | sub-flow (flow with id + parent) |
| Repeated pattern | group around the repeated boxes |
| Data model | er + views |
| One record through stages | journey |
| Query, request, command, UI action | io |
| Rule or flow behaviour | examples (typical + edge/failure) |

## Examples (`../examples/`, each `<name>.json` + `<name>.html`, 0 ERROR · 0 WARN · 0 LAYOUT)
| Example | Shows |
|---|---|
| overview-pipeline | every overview recipe: `labels` (What · Why · Key idea · Result; Value · Cost), L0 flow with a person row, `people`, journey 3×3 + 2 cards, `schedule`, `assumptions` + `decisions` |
| technical-pipeline | every technical recipe for a pipeline: sub-flow (C → D), group, typed tables, two linear main flows as `ipo` (`<input> → <output>` h3, no diagram, traces 4.1a–c with 4.1c folded, 4.2a–b), statuses `Confirmed (code)`, issue `kind` → `sev`, `er` F + `views`, top issues = open Must + Should, `rules` rows with their example and `see step` pointers, fixed Deploy steps, `environments`, Operations `tasks` with "Rerun and backfill" |
| technical-webapp | API + UI app: lanes in Architecture, screen map + `elements`, request flow + `endpoints`, two main flows as `ipo`: a linear one (no diagram, a `branch` folded into its step) and one whose strip shows the main path and marks the branch step, with a diagram of the decision and fail branch, `er` with real FKs, `access`, config `code / deploy` values, Operations `tasks` pointing to Deploy instead of repeating its command |
| technical-library | library + CLI: package map + `api` table (public calls), command map + `commands`, two linear main flows as `ipo` (failure and rejected traces), traces with `–` (not reached), Deploy as install · test · build and publish, no Operations (not a service) |
| user-guide-data | data user guide: view map + sub-flow, `table` + "Columns every …", How to … with `io` and with `journey`, `schedule`, `problems` |
| user-guide-app | UI user guide: How it reaches you (sign-in flow), screen map + sub-flow, `elements`, How to … with steps + cards, `messages`, `problems` |
| stress-technical | layout limits: long identifiers (wrap, middle ellipsis), 12-child fan-out + fan-in in one frame, 12 tables split into two ERs (E, F) with an `FK → table` note, ipo with long names in strip and traces, long card values, Known issues with `unused` |

Rebuild one: from an empty folder outside any git repo (no stamp; no repo files, so path, name, plan, coverage and facts checks are skipped with a `note:`), `python <skill>/references/templates/build.py <skill>/references/examples/<name>.json <name>.html`, copy the html back, then `check.py` it. Don't leave the marker file in `examples/`.

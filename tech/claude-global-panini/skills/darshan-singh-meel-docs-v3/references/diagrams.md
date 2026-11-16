# Diagrams in docs v3

Docs v3 draws a diagram with one of two tools:
- **Its own blocks** (`flow`, `er`, `journey`, plus `ipo`, `story` and the test map), kept from v2.
- **A `diagram` block**, drawn by the `darshan-singh-meel-diagrams` engine. It takes any type in the engine's registry: flow, architecture, data, interaction, AI and business families.

Load `darshan-singh-meel-diagrams` and the family skill of the type before you write the block.

## Which v2 drawings stay, which are replaced
| Drawing | v3 | Why |
|---|---|---|
| ipo strip + example traces (Main flows) | **stays** | It ties each step to its `where`, `why` and the example values at that step. No engine type does that. |
| Main flows branch `flow` (one actor) | **stays** | The build checks `step: k` against the strip and checks that every `branch` step is drawn. |
| Overview L0 `flow` (How it works) | **stays** | The build checks it for 3-7 boxes, people in row 1 and business words. |
| Screen map, command map, Code files file map, sub-flows (`parent`) | **stay** | The build checks code and entry boxes against the plan's `boxes` and entry points. |
| Code files and Tests per-file map | **drawn by the build with the engine** → `lineage` dbt style per `file` / `testfile`; `boxes` airflow style for all files (a group per file, functions inside, data) | Built from the blocks' fields, nothing to write. Chip map when the engine is missing. |
| `journey`, `story`, example cards, test map | **stay** | They are examples with data, not diagrams of structure. |
| Architecture L2 `flow` | **replaced** → `c4-container` · `layered-architecture` · `deployment` | Standard C4 notation, with technology on every container and a system boundary. |
| Data model `er` | **replaced** → `er` (crow's foot, subject areas) · `star-schema` | Uses UML/IE cardinality, PK/FK/UK and areas as frames. The old `er` block still builds. |
| Job DAG `flow` | **replaced** → `dbt-lineage` · `airflow-overview` + `airflow-dag` · `orchestration` | Gives the look of the tool the reader knows: layer columns, operators, task groups, asset triggers. |
| Deploy `flow` | **replaced** → `deployment` (+ `grid` for an environment matrix) | Shows environments and clusters as nested frames. |
| Endpoints / Events `flow` | **replaced** → `c4-component` · `request-path` · `event-driven` · `cdc-streaming` | Shows routes, tiers, topics and dead letters with their own shapes. |
| Technical Overview `flow` (repo that is not scheduled) | **replaced** → `c4-context` | Shows the system, its users and the systems around it. |

"Replaced" means the plan prefers the engine type. A v2 `flow` in its place still builds.

## Preferred types (inventory.json `plan.diagrams`)
`inventory.py` writes `plan.diagrams {doc: {section: [entry]}}` for the sections that apply to the repo.
- Each entry is `{block: "flow"}` (the builder's own flow) or `{block: "diagram", type, use, style?, view?, optional?}`.
- The first entry is the section's main diagram. The others fit other content.
- `optional: true`: add it only when it answers a question the text cannot.
- The plan is guidance and the build does not check it. The content decides.

| Section | Repo kind → preferred |
|---|---|
| Overview (technical) | pipeline, dbt → `flow` (one run, numbered) · any other → `c4-context` |
| Architecture | web API, UI, streaming, pipeline → `c4-container` · dbt → `medallion` · library, CLI → `layered-architecture` (an import against the layers in red) · infra → `deployment` (+ `network-topology`) · config/docs → `boxes` · ML/AI → also `rag-pipeline`, `agent-loop`, `ml-lifecycle`, `feature-store` or `model-serving`, whichever the code is |
| Job DAG and schedule | dbt → `dbt-lineage` `view: "overview"` (one pill per layer), then one detail per layer · Airflow (dag nodes) → `airflow-overview`, then one `airflow-dag` per DAG · other schedulers (ADF, Databricks Workflows, cron jobs) → `orchestration` style airflow |
| Endpoints | `c4-component` (routes → handlers → stores) · one request through the tiers → `request-path` |
| Events and messages | `event-driven` · `cdc-streaming` |
| Main flows | ipo always; plan `diagram: true` → `flow` (one actor) · `sequence` (3+ parties exchange messages) · `state-machine` (a record moves through statuses) · `retry-flow` (retries, dead letters) · `agent-loop` (an agent run). A file-scan plan has `diagram: false` everywhere and no Main flows entry: Main flows diagrams need the graph |
| Data model | `er` per plan ER area (title `ER: <area>`) · `star-schema` for a mart |
| Business rules | `state-machine` (status lifecycle) · `decision-tree` (nested rule branches), optional |
| Security and access | `trust-boundaries`, optional |
| Deploy and environments | `deployment` · `grid` (unit × environment), optional |
| Performance and limits | `gantt` run timing, optional, scheduled repos |
| Key decisions | `decision-matrix`, optional |
| Overview doc | How it works: L0 `flow` · `c4-context` or `capability-map` when the systems or capabilities matter more than the steps · Value and cost: `kpi-tree` · Schedule: `gantt` |
| User guide | How it reaches you: `flow` · How to …: `flowchart` when the task branches · When data is fresh: `gantt` |

## Graph style: dbt, airflow or plain, picked per diagram
The engine's three graph styles fit any node-edge type in any section and any repo kind, not only dbt or Airflow repos: lineage, dependencies, call chains, job chains, impact, service maps, agent workflows. Set `"style"` in the diagram's `spec` and pick the style by what the picture shows:

| Style | Pick it when the picture shows | Looks like |
|---|---|---|
| `dbt` | what depends on what: lineage, dependencies, impact ("what breaks if X changes"), service calls, job chains | left to right, one column per layer (group), pills coloured by `kind`, legend; `view: "overview"` = one pill per group with counts; `dim` the unaffected nodes for impact |
| `airflow` | steps that run, with or without a run state: DAG runs, CI pipelines, agent workflows, batch jobs, job chains | task boxes with the operator as tag and `state` as border colour, task-group frames, `collapse`, `kind: "asset"` / `"trigger"` edges |
| `plain` (default) | anything else | rounded boxes, groups as frames |

- A job chain fits both. Use `dbt` when the reader asks what is downstream. Use `airflow` when the reader asks what runs, in what order, and what failed.
- `dbt` on calls (service-map, call graph): every edge must point the way impact flows. Draw a call provider → consumer (label "used by"), or keep caller → callee and list the groups callers first. Calls mixed with data edges in one dbt picture give a back-link ERROR.
- Never force a style: a C4 diagram, ER or sequence has its own notation.

## The `diagram` block
```json
{"type": "diagram", "id": "C", "title": "orders_daily tasks and their order",
 "key": "Box = task (what runs it in the tag) · frame = task group", "notice": "create_views waits for all four tables.",
 "source": "job.template.json:1-60",
 "spec": {"type": "orchestration", "style": "airflow", "activities": [...]}}
```
- **`spec`:** the engine spec without its common fields: `type` plus the type's own fields, as in the family skill's `references/` and `references/examples/`. The build copies in `id` (lower-cased), `title`, `key` and `notice`.
- **Id and title:**
  - `id`: the next letter. It counts with `flow`, `er` and `journey` blocks, A, B… in document order.
  - `title`: says what the picture shows, ≤ 90 characters, never starts with "Diagram", unique in the doc.
  - Main flows: leave the title out. The build writes `<h3>, <type>`, e.g. `POST /orders → 201, sequence`.
  - Data model: an `er` or `star-schema` diagram is titled `ER: <area>` and counts for the plan's ER areas, in order.
- **`key` and `notice`:** required, one line each. The key is shown once per section.
  - The key names only colours and shapes the picture draws, in the engine legend's words. C4: the in-scope system is dark, external systems grey, containers blue.
- **Where it goes:**
  - In place of any `flow`, `er` or `journey` in a recipe.
  - Up to 3 more in any section. More → WARN, except in Main flows.
  - Not inside a `file` block.
  - In Main flows, one diagram per h3 (more only as v2 sub-flows), and only when the plan says `diagram: true`.
- **Errors:**
  - A spec error from the engine → build ERROR `diagram X (type): …`, with the engine's fix.
  - An engine `LAYOUT` line → build WARN, and a LAYOUT line from `check.py`.
  - The engine folder is missing → ERROR naming the folder and how to install it.
- **Page:** a "Diagram X · title" heading, then the SVG in a frame that scrolls sideways on phones (class `dgv`, layout record in `data-geo`), then Key and Notice. The page is light (`data-theme="light"`), so the SVG stays light in a dark OS theme.
- **Markdown / Confluence:**
  - `build.py <spec> <out.html> --diagrams generated-docs/diagrams` writes `<id>.mmd` (Mermaid) for each `diagram` block. A type with no Mermaid form gets `<id>.svg` instead (title, key and Notice drawn in), and the build prints `NOTE diagram X | no Mermaid form`.
  - Paste each `.mmd` in a ```` ```mermaid ```` block. Embed each `.svg` as an image. Write the key and Notice under it as text.
  - Confluence: never upload; give one line on how to import.

## Engine location
`build.py` and `check.py` load the engine from `<skills>/darshan-singh-meel-diagrams/scripts/`, the folder next to this skill's folder. The family types load from `<skills>/darshan-singh-meel-diagrams-*/scripts/`. This holds in the repo (`tech/claude-global/skills/`) and once installed (`~/.claude/skills/`). The engine loads only when a doc has a `diagram` block, so a doc without one builds without it.

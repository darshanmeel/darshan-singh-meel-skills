---
name: darshan-singh-meel-diagrams-data
description: Data diagrams on the darshan-singh-meel-diagrams engine (load both) - ER with crow's foot, PK/FK and subject areas, star and snowflake schema, generic lineage or dependency DAG with dbt-style select and impact views, dbt lineage graph (layer columns, test counts, per-layer overview, from manifest.json), Airflow Graph view (operators, task states, task groups, collapse, asset outlets), Airflow multi-DAG overview (schedules, asset triggers, TriggerDagRun, sensors), data flow diagram (DFD), medallion layer view, ADF or generic orchestration pipeline, CDC and streaming topology, data mesh domains and products. SVG (light and dark) plus Mermaid. Use for data models, lineage and pipelines in docs v1 and v3, tech summaries, reviews, review v2, architecture reviews and briefs. Triggers - "ER diagram", "data model diagram", "star schema", "lineage", "what breaks if", "dbt DAG", "Airflow DAG diagram", "DAG overview", "data flow diagram", "medallion", "ADF pipeline diagram", "CDC", "Kafka topology", "data mesh".
---

# Diagrams: data family

Eleven data types plugged into `darshan-singh-meel-diagrams` (engine, style, embedding, checker). Load the base skill too; this skill never repeats its rules.

## Pick the type
| Question | Type | Not when → instead |
|---|---|---|
| Which tables exist, their keys, how they relate? | `er` | > 9 tables → one diagram per area · physical columns not decided → header-only boxes |
| How is one fact table sliced? | `star-schema` | several facts sharing dimensions → `er` with areas |
| Where does this data come from, what does it feed, what breaks if X changes? | `lineage` | dbt project → `dbt-lineage` · run order and state → `airflow-dag` |
| How do dbt models depend on each other, layer by layer? | `dbt-lineage` | non-dbt tools in the chain → `lineage` |
| What does one DAG run do and where did it stop? | `airflow-dag` | several DAGs → `airflow-overview` |
| Which DAGs trigger which, on what schedule or asset? | `airflow-overview` | task detail → one `airflow-dag` per DAG |
| What data moves between people, processes and stores? | `dfd` | system parts and protocols → architecture family |
| What lives in each lake or warehouse layer and its rule? | `medallion` | table-level dependencies → `lineage` |
| How does an ADF / Databricks Workflows / Step Functions pipeline run? | `orchestration` | Airflow → `airflow-dag` |
| How do changes stream from a database to consumers? | `cdc-streaming` | batch loads → `lineage` |
| Which domain owns which data product, who consumes it? | `data-mesh` | team structure only → business family org chart |

Fields per type: `references/tables.md` (er, star-schema), `references/lineage.md` (lineage, dbt-lineage, medallion), `references/orchestration.md` (airflow-dag, airflow-overview, orchestration), `references/flows.md` (dfd, cdc-streaming, data-mesh).

## Graph style: plain, dbt or airflow
Every node-edge type takes `style` (base `references/spec.md`). Pick by content, not by tool:
- **dbt** (lineage look) - things that depend on things: `lineage` (default), `dbt-lineage` (default), `medallion`, `cdc-streaming`, `data-mesh`. Pills by kind, layers as columns.
- **airflow** (Graph view look) - executable steps with a run state: `airflow-dag`, `airflow-overview`, `orchestration` (all default airflow); `lineage` when nodes carry job states.
- **plain** - notation shapes carry meaning: `dfd` (plain only), `medallion`, `cdc-streaming`, `data-mesh` (default plain).
- `er` and `star-schema` draw tables; no style.

## High level first, then detail
- `dbt-lineage`: `view: "overview"` = one box per layer with counts → then `select` per area (`"+fct_orders"`, `"stg_orders+"`).
- `airflow-overview` for all DAGs → one `airflow-dag` per DAG that matters; `collapse` task groups the reader does not need.
- `data-mesh`: `view: "overview"` = one box per domain → detail for one domain.
- `er`: one diagram per subject area (`areas`) when over 9 tables; `more: n` instead of listing every column.
- `orchestration`: `collapse` container activities (ForEach, Until) for the run picture; draw a container's inner activities as their own diagram.

## Process
1. Pick the type above; read its reference file.
2. Write the spec from the code or artifact: dbt `manifest.json` → `python scripts/dbt_manifest.py target/manifest.json -o spec.json [--select +fct_x] [--view overview]` then write title, key and notice; Airflow DAG files, ADF pipeline JSON, DDL or model YAML → map by hand. Names stay real.
3. Build and check with the base CLI: `python ../darshan-singh-meel-diagrams/scripts/diagram.py spec.json -o x.svg --mermaid x.mmd --png x.png`.
4. Look at the PNG (light and `--dark`); fix every `LAYOUT` line in the spec.
5. Embed per base `references/embedding.md`.

## Notation rules
- Crow's foot: bar = one, circle = zero (optional), toes = many; `card` reads `<from>:<to>` (`"1:0..N"`). Solid line = identifying, dashed = non-identifying (`identifying: false`). Same markers as Mermaid `erDiagram`.
- Star: fact header blue with the grain as `sub`; dimensions teal; snowflaked outriggers grey under their parent.
- dbt kinds and Airflow states use the base maps; the state word is always written in the box, so colour is never the only signal.
- DFD: every flow starts or ends at a process and is named with the data it carries; stores are two parallel lines with a D-number; processes carry a number.
- Asset or dataset triggers dashed purple, TriggerDagRun dashed blue, sensors dotted grey, failure paths red.
- Impact views: changed node and the paths it reaches red, everything else faded (`impact`).

## Sizing limits
- Canvas ≤ 1000px. A styled graph tries left to right, then groups as bands, then top-down; when all fail the error names the fix (overview, `select`, split, shorter labels).
- About five layers fit left to right with dbt pills; more → overview or `select`.
- `er`: about three entity columns side by side; `star-schema`: dimensions on two sides, outriggers stacked under their parent.
- Edge labels ≤ 36 characters; port, asset and flow names only.

## Common mistakes
- Lineage of a whole project in one picture → overview plus `select` detail.
- Edge from a dimension to a fact drawn as fact → dimension: the one side is the dimension (`from`).
- Airflow tasks without a state in a run diagram: they show as "no status" - give every task its state or none of them.
- Using `lineage` for run order: lineage shows data dependency, not execution order or schedule.
- DFD with control flow ("if valid") on arrows: arrows carry data names only; decisions belong in the flow family.
- Data mesh drawn as a pipeline: domains own products; draw ports between products, not jobs.

## Rules
- Synthetic or real structural names only; no data rows, no secrets or connection strings in labels.
- Notation facts from `references/sources.md`; unverified points are marked `check:` there.
- This skill adds types through `scripts/types_data.py`; it never edits the base skill's files.
- Tests: `python tests/run.py` (builds every example, runs the base `check.py`); `python tests/run.py --write` rebuilds the example SVGs.

# Spec format

One JSON object per diagram. Common fields first, then the type's own fields (family skills document theirs).

## Common fields (every type)
| Field | Rule |
|---|---|
| `id` | lowercase, digits, `-`; unique on the page (it scopes CSS and marker ids) |
| `type` | a registered type (`python scripts/diagram.py --list`) |
| `title` | ≤ 90 chars, one line, says what the picture shows: "Orders lineage: sources to the revenue dashboard" |
| `key` | ≤ 200 chars, one line: what shapes, colours and line styles mean; "Key:" is added |
| `notice` | ≤ 220 chars, one line: the one thing the reader should see; "Notice:" is added |
| `max_w` | optional box width limit in px (default 200) |

## `boxes` - any node-edge graph
```json
{"id": "order-flow", "type": "boxes", "title": "…", "key": "…", "notice": "…",
 "direction": "LR", "style": "plain",
 "groups": [{"id": "api", "label": "checkout-api (FastAPI)", "tone": "teal"}],
 "nodes": [{"id": "pay", "label": "Charge card", "sub": "PSP REST", "group": "api"}],
 "edges": [{"from": "pay", "to": "ok", "label": "202", "style": "dashed"}]}
```
- **Node:** `id`, `label` (required); `sub` (second line, muted), `tag` (small mono line), `shape` (`box rounded pill circle cylinder document actor cloud diamond hexagon note`; default rounded), `tone` (`plain soft teal amber lav green red blue ink`), `solid` (filled with the strong colour), `dashed`, `strong` (thick border), `dim` (faded, for impact views), `mono`, `align: "left"`, `tip` (hover text), `href`, `group`, `rank` (fix the layer), `col` + `row` on every node (fixed grid instead of layered layout), `decision` (checked for ≥ 2 exits), `free` (no unconnected warning).
- Style fields read by styles: `kind`, `state`, `operator`, `materialized`, `tests`.
- **Edge:** `from`, `to`; `label` (≤ 36 chars), `style` (`solid dashed dotted thick`), `head` / `tail` (`filled open none tri diamond odiamond circle one only-one zero-one many one-many zero-many`), `tone` (`red blue green muted teal amber lav`), `kind` (see edge kinds), `dim`, `from_side` / `to_side` (`left right top bottom`), `own_port` (true: this arrow does not join a shared trunk, so its label reads as its own).
- **Group:** `id`, `label`, `tone`; for overviews also `tag`, `sub`, `kind`, `state`, `shape`.
- `direction`: `LR` (default) or `TB`; when LR would exceed 1000px and no direction is set, the engine tries TB.

## Graph style fields (any node-edge type)
| Field | Values | Effect |
|---|---|---|
| `style` | `plain` (default), `dbt`, `airflow` | look (below) |
| `view` | `detail` (default), `overview` | overview collapses every group into one node with counts |
| `collapse` | `[group ids]` | collapse only these groups (Airflow-style collapsed task groups) |
| `group_layout` | `auto` (default; `dbt` → `columns`), `bands`, `columns` | `columns`: each group owns consecutive layers in `groups` order (dbt layers, pipeline stages); `bands`: a stripe across the flow (parallel groups); `auto`: columns when groups already follow one another |
| `kinds` | `{kind: tone}` or `{kind: {"tone", "label", "shape", "solid", "dashed"}}` | node look by `kind`; overrides the style's map; drives the legend |
| `states` | same form | node look by `state` |
| `edge_kinds` | `{kind: {"style", "tone", "label"}}` | edge look by `kind` |
| `legend` | `true` (default) / `false` | legend under the diagram for kinds, states and edge kinds used |

### dbt style
- Pills, filled with the kind colour, mono names, left to right, groups as layer columns, grey edges, legend.
- Default kinds: `source` green · `seed` teal · `model` blue · `snapshot` ink · `semantic_model`, `metric`, `saved_query` lav · `exposure` amber · `analysis`, `test`, `function` soft. Our palette - dbt Docs does not document its own colours.
- `tag` = kind + `materialized`; `tests: 6` → sub "6 tests".
- Overview: one pill per group, tag "folder · n nodes", sub counts per kind ("2 sources · 1 seed").
- Fits: dbt lineage, any lineage or dependency graph, impact analysis (`dim` the unaffected nodes), service call graphs, job chains. For non-dbt content pass your own `kinds` (e.g. `{"edge": "green", "core": "blue", "data": "ink"}`).

### airflow style
- Boxes, mono task ids, `operator` as tag, `state` as sub line and border colour, thick border when a state is set.
- States (Airflow task instance states): `failed` red · `upstream_failed` amber · `up_for_retry` amber dashed · `up_for_reschedule` teal dashed · `running` teal · `restarting` teal dashed · `deferred` lav dashed · `awaiting_input` lav · `queued` soft · `scheduled` soft dashed · `skipped` lav · `removed` soft dashed · `success` green · `none` dashed ("no status").
- Collapsed group: tag "task group · n tasks" (or the group's `tag`, e.g. "DAG @daily"), sub counts per state, colour = worst state.
- Multi-DAG overview: one group per DAG, `view: "overview"`, edges `kind: "asset"` (or `dataset`, `trigger`) between DAGs, labelled with the asset name.
- Fits: DAG runs, CI/CD pipelines, agent or batch workflows, any executable steps with a run state.

### Edge kinds (all styles)
`asset`, `dataset` dashed lav · `trigger` dashed blue · `async` dashed · `failure` red. Each used kind gets a legend line.

## `layers`
```json
{"type": "layers", "layers": [{"id": "serve", "label": "Serving", "items": [{"id": "bi", "label": "Power BI", "sub": "12 reports"}]}],
 "edges": [], "header_w": 130}
```
Top band first; items are nodes; optional edges between items.

## `grid`
```json
{"type": "grid", "columns": ["dev", "prod"],
 "rows": [{"label": "checkout-api", "cells": [{"label": "on merge", "tone": "green"}, "manual"]}]}
```
A cell is a string or `{label, sub, tone}`; one cell per column; empty string = blank cell.

## Examples
`references/examples/`: `order-checkout` (boxes, groups, decision), `platform-layers` (layers), `env-matrix` (grid), `shop-lineage` (dbt style, detail), `nightly-dag` (airflow style, columns), `dag-overview` (airflow style, multi-DAG overview with asset triggers).

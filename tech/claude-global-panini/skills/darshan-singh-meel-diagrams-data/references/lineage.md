# Lineage: `lineage`, `dbt-lineage`, `medallion`

All three map onto the base node-edge graph, so every base node, edge and style field works (`style`, `view`, `collapse`, `group_layout`, `kinds`, `legend`, `direction`, `max_w`).

## Shared fields
| Field | Rule |
|---|---|
| `depends_on` (on a node) | ids it reads from; becomes edges upstream → node. `edges` may be used instead or as well |
| `select` | dbt graph operators on node ids, space = union: `x`, `+x` (ancestors), `x+` (descendants), `2+x+1` (depth), `@x` (descendants and all their ancestors) |
| `impact` | a node id: it and everything downstream stay in colour (it red, the paths red), the rest fades |
| `impact_dir` | `down` (default, "what breaks") or `up` ("what feeds it": upstream stays, no red) |

Layout falls back on its own when a picture is too wide: left to right, then groups as bands, then top-down. Setting `direction` or `group_layout` turns the fallback off for that field.

## `lineage` (generic)
```json
{"id": "customer-impact", "type": "lineage", "style": "dbt", "impact": "crm_contacts",
 "groups": [{"id": "src", "label": "sources"}],
 "nodes": [{"id": "crm_contacts", "label": "crm.contacts", "kind": "source", "group": "src"}],
 "edges": [{"from": "crm_contacts", "to": "stg_contacts"}]}
```
- Kinds: `source` (green), `table` (blue), `view` (teal, dashed in plain), `file` (grey), `job`, `stream`, `api` (dark), `ml_model` (purple), `report` (amber), plus every dbt kind. Plain style adds shapes (cylinder, document, hexagon, pill).
- Default style `dbt`; use `plain` when shapes matter (files vs tables), `airflow` when nodes are jobs with `state`.
- Groups in flow order become columns (sources → staging → marts → consumers).
- Fits: warehouse lineage, cross-tool dependencies, service call graphs, job chains, impact analysis in reviews.

## `dbt-lineage`
```json
{"id": "billing-dbt", "type": "dbt-lineage",
 "nodes": [{"id": "stg_invoices", "resource_type": "model", "materialized": "view", "tests": 4,
            "layer": "staging", "depends_on": ["src_invoices"]}]}
```
- `resource_type`: `source`, `seed`, `model`, `snapshot`, `exposure`, `metric`, `semantic_model`, `saved_query`, `analysis`, `function`, `test`.
- `layer` = folder; `layers: [{id, label}]` fixes the order, else it follows sources, seeds, snapshots, staging, intermediate, marts, semantic, metrics, exposures, then the rest in order of appearance.
- `label` defaults to the id; sources read `source_name.table`.
- Pill tag = resource type and materialization; sub = "n tests".
- `view: "overview"` → one rounded box per layer, tag "folder · n nodes", one count per resource type below, colour of the main type.
- Pills wrap at 128px (`max_w`) so five layers fit side by side.
- From a project: `python scripts/dbt_manifest.py target/manifest.json -o spec.json [--id x] [--select "+fct_x"] [--view overview] [--layers staging,intermediate,marts]`. It reads names, types, folders, refs and test counts only; write `title`, `key` and `notice` before the build (an empty notice stops it).

## `medallion`
```json
{"id": "lakehouse-medallion", "type": "medallion",
 "layers": [{"id": "bronze", "label": "bronze", "sub": "raw, append-only"}],
 "nodes": [{"id": "b_orders", "label": "bronze.orders", "kind": "table", "layer": "bronze", "depends_on": ["f_orders"]}]}
```
- One column per layer, labelled "label · sub" (the layer's rule). Layer `tone` optional.
- Kinds as in `lineage`; default style `plain` (cylinders, documents), `dbt` for the pill look.
- Datasets without arrows are allowed (each layer still gets its column); they warn as unconnected.
- Stacked horizontal bands instead → base type `layers`.

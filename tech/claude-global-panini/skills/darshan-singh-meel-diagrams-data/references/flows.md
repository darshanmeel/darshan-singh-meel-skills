# Flows: `dfd`, `cdc-streaming`, `data-mesh`

All three map onto the base node-edge graph (`groups`, `edges`, `direction`, `max_w`, `legend`, `select`, `impact` work as in `lineage.md`).

## `dfd` - data flow diagram
```json
{"id": "refund-dfd", "type": "dfd",
 "nodes": [{"id": "customer", "label": "Customer", "role": "external"},
           {"id": "p2", "label": "Check eligibility", "role": "process", "ref": "2.0"},
           {"id": "orders", "label": "Orders", "role": "store", "ref": "D1"}],
 "edges": [{"from": "orders", "to": "p2", "label": "order and payment"}]}
```
- `role`: `external` (grey square, bold border), `process` (blue rounded, `ref` number in the tag), `store` (two parallel lines, `ref` D-number).
- Rules the build enforces: every flow has a `label` (the data it carries); every flow starts or ends at a process (no store → store, external → store, external → external).
- Plain style only; no legend (the key explains the four symbols). Each flow keeps its own arrowhead.
- Level 0 (context): one process for the whole system, externals around it. Level 1: the main processes and stores. Level 2: one diagram per level-1 process, numbered 2.1, 2.2, ...
- Two flows competing for one side: set `to_side` / `from_side` on one of them.

## `cdc-streaming`
```json
{"id": "orders-cdc", "type": "cdc-streaming",
 "nodes": [{"id": "t_orders", "label": "orders.cdc", "role": "topic", "partitions": 12, "retention": "7d"}],
 "edges": [{"from": "enrich", "to": "t_dlq", "kind": "failure"}, {"from": "cdc", "to": "registry", "kind": "lookup"}]}
```
- `role`: `db` (green cylinder), `connector` (hexagon), `topic` (teal pill, mono name), `processor` (blue), `sink` (purple cylinder), `registry` (dashed grey), `dlq` (red pill), `app` (amber).
- Topics: `partitions` and `retention` become the tag ("12 partitions · keep 7d").
- Edge kinds: `failure` (red, dead-letter path), `lookup` (dotted, schema registry), `snapshot` (dashed, initial load), `async`.
- Six or more steps run top-down; a cluster frame across the flow (`groups`) makes lines cross - prefer the topic tag over a frame.
- Style `plain` (default) or `dbt`.

## `data-mesh`
```json
{"id": "retail-mesh", "type": "data-mesh",
 "domains": [{"id": "customer", "label": "Customer", "owner": "CRM team"}],
 "nodes": [{"id": "c360", "label": "customer_360", "kind": "aggregate", "slo": "daily 06:00", "domain": "customer"}],
 "edges": [{"from": "c360", "to": "segments", "label": "c360_daily"}]}
```
- `kind`: `source_aligned` (blue), `aggregate` (teal), `consumer_aligned` (purple) - bold box, tag "data product", sub "SLO ..."; `system` (operational system, grey cylinder); `consumer` (amber document, outside domains).
- Domains are frames labelled "name · owner"; edge labels name the output port.
- `view: "overview"` → one box per domain ("domain · n data products", owner below) with the ports between domains.
- Domains lay out as bands (default, parallel domains). When each domain feeds the next, set `group_layout: "columns"`: domains follow the flow and a too-wide picture turns top-down instead of leaving empty corners. Boxes wrap at 150px (`max_w`). Style `plain` (default) or `dbt` (fits in the overview).
- Platform and governance layers → base `layers` type under the mesh picture.

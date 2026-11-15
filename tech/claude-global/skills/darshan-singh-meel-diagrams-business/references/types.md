# Business types: spec fields

Every spec also has the common fields of the base (`id`, `type`, `title`, `key`, `notice`, optional `max_w`, `legend: false`). A full spec per type is in `examples/`. Tones: `plain soft teal amber lav green red blue ink`.

## org-chart
```json
{"type": "org-chart", "kinds": {"eng": {"tone": "blue", "label": "engineering"}},
 "units": [{"id": "hod", "label": "Head of Data"}, {"id": "pe", "label": "Platform lead", "parent": "hod", "kind": "eng", "vacant": true}]}
```
- `units[]`: `id`, `label` (role or team), `parent` (one entry without = root; several roots sit side by side), `sub` (size, location), `tag`, `kind` (looked up in `kinds`, drives the legend), `tone`, `vacant` (dashed, sub "vacant").
- `stack_leaves`: `auto` (default; stack leaf teams under their manager only when the tree is wider than 1000px), `true`, `false`.
- Mermaid: flowchart TB.

## team-topology (node-edge, style plain | dbt | airflow)
```json
{"type": "team-topology", "style": "dbt", "groups": [{"id": "stream", "label": "stream-aligned"}],
 "teams": [{"id": "cart", "label": "Cart & checkout", "type": "stream-aligned", "group": "stream"}],
 "interactions": [{"from": "cart", "to": "pay", "mode": "x-as-a-service", "label": "payments API"}]}
```
- `teams[]`: base node fields plus `type`: `stream-aligned` (amber), `platform` (blue), `enabling` (teal), `complicated-subsystem` (lav); override or add with `kinds`.
- `interactions[]`: base edge fields plus `mode`: `collaboration` (thick lav), `x-as-a-service` (solid), `facilitating` (dashed teal); override with `edge_kinds`.
- Base style fields apply: `style`, `view`, `collapse`, `group_layout`, `states`, `direction`.
- Mermaid: flowchart via the base `mermaid_graph`.

## capability-map
```json
{"type": "capability-map", "layout": "auto",
 "areas": [{"id": "merch", "label": "Merchandising",
            "caps": [{"label": "Pricing", "heat": "weak", "children": ["promotions", "markdowns"]}]}]}
```
- `areas[]` = L1: `id`, `label`, `caps[]` = L2: `label`, `heat`, `children` (L3 names, shown as sub), `sub`, `tone`, `id`.
- `heat` scale default: `strong` green · `adequate` plain · `weak` amber · `missing` red dashed. Own scale: `"scale": {"invest": {"tone": "blue", "label": "invest 2027"}}` (merged with the default).
- `layout`: `columns` (one framed column per L1), `bands` (one stripe per L1, L2 boxes flow in rows), `auto` (columns up to 5 areas and 8 caps each).
- Mermaid: flowchart TB, one subgraph per L1.

## value-stream
```json
{"type": "value-stream", "unit": "h", "start": "Ticket ready", "end": "Live",
 "stages": [{"label": "Code review", "sub": "peers", "time": 2, "wait": 20, "ca": 80, "tone": "amber"}]}
```
- `stages[]`: `label`, `sub` (team), `time` (process time), `wait` (waiting before this stage), `ca` (% complete and accurate, shown as tag), `tone` (mark bottlenecks amber), `id`.
- `unit`: one unit for every number (`min`, `h`, `d`). Totals: lead time = Σ time + Σ wait; flow efficiency = Σ time / lead time.
- Mermaid: flowchart LR with waits as link text.

## value-chain
```json
{"type": "value-chain", "support": [{"label": "Technology", "sub": "pipeline engine"}],
 "primary": [{"label": "Operations", "items": ["Managed pipelines"], "tone": "green"}], "margin": {"label": "Margin", "sub": "68% gross"}}
```
- `support[]`: `label`, `sub`, `tone` (default soft). `primary[]` (2-7, left to right): `label`, `items`, `sub`, `tone` (default teal; green = source of advantage). `margin`: `label`, `sub`, `tone`. `width` (default 940).
- No Mermaid form.

## sipoc
```json
{"type": "sipoc", "suppliers": ["Police"], "inputs": ["Police report"], "process": ["Register claim", "Check cover"],
 "outputs": ["Claim decision"], "customers": ["Policyholder"], "scope": "from first notice of loss to claim closed"}
```
- Five lists of short strings; `process` holds 3-8 high-level steps; `scope` (optional) is printed under the table.
- No Mermaid form.

## quadrant
```json
{"type": "quadrant", "x": {"label": "Effort", "low": "small", "high": "large"}, "y": {"label": "Value", "low": "low", "high": "high"},
 "quadrants": {"top_left": {"label": "Quick wins", "tone": "green"}, "top_right": "Major projects"},
 "items": [{"label": "Freshness alerts", "x": 0.15, "y": 0.82, "sub": "2 weeks", "kind": "data"}]}
```
- `items[]`: `label`, `x`, `y` from 0 to 1, `sub`, `tone` (dot colour, default ink), `kind` (looked up in `kinds`, legend).
- `quadrants`: `top_left`, `top_right`, `bottom_left`, `bottom_right`, each a string or `{label, tone}` (default soft).
- `size`: `[w, h]` of the plot (default `[600, 440]`). Labels sit next to their dot inside its quadrant; a thin leader line joins label and dot when they had to move. Crowded → `layout: no free place …`.
- Mermaid: quadrantChart (quadrant-1 = top right).

## stakeholder-map
```json
{"type": "stakeholder-map", "scale": 5,
 "stakeholders": [{"label": "CFO", "power": 5, "interest": 4, "stance": "critic", "sub": "budget owner"}]}
```
- `stakeholders[]`: `label`, `power`, `interest` (1 to `scale`, default 5), `stance`: `supporter` green · `neutral` ink · `critic` amber · `blocker` red, `sub`, `tone`.
- Quadrants default to Manage closely / Keep satisfied / Keep informed / Monitor; override with `quadrants` as in `quadrant`.
- Mermaid: quadrantChart.

## swot
```json
{"type": "swot", "strengths": ["…"], "weaknesses": ["…"], "opportunities": ["…"], "threats": ["…"], "cell_w": 400}
```
- Four lists, 2-5 points each. Colours fixed: S green, W amber, O blue, T red. No Mermaid form.

## funnel
```json
{"type": "funnel", "unit": "", "scale": "steps",
 "stages": [{"label": "Started trial", "sub": "sign-up form", "value": 6100}]}
```
- `stages[]` top to bottom: `label`, `value` (never growing), `sub`, `tone` (default blue). `unit` follows each number.
- `scale`: `steps` (default, even narrowing, say "not to scale" in the key) or `value` (width ∝ value). `bar_w` (default 440).
- Right column: conversion from the previous stage, the lowest marked "biggest drop", and overall conversion on the last row. No Mermaid form.

## mind-map
```json
{"type": "mind-map", "root": "Data platform 2027",
 "branches": [{"label": "Trust", "tone": "teal", "children": ["Data contracts", {"label": "Quality checks", "children": ["freshness"]}]}]}
```
- `branches[]`: `label`, `tone` (default cycles teal, amber, lav, green, blue, soft), `children` (strings or `{label, sub, children}`), up to 3 levels.
- Branches split right then left, balanced by leaf count. `compact`: unset = fold the 3rd level into sub text only when too wide; `true` / `false` force it.
- Mermaid: mindmap.

## fishbone
```json
{"type": "fishbone", "problem": "Daily sales report after 09:00", "sub": "12 of 20 days",
 "categories": [{"label": "Data", "causes": [{"label": "POS export arrives late", "causes": ["batch window"]}, "Schema change"]}]}
```
- `categories[]` (≤ 8; first half on top, rest below, left to right): `label`, `tone`, `causes` (strings or `{label, causes: [sub-causes]}`).
- Mermaid: `ishikawa-beta` (needs Mermaid 11.12.3 or later; older renderers → embed the SVG).

## business-model-canvas
```json
{"type": "business-model-canvas", "key_partners": ["…"], "key_activities": ["…"], "key_resources": ["…"],
 "value_propositions": ["…"], "customer_relationships": ["…"], "channels": ["…"], "customer_segments": ["…"],
 "cost_structure": ["…"], "revenue_streams": ["…"], "tones": {"value_propositions": "teal"}}
```
- Nine lists, 1-5 points each; `tones` highlights blocks (name the meaning in the key); `width` (default 968). No Mermaid form.

## kpi-tree
```json
{"type": "kpi-tree",
 "metrics": [{"id": "mrr", "label": "Net new MRR", "value": "€42k", "target": "€60k", "trend": "down", "status": "off_track", "op": "−"},
             {"id": "gain", "label": "Gained MRR", "parent": "mrr", "value": "€95k", "status": "at_risk"}]}
```
- `metrics[]`: `id`, `label`, `parent` (exactly one root), `value`, `target` (tag "value · target"), `trend` (`up` ↑, `down` ↓, `flat` →), `status` (`on_track` green, `at_risk` amber, `off_track` red), `op` (how this metric's children combine: `+ − × ÷`), `sub`, `tone`.
- Mermaid: flowchart LR (operator written into the parent's label).

## decision-matrix
```json
{"type": "decision-matrix", "scale": 5, "options": ["Airflow (managed)", {"label": "Dagster", "sub": "OSS + cloud"}],
 "criteria": [{"label": "Team skills", "weight": 20, "scores": [5, {"score": 2, "note": "1 engineer"}]}]}
```
- `options[]` (≤ 6): string or `{label, sub}`. `criteria[]`: `label`, `weight` (> 0, any unit; shown as % of the sum), `scores` (one per option: number 0..`scale` or `{score, note}`), `sub`.
- Cells: green ≥ 80% of scale, amber ≤ 40%; last row = weighted score, the highest marked blue "highest". `corner` text (default "criterion · weight"). No Mermaid form.

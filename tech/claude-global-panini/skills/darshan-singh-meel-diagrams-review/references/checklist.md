# Diagram review checklist

Each finding needs evidence: `path:line` in the source, the spec field, a script line, or the PNG and the element in it. "Script" = `review_diagrams.py` catches it; the rest is reading and looking.

## 1. Right type for the question
- The title states one question; the type matches it in `<base>/SKILL.md` "Pick the type". Two questions in one picture → Must "split".
- Order over time (who calls whom) drawn as boxes and arrows instead of `sequence` → Must.
- States of one thing drawn as a flowchart of actions → Should `state-machine`.
- A plan with dates and durations drawn as `timeline` → Should `gantt` (timeline periods are not to scale).
- C4: a container picture with classes or a deployment picture with code components → wrong type.
- Graph style (plain, dbt, airflow) is the author's choice; a finding only when it misleads (dbt look on a graph with loops; airflow states on something that never runs).

## 2. Facts match the source
- Every box, arrow, state, column, cardinality, operator, schedule and count traces to the source (`path:line`, manifest node, DAG file, Terraform resource, document page). Untraceable → Must "invented".
- Missing element the Notice or the text depends on → Must; missing minor element → Should.
- Direction: arrows point the way data or control flows in the code (caller → callee, upstream → downstream, parent → child in `er`).
- Names are the real identifiers (`fct_orders`, `checkout-api`), not "Service A", "Table 1", "DB" (script: placeholder name).
- Counts in tags or subs ("6 tests", "12 reports", "4,800 tokens") match the source; recount.
- Example values are synthetic; no personal data, secrets, connection strings or machine paths (script).

## 3. Notation per type (facts from the family references; else `references/sources.md`)
| Type | Check |
|---|---|
| `sequence` (UML) | sync = solid line, filled head; async = open head; reply = dashed. Activation bars only where a call is open. Frames `alt/opt/loop/par/break/critical` with a `[guard]`; ≤ 2 nesting levels |
| `state-machine` (UML) | one top-level initial; states are conditions, not actions; transitions `event [guard] / action`; choice with ≥ 2 guarded exits (`else`); no outgoing from a final |
| `activity` (UML) | fork 1 in / ≥ 2 out, join ≥ 2 in / 1 out; every decision exit guarded |
| `swimlane` (BPMN-lite) | start thin circle, end thick circle; sequence flow solid inside one pool only; message flow dashed with open circle, between pools only; gateway marks X / + / O match the logic (parallel really runs both) |
| `c4-*` | one level per diagram, never components of two containers; every element has name, type and technology; every relationship one direction with a label (and technology for containers); external systems grey; legend names the colour mapping (C4 prescribes none) |
| `deployment`, `network-topology` | nodes nest as in the infra code (account / VPC or VNet / subnet); no vendor logos; ports and protocols on the edges that cross a boundary |
| `er`, `star-schema` | crow's foot ends match the FKs and nullability (`0..1` nullable FK, `1` NOT NULL); parent on the one side; identifying solid, non-identifying dashed; fact grain stated in the fact header |
| `lineage`, `dbt-lineage`, `medallion` | acyclic (script); columns follow the layer order sources → staging → intermediate → marts → exposures, no edge backwards (script); `tests` counts from the manifest; overview counts add up to the detail diagrams |
| `airflow-dag`, `airflow-overview`, `orchestration` | acyclic (script); task ids and operators as in the DAG file; `state` values are Airflow task instance states and the legend shows them (script: legend); `trigger_rule` other than `all_success` written in the box; asset or trigger edges match `outlets` / `schedule=[Asset]` / `TriggerDagRunOperator` |
| `gantt` | every bar inside `start`-`end`; `after` respected - no bar starts before its dependency ends (script); milestone = zero length; today line only on a dated plan; queued before start (airflow look) |
| `timeline` | periods in time order; equal spacing stated in the key (not to scale) |
| `quadrant`, `stakeholder-map` | both axes named with low and high ends (script); quadrant names match the axes (top right = high x, high y); dot positions defensible from the source |
| `raci` | exactly one A per row; at least one R per row |
| `funnel`, `kpi-tree`, `value-stream` | numbers recompute: conversion rates, sums of children, lead time = waits + process times |
| `rag-pipeline`, `agent-loop`, `model-serving`, … | ingest path and query path separated; tools, memory and guardrails as in the code; loop exits (max steps, human approval) drawn |

## 4. Density
- ≤ 7 ± 2 boxes and groups per level (script SHOULD); more → overview (`view: "overview"`, C4 context, multi-DAG overview) plus detail diagrams linked from the Notice.
- One idea per diagram: if the Notice needs "and", consider two.

## 5. Title, key, Notice
- Title says what the picture shows, not the type name ("Orders lineage: sources to the revenue dashboard", not "Lineage diagram").
- Key names every shape, colour and line style used, and nothing unused.
- Notice is one concrete observation the reader should take away, visible in the picture; not a restated title (script).

## 6. Layout and look (PNG, light and dark)
- 0 `LAYOUT` lines (script): no overlap, no arrow through a box, no label on a foreign line, no text outside its box, canvas ≤ 1000px.
- Looking: follow every arrow end to end. Arrows merged into one trunk so the reader cannot tell which source feeds which target → Should `own_port: true` or `spread`. Long detours, arrows hugging a frame border, labels far from their line → Should.
- Words wrap whole; identifiers break after `/ . _ - :` only.
- Dark PNG: every label readable, frames visible, no box that vanishes into the background.

## 7. Accessibility and theme
- `<svg role="img">` with `<title>` and `<desc>` (script); the figure has the key and Notice as HTML text.
- Colour is never the only signal: state word in the box, kind tag, edge label or kind; legend on when colour carries meaning (script).
- Palette contrast ≥ 4.5:1 for text, ≥ 3:1 for arrows, light and dark (script, palette lines); no colour outside the palette (script).

## 8. Embedding
- Every diagram on one page has its own `id` (script: duplicate id) - shared ids break CSS scope and arrow markers.
- HTML: the `<figure>` scroll frame (`overflow-x:auto`) so the diagram scrolls sideways on phones (script); static only - no script, no external fonts or images (script).
- Markdown and Confluence: Mermaid block with key and Notice as text under it (script); types with no Mermaid form embed the SVG file, and the file exists (script).
- Paths relative to the repo root (script: machine path).
- A review or review-v2 report: at most one diagram per finding, only where it explains the issue.

## 9. Mermaid parity (when the diagrams go to Markdown or Confluence)
- Every node of the SVG appears in the Mermaid text (script, for flowchart, state and ER output); groups and edge labels match.
- Mermaid starts with the frontmatter title and carries `%% Key` and `%% Notice` (script).
- Types with no Mermaid form (`*` in the base table) are not hand-written in Mermaid.

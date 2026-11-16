---
name: darshan-singh-meel-diagrams
description: Shared base for all diagrams - picks the diagram type for a question, then turns a JSON spec into static inline SVG (light and dark, docs palette) plus Mermaid text, with a layout checker (no overlaps, no arrows through boxes, wrapped text, max 1000px). Holds the engine, the type registry the six family skills plug into (flow, architecture, data, interaction, ai, business), generic types boxes, layers, grid, and three graph styles for any node-edge diagram - plain, dbt (lineage look - layer columns, colour by kind, collapsed overview) and airflow (graph-view look - operator, state colours, task groups, asset triggers). Use for any diagram in HTML pages, docs v1 and v3, tech summaries, reviews and review v2, architecture reviews, requirements briefs, blog posts and knowledge-graph answers; load the family skill for the type alongside. Triggers - "draw a diagram", "which diagram fits", "flowchart", "architecture diagram", "lineage graph", "DAG view", "dbt-style", "Airflow-style", "Mermaid", "SVG diagram".
---

# Diagrams (base)

One engine for every diagram. Family skills add types; they never copy this text.

## When to use
- Any diagram in an HTML page, docs v1 or v3, tech summary, code review or review-v2 report, architecture review, requirements brief, blog post or knowledge-graph answer.
- Load the family skill that owns the type (table below) together with this one.

## Pick the type
Match the question to a row; load that family.

| Question shape | Family skill | Types (`type` value) |
|---|---|---|
| What happens, step by step? Who does which step? What if? | `darshan-singh-meel-diagrams-flow` | `flowchart` · `swimlane` (BPMN-lite: events, tasks, gateways, lanes, message flows) · `decision-tree` · `state-machine` (event [guard] / action, composite) · `activity` (fork/join) · `retry-flow` · `approval-workflow` |
| What is the system made of and where does it run? | `darshan-singh-meel-diagrams-architecture` | `c4-context` · `c4-container` · `c4-component` · `deployment` · `network-topology` (VPC/VNet, subnets, gateways; no vendor logos) · `integration-map` · `event-driven` · `service-map` · `layered-architecture` · `request-path` · `trust-boundaries` |
| What data exists, where does it come from, what breaks? | `darshan-singh-meel-diagrams-data` | `er` (crow's foot) · `star-schema` · `lineage` · `dbt-lineage` · `airflow-dag` · `airflow-overview` (multi-DAG) · `dfd` · `medallion` · `orchestration` (ADF or generic) · `cdc-streaming` · `data-mesh` |
| Who talks to whom, in what order, over what time? | `darshan-singh-meel-diagrams-interaction` | `sequence` · `timeline` · `gantt` (roadmap, run timing) · `journey` · `service-blueprint`* · `raci`* · `handoff` |
| How does the AI / ML system work? | `darshan-singh-meel-diagrams-ai` | `rag-pipeline` · `agent-loop` · `multi-agent` · `ml-lifecycle` · `feature-store` · `eval-pipeline` · `model-serving` · `context-assembly` · `nn-block` |
| How is the business organised, where is value, what to decide? | `darshan-singh-meel-diagrams-business` | `org-chart` · `team-topology` · `capability-map` · `value-stream` · `value-chain`* · `sipoc`* · `quadrant` · `swot`* · `funnel`* · `mind-map` · `fishbone` · `business-model-canvas`* · `stakeholder-map` · `kpi-tree` · `decision-matrix`* |
| None fits, or a quick generic picture | this skill | `boxes` (any node-edge graph) · `layers` (stacked bands) · `grid`* (rows × columns, short text per cell) |

- \* = no Mermaid form: embed the SVG file in Markdown / Confluence. Every other type also gives Mermaid text.
- `python scripts/diagram.py --list` prints every registered type with its family.
- Two questions in one picture → two diagrams.

## Graph style: plain, dbt or airflow
Any node-edge type takes `"style"`. The author picks what fits the content; nothing forces one.
- **dbt** - things that depend on things: lineage, dependencies, impact ("what breaks if X changes"), service call graphs, job chains. Left to right, one column per layer (group), pill colour by `kind`, legend. Use `view: "overview"` for the one-screen picture (a pill per group with counts), then a detail diagram per group. Not only for dbt projects.
- **airflow** - executable steps with run state: DAG runs, CI pipelines, agent workflows, batch jobs. Task box with type (`operator`) and `state` colour, frames for task groups, `collapse` some groups, `kind: "asset"` / `"trigger"` edges between DAGs or pipelines.
- **plain** (default) - everything else.
- dbt and airflow read as DAGs: the build fails on a cycle (dbt style, DAG types) or an edge back against the layer order; airflow style on other types warns. Too wide left to right with no `direction` set → drawn top-down: layers are then rows, so the key says "row" (the build warns `direction fell back to TB` when the key or Notice says "column" or "left to right").
- Families map their own kinds and states onto a style (`kinds`, `states` maps). Details: `references/spec.md`.

## High level first, then detail
- Start with one overview: `view: "overview"`, a C4 context, a layer view or a multi-DAG overview, ≤ 7 ± 2 boxes.
- Then one detail diagram per area the reader needs, linked from the overview's Notice or text.
- Over 9 boxes on one level, or the engine says "canvas would be …px wide" → split, collapse groups, or switch `direction` to `TB`.

## Process (fixed)
1. **Pick the type** from the table; load its family skill.
2. **Write the spec** JSON (`references/spec.md`): `id`, `type`, `title`, `key`, `notice`, then the type's fields. Real names from the code or source, never placeholders.
3. **Build:** `python scripts/diagram.py spec.json -o out.svg --mermaid out.mmd --png out.png` (or `build(spec)` from Python, `references/engine.md`).
4. **Check:** the build runs `check.py`; every `LAYOUT` line is a defect. Fix the spec (shorter labels, split, `direction`, `view`) - never ship with a LAYOUT line.
5. **Look:** open the PNG (light and `--dark`). Read every label; confirm the picture answers the question in the title.
6. **Embed** (`references/embedding.md`): inline SVG in HTML, Mermaid in Markdown/Confluence, the SVG file where the type has no Mermaid form.

## Outputs
- `-o x.svg` standalone SVG with title, key and Notice drawn in.
- `--fragment x.html` the `<figure>` to paste into a page (scroll frame, key, Notice as HTML text).
- `--page x.html` a standalone page; `--mermaid x.mmd` Mermaid text, or `NOTE … no Mermaid form`; `--png x.png [--dark]` via Playwright, only for looking.
- `--geometry x.json` the layout record; `python scripts/check.py x.json` rechecks it.

## Style rules
- Palette and fonts of the docs pages (`references/style.md`), CSS variables with a dark set; no other colours, no gradients, shadows, icons or logos.
- Every diagram: unique `id`, `title` that states what it shows, one-line `key` (what shapes, colours and lines mean), one-line `notice` (the one thing to see).
- **Brevity:** + `darshan-singh-meel-brevity` (families inherit) → title = the point · `notice` = lede · labels plain · no text the reader does not need.
- Colour carries meaning only and is named in the key or legend; the label text says it too (state, kind).
- Labels: real names, ≤ 36 characters on arrows; long text goes in `sub` inside the box.
- Canvas ≤ 1000px wide; the frame scrolls sideways on phones.

## Rules
- Output stays local; never publish diagrams as artifacts or hosted pages.
- No real personal data, secrets or connection strings in labels; example values are synthetic.
- Notation facts come from the official pages in `references/sources.md`; anything unverified is marked `check: <page>`.
- Family types plug in through the registry (`references/engine.md`); a family never edits this skill's files.

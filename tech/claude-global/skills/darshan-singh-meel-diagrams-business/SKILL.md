---
name: darshan-singh-meel-diagrams-business
description: Business diagram family for the darshan-singh-meel-diagrams engine - org chart, team topology (team types and interaction modes, plain, dbt or airflow graph style), business capability map with maturity heat, value stream with wait and process time ladder, value chain, SIPOC, 2x2 quadrant, stakeholder map (power and interest), SWOT, funnel, mind map, fishbone / Ishikawa, business model canvas, KPI / driver tree and weighted decision matrix. Each type turns a JSON spec into static SVG (light and dark) plus Mermaid where Mermaid has the type, checked for overlaps. Use for business, product, team and strategy pictures in docs v1 and v3, tech summaries, reviews, briefs and blog posts; load darshan-singh-meel-diagrams alongside. Triggers - "org chart", "team topology", "capability map", "value stream map", "SIPOC", "2x2", "prioritisation matrix", "stakeholder map", "SWOT", "funnel", "mind map", "fishbone", "Ishikawa", "root cause diagram", "business model canvas", "KPI tree", "driver tree", "decision matrix".
---

# Diagrams - business family

Types for "how is the business organised, where is value, what do we decide". The engine, spec basics, style, checks and embedding live in `darshan-singh-meel-diagrams` (load it too); this skill adds types only.

## Pick the type
| Type | Question it answers | Not when | Instead |
|---|---|---|---|
| `org-chart` | Who reports to whom? | Teams by how they work together | `team-topology` |
| `team-topology` | Which teams depend on which, in what interaction mode? | Pure reporting lines | `org-chart` |
| `capability-map` | What must the business be able to do, and where is it weak? | Who does it, in what order | `value-stream`, swimlane (flow family) |
| `value-stream` | Where does time go from request to delivery? | Branching logic, decisions | flowchart (flow family) |
| `value-chain` | Which activities create the margin? | Step order or timing | `value-stream` |
| `sipoc` | What is the scope of one process: who feeds it, who gets what? | Detailed steps | flowchart / swimlane |
| `quadrant` | How do items compare on two axes (value vs effort, risk vs impact)? | More than two criteria | `decision-matrix` |
| `stakeholder-map` | Whom to manage closely, keep satisfied, inform, monitor? | Who approves which step | RACI (interaction family) |
| `swot` | Internal strengths and weaknesses vs external opportunities and threats? | Ranking options | `decision-matrix` |
| `funnel` | Where do we lose people or deals between stages? | Stages that branch or loop | `value-stream`, flowchart |
| `mind-map` | What belongs under one topic (themes, ideas, scope)? | Dependencies or order | `boxes`, `kpi-tree` |
| `fishbone` | What causes one problem, grouped by category? | Causes that chain into each other | `boxes` (dbt style) or flowchart |
| `business-model-canvas` | How does the business create, deliver and capture value? | One product's features | `mind-map` |
| `kpi-tree` | Which drivers make up one metric, and which is off target? | Metrics without a formula link | `capability-map` with heat, or a table |
| `decision-matrix` | Which option wins on weighted criteria? | Two axes are enough | `quadrant` |

- Two questions → two diagrams. A capability map plus a heat per value stream is two pictures.
- `python ../darshan-singh-meel-diagrams/scripts/diagram.py --list` shows them with the base types.

## Graph styles (plain, dbt, airflow)
- Only `team-topology` is a free node-edge graph, so only it takes `style`, `view: "overview"`, `collapse` and `group_layout` from the base. **dbt** fits a team dependency map (columns = team role or value-stream stage, pill colour = team type); **airflow** fits when teams carry a run-like state (e.g. onboarding status per team via `states`); **plain** otherwise. Example `team-deps` uses dbt.
- `org-chart`, `mind-map` and `kpi-tree` are trees: a tidy tree reads better than a layered lineage, so they keep their own layout. `value-stream` keeps its ladder; a stage chain with run state is a pipeline → use `boxes` with `style: "airflow"` from the base.
- Process chains, job chains and service dependencies in a business doc → base `boxes` with `dbt` or `airflow` style, not a business type.

## High level first, then detail
- Overview first: `capability-map` (L1/L2), `value-chain`, `business-model-canvas`, `mind-map`, `team-topology` with `view: "overview"`.
- Detail second: one `value-stream` per stream, one `kpi-tree` per north-star metric, one `fishbone` per problem, a `sipoc` per process before its flowchart.
- Link them in the Notice or text ("detail: #fig-feature-delivery").

## Process (fixed)
1. Pick the type from the table; open `references/types.md` for its fields and one minimal spec.
2. Write the spec: `id`, `type`, `title`, `key`, `notice`, then the type's fields. Real names from the source; synthetic numbers only when none are given, and say so in the key.
3. Build and check: `python ../darshan-singh-meel-diagrams/scripts/diagram.py spec.json -o x.svg --mermaid x.mmd --png x.png`. Every `LAYOUT` or `layout:` line is a defect; the message names the fix.
4. Look at the PNG (light and `--dark`); read every label; check the numbers (totals, conversions, weighted scores) against the source.
5. Embed per the base `references/embedding.md`; types without Mermaid ship as the SVG file in Markdown.

## Notation rules
- Colour = one meaning, always named in the key or legend and repeated in text (heat word as tag, status word in sub, stance in legend), so greyscale still works.
- Red only for failure, risk, off track, missing or threats; green for strong, on track, helpful; amber for weak, at risk, critics, waiting.
- Quadrants: Mermaid numbering (1 top right, 2 top left, 3 bottom left, 4 bottom right) in Mermaid output; the spec uses `top_left` … `bottom_right`. No point on a divider (0.5, or the middle of an odd stakeholder scale): pick a side.
- Team topology: four team types and three interaction modes as named by Team Topologies (check: https://teamtopologies.com/key-concepts).
- Funnel: default bars narrow evenly (`scale: "steps"`, key says "not to scale"); `scale: "value"` makes width proportional but small stages keep a minimum width for their number.
- Decision matrix: weights are shown as % of their sum; the weighted score is Σ(weight × score) / Σweight on the score scale.
- Fishbone: problem on the right, categories on bones; 4-8 categories (classic sets: 6M for production, 4P/8P for services) - label them in the reader's words.

## Sizing limits
- Canvas ≤ 1000px; each type raises `layout: … : <fix>` instead of overflowing.
- org chart: leaves stack under their manager automatically when wide (`stack_leaves`); still too wide → one chart per direct report.
- mind map: ≤ 3 levels; the deepest level folds into sub text when wide (`compact`).
- value stream ≤ 4 stages with `start` and `end`, ≤ 6 without; SIPOC ≤ 8 steps; fishbone ≤ 8 categories; decision matrix ≤ 6 options; quadrant ~8 items at the default size (10-12 → `size: [720, 500]` or drop `sub`).
- Labels: short names; detail in `sub`; causes and bullets a short phrase each.

## Common mistakes
- A SWOT with no "so what": the Notice names the pair that matters.
- Quadrant items placed by feel with no stated scale: say in the key how x and y were scored.
- KPI tree without an operator or with mixed units under one `+`.
- Capability map that mixes capabilities ("Pricing") with systems ("SAP") or teams.
- Value stream that sums wait and process times in different units: one `unit` per diagram.
- Funnel numbers that grow from one stage to the next (validation error) or stages from different periods.

## Rules
- Follow every rule of `darshan-singh-meel-diagrams`; this skill never edits its files.
- No real personal data in org charts or stakeholder maps unless the page's audience may see it; roles over names by default.
- Notation facts from the pages in `references/sources.md`; unverified points carry `check: <page>`.
- Examples: `references/examples/` (one spec + SVG per type); tests: `python tests/run.py`.

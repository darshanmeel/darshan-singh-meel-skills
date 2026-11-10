# Doc spec — input to build.py
`python <skill>/references/templates/build.py generated-docs/_spec/<doc>.json generated-docs/<doc>.html`
Layout check after every build: `python <skill>/references/templates/check.py <doc.html> [shot.png]` — must report 0 problems.
Working specs + rendered results: `../examples/` (technical-pipeline, overview-pipeline, user-guide-data, user-guide-app). Copy the closest one.

```json
{"type": "overview | technical | user-guide | custom",
 "app_types": ["pipeline", "ui", "api", "cli", "events"],
 "title": "…", "subtitle": "stack · schedule · sources",
 "tabs": {"does": [], "doesnt": [], "limitations": [], "top_issues": [{"text": "…", "status": "Confirmed (review) | Not verified"}]},
 "sections": {"<section name>": [<block>, …]}}
```
- `app_types`: everything that applies (mixed apps list several). Drives the required sections below.
- Build prints `WARN` for a missing required section or a flow/task without an example → fix before delivering.

## Sections — fixed names and order (build sorts them; others refused)
| Document | Sections (kept only if the code has it) | Always required | Required by app type |
|---|---|---|---|
| overview | What it is and why · How it works · Who uses it · Example · Value and cost · Schedule · Design and operational risks · Words used | What it is and why, How it works, Example | — |
| technical | Overview · Architecture · Job DAG and schedule · Screens and navigation · Endpoints · Commands · Events and messages · Main flows · Data model · Business rules · Configuration · Security and access · Deploy and environments · Operations · Performance and limits · Tests · Key decisions | Overview, Architecture, Main flows, Deploy and environments, Operations | pipeline: Job DAG and schedule, Data model · ui: Screens and navigation · api: Endpoints · cli: Commands · events: Events and messages |
| user-guide | How it reaches you · Screens · What answers what · **How to …** (one per task, any name starting "How to ") · When data is fresh · History and deletions · Errors and messages · Problems and fixes · Who to contact | How to … (≥1), Problems and fixes, Who to contact | pipeline: What answers what, When data is fresh · ui: Screens · api: What answers what |

`custom` (README, runbook, design doc, code explanation, summary of a PDF): section names free, kept in written order; same blocks and look.
Every document ends with **Known issues, assumptions, and decisions needed**. Technical sections are numbered by the build.
A required section the source doesn't cover → keep it with one bullet: "Not defined in source — confirm with owner."

## Blocks
Text fields accept `` `code` ``, `**bold**`, `[synthetic]`. Any block takes `"source": "tests/x.py:42"` → cited under it.

| type | fields |
|---|---|
| text | text — one lead line |
| h3 | text — sub-heading (one per flow, task, or job pattern) |
| bullets | items |
| table | cols, rows — a `Status` column renders badges |
| steps | rows, cols? (default Step · In · Out) — numbered |
| terms | items `[[term, meaning]]` |
| flow | nodes, edges, id?, title?, parent?, lanes?, groups?, numbered? (true), box_w? (180), key?, notice? |
| er | entities `[{id, name, schema?, grain?, cols [[name, "PK FK"]]}]`, rels `[{from, from_col, to, to_col, label?, logical? (true = dashed)}]` |
| journey | stages `[{title, sub?, changed?, what?, rows}]`; row = `[field, value]` or `{field, sub?, value, old?, changed?, calc?}`; `null` → NULL |
| io | label (SQL · Request · Command · Action), title?, input, lang (sql · json · shell · text), result (`{cols, rows, synthetic: [row idx]}` or text), result_title |
| examples | items `[{case: typical/edge/rejected/failure, tag?, title, in, out, source?, synthetic?}]`; in/out = text or `[[k, v]]` |
| issues | items `[{sev: Must/Should/Question/Other, issue, where, impact, status, fix, see, do}]` — columns chosen per document |
| details | summary, blocks, open? — collapsible |

**Flow nodes:** `{id, label, col 0–3, row, kind?, tag?, sub?, bullets?, in?, out?, runs?, tip?, see?}`
- kind: blank = step/system · person · entry · code · data · shape (data changes shape) · decision · fail · confirm (outside repo / inferred).
- `bullets` 1–3 short lines · `in`/`out` short values · `runs` "runs as 10 steps" · `tip` hover note · `see: "B"` → "▸ Diagram B".
**Edges:** `{from, to, label?, dashed? (data moves), fail? (red)}`.
**Groups:** `[{label: "Repeats for each …", nodes: [ids]}]` — dashed purple frame.
**Sub-flow:** give the parent flow `id: "A"`; the box that opens it gets `see: "B"`; the child flow gets `id: "B"`, `title`, `parent: ["A", "<box label>"]` and goes right after A.

## Which diagram for what
| Show | Block |
|---|---|
| L0 big picture (≤7 boxes) | flow, no lanes |
| L1 order of steps, who does what | flow with lanes |
| L2 architecture | flow with lanes per platform, `code` boxes |
| L3 inside one step / job | sub-flow (flow with id + parent) + steps table |
| Repeated pattern | group around the repeated boxes |
| Data model | er + views table |
| One record through stages | journey |
| Query, request, command, UI action | io |
| Rule or flow behaviour | examples (typical + edge/failure) |

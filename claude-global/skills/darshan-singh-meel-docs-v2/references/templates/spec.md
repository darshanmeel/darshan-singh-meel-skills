# Doc spec — input to build.py
Run from the repo root: `python <skill>/references/templates/build.py generated-docs/_spec/<doc>.json generated-docs/<doc>.html`
Layout check after every build: `python <skill>/references/templates/check.py <doc.html> [shot.png]` — must report 0 problems (overflow, overlaps, labels on boxes or frames, edges through boxes, frames or group labels, edges on top of each other or <20 px apart, cut-off values, diagrams, journeys or tables wider than the page, sideways scroll).
Working specs + rendered results: `../examples/` (list at the end). Copy the closest one.

```json
{"type": "overview | technical | user-guide | custom",
 "app_types": ["pipeline", "ui", "api", "cli", "events"],
 "title": "…", "subtitle": "stack · schedule · sources",
 "review": "reviews/<file>",
 "tabs": {"does": [], "doesnt": [], "limitations": [], "top_issues": [{"text": "…", "status": "Confirmed (review) | Not verified"}]},
 "sections": {"<section name>": [<block>, …]}}
```
- `app_types`: everything that applies (mixed apps list several). Drives the required sections below.
- `review`: the one review file the known issues come from — the newest in `reviews/` (several and unclear → ask the user). Shown under Known issues and in the stamp. WARN if `reviews/` has files and none is named, or the named one is missing or not the newest.
- **Build output:** `ERROR` lines (wrong block, wrong order, wrong labels, wrong row length) stop the build. `WARN` lines (missing section, below a minimum, no example, review) → fix, or explain each in the doc.
- **Added by the build, never in the spec:** version stamp under the title (repo commit from `git rev-parse --short HEAD` with `+dirty` for uncommitted changes outside the output folder · graph commit from the graph's `meta.json` · review file; a part that isn't available is left out), and an empty `.generated-by-darshan-singh-meel-docs` marker next to the HTML (the graph skill skips folders holding it). Files are read and written as UTF-8.

## Sections — fixed names and order (build sorts them; others refused)
| Document | Sections (kept only if the code has it) | Always required | Required by app type |
|---|---|---|---|
| overview | What it is and why · How it works · Who uses it · Example · Value and cost · Schedule · Design and operational risks · Words used | What it is and why, How it works, Example | — |
| technical | Overview · Architecture · Job DAG and schedule · Screens and navigation · Endpoints · Commands · Events and messages · Main flows · Data model · Business rules · Configuration · Security and access · Deploy and environments · Operations · Performance and limits · Tests · Key decisions | Overview, Architecture, Main flows, Deploy and environments, Operations | pipeline: Job DAG and schedule, Data model · ui: Screens and navigation · api: Endpoints · cli: Commands · events: Events and messages |
| user-guide | How it reaches you · Screens · What answers what · **How to …** (one per task, any name starting "How to ") · When data is fresh · History and deletions · Errors and messages · Problems and fixes · Who to contact | How it reaches you, How to … (≥1), Problems and fixes, Who to contact | pipeline: What answers what, When data is fresh · ui: Screens · api: What answers what |

`custom` (README, runbook, design doc, code explanation, summary of a PDF): section names free, kept in written order, no recipes; same blocks and look.
Every document ends with **Known issues, assumptions, and decisions needed**. Technical sections are numbered by the build.
A required section the source doesn't cover → keep it with one bullet: "Not defined in source — confirm with owner." (a recipe minimum still WARNs; say so in the doc).

## Recipes — the blocks of each section, in order
A recipe is a regex over block types: `x` exactly one · `x?` optional · `x*` any number · `x+` one or more · `(a b)+` repeat the group · `(a|b)` either. Blocks inside `details` count in place. Free inside a recipe: how many items, which boxes, steps, examples, sub-flows, wording.
Wrong block or order → ERROR with the recipe and the actual sequence. Only a required block missing → WARN.

**Overview** (business words)
| Section | Recipe | Also |
|---|---|---|
| What it is and why | `labels` | first 4 labels exactly What · Why · Key idea · Result |
| How it works | `flow steps?` | L0: one row of boxes (3–7), person boxes in row 1, no lanes, sub-flows or `box_w`, ≤2 bullets per box. Box width and gaps are set by the build from the box count and the longest arrow label (min 100 px a box): 7 boxes fit only without arrow labels, 6 with 1–2 short words, 5 with ≤3 words; too many → ERROR naming how many fit |
| Who uses it | `people` | |
| Example | `text? journey examples bullets?` | journey 3–5 stages × 3–8 rows · 2–6 cards, at least one `edge`, `rejected` or `failure` (WARN otherwise) |
| Value and cost | `labels` | each label Value or Cost |
| Schedule | `schedule bullets?` | |
| Design and operational risks | `bullets` | aim for ≤3 (guidance, not checked) |
| Words used | `terms` | |
| Known issues… | `text? issues assumptions? decisions?` | every top issue listed · WARN above ~12 |

**Technical** (complete)
| Section | Recipe |
|---|---|
| Overview | `text? flow` |
| Architecture | `flow components bullets?` |
| Job DAG and schedule | `flow+ schedule bullets?` (A plus sub-flows B, C…); each job pattern gets its examples as an `h3` in Main flows |
| Screens and navigation | `flow+ elements bullets?` |
| Endpoints | `flow+ endpoints bullets?` |
| Commands | `flow+ commands bullets?` |
| Events and messages | `flow+ events bullets?` |
| Main flows | `(h3 text? steps? flow* journey? examples io* bullets?)+` — one `h3` per flow, each with an example |
| Data model | `text? er+ views bullets?` |
| Business rules | `rules examples?` — WARN with fewer example cards than rules (one card per rule at least) |
| Configuration | `config bullets?` |
| Security and access | `access bullets?` |
| Deploy and environments | `flow? steps io* environments bullets?` |
| Operations | `io* symptoms (h3 steps io*)?` — the h3 is "Rerun and backfill" |
| Performance and limits | `bullets` |
| Tests | `tests io* bullets?` |
| Key decisions | `choices` |
| Known issues… | `text? issues (h3 table)? assumptions? decisions?` — the h3 is "Unused files" |

**User guide**
| Section | Recipe |
|---|---|
| How it reaches you | `flow bullets? examples?` |
| Screens | `flow+ elements` |
| What answers what | `text? flow* table (h3 bullets)?` — the h3 starts "Columns every" |
| How to … | `steps (io\|examples\|journey)+ bullets?` |
| When data is fresh | `flow? (schedule\|table) io? bullets?` |
| History and deletions | `text? journey bullets? io?` |
| Errors and messages | `messages` |
| Problems and fixes | `problems` |
| Who to contact | `bullets` |
| Known issues… | `text? issues assumptions? decisions?` |

## Blocks
Text fields accept `` `code` ``, `**bold**`, `[synthetic]`. Any block takes `"source": "tests/x.py:42"` → cited under it.
Any table cell (typed tables, `table`, issues) starting "Confirmed" or "Not verified" renders as a status badge; other values stay plain.

| type | fields |
|---|---|
| text | text — one lead line |
| h3 | text — sub-heading (one per flow, task, or job pattern) |
| bullets | items |
| labels | items `[[label, text]]` → bullets with a bold label |
| table | cols, rows — only where a recipe says `table` |
| *typed table* | rows — headers are fixed by the build (below); each row must have exactly that many cells |
| steps | rows, cols? (default Step · In · Out) — numbered |
| terms | items `[[term, meaning]]` |
| flow | nodes, edges, id?, title?, parent?, lanes?, groups?, numbered? (true), box_w? (fixes the width; default 180 narrowed to 140 if arrow labels need room; not in overview), key?, notice? |
| er | entities `[{id, name, schema?, grain?, cols [[name, "PK FK"]]}]`, rels `[{from, from_col, to, to_col, label?, logical? (true, default = dashed)}]`, id?, title? ("Diagram C · orders area"), box_w? (table width, default 260, narrowed to fit 1020 px), key? |
| journey | stages `[{title, sub?, changed?, what?, rows}]`; row = `[field, value]` or `{field, sub?, value, old?, changed?, calc?}`; `null` → NULL |
| io | label (SQL · Request · Command · Action), title?, input, lang (sql · json · shell · text), result (`{cols, rows, synthetic: [row idx]}` or text), result_lang? (for a text result; default text), result_title |
| examples | items `[{case: typical/edge/rejected/failure, tag?, title, in, out, source?, synthetic?}]`; in/out = text or `[[k, v]]` |
| issues | items `[{sev: Must/Should/Question/Other, issue, where, impact, status, fix, see, do}]` — columns chosen per document; any other `sev` is listed under Other |
| details | summary, blocks, open? — collapsible |

**Typed tables** — `{"type": "<name>", "rows": [[…], …]}`
| type | columns |
|---|---|
| people | Who · What they get |
| schedule | Environment · Runs · Notes |
| components | Component · Responsibility · Where |
| rules | Rule · Input → output · Where |
| config | Setting · Default · Where · Purpose |
| access | Who · Access · How |
| environments | Environment · Where · How deployed |
| symptoms | Symptom · Cause · Fix |
| tests | Test · Covers |
| choices | Decision · Why |
| elements | Element · What it does |
| endpoints | Endpoint · Does · Example |
| commands | Command · Does · Example |
| events | Event · From → to · Payload |
| messages | Message · Means · Do |
| problems | Problem · What to do |
| views | View · Built from · Rows |
| assumptions | Assumption · Why it matters — adds h3 "Assumptions" |
| decisions | Decision · Options · Recommendation · If it waits — adds h3 "Decisions needed" |

**Flow nodes:** `{id, label, col 0–3, row, kind?, tag?, sub?, bullets?, in?, out?, runs?, tip?, see?}`
- kind: blank = step/system · person · entry · code · data · shape (data changes shape) · decision · fail · confirm (outside repo / inferred).
- `bullets` 1–3 short lines · `in`/`out` short values · `runs` "runs as 10 steps" · `tip` hover note · `see: "B"` → "▸ Diagram B".
**Edges:** `{from, to, label?, dashed? (data moves), fail? (red)}`.
**Groups:** `[{label: "Repeats for each …", nodes: [ids]}]` — dashed purple frame. Groups must not overlap or enclose a box that isn't in them (ERROR).
**Sub-flow:** give the parent flow `id: "A"`; the box that opens it gets `see: "B"`; the child flow gets `id: "B"`, `title`, `parent: ["A", "<box label>"]` and goes right after A.

**Layout (done by the build — never in the spec):**
- Long names break after `_ . / -`; box heights follow the wrapped lines; one height per row. A name needing more than 3 lines (sub, in/out: 2) is shortened in the middle (`ab…yz`), full name in the hover tip.
- Arrows run orthogonally through the gaps between rows and columns, never through a box. Parallel lines stay ≥20 px apart: each line along a row or column centre, and each line in a gap, gets its own offset.
- A box with more than 4 outgoing arrows: its targets go into one frame ("12 children") reached by one arrow, no per-child arrows or numbers. To name the frame, add a group with exactly those boxes.
- Each arrow label sits above its line, right of its number; if that doesn't fit, above its number, then on two lines; never on a box, a line, the arrowhead, a number or another label. Still no room after widening the gaps → ERROR: a label over 3 words → shorten it; otherwise too many lines crowd that gap → move boxes apart, drop labels the text already says, or use a sub-flow.
- Diagram wider than 1020 px → ERROR naming the diagram and the columns and boxes that don't fit: move them into a sub-flow behind one box.
- ER: parents one column left of their children, so lines only join neighbouring columns; a key to a table further away shows as `FK → table` in the row; one key to several tables branches from one point; labels sit near the many end. More than 9 tables, or too many levels for 1020 px (~4), → ERROR: one ER per area (`er+`).
- Journey: values wrap, stages ≥240 px, 3 per row; the next row starts with "continues: stage 4". Cards ≥260 px, each value under its label. Table cells break long names after `_ . / -`.

## Which diagram for what
| Show | Block |
|---|---|
| L0 big picture (3–7 boxes) | flow, no lanes |
| L1 order of steps, who does what | flow with lanes |
| L2 architecture | flow with lanes per platform, `code` boxes |
| L3 inside one step / job | sub-flow (flow with id + parent) + steps table |
| Repeated pattern | group around the repeated boxes |
| Data model | er + views |
| One record through stages | journey |
| Query, request, command, UI action | io |
| Rule or flow behaviour | examples (typical + edge/failure) |

## Examples (`../examples/`, each `<name>.json` + `<name>.html`, 0 ERROR · 0 WARN · 0 LAYOUT)
| Example | Shows |
|---|---|
| overview-pipeline | every overview recipe: `labels` (What · Why · Key idea · Result; Value · Cost), L0 flow with a person row + `steps`, `people`, journey 3×3 + 2 cards, `schedule`, `assumptions` + `decisions` |
| technical-pipeline | every technical recipe for a pipeline: sub-flow (A → B), group, typed tables, two main flows each with an example, `er` + `views`, rules + examples, `environments`, Operations with "Rerun and backfill" |
| user-guide-data | data user guide: view map + sub-flow, `table` + "Columns every …", How to … with `io` and with `journey`, `schedule`, `problems` |
| user-guide-app | UI user guide: How it reaches you (sign-in flow), screen map + sub-flow, `elements`, How to … with steps + cards, `messages`, `problems` |
| stress-technical | layout limits: long identifiers (wrap, middle ellipsis), 12-child fan-out + fan-in in one frame, 12 tables split into two ERs with an `FK → table` note, 4-stage journey on two rows, long card values, Known issues with "Unused files" |

Rebuild one: from a folder outside any git repo (so no stamp), `python ../templates/build.py <name>.json <tmp>/<name>.html`, copy the html back, then `check.py` it. Don't leave the marker file in `examples/`.

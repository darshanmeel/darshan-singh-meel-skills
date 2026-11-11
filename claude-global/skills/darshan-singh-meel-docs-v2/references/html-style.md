# HTML style: "workflow map", light blueprint
`templates/build.py` renders all of this from the spec (`templates/style.css`); never hand-write HTML, CSS or SVG. Rendered samples: `examples/*.html`.

## Page
- Off-white ground `#F6F6F3`, white section cards, thin `#D9DBDF` borders, ink `#17191D`. Flat: no gradients, shadows or emoji. Light only.
- IBM Plex Sans text; IBM Plex Mono for code names, tags, lane labels, table headers (system fonts as fallback).
- One self-contained file, CSS inline, no JavaScript, no network. Pure ASCII (entities). Numbered sections, table of contents. Meta generator `darshan-singh-meel-docs-v2 <templates version>`; stamp under the title.
- Opening tabs Does · Doesn't · Limitations · Top issues: CSS radio tabs, Does open; in print all four panels show.
- Print: white page, tabs expanded, tips and animation off. `prefers-reduced-motion` stops animation.

## Diagram notation — one meaning each
| Element | Look |
|---|---|
| Person | pill, ink border |
| Step / system | white box, 8 px radius |
| Code (`code`) | teal box, 4 px radius, mono name |
| Entry (`entry`) | 2 px ink border |
| Data (`data`) | grey fill |
| Data changes shape (`shape`) | amber box |
| Decision | lavender pill, ≥2 outgoing arrows |
| Failure (`fail`) | red dashed border; `fail` edge red |
| To confirm / outside repo (`confirm`) | grey dashed border |
| Group "Repeats for each …" | dashed purple frame, label top-left |
| Fan-out frame ("N children") | solid light-purple frame |
| Lane | grey band, mono caps label |
| Arrows | solid = then/calls · dashed = data moves (animated) · black dots = order |
- Box parts: `tag` (mono caps), title, `sub`, 1–3 bullets, IN (blue outline) / OUT (green fill), `runs`, "▸ Diagram X" link. Hover tip (`data-tip`) is extra only; it never counts as content.
- Above each diagram "Diagram X · title"; under it the one-line key (once per section: the same key again is left out) and "Notice:" caption.
- Main flows diagram: titled `<h3>, N steps` (the flow, not a box); draws the branches only; arrows that are strip steps show the strip's number, branch arrows a label only.
- ER: entity cards (mono name, schema, grain), columns with `PK` (ink) / `FK` (blue) badges, `FK → table` for a far table; lines = keys only, dashed = logical; no keys → grid, 3 per row.

## Other blocks
- **Example cards** ≥260 px: top border green typical · amber edge · red rejected/failure; header `EXAMPLE <id>` + case + title; EXPECT, IN, OUT, source. Business rules have none: each rule row holds its example (`in → out`) or a "see step 5.1.3" link.
- **ipo (Main flows):** one strip Input ▸ numbered step (do → out, the step's `why` as one muted line, red "else … ▸ Diagram X" on a branch step, `file.py:12` with the full path as hover title) ▸ … ▸ Output, wraps; a column under 720 px; "Sources:" (full paths) once under it. Step anchor `#st-5.1.3`. Under it the trace grid: a row per example (id `5.1a`, case badge, title, EXPECT) × In · 1…N · Out; `=` only unchanged from the column before, `–` not reached or not touched by this example (grey); one legend line for the tokens used, once per section; examples after the first two in a `<details>`; sources below. Under 720 px rows stack, each value labelled "k do", `=`/`–` cells and the legend hidden, traces after the first behind one "More examples" toggle (CSS: only the toggle input and its label are hidden on a desktop, never a trace row), strip steps compact.
- **Operations tasks:** one table Command · When · Where under one heading row per task (rows numbered when more than one); Where as `basename:line`, full paths once under it.
- **Tables:** a column with one value in every row (3+ rows) is said once above the table, "All rows: Col = value"; a status column with one status in ≥ half of its rows shows only the others ("… unless shown"). A group row's `covers` count and names are its hover title. A cell naming more than 6 names shows 6, then "+N more" (full cell in its hover title). Adjacent tables of one shape render as one. Rules: Where as `basename:line`, full paths once under the table; a "see step" row's empty cells join its example cell; Why / impact keeps a minimum width. Under 720 px every table row stacks as a labelled block (nothing scrolls or is cut).
- **Lists:** typed tables with 1–2 rows and one-column tables render as a list (first cell bold).
- **Journey:** stage cards ≥240 px, 3 per row; changed cell amber, old struck through → new green; calculated purple.
- **io / payload:** header strip (`IN` blue, `OUT` green; label SQL · Request · Command · Call · Action), pretty-printed input with token colours (sql, json, shell; others plain), result table or text.
- **Steps table:** numbered black dots, fixed columns per section.
- **Status chips:** Confirmed (review / test / code) red outline · Not verified amber · Fixed since review green · synthetic lavender. An issue status outside this list → build ERROR.

## Ported or rewritten code (old → exact copy → new), `type: "custom"`
1. Start strip: implementations joined by "ported line by line" / "rewritten" arrows, with counts.
2. Run flow of the new code with line numbers.
3. Routine map: old routine → copy → new function; what folded together; what changed.
4. Line-by-line table: step · old · new · what changed, real code lines.
5. Changes and tests: cards C1..Cn (old, new, test evidence), test table, not ported, limits.
- Line numbers from a script, never by hand. Reuse C1..Cn everywhere.

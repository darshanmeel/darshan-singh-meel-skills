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
- Above each diagram "Diagram X · title"; under it the one-line key and "Notice:" caption.
- ER: entity cards (mono name, schema, grain), columns with `PK` (ink) / `FK` (blue) badges, `FK → table` for a far table; lines = keys only, dashed = logical; no keys → grid, 3 per row.

## Other blocks
- **Example cards** ≥260 px: top border green typical · amber edge · red rejected/failure; header `EXAMPLE <id>` + case + title; EXPECT, IN, OUT, source. Business rules with >3 items: one table `Ex · Case · Expect · In · Out`, same colours.
- **ipo (Main flows):** one strip Input ▸ numbered step (do → out, `where`) ▸ … ▸ Output, wraps; a column under 720 px. Under it one trace grid: a row per example (id `5.1a`, case badge, title, EXPECT) × In · 1…N · Out, `=` = unchanged; sources below; rows stack under 720 px.
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

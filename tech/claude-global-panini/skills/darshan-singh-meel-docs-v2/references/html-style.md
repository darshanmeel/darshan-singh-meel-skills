# HTML style: "workflow map", light blueprint
`templates/build.py` renders all from spec (`templates/style.css`); never hand-write HTML/CSS/SVG. Samples: `examples/*.html`.

## Page
- Ground `#F6F6F3` · white section cards · thin `#D9DBDF` borders · ink `#17191D`. Flat: no gradients, shadows, emoji. Light only.
- IBM Plex Sans; IBM Plex Mono → code names · tags · lane labels · table headers (system fallback).
- One file: CSS inline, no JS, no network, pure ASCII (entities). Numbered sections + TOC. Meta generator `darshan-singh-meel-docs-v2 <templates version>`; stamp under title.
- Tabs Does · Doesn't · Limitations · Top issues: CSS radio, Does open.
- Print: white, all tab panels shown, tips + animation off. `prefers-reduced-motion` → no animation.

## Diagram notation — one meaning each
- Person: pill, ink border · step/system: white box, 8 px radius · `code`: teal, 4 px radius, mono name · `entry`: 2 px ink border · `data`: grey fill · `shape` (data changes shape): amber.
- Decision: lavender pill, ≥2 out-arrows · `fail`: red dashed border, `fail` edge red · `confirm` (outside repo / inferred): grey dashed border.
- Group "Repeats for each …": dashed purple frame, label top-left · fan-out "N children": solid light-purple frame · lane: grey band, mono caps label.
- Arrows: solid = then/calls · dashed = data moves (animated) · black dots = order.
- Box: `tag` (mono caps) · title · `sub` · 1–3 bullets · IN (blue outline) / OUT (green fill) · `runs` · "▸ Diagram X" link. `data-tip` hover = extra, never content.
- Above: "Diagram X · title"; below: one-line key (once per section) + "Notice:".
- Main flows diagram: title `<h3>, N steps` (flow, not a box); branches only; strip-step arrows show the strip number, branch arrows label only.
- ER: entity cards (mono name, schema, grain) · `PK` (ink) / `FK` (blue) badges · `FK → table` for far table; lines = keys only, dashed = logical; no keys → grid, 3/row.

## Other blocks
- **Example cards** ≥260 px, top border green typical · amber edge · red rejected/failure; header `EXAMPLE <id>` + case + title; EXPECT · IN · OUT · source. Rules: none, example in the row or "see step 5.1.3" link.
- **ipo (Main flows):** strip Input ▸ numbered step (do → out, muted `why` line, red "else … ▸ Diagram X", `file.py:12` + full path in hover) ▸ … ▸ Output, wraps; column <720 px; "Sources:" once; anchor `#st-5.1.3`. Trace grid: row per example (id `5.1a` · case badge · title · EXPECT) × In · 1…N · Out; `=` only unchanged · `–` not reached / not touched (grey); legend line once per section; examples 3+ in `<details>`; sources below. <720 px: rows stack, values labelled "k do", `=`/`–` + legend hidden, traces after the first behind one "More examples" toggle (CSS; desktop hides only the toggle, never a trace row), strip compact.
- **Operations tasks:** Command · When · Where under a heading row per task (rows numbered if >1); Where `basename:line`, full paths once below.
- **Tables:** column one value in all rows (3+) → "All rows: Col = value" above; status ≥½ one value → only others shown ("… unless shown"). Group row `covers` count + names = hover title. Cell >6 names → 6 + "+N more", full in hover. Adjacent same-shape tables → one. Rules: Where `basename:line`, full paths once below; "see step" row's empty cells join its example; Why / impact min width. <720 px: every row a labelled block, nothing scrolls or is cut.
- **Lists:** typed tables 1–2 rows · one-column tables → list (first cell bold).
- **Journey:** stage cards ≥240 px, 3/row; changed cell amber, old struck → new green; calculated purple.
- **io:** strip (`IN` blue, `OUT` green; SQL · Request · Command · Call · Action) · pretty input, token colours (sql · json · shell; else plain) · result table/text.
- **Steps:** numbered black dots, fixed columns per section.
- **Status chips:** Confirmed (review/test/code) red outline · Not verified amber · Fixed since review green · synthetic lavender. Other status → ERROR.

## Ported or rewritten code (old → exact copy → new), `type: "custom"`
1. Start strip: implementations, "ported line by line" / "rewritten" arrows, counts.
2. New code's run flow, line numbers.
3. Routine map: old → copy → new function; folded; changed.
4. Line table: step · old · new · change, real lines.
5. Changes + tests: cards C1..Cn (old, new, test evidence) · test table · not ported · limits.
- Line numbers by script, never hand. C1..Cn reused everywhere.

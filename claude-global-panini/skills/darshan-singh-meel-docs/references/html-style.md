# HTML style: "workflow map", light blueprint

Working examples of everything below: `example-components.html` (next to this file). Copy its CSS and markup patterns.

## Look
- Off-white ground `#F6F6F3`, white cards, thin `#D9DBDF` borders, ink `#17191D`.
- IBM Plex Sans for text; IBM Plex Mono for code names, tags, lane labels (system fonts as fallback).
- Flat: no gradients, shadows, emoji, or left-stripe cards. Light only, printable.
- One self-contained file: all CSS and any JavaScript inline — no CDN, no network calls.
- **Fully readable and printable with JavaScript off;** JS only adds enhancements.

## Zoom levels — one question each
- **L0 overview:** people, systems, inputs, outputs, numbered interactions. ≤ ~7 boxes, readable in ~10 seconds.
- **L1 flow:** swimlanes per person/system, numbered steps, loops, decisions. The default for anything that happens in order.
- **L2 architecture / code map:** frames per platform or entry on the left with calls left → right, real names.
- **L3 step-by-step:** numbered main path, decision diamonds, failure branches, exact values per step.
- **Side view:** variant table, data lineage bars (open questions only in drafts).

| Document | Levels |
|---|---|
| Overview, User guide | L0, L1, side view (L2 optional) |
| Technical | L0 for orientation, L2, L3, ER |

Typical Technical doc: L0 → L2 → ER → one L3 per important process, each followed by its examples. Failure points and silent risks: Technical only.

## Notation — one meaning each
| Element | Look |
|---|---|
| Person | Pill, ink border |
| Step | White box, 8px radius |
| Code routine | Teal box, 4px radius, mono name |
| Entry point | 2px ink border, `ENTRY` |
| Decision | Lavender diamond |
| Data (file, table, sheet) | Grey fill, `DATA` |
| Data changes shape | Amber box |
| Repeated part | Dashed purple group, "Repeats for each …" |
| To confirm / never called | Dashed grey |
| Failure branch | Red dashed |
| Swimlane | Grey band, mono caps label |
| Arrows | Solid = then/calls · dashed = data moves · numbers = order |
| Variants | Mono chips `N` (blue) / `R` (orange); variant-only arrow in its colour; "N ≠ R" where they differ |

Every diagram: a one-line key beside it and a one-line "Notice:" caption.

## Components
**Step boxes with IN / OUT** (L1, L3)
- `STEP n` tag, title (mono for code names), 1–3 bullets of what it does, then IN (outlined blue) / OUT (filled green) with short values (`2 rows · 1 rejected`). Full payloads go in payload blocks.
- Box heights fit the content — no empty space.

**Step table** under a numbered diagram: `# | Step | In | Out`, mono values, numbers matching the diagram. Use it instead of a long list with inline code.

**Payload blocks** for requests, responses, rows, configs
- Never a long JSON/SQL/call inside a sentence.
- Pretty-printed, header strip with `IN` / `OUT` and what it is; side by side when they pair.
- Token colours added at build time (work without JS). SQL one clause per line; CSV as a table.

**Data journey** — one record through a pipeline
- 3–5 stage cards left → right, each a small `field | value` table.
- Changed value = amber cell, `old` struck through → `new` in green; calculated values in purple.
- One line under each stage: what the step did. Values never wrap mid-word.

**Opening tab box** — every document: tabs Does · Doesn't · Limitations · Top issues right after the title; CSS-only radio tabs, first tab open, all panels shown in print.

**Example cards** — 2–4 per important rule or flow, same IN / OUT shape: typical, then edge / rejected / failure cases that behave differently.

**ER diagram** — data model only
- Entity cards: table name (mono), schema label, grain as subtitle, key columns with `PK` / `FK` badges, long column lists summarised (`+ 31 business columns`).
- Lines mean keys only: PK row → FK row, `‖` = one, crow's foot = many, labelled with the key columns. Solid = enforced, dashed = logical (not enforced).
- **Never flow:** no app code, procedures, jobs, or "calls / writes / reads" arrows — those go in flow and architecture diagrams.
- Tables with no keys to others stand alone (say so in one bullet). Views go in a `View | Built from | Rows` table under the diagram.

**Same patterns for every stack**
| Stack | Swimlanes | Step (IN → OUT) | Payload | Data journey |
|---|---|---|---|---|
| Airflow | Scheduler · worker · target | Task: interval + upstream data → partition written | Rendered SQL/command for one `ds` | One partition through the DAG |
| dbt | Sources · staging · intermediate · marts | Model: refs → grain + row count | Compiled SQL | One key through the models |
| SQL / Snowflake | Objects or CTEs | Statement: rows + grain → rows + grain | Formatted SQL + result table | Sample rows per CTE |
| Spark / Databricks | Driver · cluster · storage | Stage: schema + rows → schema + rows | Schema, job config | One record per stage |
| Athena / Iceberg | S3 · catalog · engine | Query/MERGE: files scanned → snapshot | SQL + scan size | One row across snapshots |
| Terraform | Repo · CI · cloud account | Plan/apply: config → resources changed | Plan excerpt (`+ ~ -`) | Resource before → after |
| RBAC / governance | Identity · roles · objects | Grant: role → privilege | Grant statements | Person → role → access |
| APIs / apps | Client · app · database | Endpoint: request → response/rows | Request/response JSON | One record client → table |

## Interactive and flowing
- Dashed data arrows animate in the direction data moves.
- Hover a box → its connections highlight, the rest fades (CSS `:has()`, rules generated at build time). Tooltips (`data-tip`) for one-line details.
- `<details>` for drill-downs; CSS-only tabs (radio inputs) where useful.
- Optional inline JS: click to pin a highlight, Play / Next through numbered steps, search/filter big tables, zoom/pan big diagrams.
- Animation off for `prefers-reduced-motion` and print; interactive controls hidden in print.

## Building diagrams
- Boxes absolutely positioned on a fixed canvas (grid-aligned, gaps ≥ 40px); arrows in one inline SVG layer, straight or right-angled, never crossing a box.
- Built by a small build script kept next to the HTML, injecting each diagram between `<!--map:NAME-->` … `<!--/map:NAME-->` so it can be regenerated.
- **Tools, best available first** (use what's installed; ask before installing anything):
  1. Node/JavaScript — `elkjs`/`dagre` auto-layout for big graphs, `mermaid-cli` to SVG, D3 for charts, Playwright to screenshot.
  2. Python — the build script lays out boxes; Graphviz `dot -Tsvg` for dense graphs; matplotlib for charts.
  3. Hand-written SVG/CSS.
- Output is always static SVG/HTML in the page, restyled to this palette — never rendered at view time.
- Tables, lists, and bars use normal flex/grid layout.

## Checks before finishing
- Text never overflows or touches a border: size boxes from the longest label (~7.5px per mono character at 12px, plus padding) or shorten it; tags sit inside the padding.
- Canvas ≤ 1000px wide — no horizontal scroll; split into two diagrams instead.
- Arrows never cross boxes or labels; parallel lines ≥ 20px apart; labels ≥ 12px, 2–4 words.
- Every example is in a proper format (table, pretty JSON, formatted SQL, command block).
- Render and screenshot at 100% and in print preview; fix overlap, wrapping, empty space.

## Ported or rewritten code (old → exact copy → new)
One developer page:
1. **Start strip:** implementations joined by "ported line by line" / "rewritten" arrows, with counts.
2. **Run flow** of the new code with line numbers.
3. **Routine map:** old routine → copy → new function; groups that fold together; what changed.
4. **Line-by-line deep dive:** step / old per variant / new / what changed, real code lines, a dark "tricky code in plain words" panel.
5. **One section per routine:** what it does, then code tabs — old (default), exact copy, new (CSS-only tabs).
6. **Changes and tests:** cards C1..Cn (old, new, test evidence), test table, not ported, limits.
- Tags: `OLD` ink-filled, `COPY` ink-outlined, `NEW` green `#1E6B43` (green = new code only). Reuse C1..Cn everywhere. Compute every line number with a script, never by hand.

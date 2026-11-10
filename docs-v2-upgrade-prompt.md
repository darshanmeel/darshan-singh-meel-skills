# Prompt: finish darshan-singh-meel-docs-v2

Paste everything below the line into Claude Code (Opus). Start it inside a repo that already has v2 docs, so it can test against real output.

---

Finish the skill `~/.claude/skills/darshan-singh-meel-docs-v2/`. Do **not** touch `~/.claude/skills/darshan-singh-meel-docs/` (v1 stays as is). Follow my CLAUDE.md. Plan with me first (one AskUserQuestion round at most), then build, then test until everything passes.

## Goal
Docs from any repo (pipeline, UI app, API, CLI, events) come out with the **same skeleton every run**: same sections, same block order inside each section, same look. The model stays free to choose the content inside that skeleton. **Some differences are fine; a different-looking page is not.** Diagrams never overlap and stay readable.

## Already done (in the skill now)
- **Same four questions and rules as v1:** opening tabs Does · Doesn't · Limitations · Top issues; last section "Known issues, assumptions, and decisions needed"; docs describe and don't review.
- **`references/templates/build.py`:** builds HTML from a JSON spec. The model never hand-writes HTML, CSS or SVG.
  - **Sections:** fixed names and order per document (overview · technical · user-guide), plus `custom` with free section names.
  - **Required sections:** by `app_types` (pipeline · ui · api · cli · events). WARN for missing sections and for a flow or task with no example.
  - **Blocks:** text · h3 · bullets · table · steps · terms · flow · er · journey · io (query/request/command + result) · examples (cards) · issues · details.
  - **Flows:**
    - lanes, dashed groups ("Repeats for each …")
    - sub-flows: a box with `see: "B"` opens Diagram B, which carries `parent`
    - box contents: tags, bullets, IN/OUT, `runs`, hover `tip`
    - arrow styles: failure arrows, numbered arrows, label-aware gaps
  - **Typed issue tables:** columns set per document; Must · Should · Question · Other groups.
  - **Example markers:** synthetic badges and a source line on any block.
- **`references/templates/style.css`:** the shared look. **`spec.md`:** the spec format. **`references/examples/`:** 4 working specs with rendered HTML (technical-pipeline, overview-pipeline, user-guide-data, user-guide-app).
- **`references/templates/check.py`:** renders the doc in Playwright at 1200 px and prints `LAYOUT section | problem | item` for:
  - text overflowing a box
  - boxes overlapping
  - a label or number on a box
  - labels overlapping
  - a group label on a box
  - a value cut off
  - a diagram or journey wider than the page
  - sideways page scroll

  Exits 1 if anything is found.
- **Output:** specs saved in `generated-docs/_spec/`; files tagged `darshan-singh-meel-docs-v2`.

## Problems seen in real runs (why this is needed)
- **Insides differ between runs:** two runs on the same code got the same section list but different insides: block types, table column names, box sizes, amounts, decisions as bullets in one run and a table in the other.
- **Workflows differ:** each run built its own (plan/build/verify, or plan/build/check/fix, with or without render).
- **Overlaps are heavy in technical docs:** long code names overflow boxes; labels and numbers sit on boxes; edges cut through boxes; 12-way fan-outs pile labels on one trunk; group labels collide; ER lines cross entities and the grain text overlaps the first row; diagrams and journeys are wider than the page. One real technical doc had ~100 `check.py` problems.
- **Small bugs:**
  - em dashes became � on Windows (no explicit UTF-8)
  - any column named "Status" turned plain values like "active" into amber badges
  - journey values never wrap
  - Known issues pulled from different review files in different runs

## Pending — do all of this

### 1. Section recipes (skeleton fixed, content free)
- Each section has a recipe: allowed block types, in order, with quantifiers, written as a tiny regex over block types, e.g. `"text? flow steps?"`, `"(h3 text? steps? flow* journey? examples io*)+"`.
- Wrong block or order → build error showing the recipe and the actual sequence. Missing minimum → WARN.
- Free inside a recipe: how many items (above the minimum), which boxes, steps and examples, sub-flows when needed, and wording.

Overview (simple, business words):
| Section | Recipe |
|---|---|
| What it is and why | `labels`, first 4 labels exactly What · Why · Key idea · Result |
| How it works | `flow` (L0: one row plus people below, fixed box width, ≤2 bullets per box, no lanes or sub-flows), then `steps?` |
| Who uses it | `people` |
| Example | `text?` `journey` `examples` `bullets?` |
| Value and cost | `labels`, each label Value or Cost |
| Schedule | `schedule` `bullets?` |
| Design and operational risks | `bullets` |
| Words used | `terms` |
| Known issues… | `text?` `issues` `assumptions?` `decisions?` |

Technical (complete):
| Section | Recipe |
|---|---|
| Overview | `text?` `flow` |
| Architecture | `flow` `components` `bullets?` |
| Job DAG and schedule · Screens and navigation · Endpoints · Commands · Events and messages | `flow+` (A plus sub-flows B, C…), then that slot's table (`schedule` · `elements` · `endpoints` · `commands` · `events`), `bullets?` |
| Main flows | repeat per flow: `h3` `text?` `steps?` `flow*` `journey?` `examples` `io*` `bullets?` |
| Data model | `text?` `er+` `views` `bullets?` |
| Business rules | `rules` `examples?` |
| Configuration | `config` `bullets?` |
| Security and access | `access` `bullets?` |
| Deploy and environments | `flow?` `steps` `io*` `environments` `bullets?` |
| Operations | `io*` `symptoms`, then optionally `h3` "Rerun and backfill" `steps` `io*` |
| Performance and limits | `bullets` |
| Tests | `tests` `io*` `bullets?` |
| Key decisions | `choices` |
| Known issues… | `text?` `issues` (optional `h3` "Unused files" + table) `assumptions?` `decisions?` |

User guide (fixed frame; a section is kept only when the code has it, per SKILL.md):
| Section | Recipe |
|---|---|
| How it reaches you | `flow` `bullets?` `examples?` |
| Screens | `flow+` `elements` |
| What answers what | `text?` `flow*` `table`, then optionally `h3` "Columns every …" `bullets` |
| How to … (one per task) | `steps`, then ≥1 of `io` / `examples` / `journey`, `bullets?` |
| When data is fresh | `flow?` `schedule` or `table` `io?` `bullets?` |
| History and deletions | `text?` `journey` `bullets?` `io?` |
| Errors and messages | `messages` |
| Problems and fixes | `problems` |
| Who to contact | `bullets` |
| Known issues… | `text?` `issues` `assumptions?` `decisions?` |

**Typed tables:** the builder writes the headers, the model supplies rows only, and row length is checked.

| Block | Columns |
|---|---|
| `people` | Who · What they get |
| `schedule` | Environment · Runs · Notes |
| `components` | Component · Responsibility · Where |
| `rules` | Rule · Input → output · Where |
| `config` | Setting · Default · Where · Purpose |
| `access` | Who · Access · How |
| `environments` | Environment · Where · How deployed |
| `symptoms` | Symptom · Cause · Fix |
| `tests` | Test · Covers |
| `choices` | Decision · Why |
| `elements` | Element · What it does |
| `endpoints` | Endpoint · Does · Example |
| `commands` | Command · Does · Example |
| `events` | Event · From → to · Payload |
| `messages` | Message · Means · Do |
| `problems` | Problem · What to do |
| `views` | View · Built from · Rows |
| `assumptions` | Assumption · Why it matters (adds its own h3) |
| `decisions` | Decision · Options · Recommendation · If it waits (adds its own h3) |

New block `labels`: `[[label, text]]` → bullets with a bold label.

### 2. Amount rules (too little is the problem; a bit more is fine)
All of these are warnings only.

| Item (Overview) | Minimum | Warn above |
|---|---|---|
| Known issues | every Top-issues item | ~12 |
| Journey | 3 stages × 3 rows | 5 stages, 8 rows |
| Cards | 2 (typical + edge or failure) | 6 |
| L0 boxes | 3 | 7 |

Technical and User guide: minimums only. Every main flow, job pattern, rule and task has an example, and required sections are present.

### 3. Diagram layout (builder)
- **Long names:**
  - insert `<wbr>` after `_ . / -`
  - size mono text at ~7.4 px/char and set box heights from wrapped line counts
  - extreme identifiers get a middle ellipsis, with the full name in `tip`
- **Rows:** same height across a row. Overview box width is fixed (`box_w` not allowed).
- **Edges never cross boxes:** route orthogonally through the gaps between rows and columns, with parallel lines ≥20 px apart.
- **Fan-out > 4 from one box:** one arrow into a group frame ("12 child tasks"), children in a grid inside, no per-child arrows or numbers.
- **Labels:** each label sits beside its number, above the line, never on a box, number or other label. If it doesn't fit, widen the gap; if the page is full, fail the build and ask for a shorter label (≤3 words).
- **Groups:** never overlap; the label goes inside the frame, top-left, with padding to fit it.
- **ER:**
  - lay out by relationship tree (parent column → child column), so lines only join adjacent columns
  - header height grows with the grain text
  - an FK to a non-adjacent table shows as `FK → table` in the row instead of a line
  - more than ~9 entities → split into one ER per area
- **Width:** ≤1020 px per diagram; otherwise split into sub-flows, with the build saying which.
- **Journey:** values wrap; stages are at least 240 px wide; more than 3 stages wrap onto a second row.
- **Cards:** at least 260 px wide; values wrap under their label.

### 4. Other builder fixes
- **UTF-8:** read and write files as UTF-8 explicitly. Output strings in `build.py` use entities (`&mdash;` `&middot;` `&rarr;`), never raw non-ASCII.
- **Status badges:** only for values starting "Confirmed" or "Not verified".
- **Version stamp under the title, added automatically:** repo commit (`git rev-parse --short HEAD`, `+dirty`), graph commit from the graph's `meta.json`, and the review file used.
- **Known issues:** from one review only, the newest file in `reviews/` (several and unclear → ask), named under the section.
- **`check.py`:** add an edge-through-box check (sample points along each polyline and hit-test the boxes).
- **Optional, ask me first:** drop an empty `.generated-by-darshan-singh-meel-docs` marker in every output folder, and make the graph skill skip any folder that contains it, so copied or renamed doc folders are skipped.

### 5. Fixed workflow (write into SKILL.md; every run builds exactly this, named `docs-v2-<repo>`)
| Phase | Per document | Model | Does |
|---|---|---|---|
| 1 Plan | 1 agent | Opus | fills the recipes: boxes, sub-flows, examples; no layout design |
| 2 Build | 1 agent | Sonnet | writes spec → `build.py` → fixes every error and WARN |
| 3a Auto-check | script | — | `check.py` |
| 3b Accuracy reviewer | 1 agent, parallel with 3c | Opus | checks every name, number and step against the code and graph |
| 3c Layout reviewer | 1 agent | Haiku | runs `check.py` itself, then takes one screenshot to judge readability and confusing diagrams; **fails the doc on any LAYOUT line** |
| 4 Fix | 1 agent | Sonnet | applies 3a–3c, rebuilds, reruns `check.py` until it reports 0 |
| 5 Re-render | only if layout changed | Haiku | one screenshot to confirm |

- **Done means:** 0 build errors, 0 WARN (or each one explained in the doc), 0 LAYOUT lines, and the accuracy reviewer passed.
- **Existing docs:** read their `_spec/*.json` first and keep their sections, diagram ids, box names and groups; new items go into the existing group or sub-flow.

### 6. Finish
- Update `spec.md` (recipes, typed tables, labels, quantifiers), and the Documents, Same look, Diagrams, Examples and Process sections of SKILL.md.
- Rebuild the 4 examples to the new recipes. Add a stress example with long identifiers, a 12-child fan-out, a 12-entity ER, a 4-stage journey and long card values. All must pass `check.py`.
- Rebuild this repo's v2 docs from their saved specs. Show me before/after `check.py` counts and screenshots of the busiest diagrams.
- Keep `build.py` to plain functions and stdlib only (Playwright only in `check.py`).
- If both skill versions are installed (full and the compressed sūtra version), apply the same changes to both.
- End with one line per change, plus anything you couldn't do.

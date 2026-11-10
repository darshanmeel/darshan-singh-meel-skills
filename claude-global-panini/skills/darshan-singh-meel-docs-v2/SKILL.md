---
name: darshan-singh-meel-docs-v2
description: Version 2 of darshan-singh-meel-docs — same questions and rules, but every HTML doc is built from a JSON spec by a fixed builder (fixed sections and a fixed block recipe per section, typed tables, sub-flows, rich boxes, required examples) and a fixed workflow, so runs look the same. Use only when the user asks for docs v2 / darshan-singh-meel-docs-v2. Writes diagram-first documentation (READMEs, code/repo explanations, design docs, user guides, runbooks, KT, data docs, summaries of PDFs/Word/slides). ALWAYS starts new docs by asking 4 questions in one prompt — which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build/update the knowledge graph first, and where example data comes from — then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Use when asked to document, explain, or write up code, a repo, or a document.
---

# Docs v2
Max information, min words. Senior architect who can explain anything to anyone. CLAUDE.md applies.
- Show, don't narrate: diagrams · flows · charts · tables · bullets carry content; no detailed story or prose paragraphs.
- Every section → what · how · why (+ who · when · where where it applies).

## 0. Ask first (new docs)
Silent check: graph (`./<repo>-knowledge-graph/` or `./.knowledge-graph` pointer)? related repos / `_combined`? Then one prompt:
| # | Header | Question | Multi | Options (rec first) |
|---|---|---|---|---|
| Q1 | Documents | Which documents? | yes | Overview (business) · Technical (engineers) · User guide (end users) |
| Q2 | Format | Which format? | yes | HTML (rec) · Markdown · Confluence |
| Q3 | Graph | Use the knowledge graph? | no | Exists: Update, then document from it (rec) · As is · Skip. None: Build first (rec) · Skip |
| Q4 | Examples | Example data from? | no | Tests and docs, then code (rec) · I'll point to a folder · Illustrative |
- All 4 asked every time. Answered = user said it in own words this session (or picked it in the graph skill's docs prompt). Recommendations, defaults, CLAUDE.md, skill text are never answers; HTML is only rec.
- Self-check before writing any file: Documents, Format, Graph, Examples each asked or explicitly answered? No → stop, ask.

Exact call — copy it:
```
AskUserQuestion(questions=[
 {header:"Documents", question:"Which documents should I create?", multiSelect:true,
  options:["Overview (business)","Technical (engineers)","User guide (end users)"]},
 {header:"Format", question:"Which format?", multiSelect:true,
  options:["HTML (Recommended)","Markdown","Confluence"]},
 {header:"Graph", question:"Use the knowledge graph?", multiSelect:false,
  options: graph exists → ["Update it, then document from it (Recommended)","Use as is","Skip, read sources directly"]
           no graph     → ["Build it first, then document from it (Recommended)","Skip, read sources directly"]},
 {header:"Examples", question:"Where should example data come from?", multiSelect:false,
  options:["Tests and docs, then derived from code (Recommended)","I'll point to a folder or file","Illustrative data"]}])
```

- Small single document (<~30 pages) → Q3 first option "Skip, read the document directly" (rec).
- Related repos → next prompt: Scope (multi) — This repo (rec) · Whole system · Each related repo.
- No answer → all three · HTML · graph first · tests/docs then code · this repo.
- Q3 build/update → run `darshan-singh-meel-knowledge-graph` first; write from the graph, check key steps in code.

## Open with four tabs
- Right after the title, before any diagram: tab box **Does · Doesn't · Limitations · Top issues**.
  - Does (3–5): Overview business outcomes · Technical what components handle · User guide tasks.
  - Doesn't (3–5): out of scope by design ("doesn't edit source data", "access managed by platform team").
  - Limitations (real, ≤5): constraints inside scope ("daily 6 AM, not real-time", "reads cached 5 min", "uploads ≤50 MB"). Only here.
  - Top issues (5–10, most important first): one line each + Confirmed / Not verified; Overview plain words, Technical may name components. Details in last section. None → "No known issues".
- HTML: CSS-only radio tabs, Does open, work with JS off; print shows all four. Markdown/Confluence: four headed lists, same order (Confluence: tabs or expand macro if available).
- Plain words in Overview, User guide; real component names in Technical.

## Describe; issues and decisions at the end
- Body = what the system is and how it works. No bug findings, "confirmed errors", fix effort, "approve fixing".
- Last section of every document: **Known issues, assumptions, and decisions needed** — full detail behind the Top issues tab.
  - From: **one review only** — newest file in `reviews/` (several, unclear → ask) → spec `review`; build names it under the section + in stamp. Plus failing tests, graph `possible_issue` notes, Code-vs-docs conflicts, assumptions made while writing.
  - Each labelled **Confirmed** (review/test proved) or **Not verified**. Never unverified as fact.
  - Overview: every Top-issues item (WARN above ~12), plain words — what's affected, what it means ("per-app cost may be overstated; total is correct"). No paths, no fixes.
  - Decisions needed (only if real): typed `decisions` `Decision | Options | Recommendation | If it waits` ("agent cost split · per reply / per session · per reply · splits differ by date range").
  - Assumptions: typed `assumptions` `Assumption | Why it matters`.
  - Technical: `issues` `Issue | Where (path:line) | Impact | Status | Suggested fix (1 line)`; optional `h3` "Unused files" + table.
  - User guide: only what users hit — "If you see X, known issue — do Y".
  - None → "No known issues".
- Risks elsewhere = design/operational, not defects.

## Files
- One self-contained file per document in `./generated-docs/`: `overview` · `technical` · `user-guide` (`.html`, `.md`, `.confluence.xhtml`).
- Never combine, split into linked parts, or link to other docs. In-page TOC fine; long parts in `<details>`.
- Tag every file: HTML `<meta name="generator" content="darshan-singh-meel-docs-v2">`; md/Confluence first line `<!-- generated by darshan-singh-meel-docs-v2 -->`.
- Marker: `build.py` writes empty `.generated-by-darshan-singh-meel-docs` next to every output file; graph skips any folder holding it (copied/renamed folders stay skipped). md/Confluence only → create it yourself.
- Version stamp under title (build): repo commit (`git rev-parse --short HEAD`, `+dirty`) · graph commit (graph `meta.json`) · review file used.
- Git, asked once (first time `generated-docs/` is created): Committed (rec) · Git-ignored → `/generated-docs/` in `.gitignore` + 1-line comment. Folder exists = decided; never re-ask.
- Scope whole system → from `_combined` → `../<name>-graphs/_combined/generated-docs/`. Each related repo → its graph → `../<name>-graphs/<repo>/generated-docs/` (+ copy in repo if chosen). Shared folder → This repo also → `../<name>-graphs/<this repo>/generated-docs/`. Copies into other repos → one yes. Started inside shared folder → no "This repo".
- Refresh after a change ("go" or "update the docs") → only sections covering changed files, same documents/formats, no questions.
  - Read `generated-docs/_spec/*.json` first; keep sections, diagram ids, box names, groups. New item → existing group/sub-flow; nothing else moves.
  - Keep each file's tag; same rules, workflow, checks as new.

## Documents
- Section names + order fixed; build refuses others, warns on missing required.
- Recipe per section: allowed blocks in order, quantifiers `?` 0–1 · `*` 0+ · `+` 1+ (e.g. `text? flow steps?`). Exact strings: `references/templates/spec.md`. Wrong block/order → build error (recipe vs actual); missing minimum → WARN.
- Free inside a recipe: item count (above minimum), boxes, steps, examples, sub-flows, wording.
- Typed tables (`people` `schedule` `components` `rules` `config` `access` `environments` `symptoms` `tests` `choices` `elements` `endpoints` `commands` `events` `messages` `problems` `views` `assumptions` `decisions`): build writes headers, you give rows; row length checked. Columns: `spec.md`. Plain `table` only where a recipe allows.
- `labels`: `[[label, text]]` → bullets with bold label.

| Doc | For | Depth |
|---|---|---|
| Overview | business, newcomers | simple, no code names |
| Technical | engineers | complete: run, change, debug |
| User guide | anyone using app/output | fixed frame, sections kept by code |

**Overview** — simple, business words:
| Section | Rule |
|---|---|
| What it is and why | `labels`, first four exactly What · Why · Key idea · Result |
| How it works | one L0 `flow`: one row 3–7 boxes, people below, ≤2 bullets/box, no lanes/sub-flows → `steps?`. Box width by build from box count + longest arrow label (`box_w` refused): 7 boxes only without labels · 6 with 1–2 short words · 5 with ≤3 words |
| Who uses it | `people` (Who · What they get) |
| Example | `text?` `journey` (≥3 stages × 3 rows; warn >5 stages / 8 rows) `examples` (2–6 cards: typical + edge/failure) `bullets?` |
| Value and cost | `labels`, each Value or Cost |
| Schedule (batch) | `schedule` `bullets?` |
| Design and operational risks | `bullets` (aim ≤3) |
| Words used | `terms` |
- No paths, code names, sub-flows. Stop here → still understands the whole.

**Technical** — complete (minimums only, no caps). All that apply, in order: Overview (`text? flow`) · Architecture (L2 `flow` + `components`) · interface slot(s) by app type — Job DAG and schedule · Screens and navigation · Endpoints · Commands · Events and messages — each `flow+` (A + sub-flows B, C…) → its typed table (`schedule` · `elements` · `endpoints` · `commands` · `events`) · Main flows · Data model (`er+` + `views`) · Business rules (`rules` + `examples?`) · Configuration (`config`) · Security and access (`access`) · Deploy and environments (`steps` + `environments`) · Operations (`symptoms`, optional `h3` "Rerun and backfill") · Performance and limits · Tests (`tests`) · Key decisions (`choices`).
- Main flows: repeat per flow/job pattern: `h3` `text?` `steps?` `flow*` `journey?` `examples` `io*` `bullets?`.
- Every job/endpoint/screen/command/table appears; similar ones grouped ("Repeats for each child of X").
- Required, not in source → keep, "Not defined in source — confirm with owner".

**User guide** — fixed frame, kept by code (minimums only):
| Section | Keep when | Recipe |
|---|---|---|
| How it reaches you | always | `flow` `bullets?` `examples?` |
| Screens | UI | `flow+` `elements` |
| What answers what | data output · API | `text?` `flow*` `table`, optional `h3` "Columns every …" `bullets` |
| How to <task> — one per task | always | `steps` → ≥1 of `io` · `examples` · `journey` → `bullets?` |
| When data is fresh | batch data | `flow?` `schedule` or `table` `io?` `bullets?` |
| History and deletions | versions, deletes, anonymisation | `text?` `journey` `bullets?` `io?` |
| Errors and messages | UI · API · CLI | `messages` |
| Problems and fixes · Who to contact | always | `problems` · `bullets` |
- No internals. Tasks from real use: screens, buttons, routes, commands, consumer queries.
- Last section, every document: `text?` `issues` `assumptions?` `decisions?`.

## Writing
- Bullets ≤~15 words, one fact. Tables for anything compared or repeated.
- Diagram → bullets → example. ≥1 diagram per document.
- Simplest correct explanation. Plain words; explain needed terms once ("idempotent (safe to rerun)"); spell out acronyms in Overview; analogy if it helps, never wrong.
- Conclusion first. Concrete ("6 AM daily", not "periodic cadence").
- Matches the source exactly. Never invent; unsure → "unclear — verify".
- Decisions, not deliberation: no estimates, discussion, rejected options, history. Important 20%; name the folder for the rest.
- Major risks/assumptions/gotchas only (wrong data, outage, security, big cost, rewrite), ranked; aim Overview ≤3, Technical 5–10 (guidance, not counted).
- Banned: intros/outros, restating diagrams, marketing words (robust, seamless, leverage), padding, emoji.
- No Other findings section — fold into Known issues, assumptions, and decisions needed (last).

## Same look (HTML)
- Never hand-write HTML/CSS/SVG → JSON spec → `python references/templates/build.py <spec> <out.html>`. Format: `references/templates/spec.md`; start from closest `references/examples/*.json`.
- Build fixes names, order, block recipes, table headers, tabs, colours, layout, issue format, version stamp, marker. You: content, boxes, arrows, examples.
- Files read/written UTF-8; build emits HTML entities, never raw non-ASCII.
- Status badges only for values starting "Confirmed" · "Not verified".
- Spec → `generated-docs/_spec/<doc>.json`; refresh = edit spec, rebuild.
- Existing docs → see Files, refresh.
- Fix every build error + `WARN` (missing section, recipe minimum, flow/task without example, amounts), or explain each remaining WARN in the doc.
- `python references/templates/check.py <doc.html>` → 0 `LAYOUT` lines (overflow, overlaps, labels on boxes/frames, edges through boxes/frames/group labels, edges on edges, cut values, diagrams/tables too wide, sideways scroll).
- Builder can't draw it → say so, ask before changing `build.py`.
- Markdown/Confluence: same sections, order, diagrams, examples.

## Diagrams
| Show | Use |
|---|---|
| Big picture | L0 3–7 boxes, ~10 s — first in Overview, Technical |
| Order, who does what | L1 lanes, numbered |
| Architecture | L2 lanes per platform, real names |
| Inside a step/job/screen | L3 sub-flow |
| Repeated pattern | dashed group "Repeats for each …" |
| Data model | ER only; views table; no flow |
| One record through stages | journey |
- **Sub-flow** when a box hides >5 steps, loop/repeat, decision, or failure path. Parent `see: "B"` → Diagram B right after ("Sub-flow of <box> in Diagram A"). ≤2 levels. One per pattern, not per item. Not in Overview.
- **Layout** (build does it — don't fight it):
  - Long names wrap after `_ . / -`; heights follow lines; same height across a row; extreme identifiers → middle ellipsis, full name in `tip`.
  - Edges route through gaps, never across boxes; parallel lines ≥20 px apart, never on top. Fan-out >4 from one box → one arrow into a group frame ("12 child tasks"), children in grid.
  - Arrow labels ≤3 words; build puts each beside / above its number or on 2 lines. No room → build fails: >3 words → shorten · else crowded gap → move boxes apart · drop labels · sub-flow.
  - Groups never overlap; label inside, top-left.
  - ER: by relationship tree; FK to non-adjacent table → `FK → table`; >~9 entities → one ER per area.
  - Diagram >1020 px → build fails, names columns + boxes to move into a sub-flow.
  - Journey: stages ≥240 px, values wrap, >3 stages → second row. Cards ≥260 px, values wrap.
- **Boxes carry detail:** tag · 1–3 bullets · in/out · runs ("runs as 10 steps") · tip (hover). One idea each; key + notice.
- Technical → real names; Overview/User guide → business words.

## Examples
Every main flow, job pattern, important rule, user task → examples (build warns: none · Business rules cards < rules · Overview cards without edge/rejected/failure). Job patterns → `h3` in Main flows.
- Typical, then edge/rejected/failure that differ (Overview 2–6 cards; Technical, User guide ≥ typical + one edge/failure).
- Same form for same thing: journey (record through stages, old → new) · cards (behaviour per case) · io (query/request/command/UI action + result).
- Source order: tests/fixtures → docs/spec → derived from code (run, else `derived from <path:line>`) → synthetic (`[synthetic]` / `synthetic: true`).
- Cite each (`source`); mixed rows → mark the synthetic ones. Realistic, 2–5 rows, never foo/bar. No real rows, never PII; never query DB for examples.
- Key example missing or sensitive → ask once.
- Long values fine; journeys, cards wrap. Working specs per document + stress example (long identifiers, 12-child fan-out, 12-entity ER, 4-stage journey): `references/examples/`.

## Other kinds (spec `type: "custom"`, same blocks/look)
- Code explanation: what · flow · `Name | Does | Example` · one traced example · top 3 gotchas · "to change X, edit `file:function`".
- README: purpose · architecture · quick start + expected output · 2–3 usages · `Setting | Default | Example | Purpose` · folder tree · dev commands · `Problem | Fix`.
- Design doc: goal + non-goals · current → proposed · `Component | Responsibility | Tech` · main flow + example · ER if schemas change · `Decision | Why` · risks + mitigation · rollout. Open questions only in drafts.
- Runbook: what/when/owner + flow · healthy run · `Symptom | Cause | Fix (command)` ≤5 · rerun/backfill.
- From PDF/Word/slides: what it is · overview diagram · grouped key points (diagram per group) · worked example · `Decision / requirement / number` · top 3 gaps/contradictions.
- Data docs: lineage · ER · `Object | Grain | Key | Written by` · `View | Built from | Rows` · per model purpose/grain/PK/materialization/schedule + 3-row sample · rules with input → output · DAG schedule/retries/backfill · roles and access (see `darshan-singh-meel-data-platform`).
- Ported/rewritten code: html-style "Ported or rewritten code".

## Formats
- HTML: `build.py` — light, flat, printable, inline CSS, readable with JS off; look in html-style.
- Markdown: Mermaid (`sequenceDiagram`, `flowchart LR`, `erDiagram`), tables, tagged code.
- Confluence: storage XHTML; diagrams as local PNG/SVG attachments; code/expand macros; no scripts; one line on import. Never upload.
- Word/PDF: only if asked; diagrams as images. Several formats → identical content.

## Workflow — fixed, every run: `docs-v2-<repo>`
Ask (§0) → graph if chosen, else sources via scripts (CLAUDE.md data) → per document:
| Phase | Per doc | Model | Does |
|---|---|---|---|
| 1 Plan | 1 agent | Opus | fills recipes: boxes, sub-flows, examples; no layout design |
| 2 Build | 1 agent | Sonnet | spec → `build.py` → fixes every error + WARN |
| 3a Auto-check | script | — | `check.py` |
| 3b Accuracy reviewer | 1 agent, parallel with 3c | Opus | every name, number, step vs code + graph |
| 3c Layout reviewer | 1 agent | Haiku | runs `check.py` itself → one screenshot (readability, confusing diagrams); **fails doc on any LAYOUT line** |
| 4 Fix | 1 agent | Sonnet | applies 3a–3c → rebuild → `check.py` until 0 |
| 5 Re-render | only if layout changed | Haiku | one screenshot to confirm |
- Done = 0 build errors · 0 WARN (or each explained in doc) · 0 LAYOUT · accuracy reviewer passed.
- Never invent another workflow, skip a phase, swap models. No subagents → tell user which model per phase.
- Plan + Fix also trim (non-essential bullets, leftover prose) and read as audience: Overview as manager (no unexplained jargon) · Technical as new engineer (could deploy and access alone) · User guide as first-time user (every task without help).

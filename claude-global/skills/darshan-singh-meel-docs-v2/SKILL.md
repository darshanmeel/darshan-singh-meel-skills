---
name: darshan-singh-meel-docs-v2
description: Version 2 of darshan-singh-meel-docs — same questions and rules, but every HTML doc is built from a JSON spec by a fixed builder (fixed sections and a fixed block recipe per section, typed tables, sub-flows, rich boxes, required examples) and a fixed workflow, so runs look the same. Use only when the user asks for docs v2 / darshan-singh-meel-docs-v2. Writes diagram-first documentation (READMEs, code/repo explanations, design docs, user guides, runbooks, KT, data docs, summaries of PDFs/Word/slides). ALWAYS starts new docs by asking 4 questions in one prompt — which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build/update the knowledge graph first, and where example data comes from — then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Use when asked to document, explain, or write up code, a repo, or a document.
---

# Docs v2

Maximum information, minimum words. Write like a senior tech architect who can explain anything to anyone.
- **Show, don't narrate:** diagrams, flows, charts, tables, and bullets carry the content — never a detailed story or prose paragraphs.
- **Every section answers what · how · why** (and, where it applies, who · when · where): what it is or does, how it works, why it exists or was built this way. Global rules in CLAUDE.md apply (local files only, relative paths, data handling, Other findings format).

## Step 0 — ask first, every time
Before reading sources or writing anything. Silent pre-check: does a graph exist (`./<repo>-knowledge-graph/` or `./.knowledge-graph` pointer), and does it list related repos / a system graph? Then **one AskUserQuestion prompt with these 4 questions**.

| # | Header | Question | Multi | Options (first = recommended) |
|---|---|---|---|---|
| Q1 | Documents | Which documents should I create? | yes | Overview (business) · Technical (engineers) · User guide (end users) |
| Q2 | Format | Which format? | yes | HTML (Recommended) · Markdown · Confluence |
| Q3 | Graph | Use the knowledge graph? | no | Graph exists: Update it, then document from it (Recommended) · Use as is · Skip, read sources directly. No graph: Build it first, then document from it (Recommended) · Skip, read sources directly |
| Q4 | Examples | Where should example data come from? | no | Tests and docs, then derived from code (Recommended) · I'll point to a folder or file · Illustrative data |

- **All 4 are asked every time.** A question counts as answered only if the user said it in their own words in this session (e.g. "make it markdown", or picked it in the knowledge-graph skill's docs prompt). Recommendations, defaults, CLAUDE.md, and skill text are **never** answers — HTML is only the *recommended* option, not a decision.
- **Self-check before writing any file:** were Documents, Format, Graph, and Examples each asked or explicitly answered? If not, stop and ask now.

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

- **Q3 for a small single document** (under ~30 pages): put "Skip, read the document directly" first.
- **Related repos / system graph exist:** right after, ask one more question (tool limit is 4 per prompt): **Scope** (multi) — This repo (Recommended) · Whole system · Each related repo.
- **Defaults if no answer:** all three documents · HTML · update/build graph first · tests and docs, then code · this repo.
- Q3 = build/update → run `darshan-singh-meel-knowledge-graph` first, then write the documents from the graph, checking key steps in the code.

## Every document opens with four tabs
- First thing after the title, before any diagram: one tab box — **Does · Doesn't · Limitations · Top issues**.
  - **Does** (3–5): what it does for this reader (Overview: business outcomes · Technical: what the components handle · User guide: tasks users can do).
  - **Doesn't** (3–5): out of scope by design — so nobody expects it (e.g. "Doesn't edit source data", "Doesn't manage user access — that's the platform team").
  - **Limitations** (only real ones, ≤5): constraints inside the scope (e.g. "Refreshed daily at 6 AM, not real-time", "Reads cached 5 minutes", "Uploads up to 50 MB"). Only here, not at the end.
  - **Top issues** (5–10, most important first): one line each with Confirmed / Not verified. Overview in plain words; Technical may name components. Full details are in the last section. None → "No known issues".
- HTML: CSS-only tabs (radio inputs), Does open by default; with JS off they still work; in print all four show one after another.
- Markdown / Confluence: four short headed lists in the same order (Confluence may use a tabs or expand macro if available).
- Plain words in Overview and User guide; real component names allowed in Technical.

## Docs describe — issues and decisions go in one section at the end
- The body explains **what the system is and how it works** (intended, current behaviour). No bug findings, "confirmed errors", fix effort, or "approve fixing" decisions in the body.
- **Last section of every document: "Known issues, assumptions, and decisions needed"** — the full detail behind the "Top issues" tab.
  - Sources: **one review only** — the newest file in `reviews/` (several and unclear which → ask); set it as `review` in the spec, the build names it under the section and in the version stamp. Plus failing tests, the graph's `possible_issue` notes, conflicts ("Code vs docs"), and assumptions made while writing.
  - Every item labelled **Confirmed** (a review or test proved it) or **Not verified** (noticed, not checked). Never present unverified items as fact.
  - **Overview:** covers every Top-issues item (WARN above ~12), plain words — what's affected and what it means for the reader (e.g. "Per-app cost figures may be overstated; total spend is correct"). No file paths, no fix details.
  - **Decisions needed** (any document, only if real): typed `decisions` table `Decision | Options | Recommendation | If it waits` (e.g. "Choose how agent cost is split · per reply / per session · per reply · agent splits differ by date range").
  - **Assumptions:** typed `assumptions` table `Assumption | Why it matters`.
  - **Technical:** `issues` columns `Issue | Where (path:line) | Impact | Status | Suggested fix (one line)`; optional `h3` "Unused files" + table.
  - **User guide:** only issues a user can hit, as "If you see X, it's a known issue — do Y".
  - Nothing known → "No known issues" (one line).
- Risks elsewhere in the doc = design or operational risks (single point of failure, cost growth, delays), not defects.

## Files
- **One self-contained file per chosen document** in `./generated-docs/` (or a folder the user names): `overview.html`, `technical.html`, `user-guide.html`, plus `.md` / `.confluence.xhtml` for other chosen formats.
- Never combine documents into one file, never split one into linked parts, never link to other docs. Jump links inside the page (table of contents) are fine; long parts go in `<details>`.
- **Tag every generated file** so the graph skips it later: HTML `<meta name="generator" content="darshan-singh-meel-docs-v2">`; Markdown/Confluence first line `<!-- generated by darshan-singh-meel-docs-v2 -->`.
- **Marker file:** `build.py` writes an empty `.generated-by-darshan-singh-meel-docs` next to every output file; the graph skill skips any folder that holds it, so copied or renamed doc folders stay skipped. Markdown/Confluence only → create it yourself.
- **Version stamp** under the title, added by the build: repo commit (`git rev-parse --short HEAD`, `+dirty`), graph commit (graph `meta.json`), review file used.
- **Git, asked once:** the first time `generated-docs/` is created in a repo, ask: "Commit generated docs to git?" Committed (Recommended) · Git-ignored. Git-ignored → add `/generated-docs/` to `.gitignore` with a one-line comment. Never ask again in that repo (folder exists = decided).
- **Scope = whole system:** written from the `_combined` graph to `../<name>-graphs/_combined/generated-docs/`. **Scope = each related repo:** written from each repo's graph to `../<name>-graphs/<repo>/generated-docs/` (plus a copy in `<repo>/generated-docs/` if chosen in graph setup). With a shared graphs folder, **This repo** also goes to `../<name>-graphs/<this repo>/generated-docs/` (plus the in-repo copy if chosen). Writing copies into other repos needs one yes. Started from inside the shared graphs folder → "This repo" isn't offered.

## Updating existing docs
- Triggered by "go" after a change (knowledge-graph skill, section 5) or "update the docs".
- Refresh only the sections that cover the changed files, in the existing documents and formats. No Step 0 questions.
- Read `generated-docs/_spec/*.json` first and keep their sections, diagram ids, box names, and groups; a new item goes into the existing group or sub-flow, nothing else moves.
- Keep each file's tag; same rules, workflow, and checks as a new document.

## The three documents
| Document | For | Depth |
|---|---|---|
| **Overview** | Business, management, newcomers | Simple: one screen per section, no code names |
| **Technical** | Engineers | Complete: everything an engineer needs to run, change, and debug it |
| **User guide** | Anyone who uses the app or its output | Fixed frame; sections kept only where the code has them |

- **Section names and order are fixed;** the build refuses others and warns about missing required ones.
- **Each section has a recipe:** allowed block types, in order, with quantifiers (`?` 0–1, `*` 0+, `+` 1+), e.g. `text? flow steps?`. Exact strings: `references/templates/spec.md`. Wrong block or order → build error showing recipe and actual sequence; missing minimum → WARN.
- **Free inside a recipe:** how many items (above the minimum), which boxes, steps, examples, sub-flows, and wording.
- **Typed tables** (`people` `schedule` `components` `rules` `config` `access` `environments` `symptoms` `tests` `choices` `elements` `endpoints` `commands` `events` `messages` `problems` `views` `assumptions` `decisions`): the build writes the headers, you give rows only; row length is checked. Columns: `spec.md`. Plain `table` only where a recipe allows it.
- **`labels`** block: `[[label, text]]` → bullets with a bold label.

**Overview — keep it simple** (business words)
| Section | Rule |
|---|---|
| What it is and why | `labels`, first four exactly What · Why · Key idea · Result |
| How it works | one L0 `flow`: one row of 3–7 boxes, people below, ≤2 bullets per box, no lanes or sub-flows; then `steps?`. Box width set by the build from box count and longest arrow label (`box_w` refused): 7 boxes fit only without arrow labels, 6 with 1–2 short words, 5 with ≤3 words |
| Who uses it | `people` (Who · What they get) |
| Example | `text?` `journey` (≥3 stages × 3 rows; warn above 5 stages / 8 rows) `examples` (2–6 cards: typical + edge or failure) `bullets?` |
| Value and cost | `labels`, each label Value or Cost |
| Schedule (if batch) | `schedule` `bullets?` |
| Design and operational risks | `bullets` (aim for ≤3) |
| Words used | `terms` |
- No paths, code names, or sub-flows. Someone who stops here still understands the whole thing.

**Technical — complete** (minimums only, no caps)
- Every section that applies, in order: Overview (`text? flow`) · Architecture (L2 `flow` + `components`) · interface slot(s) for the app type — Job DAG and schedule · Screens and navigation · Endpoints · Commands · Events and messages — each `flow+` (A plus sub-flows B, C…) then its typed table (`schedule` · `elements` · `endpoints` · `commands` · `events`) · Main flows · Data model (`er+` + `views`) · Business rules (`rules` + `examples?`) · Configuration (`config`) · Security and access (`access`) · Deploy and environments (`steps` + `environments`) · Operations (`symptoms`, optional `h3` "Rerun and backfill") · Performance and limits · Tests (`tests`) · Key decisions (`choices`).
- **Main flows:** repeat per flow or job pattern: `h3` `text?` `steps?` `flow*` `journey?` `examples` `io*` `bullets?`.
- Every job, endpoint, screen, command, or table appears somewhere; similar ones in one group ("Repeats for each child of X"), not one diagram each.
- Required section not in source → keep it, one bullet "Not defined in source — confirm with owner".

**User guide — fixed frame, kept by the code** (minimums only)
| Section | Keep when | Recipe |
|---|---|---|
| How it reaches you | always | `flow` `bullets?` `examples?` |
| Screens | UI | `flow+` `elements` |
| What answers what | data output or API | `text?` `flow*` `table`, optional `h3` "Columns every …" `bullets` |
| How to <task> — one per task | always | `steps`, then ≥1 of `io` / `examples` / `journey`, `bullets?` |
| When data is fresh | batch data | `flow?` `schedule` or `table` `io?` `bullets?` |
| History and deletions | versions, deletes, anonymisation | `text?` `journey` `bullets?` `io?` |
| Errors and messages | UI, API, CLI | `messages` |
| Problems and fixes · Who to contact | always | `problems` · `bullets` |
- No internals. Tasks come from what users actually do: screens, buttons, routes, CLI commands, consumer queries.
- Last section of every document: `text?` `issues` `assumptions?` `decisions?`.

## Writing rules
- **Bullets only**, ≤ ~15 words, one fact each. Tables for anything compared or repeated.
- **Diagram first, then bullets, then example.** Every document has at least one diagram.
- **Simplest correct explanation wins.** Plain words; explain a needed term once ("idempotent (safe to rerun — same result)"); spell out acronyms in the Overview; an everyday analogy when it helps, never so simple it's wrong.
- **Lead each section with the conclusion.** Concrete over abstract ("daily at 6 AM", not "periodic cadence").
- **Accurate:** every name, number, command, and diagram matches the source. Never invent; if unsure, "unclear — verify".
- **Architect voice:** state decisions, not deliberation (no estimates, discussion, rejected options, or version history). Cover the important 20%; name the folder for the rest (`other helpers: utils/`).
- **Only the major risks, assumptions, and gotchas** — the ones that could cause wrong data, outages, security problems, big cost, or a rewrite. Aim for Overview ≤3, Technical 5–10 (guidance; the build doesn't count them). Rank by impact.
- **Banned:** intros/outros ("This document describes…", "In summary"), restating diagrams in prose, marketing words (robust, seamless, leverage), generic best-practice padding, emoji.
- **No separate Other findings section in docs** — anything worth noting goes in "Known issues, assumptions, and decisions needed" (last section).

## Same look every time (HTML)
- Never hand-write HTML, CSS, or SVG. Write a JSON spec → `python references/templates/build.py <spec> <out.html>`. Spec format: `references/templates/spec.md`; working specs and results: `references/examples/` — start from the closest one.
- The build fixes section names and order, block recipes, table headers, tabs, colours, diagram layout, issue format, version stamp, marker file. You decide only content, boxes, arrows, examples.
- Files read and written as UTF-8; the build emits HTML entities, never raw non-ASCII.
- Status badges only for values starting "Confirmed" or "Not verified".
- Spec saved in `generated-docs/_spec/<doc>.json`. Refresh = edit spec, rebuild.
- **Existing docs:** see "Updating existing docs".
- Fix every build error and `WARN` (missing section, recipe minimum, flow/task without example, amounts), or explain each remaining WARN in the doc.
- `python references/templates/check.py <doc.html>` must print 0 `LAYOUT` lines (overflow, overlaps, labels on boxes or frames, edges through boxes, frames or group labels, edges on top of each other, cut values, diagrams or tables too wide, sideways scroll).
- Need something the builder can't draw → say so, ask before changing `build.py`.
- Markdown/Confluence: same sections, order, diagrams (Mermaid / images), examples.

## Diagrams
| Show | Use |
|---|---|
| Big picture | L0: 3–7 boxes, readable in ~10 s — first in Overview and Technical |
| Order of steps, who does what | L1: lanes, numbered arrows |
| Architecture | L2: lanes per platform, real component names |
| Inside one step, job, or screen | L3 sub-flow |
| Same pattern repeated | dashed group "Repeats for each …" around the repeated boxes |
| Data model | ER only — keys, cardinality; views in a table; no flow |
| One record through stages | data journey (old → new, calculated) |

**Sub-flows**
- Draw one when a box hides >5 steps, a loop or repeat, a decision, or a failure path worth showing.
- Parent box gets `see: "B"` ("▸ Diagram B"); Diagram B sits right after its parent with "Sub-flow of <box> in Diagram A". Max 2 levels (A → B → C).
- One sub-flow per distinct pattern, not per item: 10 similar child jobs = one group in A + one sub-flow B for the pattern.
- Not for the Overview.

**Layout (done by the build — don't fight it)**
- Long names wrap after `_ . / -`; box heights follow wrapped lines; extreme identifiers get a middle ellipsis, full name in `tip`. Same height across a row.
- Edges route through gaps, never across boxes; parallel lines stay ≥20 px apart, never on top of each other. Fan-out >4 from one box → one arrow into a group frame ("12 child tasks"), children in a grid.
- Arrow labels ≤3 words; the build puts each beside its number, above it, or on two lines. Still no room → build fails: over 3 words → shorten; otherwise the gap is crowded → move boxes apart, drop labels the text already says, or use a sub-flow.
- Groups never overlap; label inside, top-left.
- ER: laid out by relationship tree; FK to a non-adjacent table shows as `FK → table`; >~9 entities → one ER per area.
- Diagram >1020 px → build fails and names the columns and boxes to move into a sub-flow.
- Journey: stages ≥240 px, values wrap, >3 stages wrap to a second row. Cards ≥260 px, values wrap.

**Boxes carry detail** — `tag` (STEP n, TASK n, ENTRY), 1–3 `bullets`, `in`/`out` with short values, `runs` ("runs as 10 steps"), `tip` (hover note). One idea per diagram; one-line `key` + `notice` on each.
- Technical → real names; Overview / User guide → business words.

## Examples
**Every main flow, job pattern, important rule, and user task gets examples** — the build warns when a flow or task has none, when Business rules has fewer example cards than rules, or when Overview cards have no edge/rejected/failure case. Job patterns get theirs as an `h3` in Main flows (the Job DAG recipe has no example block).
- Typical first, then edge / rejected / failure cases that behave differently (Overview 2–6 cards; Technical and User guide at least typical + one edge or failure).
- Pick the form by what's shown — same form for the same kind of thing every time:
  | Showing | Block |
  |---|---|
  | One record changing through stages | journey (old → new amber, calculated purple) |
  | Behaviour per case | examples cards (IN → OUT) |
  | A query, request, command, or UI action and its result | io (formatted input + result table/text) |
- **Source order:** tests and fixtures (best for edge cases) → docs/README/spec examples → derived from code (follow real logic; run it if possible, else `derived from <path:line>`) → synthetic (marked `[synthetic]` / `synthetic: true`).
- Cite every example (`source`). Mixed rows → mark the synthetic ones.
- Realistic, 2–5 rows, never foo/bar. No real data rows, never PII even masked; never query the database for examples.
- Key example missing or data may be sensitive → ask once.
- Long values are fine; journeys and cards wrap them. Working specs per document plus a stress example (long identifiers, 12-child fan-out, 12-entity ER, 4-stage journey): `references/examples/`.

## Other document kinds (spec `type: "custom"`, same blocks and look)
- **Code explanation:** what (1 line) · flow diagram · `Name | Does | Example` · one example traced · top 3 gotchas · "to change X, edit `file:function`".
- **README:** title + purpose · architecture diagram · quick start with expected output · 2–3 usage examples · `Setting | Default | Example | Purpose` · short folder tree · dev commands · `Problem | Fix`.
- **Design doc:** problem/goal + non-goals · current → proposed diagrams · `Component | Responsibility | Tech` · main flow + example · ER (if schemas change) · `Decision | Why` · risks with mitigation · rollout steps. Open questions only in drafts.
- **Runbook:** what/when/owner + flow · healthy run (example output) · `Symptom | Cause | Fix (exact command)` top 5 · rerun/backfill commands.
- **From a PDF/Word/slides:** what it is · overview diagram · key points grouped, a diagram per group with structure · a worked example · `Decision / requirement / number` table · top 3 gaps or contradictions.
- **Data docs:** lineage · ER · `Object | Grain | Key | Written by` · `View | Built from | Rows` · per-model purpose/grain/PK/materialization/schedule + 3-row sample · business rules with input → output · DAG schedule, retries, backfill · roles and access (see `darshan-singh-meel-data-platform`).
- **Ported or rewritten code:** one developer page per `references/html-style.md` → "Ported or rewritten code".

## Formats
- **HTML:** built by `references/templates/build.py` — light, flat, printable, all CSS inline, readable with JavaScript off. Look explained in `references/html-style.md`.
- **Markdown:** Mermaid diagrams (`sequenceDiagram`, `flowchart LR`, `erDiagram`), tables, tagged code blocks.
- **Confluence:** storage-format XHTML; diagrams rendered locally to PNG/SVG in an assets folder and referenced as attachments; code and expand macros; no scripts. Finish with one line on how to import. Never upload yourself.
- **Word / PDF:** only if explicitly asked; diagrams as images.
- Several formats → identical content.

## Workflow — fixed, every run: `docs-v2-<repo>`
Step 0 questions → graph (if chosen) or read sources with scripts (CLAUDE.md data handling) → per document:

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
- Never invent another workflow, skip a phase, or swap models. No subagents → tell the user in one line which model to switch to per phase.
- Plan and Fix also trim (delete any non-essential bullet or leftover prose) and read as the audience: Overview as a manager (no unexplained jargon) · Technical as a new engineer (could deploy and access from it alone) · User guide as a first-time user (every task doable without help).

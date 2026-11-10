---
name: darshan-singh-meel-docs-v2
description: Version 2 of darshan-singh-meel-docs — same questions and rules, but every HTML doc is built from a JSON spec by a fixed builder (fixed sections per document and app type, sub-flows, rich boxes, required examples), so runs look the same. Use only when the user asks for docs v2 / darshan-singh-meel-docs-v2. Writes diagram-first documentation (READMEs, code/repo explanations, design docs, user guides, runbooks, KT, data docs, summaries of PDFs/Word/slides). ALWAYS starts new docs by asking 4 questions in one prompt — which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build/update the knowledge graph first, and where example data comes from — then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Use when asked to document, explain, or write up code, a repo, or a document.
- **Git, asked once:** the first time `generated-docs/` is created in a repo, ask: "Commit generated docs to git?" Committed (Recommended) · Git-ignored. Git-ignored → add `/generated-docs/` to `.gitignore` with a one-line comment. Never ask again in that repo (folder exists = decided).
---

# Docs v2

Maximum information, minimum words. Write like a senior tech architect who can explain anything to anyone. Global rules in CLAUDE.md apply (local files only, relative paths, data handling, Other findings format).

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
  - Sources: review reports, failing tests, the graph's `possible_issue` notes, conflicts ("Code vs docs"), and assumptions made while writing.
  - Every item labelled **Confirmed** (a review or test proved it) or **Not verified** (noticed, not checked). Never present unverified items as fact.
  - **Overview:** max 5 rows in plain words — what's affected and what it means for the reader (e.g. "Per-app cost figures may be overstated; total spend is correct"). No file paths, no fix details.
  - **Decisions needed** (any document, only if real): one line each — the decision, options, recommendation, and what happens if it waits (e.g. "Choose how agent cost is split: per reply (recommended) or per session — until then, agent splits differ by date range").
  - **Technical:** table `Issue | Where (path:line) | Impact | Status | Suggested fix (one line)`, then `Assumption | Why it matters`.
  - **User guide:** only issues a user can hit, as "If you see X, it's a known issue — do Y".
  - Nothing known → "No known issues" (one line).
- Risks elsewhere in the doc = design or operational risks (single point of failure, cost growth, delays), not defects.

## Files
- **One self-contained file per chosen document** in `./generated-docs/` (or a folder the user names): `overview.html`, `technical.html`, `user-guide.html`, plus `.md` / `.confluence.xhtml` for other chosen formats.
- Never combine documents into one file, never split one into linked parts, never link to other docs. Jump links inside the page (table of contents) are fine; long parts go in `<details>`.
- **Tag every generated file** so the graph skips it later: HTML `<meta name="generator" content="darshan-singh-meel-docs-v2">`; Markdown/Confluence first line `<!-- generated by darshan-singh-meel-docs-v2 -->`.
- **Scope = whole system:** written from the `_combined` graph to `../<name>-graphs/_combined/generated-docs/`. **Scope = each related repo:** written from each repo's graph to `../<name>-graphs/<repo>/generated-docs/` (plus a copy in `<repo>/generated-docs/` if chosen in graph setup). With a shared graphs folder, **This repo** also goes to `../<name>-graphs/<this repo>/generated-docs/` (plus the in-repo copy if chosen). Writing copies into other repos needs one yes. Started from inside the shared graphs folder → "This repo" isn't offered.

## Updating existing docs
- Triggered by "go" after a change (knowledge-graph skill, section 5) or "update the docs".
- Refresh only the sections that cover the changed files, in the existing documents and formats. No Step 0 questions.
- Keep each file's tag; same rules and checks as a new document.

## The three documents
| Document | For | Depth |
|---|---|---|
| **Overview** | Business, management, newcomers | Simple: one screen per section, no code names |
| **Technical** | Engineers | Complete: everything an engineer needs to run, change, and debug it |
| **User guide** | Anyone who uses the app or its output | Fixed frame; sections kept only where the code has them |

Section names and order are fixed (`references/templates/spec.md`); the build refuses others and warns about missing ones.

**Overview — keep it simple**
- What it is and why · How it works (one L0, ≤5 boxes) · Who uses it · Example (one journey in business words) · Value and cost · Schedule (if batch) · Design and operational risks (≤3) · Words used.
- No paths, tables, code names, or sub-flows. Someone who stops here still understands the whole thing.

**Technical — cover as much as possible**
- Every section that applies, in order: Overview (L0) · Architecture (L2 + `Component | Responsibility | Where`) · the interface slot(s) for the app type (Job DAG and schedule · Screens and navigation · Endpoints · Commands · Events and messages) · Main flows · Data model (ER + views) · Business rules (`Rule | Input → output | Where`) · Configuration (`Setting | Default | Where | Purpose`) · Security and access · Deploy and environments · Operations (health check, symptoms, rerun) · Performance and limits · Tests · Key decisions.
- **Main flows:** one `h3` per flow or job pattern → steps table → sub-flow if needed → journey → example cards → io (query/request/command + result).
- Every job, endpoint, screen, command, or table appears somewhere; similar ones in one group ("Repeats for each child of X"), not one diagram each.
- Required section not in source → keep it, one bullet "Not defined in source — confirm with owner".

**User guide — fixed frame, kept by the code**
| Section | Keep when |
|---|---|
| How it reaches you | always (one small flow) |
| Screens (map + sub-flows + `Element | What it does`) | UI |
| What answers what (view/endpoint map + table) | data output or API |
| How to <task> — one section per task | always; steps (`Step | You see`) + example each |
| When data is fresh | batch data |
| History and deletions | data with versions, deletes, anonymisation |
| Errors and messages (`Message | Means | Do`) | UI, API, CLI |
| Problems and fixes (≤5) · Who to contact | always |
- No internals. Tasks come from what users actually do: screens, buttons, routes, CLI commands, consumer queries.

## Writing rules
- **Bullets only**, ≤ ~15 words, one fact each. Tables for anything compared or repeated.
- **Diagram first, then bullets, then example.** Every document has at least one diagram.
- **Simplest correct explanation wins.** Plain words; explain a needed term once ("idempotent (safe to rerun — same result)"); spell out acronyms in the Overview; an everyday analogy when it helps, never so simple it's wrong.
- **Lead each section with the conclusion.** Concrete over abstract ("daily at 6 AM", not "periodic cadence").
- **Accurate:** every name, number, command, and diagram matches the source. Never invent; if unsure, "unclear — verify".
- **Architect voice:** state decisions, not deliberation (no estimates, discussion, rejected options, or version history). Cover the important 20%; name the folder for the rest (`other helpers: utils/`).
- **Only the major risks, assumptions, and gotchas** — the ones that could cause wrong data, outages, security problems, big cost, or a rewrite. Overview: max 3. Technical: max 5–10. Rank by impact.
- **Banned:** intros/outros ("This document describes…", "In summary"), restating diagrams in prose, marketing words (robust, seamless, leverage), generic best-practice padding, emoji.
- **No separate Other findings section in docs** — anything worth noting goes in "Known issues, assumptions, and decisions needed" (last section).

## Same look every time (HTML)
- Never hand-write HTML, CSS, or SVG. Write a JSON spec → `python references/templates/build.py <spec> <out.html>`. Spec format: `references/templates/spec.md`; working specs and results: `references/examples/` — start from the closest one.
- The build fixes section names and order, tabs, components, colours, diagram layout, issue format. You decide only content, boxes, arrows, examples.
- Spec saved in `generated-docs/_spec/<doc>.json`. Refresh = edit spec, rebuild.
- **Existing docs:** read their spec first and match it — same sections, diagram ids, box names, groups. A new job/screen/endpoint goes into the existing diagram or group; nothing else moves.
- Fix every `WARN` the build prints (missing section, flow/task without example) before delivering.
- Need something the builder can't draw → say so, ask before changing `build.py`.
- Markdown/Confluence: same sections, order, diagrams (Mermaid / images), examples.

## Diagrams
| Show | Use |
|---|---|
| Big picture | L0: ≤~7 boxes, readable in ~10 s — first in Overview and Technical |
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

**Boxes carry detail** — `tag` (STEP n, TASK n, ENTRY), 1–3 `bullets`, `in`/`out` with short values, `runs` ("runs as 10 steps"), `tip` (hover note). One idea per diagram; one-line `key` + `notice` on each.
- Technical → real names; Overview / User guide → business words.

## Examples
**Every main flow, job pattern, important rule, and user task gets examples** — the build warns when a flow or task has none.
- Typical first, then edge / rejected / failure cases that behave differently (2–4 cards).
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

## Models
- **Opus plans:** reads the graph/sources, decides the diagrams, what goes in each box, IN/OUT, and which examples.
- **Sonnet builds:** writes the spec JSON from Opus's plan and runs the build.
- **Haiku checks:** renders, screenshots, lists layout problems.
- No subagents → tell the user in one line which model to switch to.

## Process
1. Step 0 questions.
2. Graph (if chosen) → else read sources with scripts first (CLAUDE.md data handling).
3. Opus plans each document: sections, diagrams, examples.
4. Write the spec, run the build, fix every WARN; verify every name, number, command, and example against the source; render and screenshot.
5. Trim: delete any bullet that isn't essential and any prose sentence left over.
6. Read as the audience: Overview as a manager (no unexplained jargon) · Technical as a new engineer (could deploy and access from it alone) · User guide as a first-time user (every task doable without help).

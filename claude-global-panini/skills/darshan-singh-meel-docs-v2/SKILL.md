---
name: darshan-singh-meel-docs-v2
description: Version 2 of darshan-singh-meel-docs — same questions and rules, but every HTML doc is built from a JSON spec by a fixed builder (fixed sections per document and app type, sub-flows, rich boxes, required examples), so runs look the same. Use only when the user asks for docs v2 / darshan-singh-meel-docs-v2. Writes diagram-first documentation (READMEs, code/repo explanations, design docs, user guides, runbooks, KT, data docs, summaries of PDFs/Word/slides). ALWAYS starts new docs by asking 4 questions in one prompt — which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build/update the knowledge graph first, and where example data comes from — then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Use when asked to document, explain, or write up code, a repo, or a document.
- Git, asked once (first time `generated-docs/` is created): Committed (rec) · Git-ignored → `/generated-docs/` in `.gitignore`. Folder exists = decided; never re-ask.
---

# Docs v2
Max information, min words. Senior architect who can explain anything to anyone. CLAUDE.md applies.

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

- Small single document (<~30 pages) → Q3 rec = Skip.
- Related repos → next prompt: Scope (multi) — This repo (rec) · Whole system · Each related repo.
- No answer → all three · HTML · graph first · tests/docs then code · this repo.
- Q3 build/update → run `darshan-singh-meel-knowledge-graph` first; write from the graph, check key steps in code.

## Open with four tabs
- Right after the title, before any diagram: tab box **Does · Doesn't · Limitations · Top issues**.
  - Does (3–5): Overview business outcomes · Technical what components handle · User guide tasks.
  - Doesn't (3–5): out of scope by design ("doesn't edit source data", "access managed by platform team").
  - Limitations (real, ≤5): constraints inside scope ("daily 6 AM, not real-time", "reads cached 5 min", "uploads ≤50 MB"). Only here.
  - Top issues (5–10, most important first): one line each + Confirmed / Not verified. Details in last section. None → "No known issues".
- HTML: CSS-only radio tabs, Does open, work with JS off; print shows all four. Markdown/Confluence: four headed lists, same order.

## Describe; issues and decisions at the end
- Body = what the system is and how it works. No bug findings, "confirmed errors", fix effort, "approve fixing".
- Last section of every document: **Known issues, assumptions, and decisions needed** — full detail behind the Top issues tab.
  - From: review reports, failing tests, graph `possible_issue` notes, Code-vs-docs conflicts, assumptions made while writing.
  - Each labelled **Confirmed** (review/test proved) or **Not verified**. Never unverified as fact.
  - Overview: ≤5 plain rows — what's affected, what it means ("per-app cost may be overstated; total is correct"). No paths, no fixes.
  - Decisions needed (only if real): decision · options · recommendation · what happens if it waits.
  - Technical: `Issue | Where (path:line) | Impact | Status | Suggested fix (1 line)` + `Assumption | Why it matters`.
  - User guide: only what users hit — "If you see X, known issue — do Y".
  - None → "No known issues".
- Risks elsewhere = design/operational, not defects.

## Files
- One self-contained file per document in `./generated-docs/`: `overview` · `technical` · `user-guide` (`.html`, `.md`, `.confluence.xhtml`).
- Never combine, split into linked parts, or link to other docs. In-page TOC fine; long parts in `<details>`.
- Tag every file: HTML `<meta name="generator" content="darshan-singh-meel-docs-v2">`; md/Confluence first line `<!-- generated by darshan-singh-meel-docs-v2 -->`.
- Scope whole system → from `_combined` → `../<name>-graphs/_combined/generated-docs/`. Each related repo → its graph → `../<name>-graphs/<repo>/generated-docs/` (+ copy in repo if chosen). Shared folder → This repo also → `../<name>-graphs/<this repo>/generated-docs/`. Copies into other repos → one yes. Started inside shared folder → no "This repo".
- Refresh after a change ("go" or "update the docs") → only sections covering changed files, same documents/formats, no questions.

## Documents
Names + order fixed (`references/templates/spec.md`); build refuses others, warns on missing.
| Doc | For | Depth |
|---|---|---|
| Overview | business, newcomers | simple, no code names |
| Technical | engineers | complete: run, change, debug |
| User guide | anyone using app/output | fixed frame, sections kept by code |

**Overview** — What it is and why · How it works (L0 ≤5 boxes) · Who uses it · Example (journey, business words) · Value and cost · Schedule (batch) · Design and operational risks (≤3) · Words used. No paths, code names, sub-flows.

**Technical** — all that apply, in order: Overview (L0) · Architecture (L2 + `Component | Responsibility | Where`) · interface slot by app type (Job DAG and schedule · Screens and navigation · Endpoints · Commands · Events and messages) · Main flows · Data model (ER + views) · Business rules (`Rule | Input → output | Where`) · Configuration (`Setting | Default | Where | Purpose`) · Security and access · Deploy and environments · Operations (health, symptoms, rerun) · Performance and limits · Tests · Key decisions.
- Main flows: `h3` per flow/job pattern → steps → sub-flow if needed → journey → cards → io.
- Every job/endpoint/screen/command/table appears; similar ones grouped ("Repeats for each child of X").
- Required, not in source → keep, "Not defined in source — confirm with owner".

**User guide** — fixed frame, kept by code:
| Section | Keep when |
|---|---|
| How it reaches you | always |
| Screens (map + sub-flows + `Element | What it does`) | UI |
| What answers what | data output · API |
| How to <task> — one per task, `Step | You see` + example | always |
| When data is fresh | batch data |
| History and deletions | versions, deletes, anonymisation |
| Errors and messages (`Message | Means | Do`) | UI · API · CLI |
| Problems and fixes (≤5) · Who to contact | always |
- No internals. Tasks from real use: screens, buttons, routes, commands, consumer queries.

## Writing
- Bullets ≤~15 words, one fact. Tables for anything compared or repeated.
- Diagram → bullets → example. ≥1 diagram per document.
- Simplest correct explanation. Plain words; explain needed terms once ("idempotent (safe to rerun)"); spell out acronyms in Overview; analogy if it helps, never wrong.
- Conclusion first. Concrete ("6 AM daily", not "periodic cadence").
- Matches the source exactly. Never invent; unsure → "unclear — verify".
- Decisions, not deliberation: no estimates, discussion, rejected options, history. Important 20%; name the folder for the rest.
- Major risks/assumptions/gotchas only (wrong data, outage, security, big cost, rewrite), ranked.
- Banned: intros/outros, restating diagrams, marketing words (robust, seamless, leverage), padding, emoji.
- No Other findings section — fold into Known issues, assumptions, and decisions needed (last).

## Same look (HTML)
- Never hand-write HTML/CSS/SVG → JSON spec → `python references/templates/build.py <spec> <out.html>`. Format: `references/templates/spec.md`; start from closest `references/examples/*.json`.
- Build fixes names, order, tabs, components, colours, layout, issue format. You: content, boxes, arrows, examples.
- Spec → `generated-docs/_spec/<doc>.json`; refresh = edit spec, rebuild.
- Existing docs → read spec, match: sections, diagram ids, box names, groups. New job/screen/endpoint → into existing diagram/group; nothing else moves.
- Fix every `WARN` (missing section, flow/task without example) before delivering.
- Builder can't draw it → say so, ask before changing `build.py`.
- Markdown/Confluence: same sections, order, diagrams, examples.

## Diagrams
| Show | Use |
|---|---|
| Big picture | L0 ≤~7 boxes — first in Overview, Technical |
| Order, who does what | L1 lanes, numbered |
| Architecture | L2 lanes per platform, real names |
| Inside a step/job/screen | L3 sub-flow |
| Repeated pattern | dashed group "Repeats for each …" |
| Data model | ER only; views table; no flow |
| One record through stages | journey |
- **Sub-flow** when a box hides >5 steps, loop/repeat, decision, or failure path. Parent `see: "B"` → Diagram B right after ("Sub-flow of <box> in Diagram A"). ≤2 levels. One per pattern, not per item. Not in Overview.
- **Boxes carry detail:** tag · 1–3 bullets · in/out · runs ("runs as 10 steps") · tip (hover). One idea each; key + notice.
- Technical → real names; Overview/User guide → business words.

## Examples
Every main flow, job pattern, important rule, user task → examples (build warns if none).
- Typical, then edge/rejected/failure that differ (2–4 cards).
- Same form for same thing: journey (record through stages, old → new) · cards (behaviour per case) · io (query/request/command/UI action + result).
- Source order: tests/fixtures → docs/spec → derived from code (run, else `derived from <path:line>`) → synthetic (`[synthetic]`).
- Cite each (`source`). Realistic, 2–5 rows, never foo/bar. No real rows, never PII; never query DB for examples.
- Key example missing or sensitive → ask once.

## Other kinds (spec `type: "custom"`, same blocks/look)
- Code explanation: what · flow · `Name | Does | Example` · one traced example · top 3 gotchas · "to change X, edit `file:function`".
- README: purpose · architecture · quick start + expected output · 2–3 usages · `Setting | Default | Example | Purpose` · folder tree · dev commands · `Problem | Fix`.
- Design doc: goal + non-goals · current → proposed · `Component | Responsibility | Tech` · main flow + example · ER if schemas change · `Decision | Why` · risks + mitigation · rollout. Open questions only in drafts.
- Runbook: what/when/owner + flow · healthy run · `Symptom | Cause | Fix (command)` ≤5 · rerun/backfill.
- From PDF/Word/slides: what it is · overview diagram · grouped key points (diagram per group) · worked example · `Decision / requirement / number` · top 3 gaps/contradictions.
- Data docs: lineage · ER · `Object | Grain | Key | Written by` · `View | Built from | Rows` · per model purpose/grain/PK/materialization/schedule + 3-row sample · rules with input → output · DAG schedule/retries/backfill · roles and access.
- Ported/rewritten code: html-style "Ported or rewritten code".

## Formats
- HTML: `build.py` — light, flat, printable, inline CSS, readable with JS off; look in html-style.
- Markdown: Mermaid (`sequenceDiagram`, `flowchart LR`, `erDiagram`), tables, tagged code.
- Confluence: storage XHTML; diagrams as local PNG/SVG attachments; code/expand macros; no scripts; one line on import. Never upload.
- Word/PDF: only if asked; diagrams as images. Several formats → identical content.

## Models · process
- Opus plans (diagrams, boxes, IN/OUT, examples) · Sonnet writes spec, runs build · Haiku renders, screenshots, lists layout problems. No subagents → tell user which model.
1. Ask (§0). 2. Graph if chosen, else sources via scripts. 3. Opus plans each document. 4. Build; verify every name, number, command, example; render and screenshot. 5. Trim non-essential bullets, leftover prose. 6. Read as audience: manager (no unexplained jargon) · new engineer (could deploy and access alone) · first-time user (every task without help).

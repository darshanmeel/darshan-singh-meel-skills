---
name: darshan-singh-meel-docs
description: Write diagram-first documentation (READMEs, code/repo explanations, design docs, user guides, runbooks, KT, data docs, summaries of PDFs/Word/slides). ALWAYS starts new docs by asking 4 questions in one prompt — which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build/update the knowledge graph first, and where example data comes from — then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Use when asked to document, explain, or write up code, a repo, or a document.
- Git, asked once (first time `generated-docs/` is created): Committed (rec) · Git-ignored → `/generated-docs/` in `.gitignore`. Folder exists = decided; never re-ask.
---

# Docs
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
  - Overview: ≤5 plain bullets — what's affected, what it means ("per-app cost may be overstated; total is correct"). No paths, no fixes.
  - Decisions needed (only if real): decision · options · recommendation · what happens if it waits.
  - Technical: `Issue | Where (path:line) | Impact | Status | Suggested fix (1 line)` + `Assumption | Why it matters`.
  - User guide: only what users hit — "If you see X, known issue — do Y".
  - None → "No known issues".
- Risks elsewhere = design/operational, not defects.

## Files
- One self-contained file per document in `./generated-docs/`: `overview` · `technical` · `user-guide` (`.html`, `.md`, `.confluence.xhtml`).
- Never combine, split into linked parts, or link to other docs. In-page TOC fine; long parts in `<details>`.
- Tag every file: HTML `<meta name="generator" content="darshan-singh-meel-docs">`; md/Confluence first line `<!-- generated by darshan-singh-meel-docs -->`.
- Scope whole system → from `_combined` → `../<name>-graphs/_combined/generated-docs/`. Each related repo → its graph → `../<name>-graphs/<repo>/generated-docs/` (+ copy in repo if chosen). Shared folder → This repo also → `../<name>-graphs/<this repo>/generated-docs/`. Copies into other repos → one yes. Started inside shared folder → no "This repo".
- Refresh after a change ("go" or "update the docs") → only sections covering changed files, same documents/formats, no questions.

## Documents
**Overview** — business, management, newcomers
- What · why · who · value · costs · design/operational risks (not bugs). Decisions needed → last section.
- Business diagram: people, systems, outcomes; no code names.
- Real scenario: "Customer orders → in dashboard by 7 AM". Fits one screen; risks ≤3.

**Technical** — engineers
- Real names: components, flow, data model, configs, commands, failure modes, performance, security.
- Diagrams: architecture, flows, ER, lineage, DAG. Examples: code, queries, commands, input → output.
- Deploy & access (always): environments + diagram · deploy and roll back (exact commands/CI) · prerequisites (names, never values) · access (URLs, schemas, roles, how to request) · health check. Not in source → "Not defined in source — confirm with owner".
- Decisions (what + why), design risks ≤5–10 (limitations → opening section).

**User guide** — anyone using the app or its output (UI, dashboard, report, CLI, API, data, files); skip only if just the builders
- "How to <task>": numbered steps, what the user sees, example each.
- UI: screen flow, `Element | What it does`, `[Screenshot: <screen>]` only if needed. Non-UI: commands, requests/responses, which table/dashboard answers what.
- `Problem | What to do` ≤5. Who to contact. No internals.

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

## Diagrams
Style, notation, components: `references/html-style.md` · working examples: `references/example-components.html`.
| Show | Use |
|---|---|
| Big picture | L0 (≤~7 boxes, ~10 s) — always first |
| Anything in order | L1 swimlanes, numbered, IN → OUT |
| Architecture | L2, frames per platform |
| Exact steps, decisions, values | L3 |
| Data model | ER only — keys, cardinality; views as table; no flow |
| Lineage, big DAGs | auto-laid-out, pre-rendered SVG |
| Numbers | simple bars |
- One idea each; one-line key + "Notice:" caption.
- Technical → real names; Overview/User guide → business words.
- Example values on diagrams where they help.
- Any document listing tables → ER above that table (graph `data/model.json`, else DDL/dbt/code).

## Examples
- No data rows in docs/diagrams: built from structure; examples only from tests/fixtures/docs/code or synthetic (`illustrative`). Never query the DB for examples; never PII in a document, even masked.
- Source order: tests and docs (fixtures, dbt tests, README/spec examples, samples) → derived from code (follow real logic, show result, e.g. `add(1, 3) → 4`; run it, else label `derived from <path:line>`) → illustrative (labelled).
- Cite source (`from tests/test_rules.py:42`). 3–5 realistic rows, never foo/bar. Proper format: table, pretty JSON, formatted SQL, command block.
- Important rules/flows → 2–4 cards: typical, then edge / rejected / failure that behave differently.
- Missing key example or sensitive data → ask once.

## Templates (Technical unless noted)
- Code explanation: what · flow · `Name | Does | Example` · one traced example · top 3 gotchas · "to change X, edit `file:function`".
- README: purpose · architecture · quick start + expected output · 2–3 usages · `Setting | Default | Example | Purpose` · folder tree · dev commands · `Problem | Fix`.
- Design doc: goal + non-goals · current → proposed · `Component | Responsibility | Tech` · main flow + example · ER if schemas change · `Decision | Why` · risks + mitigation · rollout. Open questions only in drafts.
- Runbook: what/when/owner + flow · healthy run · `Symptom | Cause | Fix (command)` ≤5 · rerun/backfill.
- From PDF/Word/slides: what it is · overview diagram · grouped key points (diagram per group) · worked example · `Decision / requirement / number` · top 3 gaps/contradictions.
- Data docs: lineage · ER · `Object | Grain | Key | Written by` · `View | Built from | Rows` · per model purpose/grain/PK/materialization/schedule + 3-row sample · rules with input → output · DAG schedule/retries/backfill · roles and access.
- Ported/rewritten code: html-style "Ported or rewritten code".

## Formats
- HTML: html-style — light, flat, printable, inline CSS/JS, no CDN, readable with JS off.
- Markdown: Mermaid (`sequenceDiagram`, `flowchart LR`, `erDiagram`), tables, tagged code.
- Confluence: storage XHTML; diagrams as local PNG/SVG attachments; code/expand macros; no scripts; one line on import. Never upload.
- Word/PDF: only if asked; diagrams as images. Several formats → identical content.

## Models · process
- Opus plans (diagrams, boxes, IN/OUT, examples) · Sonnet builds · Haiku renders, screenshots, lists layout problems. No subagents → tell user which model.
1. Ask (§0). 2. Graph if chosen, else sources via scripts. 3. Opus plans each document. 4. Build; verify every name, number, command, example; render and screenshot. 5. Trim non-essential bullets, leftover prose. 6. Read as audience: manager (no unexplained jargon) · new engineer (could deploy and access alone) · first-time user (every task without help).

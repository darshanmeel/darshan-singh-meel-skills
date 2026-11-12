---
name: darshan-singh-meel-docs
description: Write diagram-first documentation (READMEs, code/repo explanations, design docs, user guides, runbooks, KT, data docs, summaries of PDFs/Word/slides). ALWAYS starts new docs by asking 4 questions in one prompt — which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build/update the knowledge graph first, and where example data comes from — then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Use when asked to document, explain, or write up code, a repo, or a document.
---

# Docs
Max information, min words. Senior architect who can explain anything to anyone, owner's voice (CLAUDE.md "Author voice"). CLAUDE.md applies.

## 0. Ask first (new docs only)
Before reading sources or writing. Silent check: graph (`./<repo>-knowledge-graph/` or `./.knowledge-graph` pointer)? related repos / `_combined`? Then one AskUserQuestion call, headers and labels exactly as in the table:
| # | Header | Question | Multi | Options (rec first) |
|---|---|---|---|---|
| Q1 | Documents | Which documents? | yes | Overview (business) · Technical (engineers) · User guide (end users) |
| Q2 | Format | Which format? | yes | HTML (rec) · Markdown · Confluence |
| Q3 | Graph | Use the knowledge graph? | no | Exists: Update, then document from it (rec) · As is · Skip. None: Build first (rec) · Skip |
| Q4 | Examples | Example data from? | no | Tests and docs, then code (rec) · I'll point to a folder · Illustrative |
- All 4 asked unless answered = user said it in own words this session. From the graph skill's docs prompt: Documents, Format, Graph ("As is") answered → ask only Examples. Recommendations, defaults, CLAUDE.md, skill text are never answers; HTML is only rec.
- Self-check before writing any file: Documents, Format, Graph, Examples each asked or explicitly answered? No → stop, ask.

- Small single document (<~30 pages) → Q3 first option "Skip, read the document directly (rec)"; no answer → Skip.
- Second prompt, only if needed: Scope (multi, related repos exist) — This repo (rec) · Whole system · Each related repo · Git (`generated-docs/` not yet created) — see Files.
- No answer → all three · HTML · graph first (small single document: skip) · tests/docs then code · this repo.
- Q3 build/update → run `darshan-singh-meel-knowledge-graph` first; write from the graph, check key steps in code. Record: graph `update.py --choice now` (update) · `--choice skip` (as is) → no repeat graph question. Docs being built → no docs question after that update.

## Open with four tabs
- Right after the title, before any diagram: tab box **Does · Doesn't · Limitations · Top issues**.
  - Does (3–5): Overview business outcomes · Technical what components handle · User guide tasks.
  - Doesn't (3–5): out of scope by design ("doesn't edit source data", "access managed by platform team").
  - Limitations (real, ≤5): constraints inside scope ("daily 6 AM, not real-time", "reads cached 5 min", "uploads ≤50 MB"). Only here.
  - Top issues (≤10; Overview ≤5; only real; most important first): one line each + Confirmed / Not verified. Details in last section. None → "No known issues".
- HTML: CSS-only radio tabs, Does open, work with JS off; print shows all four. Markdown/Confluence: four headed lists, same order (Confluence: tabs/expand macro ok).
- Overview/User guide plain words; Technical may name components.

## Describe; issues and decisions at the end
- Body = what the system is and how it works. No bug findings, "confirmed errors", fix effort, "approve fixing".
- Last section of every document: **Known issues, assumptions, and decisions needed** — full detail behind the Top issues tab.
  - From: review reports, failing tests, graph `possible_issue` notes, Code-vs-docs conflicts, assumptions made while writing.
  - Each labelled **Confirmed** (review/test proved) or **Not verified**. Never unverified as fact.
  - Each = fact about the system, never a request to the reader: "Not yet tested in production", not "run on prod to confirm".
  - Overview: ≤5 plain bullets — what's affected, what it means ("per-app cost may be overstated; total is correct"). No paths, no fixes.
  - Decisions needed (any document, only if real): decision · options · recommendation · what happens if it waits.
  - Technical: `Issue | Where (path:line) | Impact | Status | Suggested fix (1 line)` + `Assumption | Why it matters`.
  - User guide: only what users hit — "If you see X, known issue — do Y".
  - None → "No known issues".
- Risks elsewhere = design/operational, not defects.

## Files
- Git, asked once (first time `generated-docs/` is created): Committed (rec) · Git-ignored → `/generated-docs/` in `.gitignore` + one-line comment (create file if missing). Folder exists = decided; never re-ask.
- One self-contained file per document in `./generated-docs/` (or a folder the user names): `overview` · `technical` · `user-guide` (`.html`, `.md`, `.confluence.xhtml`).
- Never combine, split into linked parts, or link to other docs. In-page TOC fine; long parts in `<details>`.
- Tag every file: HTML `<meta name="generator" content="darshan-singh-meel-docs">`; md/Confluence first line `<!-- generated by darshan-singh-meel-docs -->`.
- Scope whole system → from `_combined` → `../<name>-graphs/_combined/generated-docs/`. Each related repo → its graph → `../<name>-graphs/<repo>/generated-docs/` (+ copy in repo if chosen). Shared folder → This repo also → `../<name>-graphs/<this repo>/generated-docs/`. Copies into other repos → one yes. Started inside shared folder → no "This repo".
- Refresh ("Update now" on the docs question after a graph update, background · or "update the docs") → only sections covering changed files, same documents/formats, no questions. Keep tag; same rules and checks. Every build/refresh → knowledge-graph `update.py --docs done` (clears pending docs; staleness note stays right).

## Documents
**Overview** — business, management, newcomers
- What · why · who · value · costs · design/operational risks (not bugs). Decisions needed → last section.
- Business diagram: people, systems, outcomes; no code names or tables.
- Real scenario: "Customer orders → in dashboard by 7 AM". Fits one screen; complete on its own.

**Technical** — engineers
- Real names: components, flow, data model, configs, commands, failure modes, performance, security.
- Diagrams: architecture, flows, ER, lineage, DAG. Examples: code, queries, commands, input → output.
- Deploy & access (always): environments + diagram · deploy and roll back (exact commands/CI) · prerequisites (names, never values) · access (URLs, schemas, roles, how to request) · health check. Not in source → "<item>: not documented yet — owner to decide" + Decisions needed.
- Decisions (what + why), design risks (limitations → opening tabs).

**User guide** — anyone using the app or its output (UI, dashboard, report, CLI, API, data, files); skip only if just the builders
- "How to <task>": numbered steps, what the user sees, example each.
- UI: screen flow, `Element | What it does`, `[Screenshot: <screen>]` only if needed. Non-UI: commands, requests/responses, which table/dashboard answers what.
- `Problem | What to do` ≤5. Who to contact. No internals.

## Writing
- Bullets ≤~15 words, one fact. Tables for anything compared or repeated.
- Diagram → bullets → example. ≥1 diagram per document.
- Simplest correct explanation. Plain words; explain needed terms once ("idempotent (safe to rerun)"); spell out acronyms in Overview; analogy if it helps, never wrong.
- Conclusion first. Concrete ("6 AM daily", not "periodic cadence").
- Matches the source exactly. Never invent; unsure → open fact ("Retry count not yet verified") → last section.
- Decisions in first person ("We load daily because…"), not deliberation: no estimates, discussion, rejected options, history. No trace of the chat or how the doc was made. Important 20%; name the folder for the rest.
- Major risks/assumptions/gotchas only (wrong data, outage, security, big cost, rewrite), ranked. Overview ≤3, Technical ≤5–10.
- Banned: intros/outros, restating diagrams, marketing words (robust, seamless, leverage), padding, emoji.
- No Other findings section inside a document (chat reply may have one) — fold into Known issues, assumptions, and decisions needed (last).

## Diagrams
Style, notation, components: `references/html-style.md` · working examples: `references/example-components.html`.
| Show | Use |
|---|---|
| Big picture | L0 (≤~7 boxes, ~10 s) — always first |
| Anything in order | L1 swimlanes / sequence, numbered, IN → OUT |
| Architecture | L2, frames per platform |
| Exact steps, decisions, values | L3 |
| Data model | ER only — keys, cardinality; views as table; no flow |
| Lineage, big DAGs | auto-laid-out, pre-rendered SVG |
| Numbers | simple bars |
- One idea each; one-line key + "Notice:" caption.
- Technical → real names; Overview/User guide → business words.
- Example values on diagrams (arrow labels, IN/OUT chips, data-journey tables) where they help.
- Any document listing tables → ER above that table (graph `data/model.json`, else DDL/dbt/code).

## Examples
- No data rows in docs/diagrams: built from structure; examples only from tests/fixtures/docs/code or synthetic (`illustrative`). Never query the DB for examples; never PII in a document, even masked.
- Source order: tests and docs (fixtures, dbt tests, README/spec examples, samples) → derived from code (follow real logic with realistic inputs from its defaults and rules, show result, e.g. `add(1, 3) → 4`; run it, else label `derived from <path:line>`) → illustrative (labelled).
- Cite source in small mono text (`from tests/test_rules.py:42`). 3–5 realistic rows, never foo/bar. Proper format (table, pretty JSON, formatted SQL, command block), never squeezed into prose.
- Important rules/flows → 2–4 cards: typical, then edge / rejected / failure that behave differently.
- Missing key example or sensitive data → ask once.

## Templates (Technical unless noted)
- Code explanation: what · flow · `Name | Does | Example` · one traced example · top 3 gotchas · "to change X, edit `file:function`".
- README: purpose · architecture · quick start + expected output · 2–3 usages · `Setting | Default | Example | Purpose` · folder tree · dev commands · `Problem | Fix`.
- Design doc: goal + non-goals · current → proposed · `Component | Responsibility | Tech` · main flow + example · ER if schemas change · `Decision | Why` · risks + mitigation · rollout. Open questions only in drafts.
- Runbook: what/when/owner + flow · healthy run · `Symptom | Cause | Fix (command)` ≤5 · rerun/backfill.
- From PDF/Word/slides: what it is · overview diagram · grouped key points (diagram per group with structure) · worked example · `Decision / requirement / number` · top 3 gaps/contradictions.
- Data docs: lineage · ER · `Object | Grain | Key | Written by` · `View | Built from | Rows` · per model purpose/grain/PK/materialization/schedule + 3-row example (tests/fixtures, else `illustrative`) · rules with input → output · DAG schedule/retries/backfill · roles and access (see data-platform).
- Ported/rewritten code: html-style "Ported or rewritten code".

## Formats
- HTML: html-style — light, flat, printable, inline CSS/JS, no CDN, readable with JS off.
- Markdown: Mermaid (`sequenceDiagram`, `flowchart LR`, `erDiagram`), tables, tagged code.
- Confluence: storage XHTML; diagrams rendered locally to PNG/SVG in an assets folder, attached; code/expand macros; no scripts; reply (not file) ends with one line on import. Never upload.
- Word/PDF: only if asked; diagrams as images. Several formats → identical content.

## Models · process
- Opus plans (diagrams, boxes, IN/OUT, examples) · Sonnet builds · Haiku renders, screenshots, lists layout problems. No subagents → tell user in one line which model.
1. Ask (§0). 2. Graph if chosen, else sources via scripts (CLAUDE.md data handling). 3. Opus plans each document. 4. Build; verify every name, number, command, example against source; render and screenshot every diagram (no renderer → ask once; no → "layout not visually checked" in reply, not document). 5. Trim non-essential bullets, leftover prose · chat leakage ("you said" · "the user" · "as discussed" · "confirm with" · "Claude" · requests to the reader ("run on prod to confirm") · skipped/unchecked/asked notes) → author's statement; Should fix, Must if it misstates a fact or exposes private chat content. 6. Read as audience: manager (no unexplained jargon) · new engineer (could deploy and access alone) · first-time user (every task without help). 7. Technical doc built → reply ends with one line: "Architecture review with a proposed target (darshan-singh-meel-architecture)?" No other unprompted suggestion.

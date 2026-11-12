---
name: darshan-singh-meel-docs
description: Write diagram-first documentation (READMEs, code/repo explanations, design docs, user guides, runbooks, KT, data docs, summaries of PDFs/Word/slides). ALWAYS starts new docs by asking 4 questions in one prompt — which documents (Overview, Technical, User guide), format (HTML, Markdown, or Confluence), whether to build/update the knowledge graph first, and where example data comes from — then writes one self-contained file per document to ./generated-docs/ (refreshing existing docs after a change needs no questions). Use when asked to document, explain, or write up code, a repo, or a document. Not for requirements briefs (a brief from pasted requirements, epics, source tables → darshan-singh-meel-requirements-brief) or a mid-depth tech summary for engineers and tech leads (→ darshan-singh-meel-docs-tech-summary).
---

# Docs

Maximum information, minimum words. Write like a senior tech architect who can explain anything to anyone, in the owner's voice (CLAUDE.md "Author voice in produced files"). Global rules in CLAUDE.md apply (local files only, relative paths, data handling).
- **Not for / see:** mid-depth tech summary (engineers and tech leads, 10–15 min read) → `darshan-singh-meel-docs-tech-summary` · requirements brief → `darshan-singh-meel-requirements-brief` · architecture review → `darshan-singh-meel-architecture`.

## Step 0 — ask first (new docs only)
Before reading sources or writing anything. Silent pre-check: does a graph exist (`./<repo>-knowledge-graph/` or `./.knowledge-graph` pointer), and does it list related repos / a system graph? Then **one AskUserQuestion call, headers and labels exactly as in this table**.

| # | Header | Question | Multi | Options (first = recommended) |
|---|---|---|---|---|
| Q1 | Documents | Which documents should I create? | yes | Overview (business) · Technical (engineers) · User guide (end users) |
| Q2 | Format | Which format? | yes | HTML (Recommended) · Markdown · Confluence |
| Q3 | Graph | Use the knowledge graph? | no | Graph exists: Update it, then document from it (Recommended) · Use as is · Skip, read sources directly. No graph: Build it first, then document from it (Recommended) · Skip, read sources directly |
| Q4 | Examples | Where should example data come from? | no | Tests and docs, then derived from code (Recommended) · I'll point to a folder or file · Illustrative data |

- **Tech summary is not a Q1 option:** a request for a mid-depth tech summary (or "Other: tech summary" in Q1) → hand over to `darshan-singh-meel-docs-tech-summary`, which asks its own setup questions.
- **All 4 are asked unless answered.** A question counts as answered only if the user said it in their own words in this session (e.g. "make it markdown"). Called from the knowledge-graph skill's docs prompt: Documents, Format, and Graph ("Use as is") are answered — ask only Examples. Recommendations, defaults, CLAUDE.md, and skill text are **never** answers — HTML is only the *recommended* option, not a decision.
- **Self-check before writing any file:** were Documents, Format, Graph, and Examples each asked or explicitly answered? If not, stop and ask now.

- **Q3 for a small single document** (under ~30 pages): first option = "Skip, read the document directly (Recommended)"; no answer → Skip.
- **Second prompt, only if needed** (tool limit is 4 per prompt): **Scope** (multi, if related repos / a system graph exist) — This repo (Recommended) · Whole system · Each related repo; **Git** (if `generated-docs/` doesn't exist yet) — see Files.
- **Defaults if no answer:** all three documents · HTML · update/build graph first (small single document: skip) · tests and docs, then code · this repo.
- Q3 = build/update → run `darshan-singh-meel-knowledge-graph` first, then write the documents from the graph, checking key steps in the code. Record the answer with knowledge-graph `update.py --choice now` (update) or `--choice skip` (use as is), so the end-of-task graph question is not repeated. Docs being built → no docs question after that update.

## Every document opens with four tabs
- First thing after the title, before any diagram: one tab box — **Does · Doesn't · Limitations · Top issues**.
  - **Does** (3–5): what it does for this reader (Overview: business outcomes · Technical: what the components handle · User guide: tasks users can do).
  - **Doesn't** (3–5): out of scope by design — so nobody expects it (e.g. "Doesn't edit source data", "Doesn't manage user access — that's the platform team").
  - **Limitations** (only real ones, ≤5): constraints inside the scope (e.g. "Refreshed daily at 6 AM, not real-time", "Reads cached 5 minutes", "Uploads up to 50 MB"). Only here, not at the end.
  - **Top issues** (up to 10; Overview up to 5; only real ones; most important first): one line each with Confirmed / Not verified. Overview in plain words; Technical may name components. Full details are in the last section. None → "No known issues".
- HTML: CSS-only tabs (radio inputs), Does open by default; with JS off they still work; in print all four show one after another.
- Markdown / Confluence: four short headed lists in the same order (Confluence may use a tabs or expand macro if available).

## Docs describe — issues and decisions go in one section at the end
- The body explains **what the system is and how it works** (intended, current behaviour). No bug findings, "confirmed errors", fix effort, or "approve fixing" decisions in the body.
- **Last section of every document: "Known issues, assumptions, and decisions needed"** — the full detail behind the "Top issues" tab.
  - Sources: review reports, failing tests, the graph's `possible_issue` notes, conflicts ("Code vs docs"), and assumptions made while writing.
  - Every item labelled **Confirmed** (a review or test proved it) or **Not verified** (noticed, not checked). Never present unverified items as fact.
  - Each item is a fact about the system, not a request to the reader: "Not yet tested in production", not "run this on prod to confirm".
  - **Overview:** max 5 bullets in plain words — what's affected and what it means for the reader (e.g. "Per-app cost figures may be overstated; total spend is correct"). No file paths, no fix details.
  - **Decisions needed** (any document, only if real): one line each — the decision, options, recommendation, and what happens if it waits (e.g. "Choose how agent cost is split: per reply (recommended) or per session — until then, agent splits differ by date range").
  - **Technical:** table `Issue | Where (path:line) | Impact | Status | Suggested fix (one line)`, then `Assumption | Why it matters`.
  - **User guide:** only issues a user can hit, as "If you see X, it's a known issue — do Y".
  - Nothing known → "No known issues" (one line).
- Risks elsewhere in the doc = design or operational risks (single point of failure, cost growth, delays), not defects.

## Files
- **Git, asked once:** the first time `generated-docs/` is created in a repo, ask "Commit generated docs to git?" Committed (Recommended) · Git-ignored. Git-ignored → add `/generated-docs/` to `.gitignore` with a one-line comment (create the file if missing). Folder exists = decided; never re-ask.
- **One self-contained file per chosen document** in `./generated-docs/` (or a folder the user names): `overview.html`, `technical.html`, `user-guide.html`, plus `.md` / `.confluence.xhtml` for other chosen formats.
- Never combine documents into one file, never split one into linked parts, never link to other docs. Jump links inside the page (table of contents) are fine; long parts go in `<details>`.
- **Tag every generated file** so the graph skips it later: HTML `<meta name="generator" content="darshan-singh-meel-docs">`; Markdown/Confluence first line `<!-- generated by darshan-singh-meel-docs -->`.
- **Scope = whole system:** written from the `_combined` graph to `../<name>-graphs/_combined/generated-docs/`. **Scope = each related repo:** written from each repo's graph to `../<name>-graphs/<repo>/generated-docs/` (plus a copy in `<repo>/generated-docs/` if chosen in graph setup). With a shared graphs folder, **This repo** also goes to `../<name>-graphs/<this repo>/generated-docs/` (plus the in-repo copy if chosen). Writing copies into other repos needs one yes. Started from inside the shared graphs folder → "This repo" isn't offered.

## Updating existing docs
- Triggered by "Update now" on the docs question after a graph update (knowledge-graph skill, "Keep it updated"; runs in the background) or "update the docs".
- Refresh only the sections that cover the changed files, in the existing documents and formats. No Step 0 questions.
- Keep each file's tag; same rules and checks as a new document. After every build or refresh: knowledge-graph `update.py --docs done` (clears these docs from its pending list, so the staleness note stays right).

## The three documents
**Overview** — business, management, newcomers; high-level, minimal jargon
- What it is, why it exists, who uses it, the value, costs, design/operational risks (not bugs). Decisions needed go in the last section.
- Business diagram: people, systems, outcomes — no code names or tables.
- Example as a real scenario: "A customer places an order → it appears in the dashboard by 7 AM."
- Fits on one screen; complete on its own.

**Technical** — engineers; real names and detail, incl. deploy & access
- Real names: components, data flow, data model, configs, commands, failure modes, performance, security.
- Diagrams: architecture, flows, ER, lineage, DAG. Examples as code, queries, commands, input → output.
- **Deploy & access (always):** environments + deployment diagram · how to deploy and roll back (exact commands/CI steps) · prerequisites (tools, versions, config names — never values) · how to access (URLs, schemas, roles, how to request) · how to check it's healthy. If the source doesn't define something: "<item>: not documented yet — owner to decide", also listed under Decisions needed.
- Decisions (what + why) and design risks (limitations go in the opening tabs).

**User guide** — anyone who uses the app or its output, UI or not; task-based, plain steps
- Include whenever someone uses the app or its output (UI, dashboard, report, CLI, API, data consumers, emailed files); skip only if only the builders use it.
- "How to <task>": numbered steps, what the user sees at each, an example per task.
- UI: screen-flow diagram, `Element | What it does` table, `[Screenshot: <screen>]` only where words aren't enough. Non-UI: commands, requests/responses, which table/dashboard answers which question.
- `Problem | What to do` — top 5. Who to contact. No internals.

## Writing rules
- **Bullets only**, ≤ ~15 words, one fact each. Tables for anything compared or repeated.
- **Diagram first, then bullets, then example.** Every document has at least one diagram.
- **Simplest correct explanation wins.** Plain words; explain a needed term once ("idempotent (safe to rerun — same result)"); spell out acronyms in the Overview; an everyday analogy when it helps, never so simple it's wrong.
- **Lead each section with the conclusion.** Concrete over abstract ("daily at 6 AM", not "periodic cadence").
- **Accurate:** every name, number, command, and diagram matches the source. Never invent; if unsure, state it as an open fact ("Retry count not yet verified") and list it in the last section.
- **Architect voice:** state decisions in first person ("We load daily because…"), not deliberation (no estimates, discussion, rejected options, or version history). No trace of the chat or how the doc was made. Cover the important 20%; name the folder for the rest (`other helpers: utils/`).
- **Only the major risks, assumptions, and gotchas** — the ones that could cause wrong data, outages, security problems, big cost, or a rewrite. Overview: max 3. Technical: max 5–10. Rank by impact.
- **Banned:** intros/outros ("This document describes…", "In summary"), restating diagrams in prose, marketing words (robust, seamless, leverage), generic best-practice padding, emoji.
- **No Other findings section inside a document** (the chat reply may have one) — anything worth noting goes in "Known issues, assumptions, and decisions needed" (last section).

## Diagrams
Start with one big-picture diagram (≤ ~7 boxes, readable in ~10 seconds), then detail. Style, notation, and components: `references/html-style.md`; working examples: `references/example-components.html`.

| Show | Use |
|---|---|
| Big picture | L0 overview |
| Any flow in order (request, pipeline run, user journey) | L1 swimlanes / sequence, numbered, IN → OUT per step |
| Architecture | L2: frames per platform, real component names |
| Exact steps with decisions and values | L3 step-by-step |
| Data model | ER diagram — tables, keys, cardinality only; views as a table; **no flow** |
| Lineage, big DAGs | Auto-laid-out graph (pre-rendered SVG) |
| Numbers | Simple bars |

- One idea per diagram; a one-line key and a one-line "Notice:" caption each.
- Real names in Technical; business words in Overview and User guide.
- Put example values on diagrams where they help (arrow labels, IN/OUT chips, data-journey tables).
- Any document that lists tables gets an ER diagram above that table — from the graph's `data/model.json` if present, else from DDL, dbt, and code.

## Examples
- **No data rows in docs or diagrams:** diagrams are built from structure (names, steps, keys); example values come only from tests, fixtures, docs, or code, or are synthetic and labelled `illustrative`. Never query the database for doc examples; never show PII, even masked, in a document.
**Where they come from, in order:**
1. **Tests and docs** — test inputs/expected outputs, fixtures, dbt tests, doc/README/spec examples, sample folders. Best for edge and failure cases.
2. **Derived from the code** — follow the actual logic with realistic inputs from its defaults and rules, show the result (`add(1, 3) → 4`). Run it when possible; else label `derived from <path:line>`.
3. **Illustrative** — last resort, labelled `illustrative`.

- Cite the source in small mono text (`from tests/test_rules.py:42`).
- Small and realistic (3–5 rows), never foo/bar; in a proper format (table, pretty JSON, formatted SQL, command block), never squeezed into prose.
- Important rules and flows get 2–4 example cards: typical, then edge / rejected / failure cases that behave differently.
- Key example missing, or data may be sensitive → ask once (one prompt).

## Templates (sections for the Technical document unless noted)
- **Code explanation:** what (1 line) · flow diagram · `Name | Does | Example` · one example traced · top 3 gotchas · "to change X, edit `file:function`".
- **README:** title + purpose · architecture diagram · quick start with expected output · 2–3 usage examples · `Setting | Default | Example | Purpose` · short folder tree · dev commands · `Problem | Fix`.
- **Design doc:** problem/goal + non-goals · current → proposed diagrams · `Component | Responsibility | Tech` · main flow + example · ER (if schemas change) · `Decision | Why` · risks with mitigation · rollout steps. Open questions only in drafts.
- **Runbook:** what/when/owner + flow · healthy run (example output) · `Symptom | Cause | Fix (exact command)` top 5 · rerun/backfill commands.
- **From a PDF/Word/slides:** what it is · overview diagram · key points grouped, a diagram per group with structure · a worked example · `Decision / requirement / number` table · top 3 gaps or contradictions.
- **Data docs:** lineage · ER · `Object | Grain | Key | Written by` · `View | Built from | Rows` · per-model purpose/grain/PK/materialization/schedule + 3-row example (from tests/fixtures, else `illustrative`) · business rules with input → output · DAG schedule, retries, backfill · roles and access (see `darshan-singh-meel-data-platform`).
- **Ported or rewritten code:** one developer page per `references/html-style.md` → "Ported or rewritten code".

## Formats
- **HTML:** per `references/html-style.md` — light, flat, printable, all CSS/JS inline (no CDN), fully readable with JavaScript off.
- **Markdown:** Mermaid diagrams (`sequenceDiagram`, `flowchart LR`, `erDiagram`), tables, tagged code blocks.
- **Confluence:** storage-format XHTML; diagrams rendered locally to PNG/SVG in an assets folder and referenced as attachments; code and expand macros; no scripts. End the reply (not the file) with one line on how to import. Never upload yourself.
- **Word / PDF:** only if explicitly asked; diagrams as images.
- Several formats → identical content.

## Models
- **Opus plans:** reads the graph/sources, decides the diagrams, what goes in each box, IN/OUT, and which examples.
- **Sonnet builds:** writes the files and the diagram build script from Opus's plan.
- **Haiku checks:** renders, screenshots, lists layout problems.
- No subagents → tell the user in one line which model to switch to.

## Process
1. Step 0 questions.
2. Graph (if chosen) → else read sources with scripts first (CLAUDE.md data handling).
3. Opus plans each document: sections, diagrams, examples.
4. Build, then verify every name, number, command, and example against the source; render and screenshot every diagram (no renderer installed → ask once; if no, say "layout not visually checked" in the reply, not the document).
5. Trim: delete any bullet that isn't essential and any prose sentence left over. Rewrite any chat leakage ("you said", "the user", "as discussed", "confirm with", "Claude", requests to the reader like "run on prod to confirm", notes on what was skipped, unchecked or asked) as the author's statement — a Should fix; Must if it misstates a fact or exposes private chat content.
6. Read as the audience: Overview as a manager (no unexplained jargon) · Technical as a new engineer (could deploy and access from it alone) · User guide as a first-time user (every task doable without help).
7. After a Technical doc is built, end the reply with one line: "Architecture review with a proposed target (darshan-singh-meel-architecture)?" — no other unprompted suggestions. The CLAUDE.md Self-check still comes before it.


# Context prompt: my Claude Code setup (paste at the start of a new chat)

Paste everything below the line into a new Claude chat or Claude Code session, then add what you want to do next.

---

You're continuing work on my personal Claude Code global setup. Read this first so I don't have to explain it again.

## What this is
A generic Claude Code setup I install with `unzip -o <zip> -d ~/.claude/`. It holds `CLAUDE.md` (global rules), `skills/` (all prefixed `darshan-singh-meel-`) and `hooks/`. It must stay generic: no project, person or company names anywhere.

Two versions, always updated together and always delivered as **complete zips**, never single files:
- **Full:** `tech/claude-global.zip`, plain English.
- **Panini:** `tech/claude-global-panini.zip`, the same rules compressed in sūtra style (each heading sets scope, `→` = then, `·` = list, "rec" = recommended).

## How I want you to work
- **Answers:** minimal words, maximum information. Bullets, answer first, no preamble, recap or AI filler. Lead with the result.
- **Pushback:** if something is unclear, risky, or there's a better way, say so in 1–2 lines first. If I insist, do it my way.
- **Corrections** of something you said earlier go first in the reply.
- **Estimates:** agent effort (tokens and agent minutes, as ranges) before multi-step tasks, actuals after where reported; human effort only if I ask for both.
- **"Other findings":** optional and last, only if worth it. Each one: what · why it matters · impact of doing vs not doing.
- **A question only** (e.g. "don't change anything, just…") → answer, change nothing.
- **Questions to me:** AskUserQuestion, up to 4 per prompt, recommended option first. Defaults are never answers.
- **Output:** local files only, never artifacts, hosted pages or shared links. Relative paths only.
- **Model choice:** cheapest that works.
  - Haiku: mechanical work.
  - Sonnet: coding, building, answers.
  - Opus: planning, architecture, the knowledge graph, accuracy checks.
- **Code:** simplest that works, one file if it fits, plain functions, stdlib first, no over-engineering.
- **Every reply ends with** `Skills: <used> (<refs read>)` or `Skills: none`.

## Skills in the setup
| Skill | Job |
|---|---|
| `-code` | write, edit, debug, refactor; after a change, run the changed tests first, then ask once about running the full suite in the background |
| `-review` | change review (any diff/PR/commit, or ≤20 named files) vs large review; asks about an unused-files check each time; uses the graph as a map; report in `reviews/` (git-ignored) |
| `-review-v2` | same checks as `-review`, but the HTML report is built from a JSON spec by a fixed builder (`build.py`): main review, then a detailed section per file with Must/Should findings, a diagram only where it helps; used only when I say "v2" |
| `-docs` (v1) | diagram-first docs; always asks 4 questions (Documents, Format HTML/MD/Confluence, Graph, Examples); one file per doc in `generated-docs/` |
| `-docs-v2` | same rules, but HTML is built from a JSON spec by a fixed builder (`build.py`): fixed section recipes, typed tables, fixed workflow `docs-v2-<repo>`; used only when I say "v2" |
| `-docs-v3` | docs-v2 unchanged plus engine diagrams: a `diagram` block takes any type from the diagram skills (C4, ER, dbt lineage, Airflow DAG, sequence, state, RAG, agent…) as inline SVG, Mermaid for Markdown/Confluence; the plan names the preferred diagram per section and repo kind, graph style (plain · dbt · airflow) picked per diagram; used only when I say "v3" |
| `-docs-tech-summary` | mid-depth tech summary for engineers and tech leads (10–15 min read): 11 fixed sections (components, main flows as sequence diagrams, entity-level data model, integrations, pinned stack, deploy, security, run locally, top risks, where to look next) with a depth budget the build checks; one HTML page (+ optional Markdown) from a JSON spec; docs and docs-v2 route to it |
| `-diagrams` (+ families, `-review`) | base engine for every diagram: picks the type, JSON spec → static inline SVG (light/dark) + Mermaid, layout checker (no overlaps, no arrows through boxes); graph styles plain · dbt (lineage look) · airflow (DAG graph-view look) usable by any node-edge type, picked per diagram; families `-diagrams-flow` · `-architecture` · `-data` · `-interaction` · `-ai` · `-business` add the types; `-diagrams-review` re-derives each picture from the source and checks notation, layout, dark mode, Mermaid parity; used by docs v1/v3, tech summary, review, review-v2, architecture, brief, blog, graph answers |
| `-brevity` | shared writing base for every produced text and chat reply: plain title that states the point · one-sentence lede · why it matters · detail in layers · diagram where it replaces text; no word targets, length judged; `check_brevity.py` flags missing lede, filler, buried point in .md and .html |
| `-architecture` | architecture review from the graph: current, problems, per-component keep/move/later target in Technical-doc shape (hybrid by default), one pick + 2–3 alternatives on every row ("use <alt> instead" rebuilds it), workflows current vs proposed, impact, migration; one HTML page from a JSON spec; only on request or offered after a Technical doc |
| `-requirements-brief` (+ `-review`) | requirements → one HTML brief with SVG in `generated-docs/`: 12 fixed sections (at a glance, context, traceable requirements, sources and data points, linking, flows, use cases, data findings, tech options per need with the confirmed stack as given, what needs to be done, gaps and risks, glossary); the review re-reads the inputs, rebuilds traceability and numbers |
| `-tech-blog` (+ `-review`) | English technical blog posts: thesis, outline, code run, official-docs claims, `blog/<slug>.md` |
| `-knowledge-graph` | detailed, verifiable repo map in a git-ignored `<repo>-knowledge-graph/` (nodes and edges with `path:line`, data model, flows); mapping only, never a code review (suspicious code → "not verified"); Opus builds it, a separate Opus agent reviews it; after a commit, asks (update now in background · after next commit · when work is done · skip), then separately asks about the affected docs; declined → "Graph/Docs are N commits behind" note in every later repo reply; fast incremental updates via `references/update.py`; related repos share `../<name>-graphs/` + `_combined/` |
| `-notebook` | every data query goes through notebook cells in `analysis/`; Claude runs only read-only SELECT cells; DML/DDL/DCL go in notebooks I run; PII handled metadata-first (PII discovery step; keyed hashing for masked values) |
| `-data-platform` | cross-stack rules: SQL, Spark/Delta, Athena, Iceberg, Airflow, ADF, Terraform, RBAC, governance; checks official docs sites only when unsure; Snowflake, Databricks and dbt depth goes to their skills |
| `-snowflake` (+ `-review`) | Snowflake SME answering in minutes: cost and credits, warehouses, performance, which queries join which tables on which columns, dependencies, failures, grants, audit-type apps; read-only SQL over ACCOUNT_USAGE / INFORMATION_SCHEMA / SHOW with how to read it; asks where queries go: notebook (rec: `00_connection.ipynb` first, a markdown note before each query) · on screen · `.sql` files; the review re-derives every answer and runs `check_queries.py` |
| `-databricks` (+ `-review`) | Databricks SME: cost and DBUs to list dollars, compute, performance, joins and columns, lineage, jobs, Unity Catalog grants, audit logs, audit-type apps; read-only SQL on system tables; same notebook · screen · `.sql` choice; the review re-derives and runs `check_queries.py` |
| `-dbt` (+ `-review`) | all dbt work (Core, Fusion, platform) on Snowflake and Databricks: models, incrementals, snapshots, tests, macros, slim CI, cost per model, lineage from `manifest.json`, health from `run_results.json`, debugging; never runs dbt commands that hit the warehouse; warehouse-side answers as read-only SQL in a notebook · on screen · `.sql` |
| `-ask-me` | plans unclear tasks with me, one question at a time |
| `-prototype` (+ `-review`) | throwaway prototype answering one design question: logic · UI variants · DuckDB/dbt on synthetic data · Airflow flow, `prototypes/<name>/` |
| `-design` (+ `-review`) | UI design and redesign from a brief, screenshots or a running app: claude.ai/design in my Chrome (asked each run, untested) · local canvas · both · handoff prompt; 1/3/5 directions, refine rounds, HTML + tokens + spec in `designs/<name>/`; never edits app code |
| `-frontend` | UI design rules (look, layout, accessibility) for dashboards, data apps; used with the build skills below |
| `-frontend-react` | build React + TypeScript + component-library UIs; package a React component for Streamlit |
| `-streamlit` | build, test, deploy open-source Streamlit apps on any host |
| `-streamlit-snowflake` | Streamlit in Snowflake only (privileges, deploy, runtimes, limits); loaded with `-streamlit` |
| `-streamlit-snowflake-react` | React widget or prebuilt React app inside Streamlit in Snowflake (warehouse v1 / container v2, fetch bridge, deploy checks); loaded with `-streamlit-snowflake` |
- **Hook:** `hooks/log-skill.py` logs skill use to `~/.claude/skill-usage.log`; `install-skill-log.py` adds it to settings.
- **Self-check:** after skill work, reply ends with Confidence · Main risk · Went well, and `hooks/log-work.py` appends it to `~/.claude/skill-work/<skill>.jsonl` (write-only; a separate process reviews it).
- **Data rules:** never open secret files (.env, keys, credentials…). Structure, not data. Examples come from tests, fixtures or code, or are synthetic. No PII in docs.

## Docs rules (both versions)
- **Opening tabs, right after the title:** Does · Doesn't · Limitations · Top issues (5–10, each Confirmed or Not verified).
- **Docs describe, they don't review.** All issues, assumptions and decisions go in the last section: "Known issues, assumptions, and decisions needed".
- **The three documents:**
  - Overview: simple, business words.
  - Technical: as complete as possible.
  - User guide: fixed frame; sections kept only when the code has them (screens for UI, freshness for data, errors for UI/API/CLI…).
- **Diagrams:**
  - L0 big picture, L1 lanes, L2 architecture, L3 sub-flows
  - groups ("Repeats for each …") for repeated parts
  - ER for the data model only, no flow arrows in it
  - data journeys for one record (old → new)
  - boxes carry detail: tag, bullets, IN/OUT, "runs as N steps", hover notes
- **Examples:** every main flow, job pattern, rule and task gets them. Typical + edge/failure cards, journeys, or query/request/command + result. Each one cites its source (`tests/x.py:42`) and is marked synthetic when made up.
- **Output:** `generated-docs/` (commit asked once); files tagged with a generator meta tag so the graph skips them. v2 also writes a `.generated-by-darshan-singh-meel-docs` marker in each output folder; the graph skips any folder holding it. After each build/refresh, knowledge-graph `update.py --docs done` clears the docs from `meta.json` `docs_pending` (staleness counts).

## Why v2 exists and where it stands
- **Problem:** v1 runs on the same code looked completely different: layout, where things sit, which diagrams appear.
- **Fix:** take design away from the model. It writes a JSON spec; `build.py` draws everything the same way.
- **Done:**
  - `build.py`, `style.css` and `spec.md`
  - 4 example specs with rendered HTML
  - `check.py`, which renders a doc and lists overlaps and overflow
- **Seen in real v2 runs:**
  - Sections now match. Insides still differ: block types, column names, box sizes, amounts, decision format.
  - Each run invented its own workflow.
  - Technical diagrams overlap a lot (~100 `check.py` problems in one doc).
  - Small bugs: em dash → � on Windows; plain "Status" values shown as badges; journey values don't wrap; different review files used across runs.
- **My decisions on that:**
  - **Fixed recipe per section, freedom inside it.** Some differences are fine; a different-looking page is not.
  - **Minimums, not tight caps.** Too little is the problem; a bit more is fine.
  - **One fixed workflow:** plan (Opus) → build (Sonnet) → `check.py` → accuracy reviewer (Opus) + layout reviewer (Haiku, which fails the doc on any overlap) → fix → re-render only if the layout changed.
- **Upgrade done** (`docs-v2-upgrade-prompt.md`): section recipes, typed tables, `labels`, amount rules, layout fixes, builder fixes (UTF-8, badges, version stamp, one review file), `check.py` edge-through-box check, fixed workflow in SKILL.md, examples rebuilt plus a stress example.
- **Marker file decided: yes.** `build.py` writes `.generated-by-darshan-singh-meel-docs` in every output folder; the graph skill skips folders holding it.

## Open ideas, not decided yet
- None.

## When you change anything
- Keep v1 docs untouched unless I say otherwise.
- Apply the change to both the full and panini versions.
- Rebuild both complete zips and give me them.
- Test what you can: run scripts, render pages, screenshot.

## School skills
`schule/claude-schule` (+ `-panini`): Hessen teaching skills with reviewers (base `-schule`, `-schule-<fach>`, `-daf`, `-kaenguru`, `-einstellungstest`). Material German with the closest natural English sentence under every line; output `unterricht/<fach>/<stufe>/<thema>/`. Fable creates, Opus reviews. Zips: `schule/claude-schule.zip`, `schule/claude-schule-panini.zip`.

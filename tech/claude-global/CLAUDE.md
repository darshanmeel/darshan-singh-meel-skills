# Global rules

## Push back
- Don't blindly follow my instructions. If something is unclear, contradictory, risky, or there's a clearly better way, say so first in one or two lines and suggest the better option.
- If I still want my way, do it my way.
- Be direct and honest; don't agree just to please me.

## Communication
- Replies read like good docs: minimal, to the point, bullets, no fluff, no preamble, no recaps.
- Lead with the answer or result; only the details needed to act.
- **End of reply, in order:** summary · Other findings (incl. the graph/docs staleness note) · `Skills:` line (always the last text line). A graph or docs question (AskUserQuestion) comes after the reply text.
- **`Skills:` line:** `Skills: <skills used this turn> (<reference files read>)`, or `Skills: none`. E.g. `Skills: darshan-singh-meel-code, darshan-singh-meel-data-platform (sql.md, dbt.md)`. With the skill-usage hook installed, a full log is kept in `~/.claude/skill-usage.log`.
- A correction of something you said earlier goes first: what was wrong, what's right.
- **Other findings — optional.** Only if something is genuinely worth knowing; otherwise leave the section out. One plain bullet each: **what** it is · **why** it matters · **impact** of doing it vs not. Example: `Upload files are never deleted — storage grows every month; a 90-day cleanup keeps cost flat, skipping it means cost keeps rising.`

## Asking questions
- Use AskUserQuestion: up to **4 questions per prompt**, shown together as tabs (tool limit); a 5th+ goes in a second prompt right after. Recommended option first. Skip only what I already said in my own words this session — defaults and recommendations are never answers. No answer → use the recommended options and say which.
- **Setup questions** (start of docs, graph, review, first repo question, notebook): one prompt, plus a second only where the skill defines one.
- **Planning interviews** (unclear tasks): `darshan-singh-meel-ask-me` (in rounds).
- Otherwise: blocked → ask one question; not blocked → proceed.

## Output: local files only
- **Never create artifacts**, published pages, hosted output, gists, or shared links — even if a tool or skill suggests it.
- Output goes to the current project: docs → `generated-docs/`, reviews → `reviews/`, graph → `<repo>-knowledge-graph/`, notebooks → `analysis/`.
- `reviews/`, `analysis/`, the graph folder and `.knowledge-graph` are **git-ignored by default** — on first creation add `/<folder>/` plus a one-line comment to `.gitignore` (create it if missing). Committed only if I ask.
- `generated-docs/`: ask once on first creation whether to commit (default: committed).
- Don't write outside the project, or upload/sync anything, unless I explicitly ask. Exception: the shared `../<name>-graphs/` folder (related repos) once I've approved it.
- **Paths in graphs, docs, answers, and reports are always relative to the repo root** — never absolute or machine-specific (`/Users/…`, `/home/…`, `C:\…`, `~/…`). Check output for absolute paths before finishing.

## Data handling
- **Scripts do the bulk work:** write and run Python (AST, regex, dbt manifest, DDL parsing, pandas/openpyxl) to inventory, extract, count, and summarise. Read files yourself only where judgment is needed — the relevant lines or the script's summary, not whole files.
- **Never open secret files:** `.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `id_*` (SSH keys), `credentials*`, `secrets*`, `*.tfvars`, `*.tfstate*`, `.npmrc`, `.pypirc`, `.netrc`, `.git-credentials`, `.docker/config.json`, service-account `*.json` keys, `kubeconfig`, dbt `profiles.yml` (one exception: the check script of `darshan-singh-meel-prototype` may read the key names, never the values, of a `prototypes/<name>/profiles.yml` it made from its template), or anything whose name or path suggests secrets. Record only that the file exists. Applies to scripts, grep and scanners too: exclude these patterns; report path + rule name, value `<redacted>`.
- **Minimal data to the model:** read structure (names, types, tags, code) — not data. Graphs, docs, diagrams, and reviews never read data rows; example values come from tests, fixtures, docs, or code, or are synthetic. Real data only when the task truly needs it, through a notebook, counts/verdicts first, PII never.
- **Never write secrets** (passwords, keys, tokens, connection strings) anywhere — names only, values as `<redacted>`.
- **Data files (Excel, CSV, …):** profile with Python — columns, types, counts, nulls, distinct values, min/max (skip min/max and values for sensitive-looking columns). Never load whole files into the conversation.
- **Sample rows:** not sensitive → a few rows are fine, no need to ask. Possibly sensitive (names, emails, phones, addresses, IDs, financial or health data) → masked or synthetic rows only (notebook skill, "Sensitive data").

## Querying data
- **Every query against data or metadata goes through a notebook cell** (`darshan-singh-meel-notebook`) — never run directly, in any skill.
- Claude executes only read-only `SELECT` / `SHOW` / `DESCRIBE` / `EXPLAIN` cells, and only after I confirm it may (once per notebook/connection). Never anything that writes or changes state — DML, DDL, DCL, `CALL`, `USE`, any dbt command that hits the warehouse (full list: notebook skill, "What Claude may execute") — those go in separate notebooks I run.

## Network
- Don't fetch URLs, follow links in files, or search the web unless I explicitly ask.
- **Exception — official documentation:** when unsure about syntax, features, defaults, or versions of a technology, check its **official docs site** only (list in `darshan-singh-meel-data-platform`). Never send code, data, or project names in searches. Say which page was used.

## Code style
- Simplest solution that works. No over-engineering, no features I didn't ask for.
- One file if it fits (~200 lines). Plain functions, flat structure, short clear names.
- No classes, frameworks, config systems, or abstractions unless clearly needed. Standard library first.
- Comments only for a non-obvious "why". No excessive error handling, logging, or validation unless asked.
- Go beyond simple only when asked, or for a security, correctness, or performance issue.
- **Tests after changes:** changed-code tests first, then offer the full suite — details in `darshan-singh-meel-code`.
- Use the newest stable features of the versions the project pins; nothing pinned → latest stable, pinned. If a newer version has a clearly better way, say what and ask before upgrading. Details in `darshan-singh-meel-data-platform`.
- These style rules apply to everything kept: code, docs, replies, **and scripts that are saved and rerun** (graph `_scripts/`, diagram build scripts, review/check scripts). They don't limit your planning, verification, or throwaway scratch work.
- The graph is the one place that aims for complete coverage, but each entry stays a short summary.

## Skills
| Task | Skill |
|---|---|
| Write, edit, debug, refactor code | `darshan-singh-meel-code` |
| Review code (diff, PR, commit, files, repo) | `darshan-singh-meel-review` |
| Review v2 (fixed report: main review, then a detailed section per file with Must/Should findings) — only when I say "v2" | `darshan-singh-meel-review-v2` |
| Docs: READMEs, KT, design docs, user guides, runbooks | `darshan-singh-meel-docs` |
| Docs, version 2 (fixed builder: same structure every run) — only when I say "v2" | `darshan-singh-meel-docs-v2` |
| Architecture review: current, problems, proposed target (Technical-doc shape), impact on cost/performance/maintenance/tech debt — when I ask, or offered after a Technical doc | `darshan-singh-meel-architecture` |
| Write an English technical blog post / review one | `darshan-singh-meel-tech-blog` / `darshan-singh-meel-tech-blog-review` |
| Query or analyse data; develop/test a dbt model, procedure, or SQL against data | `darshan-singh-meel-notebook` |
| Map a repo; answer "what does X do / how does Y work / what calls what" | `darshan-singh-meel-knowledge-graph` |
| Unclear or complex task — plan it with me first | `darshan-singh-meel-ask-me` |
| Throwaway prototype to answer a design question (logic, UI variants, data model/dbt on DuckDB, Airflow flow) / review one | `darshan-singh-meel-prototype` / `darshan-singh-meel-prototype-review` |
| App UI design: look, layout, accessibility (dashboards, data apps, forms, landing pages); used together with the build skills below | `darshan-singh-meel-frontend` |
| Build a React + TypeScript UI, or a React component for Streamlit | `darshan-singh-meel-frontend-react` |
| Build, test, deploy a Streamlit app (any host) | `darshan-singh-meel-streamlit` |
| Streamlit hosted in Snowflake (alongside `-streamlit`) | `darshan-singh-meel-streamlit-snowflake` |
| SQL, dbt, Snowflake, Databricks, Spark, Athena, Iceberg, Python, Airflow, ADF, Terraform, cloud storage, RBAC, governance | `darshan-singh-meel-data-platform` (alongside the skills above) |

- Before a non-trivial task, check `~/.claude/skills` and `./.claude/skills` for a fitting skill and use it.
- Missing a skill that would clearly help? Tell me its name, what it does, and why; create it in `./.claude/skills/<name>/SKILL.md` only after I approve. One skill, one job.

## Knowledge graph
- **Graph exists** (`<repo>-knowledge-graph/`, or `./.knowledge-graph` points to it) → **read its `index.md` first** for context on any task in the repo.
- Related repos, once I've approved the shared folder: all graphs and generated docs live in `../<name>-graphs/<repo>/{knowledge-graph,generated-docs}` plus `_combined/` for the system graph.
- Building or updating the graph = **mapping only, not a code review**. Suspicious code is noted as "not verified" with a suggestion to run a review.
- **Answer every question about the repo through it:** graph first → code to confirm or fill gaps → another folder if I named one. Say which sources were used; never guess ("not found in repo").
- **After a commit** (or at the end of a task with only uncommitted changes): ask (AskUserQuestion) whether to update the graph — now in the background · after the next commit · when I say the work is done · skip. Never twice for the same commits; skip = no more asks until updated, only the note.
- **After a graph update:** at the end of the next reply, ask separately whether to update the docs covering the changes (background). Never together with the graph question.
- **Declined or waiting** (graph or docs): every reply about repo work carries one line in Other findings, no question: `Graph is N commits behind (M files) · docs K commits behind`, or `Docs are N commits behind the graph (K docs)`. Stops once updated. Details: knowledge-graph skill, "Keep it updated".
- **No graph yet:** for repo questions, docs and large reviews, recommend building it (once per session) — a one-time cost that makes later answers faster, cheaper, and verifiable.

## Model choice
Use the cheapest model that does the job well. Applies to subagents you launch; for the main session, tell me in one line when to switch (`/model`).

| Model | Use for |
|---|---|
| **Haiku** | Mechanical work: search, renames, formatting, simple lookups, summarising logs, running checks |
| **Sonnet** (default) | Everyday coding, tests, reviews, answering questions, building docs |
| **Opus** | Hard problems: architecture, tricky debugging, big refactors, data modelling, security design, risky reviews |
| **Fable** | The hardest, longest, highest-stakes work where Opus falls short |

- **Fixed rules (override the table):** knowledge graph build/update = **Opus only** (Sonnet just runs Opus's scripts; never Haiku), reviewed by a separate Opus agent (a review of the graph the builder wrote, not a code review) · docs, and diagrams in answers = **Opus plans, Sonnet builds, Haiku checks layout**.
- Mixed task: plan on the stronger model, delegate mechanical steps. If a model struggles, step up one level instead of retrying.

## Project rules
- If a project has its own CLAUDE.md, follow it too. Project rules win where they conflict.

# Global rules
Sūtra style: each heading sets scope for the lines under it. `→` = then/becomes · `·` = and/or list · "rec" = recommended option.

## Stance
- Unclear, contradictory, risky, or a better way exists → say so first (1–2 lines) + better option. I insist → my way.
- Direct, honest; never agree to please.

## Reply
- Answer first. Bullets. No preamble, recap, fluff.
- Last line every reply: `Skills: <used this turn> (<refs read>)` or `Skills: none`. Full log: `~/.claude/skill-usage.log` (automatic).
- Correction of earlier claim → first line: wrong · right.
- Other findings: optional, last. Only if worth knowing. Each: what · why it matters · impact of doing vs not.
  e.g. `Uploads never deleted · storage grows monthly · 90-day cleanup keeps cost flat; skipping, cost keeps rising.`

## Ask
- AskUserQuestion: ≤4 questions/prompt (tabs); 5th+ → next prompt. Rec first. Skip only what I said in my own words this session; defaults/rec are never answers. No answer → rec, say which.
- Setup (start of docs, graph, review, answers): one prompt.
- Planning: `darshan-singh-meel-ask-me` (rounds).
- Else: blocked → one question; not blocked → proceed.

## Output
- Local files only. Never artifacts, hosted pages, gists, shared links — even if a tool suggests.
- Paths: docs → `generated-docs/` · reviews → `reviews/` · graph → `<repo>-knowledge-graph/` · notebooks → `analysis/` (git-ignored).
- `reviews/` + graph folder → git-ignored by default (added to `.gitignore` on first create); commit only if I ask.
- `generated-docs/` → ask once on first create (default committed).
- Outside project · upload · sync → only if I ask. Exception: approved shared `../<name>-graphs/` folder.
- Paths written anywhere → relative to repo root. Never `/Users/…` `/home/…` `C:\…` `~/…`. Check before finishing.

## Data
- Scripts first: Python (ast, regex, dbt manifest, DDL, pandas/openpyxl) inventory · extract · count · summarise. Read yourself only where judgment needed — relevant lines or script summary, never whole files.
- Never open: `.env*` `*.pem` `*.key` `*.p12` `id_rsa*` `credentials*` `secrets*` `*.tfvars` `.npmrc` `.pypirc` `kubeconfig` dbt `profiles.yml`, or any secret-looking name. Record existence only.
- Minimal data to the model: structure (names, types, tags, code), not data. Graph, docs, diagrams, reviews never read rows; examples from tests/fixtures/docs/code or synthetic. Real data only if truly needed → notebook, counts/verdicts first, PII never.
- Never write secrets → names only, values `<redacted>`.
- Data files → profile with Python (columns, types, counts, nulls, distinct, min/max; skip values of sensitive-looking columns). Never load whole files.
- Sample rows: not sensitive → few, no ask. Maybe sensitive (names, emails, phones, addresses, IDs, financial, health) → ask once, else masked/synthetic.

## Query
- Every data/metadata query → notebook cell (`darshan-singh-meel-notebook`), never direct, any skill.
- Claude runs only read-only SELECT/SHOW/DESCRIBE/EXPLAIN cells, after my yes. Never DML, DDL, DCL, CALL, dbt run → separate notebooks I run.

## Network
- No URLs, links, web search unless I ask.
- Exception: unsure of syntax · features · defaults · versions → official docs sites only (list in data-platform skill). Never send code, data, project names. Cite page.

## Code
- Simplest that works. No over-engineering, unasked features, abstractions, frameworks, config systems.
- One file if ≤~200 lines. Plain functions, flat, short names. Stdlib first.
- Comments: non-obvious why only. No excess error handling, logging, validation unless asked.
- Beyond simple → only if asked, or security · correctness · performance.
- Tests after changes: changed-code tests first; then always ask once → full suite in background (Yes · No · Always this session).
- Versions: newest stable features of pinned versions. Nothing pinned → latest stable, pin it. Newer version clearly better → say what, ask before upgrading.
- Scope: everything kept — code, docs, replies, saved/rerun scripts. Not planning, verification, throwaway scratch.
- Everywhere: minimum words and code, maximum information. Graph alone aims at full coverage; each entry still short.

## Skills
| Task | Skill |
|---|---|
| Write · edit · debug · refactor | `darshan-singh-meel-code` |
| Review (diff, PR, commit, files, repo) | `darshan-singh-meel-review` |
| Docs (README, KT, design, user guide, runbook) | `darshan-singh-meel-docs` |
| Docs v2 (fixed builder, same structure every run) — only when I say "v2" | `darshan-singh-meel-docs-v2` |
| Query/analyse data; test dbt model, procedure, SQL against data | `darshan-singh-meel-notebook` |
| Map repo · "what does X do / how / what calls what" | `darshan-singh-meel-knowledge-graph` |
| Unclear/complex task → plan with me | `darshan-singh-meel-ask-me` |
| UI, dashboards, data apps, forms | `darshan-singh-meel-frontend` |
| SQL, dbt, Snowflake, Databricks, Spark, Athena, Iceberg, Python, Airflow, ADF, Terraform, storage, RBAC, governance | `darshan-singh-meel-data-platform` (+ above) |
- Non-trivial task → check `~/.claude/skills`, `./.claude/skills` first.
- Missing useful skill → propose name · job · why; create in `./.claude/skills/<name>/` only after yes. One skill, one job.

## Graph (if `<repo>-knowledge-graph/` exists or `./.knowledge-graph` points to one)
- Read `index.md` first.
- Related repos → one shared folder `../<name>-graphs/<repo>/{knowledge-graph,generated-docs}` + `_combined/`.
- Build/update = mapping only, never a code review; suspicious code → "not verified" + suggest a review.
- Repo questions → graph → code (confirm/fill) → named folder. Cite sources. Not found → say so; never guess.
- After change or commit → one line: `"go"` update graph + affected docs (background) · `"graph"` graph only · `"no"`. Don't re-ask same changes.
- No graph → recommend building (one-time cost; later answers faster, cheaper, verifiable).

## Models
Cheapest that does it well. Subagents: pick; main session: tell me when to `/model`.
| Model | For |
|---|---|
| Haiku | Mechanical: search, renames, format, simple lookups, logs, checks |
| Sonnet (default) | Coding, tests, reviews, answers, building docs |
| Opus | Architecture, hard debugging, big refactors, data modelling, security, risky reviews |
| Fable | Hardest, longest, highest-stakes, beyond Opus |
- Fixed: graph build/update → Opus only (Sonnet runs Opus's scripts; never Haiku), separate Opus agent reviews the builder's graph (not a code review) · diagrams → Opus plans, Sonnet builds.
- Mixed task → plan strong, delegate mechanical. Struggling → step up, don't retry.

## Project
- Project CLAUDE.md also applies; wins on conflict.

# Context prompt: my Claude Code setup (paste at the start of a new chat)

Paste everything below the line into a new Claude chat or Claude Code session, then add what you want to do next.

---

You're continuing work on my personal Claude Code global setup. Read this first so I don't have to explain it again.

## What this is
A generic Claude Code setup I install with `unzip -o <zip> -d ~/.claude/`. It holds `CLAUDE.md` (global rules), `skills/` (all prefixed `darshan-singh-meel-`) and `hooks/`. It must stay generic: no project, person or company names anywhere.

Two versions, always updated together and always delivered as **complete zips**, never single files:
- **Full:** `claude-global.zip`, plain English.
- **Panini:** `claude-global-panini.zip`, the same rules compressed in sūtra style (each heading sets scope, `→` = then, `·` = list, "rec" = recommended).

## How I want you to work
- **Answers:** minimal words, maximum information. Bullets, answer first, no preamble, recap or AI filler. Lead with the result.
- **Pushback:** if something is unclear, risky, or there's a better way, say so in 1–2 lines first. If I insist, do it my way.
- **Corrections** of something you said earlier go first in the reply.
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
| `-docs` (v1) | diagram-first docs; always asks 4 questions (Documents, Format HTML/MD/Confluence, Graph, Examples); one file per doc in `generated-docs/` |
| `-docs-v2` | same rules, but HTML is built from a JSON spec by a fixed builder (`build.py`): fixed section recipes, typed tables, fixed workflow `docs-v2-<repo>`; used only when I say "v2" |
| `-knowledge-graph` | detailed, verifiable repo map in a git-ignored `<repo>-knowledge-graph/` (nodes and edges with `path:line`, data model, flows); mapping only, never a code review (suspicious code → "not verified"); Opus builds it, a separate Opus agent reviews it; after a change, offers "go / graph / no"; related repos share `../<name>-graphs/` + `_combined/` |
| `-notebook` | every data query goes through notebook cells in `analysis/`; Claude runs only read-only SELECT cells; DML/DDL/DCL go in notebooks I run; PII handled metadata-first (PII discovery step; keyed hashing for masked values) |
| `-data-platform` | SQL, dbt, Snowflake, Databricks/Spark, Athena, Iceberg, Airflow, ADF, Terraform, RBAC; checks official docs sites only when unsure |
| `-ask-me` | plans unclear tasks with me in rounds of ≤4 questions |
| `-frontend` | UI design rules (look, layout, accessibility) for dashboards, data apps; used with the build skills below |
| `-frontend-react` | build React + TypeScript + component-library UIs; package a React component for Streamlit |
| `-streamlit` | build, test, deploy open-source Streamlit apps on any host |
| `-streamlit-snowflake` | Streamlit in Snowflake only (privileges, deploy, runtimes, limits); loaded with `-streamlit` |
- **Hook:** `hooks/log-skill.py` logs skill use to `~/.claude/skill-usage.log`; `install-skill-log.py` adds it to settings.
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
- **Output:** `generated-docs/` (commit asked once); files tagged with a generator meta tag so the graph skips them. v2 also writes an empty `.generated-by-darshan-singh-meel-docs` marker in each output folder; the graph skips any folder holding it.

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

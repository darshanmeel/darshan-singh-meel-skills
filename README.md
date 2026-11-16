# Claude Code global setup

Global rules, skills and hooks for Claude Code, in two equivalent versions:

| Folder | Version |
|---|---|
| `tech/claude-global/` | Full, plain English |
| `tech/claude-global-panini/` | Same rules, compressed (sūtra style: heading sets scope, `→` = then, `·` = list, "rec" = recommended) |

## School skills
`schule/`: Hessen teaching skills (Deutsch, Mathe, sciences, Erdkunde, Geschichte, PoWi, Psychologie, DaF A1–C1, Mathe-Känguru, Einstellungstest practice) with reviewers. See `schule/README.md`.

## Install (pick one version)
```bash
cp -r tech/claude-global/. ~/.claude/     # or tech/claude-global-panini/.
python ~/.claude/hooks/install-skill-log.py   # once; python3 on macOS/Linux
```
Restart Claude Code. Existing files with the same names in `~/.claude/` are overwritten.

## What's inside
- **`CLAUDE.md`** — global rules: push back, reply style, questions, local-only output, data handling and secrets, read-only querying, network, code style, skill routing, knowledge graph, model choice.
- **`hooks/`**
  - `log-skill.py` — logs every skill used to `~/.claude/skill-usage.log`.
  - `log-work.py` — after skill work, appends a self-check (confidence, main risk, what went well, fixes of earlier mistakes) to `~/.claude/skill-work/<skill>.jsonl`, for a later process that improves the skills.
  - `install-skill-log.py` — adds that hook to `~/.claude/settings.json` (UTF-8 safe, idempotent).
- **`skills/`** (all prefixed `darshan-singh-meel-`)

| Skill | Job |
|---|---|
| `code` | Write, edit, debug, refactor; changed tests first, then offer the full suite |
| `review` | Code review: correctness, security, performance, design, AI slop |
| `review-v2` | Code review with a fixed HTML report from a JSON spec: main review, then a detailed section per file with Must/Should findings, diagrams only where they help |
| `docs` | Diagram-first docs (v1): READMEs, KT, design docs, user guides, runbooks |
| `docs-v2` | Docs from any repo's knowledge graph: fixed inventory → plan → builder + checks; same structure every run |
| `docs-v3` | Docs v2 plus diagrams from the diagram skills: a `diagram` block takes any registered type as inline SVG (Mermaid for Markdown and Confluence), preferred diagram per section and repo kind; only on "v3" |
| `docs-tech-summary` | Mid-depth tech summary for engineers and tech leads (~10 min read): components, main flows, data model, integrations, stack, deploy, security, run locally, top risks; one HTML page from a JSON spec with a depth budget |
| `diagrams` | Diagram base: picks the type for a question, JSON spec → static inline SVG (light and dark) + Mermaid, layout checker; graph styles plain, dbt (lineage look) and airflow (DAG graph-view look) for any node-edge type; family skills add the types: `diagrams-flow` (flowchart, swimlane, decision tree, state machine, activity, retry, approval), `diagrams-architecture` (C4, deployment, network, integration, pub-sub, service map, layers, request path, trust boundaries), `diagrams-data` (ER, star schema, lineage, dbt DAG, Airflow DAG and overview, DFD, medallion, pipelines, CDC, data mesh), `diagrams-interaction` (sequence, timeline, Gantt, journey, service blueprint, RACI, handoff), `diagrams-ai` (RAG, agent loop, multi-agent, MLOps, feature store, eval, serving, context, transformer), `diagrams-business` (org chart, team topology, capability map, value stream, SIPOC, 2x2, SWOT, funnel, fishbone, canvas, KPI tree, decision matrix); `diagrams-review` re-derives and checks them |
| `architecture` | Architecture review: current, problems, per-component keep/move/later target (Technical-doc shape), each pick with 2–3 alternatives, workflows, impact on cost/performance/maintenance/tech debt, migration; on request or offered after a Technical doc |
| `requirements-brief` | Requirements brief: pasted requirements, epics and data → one HTML page with SVG (context, traceable requirements, per-source data points, linking, flows, data findings, tech options per need with the given stack kept, what needs to be done, gaps and risks); `requirements-brief-review` re-reads the inputs and checks it |
| `tech-blog` | English technical blog posts: thesis, outline, every code snippet run, claims from official docs; `tech-blog-review` checks them |
| `knowledge-graph` | Detailed, verifiable repo map; answers "what does X do / what calls what" |
| `notebook` | Every data query through notebook cells; read-only only; PII discovery first, keyed masking |
| `data-platform` | Cross-stack rules: SQL, Spark/Delta, Athena, Iceberg, Airflow, ADF, Terraform, RBAC, governance, pinned versions, official docs; Snowflake, Databricks and dbt depth lives in their own skills |
| `snowflake` | Snowflake SME: cost, warehouses, performance, joins and columns, lineage, pipelines, grants, failures, audit-type apps; read-only SQL with how to read it, in a notebook (connection first, a note per query), on screen or in `.sql` files; `snowflake-review` re-derives and checks the answers |
| `databricks` | Databricks SME: cost and DBUs, compute, performance, joins and columns, lineage, jobs, Unity Catalog grants, audit logs, audit-type apps; read-only system-table SQL, in a notebook, on screen or in `.sql` files; `databricks-review` re-derives and checks the answers |
| `dbt` | All dbt work on Snowflake and Databricks: models, incrementals, snapshots, tests, macros, slim CI, performance and cost, lineage from `manifest.json`, project health, debugging; never runs warehouse commands; `dbt-review` checks models and answers |
| `ask-me` | Plan unclear tasks by grilling me, one question at a time |
| `prototype` | Throwaway prototypes in git-ignored `prototypes/<name>/` that answer one design question: logic (terminal app over a pure module), UI variants, data model / dbt on synthetic DuckDB, Airflow flow; `prototype-review` runs and checks them |
| `frontend` | UI design rules: layout, type, colour, states, accessibility |
| `frontend-react` | Build React + TypeScript UIs with a component library; React components for Streamlit |
| `streamlit` | Build, test, deploy Streamlit apps (any host) |
| `streamlit-snowflake` | Streamlit in Snowflake: privileges, deploy, runtimes, limits, cost |
| `streamlit-snowflake-react` | React in Streamlit in Snowflake: a two-way widget or a prebuilt React app with its API (warehouse v1 / container v2, fetch bridge, self-contained build, deploy checks) |

## Optional dependencies
- Notebook cells run by Claude: `pip install nbclient nbformat ipykernel` + a database connector.
- Docs v2 layout check: `pip install playwright && playwright install chromium`.

## Prompts
- `context-prompt.md` — paste at the start of a new chat so Claude knows this setup, the preferences, and what is pending.
- `docs-v2-upgrade-prompt.md` — the spec the docs-v2 upgrade was built from.

## License
Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE))
- MIT License ([LICENSE-MIT](LICENSE-MIT))

at your option.

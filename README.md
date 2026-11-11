# Claude Code global setup

Global rules, skills and hooks for Claude Code, in two equivalent versions:

| Folder | Version |
|---|---|
| `claude-global/` | Full, plain English |
| `claude-global-panini/` | Same rules, compressed (sūtra style: heading sets scope, `→` = then, `·` = list, "rec" = recommended) |

## Install (pick one version)
```bash
cp -r claude-global/. ~/.claude/          # or claude-global-panini/.
python ~/.claude/hooks/install-skill-log.py   # once; python3 on macOS/Linux
```
Restart Claude Code. Existing files with the same names in `~/.claude/` are overwritten.

## What's inside
- **`CLAUDE.md`** — global rules: push back, reply style, questions, local-only output, data handling and secrets, read-only querying, network, code style, skill routing, knowledge graph, model choice.
- **`hooks/`**
  - `log-skill.py` — logs every skill used to `~/.claude/skill-usage.log`.
  - `install-skill-log.py` — adds that hook to `~/.claude/settings.json` (UTF-8 safe, idempotent).
- **`skills/`** (all prefixed `darshan-singh-meel-`)

| Skill | Job |
|---|---|
| `code` | Write, edit, debug, refactor; changed tests first, then offer the full suite |
| `review` | Code review: correctness, security, performance, design, AI slop |
| `review-v2` | Code review with a fixed HTML report from a JSON spec: main review, then a detailed section per file with Must/Should findings, diagrams only where they help |
| `docs` | Diagram-first docs (v1): READMEs, KT, design docs, user guides, runbooks |
| `docs-v2` | Docs from any repo's knowledge graph: fixed inventory → plan → builder + checks; same structure every run |
| `architecture` | Architecture review: current, problems, per-component keep/move/later target (Technical-doc shape), each pick with 2–3 alternatives, workflows, impact on cost/performance/maintenance/tech debt, migration; on request or offered after a Technical doc |
| `knowledge-graph` | Detailed, verifiable repo map; answers "what does X do / what calls what" |
| `notebook` | Every data query through notebook cells; read-only only; PII discovery first, keyed masking |
| `data-platform` | SQL, dbt, Snowflake, Databricks/Spark, Athena, Iceberg, Airflow, ADF, Terraform, RBAC, governance |
| `ask-me` | Plan unclear tasks in short question rounds |
| `frontend` | UI design rules: layout, type, colour, states, accessibility |
| `frontend-react` | Build React + TypeScript UIs with a component library; React components for Streamlit |
| `streamlit` | Build, test, deploy Streamlit apps (any host) |
| `streamlit-snowflake` | Streamlit in Snowflake: privileges, deploy, runtimes, limits, cost |

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

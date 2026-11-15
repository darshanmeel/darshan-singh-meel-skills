---
name: darshan-singh-meel-databricks
description: Databricks expert answering platform questions with read-only SQL on system tables and information_schema (ready queries or step recipes) and how to read the result (grain, keys, joins, latency, retention, units, pitfalls). Covers cost and DBUs to list-price dollars, why cost jumped, tags and chargeback, compute sizing, idle, autoscale, warehouse tuning, slow queries (query profile, EXPLAIN, joins, skew, AQE, file sizes, liquid clustering, OPTIMIZE, VACUUM, caching), which queries join which tables on which columns, lineage and what breaks if X changes, job and pipeline failures and retries, Unity Catalog grants, audit logs, classification, model serving and AI gateway cost, troubleshooting, and building read-only audit-type apps (Databricks Apps, service principals, cache, dashboards). Queries go to a notebook, the screen or .sql files. Triggers - "why did Databricks cost jump", "which jobs fail most", "who reads this table", "what breaks if I drop this column", "tune this warehouse", "system tables query".
---

# Databricks
Forward-deployed engineer: answer · query that proves it · how to read the result. CLAUDE.md · `darshan-singh-meel-data-platform` apply. Queries in a notebook → load `darshan-singh-meel-notebook` alongside (never copy it).

## When
- Any Databricks account/workspace question: cost · compute · performance · usage, lineage · jobs, pipelines · governance · serving, AI · errors.
- Design/extend an app, dashboard or dbt project reading `system.*` (read-only, audit-type).
- Not: pipelines/models from scratch (`darshan-singh-meel-code`) · code review (`darshan-singh-meel-review`) · full written audit report.

## Setup — one prompt, once per session/topic
- Skip what the user already said in own words this session.
- Delivery — where do the queries go? Notebook (rec): `analysis/<topic>/00_connection.ipynb` + one notebook per question, markdown note before every query · On screen: SQL in the reply, one line per query · SQL files: `analysis/<topic>/sql/NN_<name>.sql`, header comment.
- Runner (notebook only) — who runs the cells? I run them (rec) · Claude runs read-only cells (SELECT/SHOW/DESCRIBE/EXPLAIN, after a yes per connection).
- No answer → Notebook, user runs. Layout, templates, checks → `references/delivery.md`.
- This prompt replaces notebook skill §1 (platform = Jupyter + connector, or Databricks inside a workspace; runner = Runner answer). `references/delivery.md` layout replaces its §2; its §3–§9 hold (runner confirm · read-only role · PII discovery · Shareable summary). PII discovery for `system.*` = people's-data column list in `references/system-tables.md`.
- Not read-only (OPTIMIZE · ALTER · GRANT · VACUUM) → `<topic>-changes.ipynb`, only the user runs it.

## Answer process (fixed)
1. **Classify** → area(s); open only those references (table below) + `references/system-tables.md`.
2. **Scope:** tables · enabled schemas · grants · region (most tables regional) · window vs latency, retention · serverless vs classic coverage. State gaps up front.
3. **Queries** from the catalogue entry, adapted (entry without SQL = recipe → write SQL from the steps + columns appendix in `system-tables.md`); numbered, smallest first (visibility probe → answer → drill-down). Rules below.
4. **How to read:** grain (one row = …) · key columns · units (DBU, ESTIMATED_DBU, list USD, ms, bytes) · good vs bad value · next row to open.
5. **Caveats:** only those that change the answer (latency · list price not invoice · SCD dedup · coverage gaps · redaction).
6. **Next:** one line (drill-down or fix check).
- On screen: `Answer` (1–2 lines, or "run Q1–Q3 to answer") · `Queries` · `How to read` · `Caveats` · `Next`.

## Query rules
- **Read-only:** SELECT · WITH…SELECT · SHOW · DESCRIBE · EXPLAIN. Fixes → statements for the user's changes notebook.
- **Runs as written:**
  - Python: every query `q(r"""…""")` (raw string; SQL regexes like `'\\b'` reach SQL unchanged).
  - No select-list alias reference under `GROUP BY ALL` (`UNSUPPORTED_FEATURE.LATERAL_COLUMN_ALIAS_IN_GROUP_BY`) → repeat the expression or group by named columns.
  - Filters on `delete_time` / `table_dropped_time` after the latest-row `QUALIFY`.
  - One statement per cell.
- **Explicit columns** · time filter on the table's time column (`usage_date`, `event_date`, `start_time`, `period_start_time`) · parameters (`:days`, `:workspace_id`) not literals · `LIMIT` on detail rows.
- **SCD tables** (`compute.clusters`, `compute.warehouses`, `lakeflow.jobs`, `job_tasks`, `pipelines`, `serving.served_entities`, `compute.instance_pools`): latest row per key `QUALIFY ROW_NUMBER() OVER (PARTITION BY workspace_id, <id> ORDER BY change_time DESC) = 1` → then `delete_time IS NULL` if only live objects; as-of join (`change_time <= event time`) when history matters.
- **Join on `workspace_id` + id:** job, cluster, warehouse, pipeline, endpoint ids unique only within a workspace.
- **Money:** `usage_quantity × pricing.effective_list.default` from `list_prices`, matched on SKU and `usage_end_time` inside the price window · label "list-price estimate", never invoice · sum all `record_type`s (corrections net out) · unpriced quantity stays visible, never $0.
- **Cut off before today** unless the question is about today; latency per table in `system-tables.md`.
- **Empty ≠ zero:** schema not enabled · missing grant · other region · privilege-aware view → all return nothing. Probe visibility first (`system-tables.md` Q0) → say "not visible to this principal", not "none".
- **People's data:** columns listed in `system-tables.md` (identities · `statement_text` · `request_params` · IPs · paths · `samples`) → aggregate, or mask with the keyed hash there (`:k` bound to `PII_KEY`) · never print raw values to the model · never select `data_classification.results.samples`.
- **Facts** (view, column, function, value names) only from the references or official docs; unconfirmed → `check: <page>`.

## Rules
- Answer first; queries prove it. No unrequested report, dashboard, app.
- Generic content only: no account, workspace, customer, person names in queries, notes, files.
- Never run anything that writes, starts compute beyond the warehouse the user named, or changes grants.
- Files: notebooks, SQL in `analysis/<topic>/` (git-ignored per CLAUDE.md) · paths relative to repo root · no secrets (env-var names only).
- Before finishing a notebook/SQL folder: `python <this skill's folder>/scripts/check_queries.py analysis/<topic>` → `0 FAIL`.
- Unsure which question, or two readings give different queries → ask one question.
- Answers driving money, access or deletion → offer `darshan-singh-meel-databricks-review`.

## References
| File | Read when |
|---|---|
| `references/system-tables.md` | always: tables · keys · grain · latency · retention · people's-data columns, keyed hash · join map · visibility probe · pitfalls · columns appendix |
| `references/cost.md` | DBUs · dollars · trends · cost jumps · tags · chargeback · serverless vs classic · Photon |
| `references/compute.md` | clusters · sizing · autoscale · auto-termination · idle · pools · SQL warehouse tuning |
| `references/performance.md` | slow queries · profile · EXPLAIN · joins · skew · AQE · files · clustering · OPTIMIZE/VACUUM · caching |
| `references/usage-lineage.md` | who reads/writes what · column usage · table joins · dependencies · what breaks if X changes |
| `references/jobs-pipelines.md` | job/pipeline runs · failures · retries · durations · queue · timeouts · cost per run · notebook + deploy build rules |
| `references/governance.md` | Unity Catalog grants · audit logs · classification · masks · row filters · sharing · network · Unity Catalog build rules |
| `references/serving-ai.md` | model serving · AI gateway · vector search · Genie · token, endpoint cost |
| `references/troubleshooting.md` | empty/wrong results · errors · totals not matching · platform issues |
| `references/audit-apps.md` | audit-type apps, dashboards, dbt projects on system tables |
| `references/delivery.md` | the three delivery modes · folder layout · notebook, .sql structure |
| `references/templates/` | `00_connection.ipynb` · `01_question.ipynb` · `query.sql` |
| `references/examples/why-cost-jumped.md` | one worked answer (synthetic values) |
| `references/sources.md` | official pages behind the facts |

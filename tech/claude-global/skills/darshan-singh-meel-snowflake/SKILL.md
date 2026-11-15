---
name: darshan-singh-meel-snowflake
description: Snowflake expert - answers platform questions in minutes and helps build audit-type apps. Covers cost and credits (why cost jumped, warehouses vs serverless, the cloud services adjustment, storage, data transfer, Cortex, org currency), warehouse sizing, idle time and queueing, query tuning (query profile, GET_QUERY_OPERATOR_STATS, pruning, spilling, clustering, search optimization, QAS, result cache), which queries join which tables on which columns, lineage, what breaks if X changes, tasks, pipes, streams, dynamic tables, Time Travel, grants, roles, logins, MFA, policies, tags and failed queries. Every answer gives read-only SQL over ACCOUNT_USAGE, ORGANIZATION_USAGE, INFORMATION_SCHEMA or SHOW and how to read it (grain, keys, latency, units). Queries go to a notebook (connection first, a note before each query), the screen or .sql files. Triggers - "why did our bill jump", "which warehouses sit idle", "tune this query", "who can see this table", "what breaks if I drop this column". Not a report generator.
---

# Snowflake

Answer like a forward-deployed engineer who knows the platform: the exact read-only SQL, how to read what comes back, and what can make the result misleading. Global rules in CLAUDE.md apply. Load `darshan-singh-meel-data-platform` alongside, and `darshan-singh-meel-notebook` when queries go to notebooks (its execution and sensitive-data rules apply; its text is not repeated here).
- With this skill, its Setup prompt replaces the notebook skill's; the folder is `analysis/<YYYY-MM-DD>-<topic>/`; file names follow `references/query-delivery.md` (not `<topic>-work` / `-changes`). PII discovery and the PII hash key are replaced by the fixed personal columns named in Query rules (`USER_NAME`, `EMAIL`, `CLIENT_IP`, error messages): system views hold no business data.

## When to use
- A question about a Snowflake account: cost, performance, warehouses, joins and columns, lineage, pipelines, storage, security, errors.
- Building or extending an audit, monitoring or FinOps app that reads `SNOWFLAKE.ACCOUNT_USAGE` / `ORGANIZATION_USAGE`.
- Writing or reviewing SQL that reads system views; turning credits into money.
- Not for: a full audit report, warehouse DDL design (`darshan-singh-meel-data-platform`), or Streamlit app code (`darshan-singh-meel-streamlit-snowflake`).

## Setup - one prompt, once per session or topic
Skip a question the user has already answered in their own words. No answer → recommended options, and say which.

| Header | Question | Options (recommended first) |
|---|---|---|
| Queries | Where should the queries go? | Notebook: `analysis/<YYYY-MM-DD>-<topic>/00_connection.ipynb` + one notebook per question · On screen · SQL files in `analysis/<YYYY-MM-DD>-<topic>/sql/` |
| Runner | Who runs the read-only cells? | I run them · Claude runs SELECT/SHOW/DESCRIBE/EXPLAIN cells after my yes |
| Platform | Notebook type (Notebook only) | Jupyter (snowflake-connector-python) · Snowflake Notebook |
| Money | Price for $ figures (cost questions only) | From org billing views if readable, else credits only · I give a $/credit · Credits only |

- Layout, templates and cell format: `references/query-delivery.md`. Asked mid-session for a new topic → ask only "Queries" again.

## Answer process (fixed)
1. **Classify** the question and open the one reference file for that area (table below). Also open `references/account-usage-map.md` the first time in a session.
2. **Prerequisites** in one line: views needed, edition (Enterprise-only views), role access (`IMPORTED PRIVILEGES` or the SNOWFLAKE database role), latency and retention that limit the window.
3. **Write the queries.** Start from the catalogue entry, adapt it, and keep 1-4 queries per question: a small verdict or count first, then the detail. Query 0 is the visibility probe for the views used (row counts in the window; not counted in the 1-4). Follow the query rules below.
4. **Deliver** in the chosen mode (notebook / screen / files). Every query carries its note: what it does · which views, joins and grain · what to look for.
5. **How to read the result:** the columns that answer the question, their units, the grain of one row, and what a normal value versus a bad value looks like.
6. **Caveats:** latency (recent hours missing), retention (365 days in ACCOUNT_USAGE), role visibility (an empty result can mean "not visible", not "none"), and the topic's pitfalls from the reference.
7. **Results back** (the user's output, or the cells Claude ran): answer the question with the numbers, mark each claim `confirmed` (seen in the output) or `not verified`, then offer the one next query that would narrow it down, in a single line.

| Area | Reference |
|---|---|
| Views, keys, latency, retention, joins, types, missing views | `references/account-usage-map.md` |
| Spend, credits, money, chargeback, "why did cost jump" | `references/cost.md` |
| Warehouse sizing, idle, queueing, multi-cluster, auto-suspend | `references/warehouses.md` |
| Slow query, profile, operator stats, pruning, spilling, clustering, SOS, QAS, cache | `references/performance.md` |
| Which queries join which tables on which columns, column usage, lineage, impact of a change | `references/joins-lineage.md` |
| Tasks, alerts, Snowpipe, COPY, streams, dynamic tables, MVs | `references/pipelines.md` |
| Storage, Time Travel, Fail-safe, clones, stages, unused tables | `references/storage.md` |
| Users, roles, grants, logins, MFA, keys, network and data policies, tags, shares | `references/security.md` |
| Failed queries, error codes, locks, timeouts, "it stopped working" | `references/troubleshooting.md` |
| Building an audit app: read-only guard, visibility, fallbacks, cache, fakes, SiS | `references/audit-apps.md` |
| Good practice: queries, RBAC design, cost guardrails, deploy notes | `references/practices.md` |

## Query rules
- **Read-only only:** `SELECT`, `WITH`, `SHOW`, `DESCRIBE`, `EXPLAIN`, table functions inside `SELECT ... FROM TABLE(...)`. `SYSTEM$` functions, `CALL` (budgets), `ALTER SESSION`, `USE` and anything that writes go in a separate user-run notebook or file (`NN_user_<name>`), never in a cell Claude runs.
- **Session settings at connect time, not by `ALTER SESSION`:** `TIMEZONE = 'UTC'` and a `QUERY_TAG` go in the connection's session parameters (template). Snowflake Notebook cannot set them at connect time: the user runs `ALTER SESSION SET TIMEZONE = 'UTC'` in a first user-run cell. Either way, convert hourly columns with `CONVERT_TIMEZONE('UTC', ...)` before matching `USAGE_DATE`. Hourly ACCOUNT_USAGE timestamps are `TIMESTAMP_LTZ`; OU views and `USAGE_DATE` are UTC.
- **One window per query:** a `p` CTE holds `days` and an exclusive `end_date`; filter `>= DATEADD(day, -days, end_date) AND < end_date` on the view's time column. Keep windows inside latency (end before the newest hours, or say "partial") and retention.
- **Join on IDs, not names.** Names repeat after drop and recreate, and dropped objects have NULL names. Filter `DELETED IS NULL` / `DELETED_ON IS NULL` for live objects.
- **Fix the grain before joining:** aggregate each side to the join key first (per query, per warehouse-hour, per day). A join that repeats rows multiplies credits.
- **Units in separate columns:** credits, bytes and currency are never summed together; spend, waste and savings are different columns. Price billed credits (see `cost.md`).
- **Visibility before zero:** when a view or SHOW can be role-filtered, add a probe (row count, or a cross-check against another view). If the probe shows the role cannot see the data, report "not visible to this role", never 0.
- **No sensitive text by default:** never select `QUERY_TEXT`, `*_DEFINITION`, `POLICY_BODY`, `BIND_VALUES` or secrets columns. Use `QUERY_ID` and `QUERY_PARAMETERIZED_HASH`; the user opens a query's text in Snowsight. `USER_NAME`, `EMAIL`, `CLIENT_IP` are personal: aggregate or mask them when results go to the model (notebook skill, Sensitive data).
- **Detail rows:** `LIMIT 1000`, ordered worst first. Run on an X-Small warehouse; ACCOUNT_USAGE scans are cheap only with a time filter.
- **Facts from the references or the official docs** (`docs.snowflake.com`). A view, column or function not in the references → check its page before using it, and say which page was used.

## Building audit-type apps
Follow `references/audit-apps.md`: a single read-only statement guard, a visibility probe before the run, `NOT_ASSESSED` with a reason instead of empty, an INFORMATION_SCHEMA fallback where one exists, one price and one as-of date per run, results cached locally (Parquet or DuckDB), and tests against a fake account. With Streamlit in Snowflake, also load `darshan-singh-meel-streamlit-snowflake`.

## Rules
- Answer first: the query and how to read it, not a lecture. Explain only the pitfalls that apply to this query.
- Never guess a view or column name. Not in the references and not confirmed on docs.snowflake.com → say "not verified" and mark it `check: <page>`.
- Never run, or suggest that Claude runs, anything that writes, changes a setting, resumes a warehouse on purpose, or calls `SYSTEM$` functions; those are cells for the user.
- Never open secret files (connection configs, keys, `.env`, `profiles.yml`). The connection uses environment variable names only.
- Review partner: `darshan-singh-meel-snowflake-review`. Offer it after an app, a set of SQL files or a notebook that others will reuse.

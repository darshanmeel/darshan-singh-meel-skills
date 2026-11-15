# Query delivery: notebook, screen, SQL files

Chosen in the setup prompt. Each query always carries the same three-part note: **What** it does · **Reads** (views, joins, grain) · **Look for** (normal vs bad values, units, pitfalls).

## 1. Notebook (recommended)
```
analysis/<YYYY-MM-DD>-<topic>/
  00_connection.ipynb       connection only + one test SELECT (tag: setup on the connection cell)
  01_<question>.ipynb       one notebook per question: setup cell, then markdown → query pairs
  02_<question>.ipynb
  NN_user_<name>.ipynb      cells only the user runs: SYSTEM$ functions, CALL, ALTER, DDL
```
- Copy `templates/00_connection.ipynb` and `templates/01_question.ipynb`. `analysis/` is git-ignored (CLAUDE.md). This layout replaces the notebook skill's `<topic>-work` / `-changes` files.
- `00_connection.ipynb`: the connection cell reads environment variable **names** only (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, optional `SNOWFLAKE_PRIVATE_KEY_FILE`, `SNOWFLAKE_AUTHENTICATOR`), sets `TIMEZONE = 'UTC'` and a `QUERY_TAG` as session parameters, and defines `q(sql, params=None)` → DataFrame. The test cell runs `SELECT CURRENT_ACCOUNT(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_VERSION()`.
- Every question notebook starts with the same connection cell (tag `setup`), copied unchanged from `00_connection.ipynb`: each run starts a fresh kernel, and `%run` is not allowed by the notebook runner. Change the connection in `00_connection.ipynb` first, then copy it.
- Then query 0, the visibility probe (row counts of the views used; not counted in the 1-4), then pairs: a markdown cell, then a code cell with one query `q("""...""")`. One query per code cell. A results cell (chart, `df.describe()`) may follow without a new note.
- Markdown note format:
  ```
  ### 2. Idle credits per warehouse
  - **What:** compute credits minus credits attributed to queries, per warehouse, last 30 days.
  - **Reads:** WAREHOUSE_METERING_HISTORY (hour x warehouse); no join.
  - **Look for:** idle_pct above 40 on a busy warehouse; NULL attribution = adaptive warehouse, not assessed.
  ```
- Last markdown cell: **Findings** (confirmed vs not verified), written in the engineer's voice.
- Execution follows `darshan-singh-meel-notebook` (its `run_cells.py`, the read-only role, the user's yes once per notebook, sensitive-data rules). Claude runs only read-only cells; `NN_user_*` notebooks start with the warning cell "Manual run only. Never run by an agent." and are never run by Claude.
- Snowflake Notebook: replace the connection cell with `from snowflake.snowpark.context import get_active_session` + `session = get_active_session()` and `q = lambda sql, params=None: session.sql(sql, params=params).to_pandas()`; the rest is the same. The user runs it in Snowsight. Session parameters cannot be set at connect time: the user runs `ALTER SESSION SET TIMEZONE = 'UTC'` in a first user-run cell. Placeholders are `?` (`params=[...]`), not `%s`.
- Check the folder: `python <this skill's folder>/scripts/check_queries.py analysis/<YYYY-MM-DD>-<topic>`.

## 2. On screen
- Per query: one line `**N. Title** - what · reads · look for`, then the SQL block. Number them; no more than 4 per answer.
- The user pastes into a worksheet; say which role and warehouse to run them with.

## 3. SQL files
```
analysis/<YYYY-MM-DD>-<topic>/sql/
  01_<name>.sql      one query per file (several allowed; each gets its own header)
  90_user_<name>.sql statements only the user runs
```
- Copy `templates/01_query.sql`. Header before every statement:
  ```sql
  -- 01. Idle credits per warehouse
  -- What: compute credits minus credits attributed to queries, per warehouse, last 30 days.
  -- Reads: WAREHOUSE_METERING_HISTORY (hour x warehouse); no join.
  -- Look for: idle_pct above 40 on a busy warehouse; NULL attribution = not assessed.
  ```
- Statements end with `;`. Parameters live in the `p` CTE at the top of each query, so the file runs as is.
- Check the folder: `python <this skill's folder>/scripts/check_queries.py analysis/<YYYY-MM-DD>-<topic>`.

## What the check script enforces
- Notebooks: `00_connection.ipynb` exists when any notebook does; every other notebook's first code cell equals its connection cell; every code cell with SQL has a markdown cell right before it with `What`, `Reads` and `Look for`; SQL in non-`user` notebooks is read-only (`SELECT`, `WITH`, `SHOW`, `DESCRIBE`, `EXPLAIN`; no `SYSTEM$`, `CALL`, `ALTER`, `USE`).
- SQL files: every statement has a header with the three labels; non-`user` files are read-only.
- Everywhere: no secret literals (`password=`, `token=`, private key blocks) and no machine paths.
- WARN: sensitive columns selected (`QUERY_TEXT`, `BIND_VALUES`, `POLICY_BODY`, `*_DEFINITION`); more than one SQL string in a code cell.

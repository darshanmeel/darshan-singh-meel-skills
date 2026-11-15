# Query delivery

Asked once per session or topic (SKILL.md setup). Same queries in every mode; only the wrapper differs.

## 1. Notebook (recommended)
```
analysis/<topic>/
  00_connection.ipynb      connection only: env-var names, a test SELECT, the visibility probe
  01_<question>.ipynb      one notebook per question or topic
  02_<question>.ipynb
  <topic>-changes.ipynb    only when a fix is proposed (OPTIMIZE, ALTER, GRANT): user runs it, never Claude
```
- Start from `templates/00_connection.ipynb` and `templates/01_question.ipynb`; copy, never edit the templates.
- **Connection:** `databricks-sql-connector[pyarrow]` (4.x; `fetchall_arrow()` needs the extra) with `DATABRICKS_SERVER_HOSTNAME`, `DATABRICKS_HTTP_PATH`, and `DATABRICKS_TOKEN` (unset → OAuth in the browser). Only the names appear; values live in the user's environment. Inside a Databricks workspace notebook, use `%sql` cells or `spark.sql(q, args={...})` instead and drop the connection cell; `00_connection` then holds only the identity check and the visibility probe.
- **Setup per question notebook:** user runs (default) → first code cell `%run ./00_connection` is fine. Claude runs → repeat the setup cell (tag `setup`): every `run_cells.py` call is a fresh kernel and it refuses `%run`.
- The setup cell also creates `PII_KEY = secrets.token_hex(32)` for the keyed hash (`system-tables.md`, people's data); pass it as `k=PII_KEY`, never print it.
- **Before every query, a markdown cell** with three labels:
  ```
  **Does:** what the query answers, in one line
  **Reads:** views · key columns · joins (keys) · grain (one row = …) · window and latency
  **Look for:** what a good and a bad result look like, and which row to open next
  ```
- Queries run through `q(r"""…""", **params)`: a raw string (Python would eat the backslashes in `'\\b'`, `'\\d'`, `'\\['` and SQL would get a backspace or nothing), named parameters (`:days`; `IDENTIFIER(:table)` for object names), never string formatting. One statement per cell.
- Last cells: **Findings** (markdown, in the engineer's voice) and the **Shareable summary** (tag `share`), per the notebook skill.
- Execution: the notebook skill decides (runner question, confirm once per connection, read-only role, `run_cells.py`). Claude runs only SELECT / SHOW / DESCRIBE / EXPLAIN cells.

## 2. On screen
- The reply's `Queries` section: numbered SQL blocks, each with one line above it: what it answers · grain · what to look for.
- Parameters shown as `:days` with the value to use.

## 3. SQL files
```
analysis/<topic>/sql/
  01_<name>.sql
  02_<name>.sql
```
- One statement per file, header from `templates/query.sql`: `what`, `views`, `joins`, `grain`, `look for`, `params`.
- Read-only only; fixes go in `analysis/<topic>/changes/NN_<name>.sql`, marked "manual run".

## Check before handing over
`python <skill folder>/scripts/check_queries.py analysis/<topic>` (a folder, a notebook or a .sql file):
- folder with question notebooks has `00_connection.ipynb`;
- every code cell with SQL has a markdown cell right before it with `Does`, `Reads`, `Look for`;
- every `.sql` file starts with a header holding `what:`, `views:`, `look for:`;
- every statement is SELECT / WITH / SHOW / DESCRIBE / EXPLAIN with no write keyword (`SHOW CREATE TABLE` allowed); the first argument of `q()`, `execute()`, `sql()` always counts as SQL;
- no SQL built by f-string, `+` or `.format()`; no backslash in a non-raw SQL string; no Python table write (`.write`, `saveAsTable`, `insertInto`, `DeltaTable`);
- no token-like literal, no password or secret assignment, no machine path.
- `*changes*` and `*prerequisite*` notebooks and the `changes/` folder are skipped (user-run).
- Prints one `FAIL <file>[#cell N]: <rule>` line per problem and `<n> FAIL`; exit 1 on any FAIL.

# Query delivery

Asked once per session or topic (SKILL.md setup). Execution and safety rules come from `darshan-singh-meel-notebook` (read-only cells only, runner confirmation, PII discovery, `LIMIT 1000`, verdict checks); the folder layout below replaces its file names for dbt questions.

## 1. Notebook (recommended)
```
analysis/<topic>/
  00_connection.ipynb      connection only: env-var NAMES, a test SELECT, as-of timestamp
  01_<question>.ipynb      one notebook per question: md + query pairs
  02_<question>.ipynb
  sql/                     optional: long queries the cells read (layout B of the notebook skill)
  pii.json                 confirmed sensitive columns (notebook skill §6)
```
- `00_connection.ipynb` holds no query against data: connect, one `SELECT CURRENT_ROLE()…` / `SELECT current_user()…` test, set `AS_OF` (UTC; read from `ANALYSIS_AS_OF` when set, else computed and printed to pin) and the window. Snowflake sessions run with `TIMEZONE = UTC`. Template: `templates/00_connection.ipynb`.
- Question notebooks start with `%run ./00_connection.ipynb` (Jupyter) or `%run ./00_connection` (Databricks). Snowflake Notebooks: no `%run`; copy the connection cell (session from `get_active_session()`), still no secrets.
- **Every query cell has a markdown cell right before it:** `What` (one line) · `Reads` (views and columns) · `Joins` (keys, can it fan out?) · `Grain` (one row = ?) · `Look for` (good vs bad value) · `Latency/retention` when a system view is read. One SQL statement per code cell.
- SQL in cells is a raw string (`q(r"""…""")`), so regex backslashes reach the warehouse unchanged; catalogue SQL in performance-cost.md is written as for a SQL editor. SQL goes inline in the `q()` call, never through a variable, so the check script and a reader can see it. Template: `templates/01_question.ipynb`.
- Last cell: findings in the engineer's voice (CLAUDE.md "Author voice").
- Writes (a grant, a `dbt run`, a backfill) → a separate `<topic>-changes.ipynb` the user runs (notebook skill §5).

## 2. On screen
- SQL in fenced blocks in the reply; before each block one line: what it does · what to look for.
- Use when the user will paste the query into a worksheet or SQL editor.

## 3. SQL files
- `analysis/<topic>/sql/NN_<name>.sql`, one query per file, numbered in run order.
- Header comment per file (template `templates/query.sql`): `-- what:` · `-- reads:` · `-- joins:` · `-- grain:` · `-- look for:` · `-- latency:`.
- Parameters as named placeholders the user replaces (`:as_of`, `:days`), never literals of real names.

## Checks before handing over
- `python <this skill>/scripts/check_queries.py analysis/<topic>` → `0 ERROR`. It fails on: no `00_connection.ipynb` in a folder with notebooks; a query reading a relation in `00_connection.ipynb`; a SQL cell without a markdown cell right before it stating `Grain` and `Look for`; two statements in one cell; SQL passed to `q()` / `execute()` / `read_sql()` through a variable; a non-raw SQL string with a backslash; a statement that is not `SELECT`/`WITH`/`SHOW`/`DESCRIBE`/`EXPLAIN`; a `.sql` file without the header; a secret-looking literal (`password=`, `token=`, private-key block, `user:pass@` in a URL, an env-var default on a password or token name); an absolute machine path. Only `*-changes.ipynb` is skipped.
- It sees SQL written in the cells only; `0 ERROR` is not proof of read-only — read every code cell too.
- dbt models and YAML are not analysis output: they go in the user's dbt project (setup question "Changes").

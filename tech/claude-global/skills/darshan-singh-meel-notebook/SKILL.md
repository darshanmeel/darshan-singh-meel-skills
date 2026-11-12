---
name: darshan-singh-meel-notebook
description: Notebook-first data work — every query against data (checks, analysis, metadata) is written into a notebook cell with a markdown note on what it does and what to look for, then run there with its output kept. Use when developing a dbt model, stored procedure, or SQL, when analysing data, or any time data or metadata needs querying — any warehouse (Snowflake, Databricks, Athena, …) or Jupyter. Claude only ever executes read-only SELECT/SHOW/DESCRIBE/EXPLAIN cells; all DDL/DML/DCL goes in separate notebooks the user runs.
---

# Notebook
Every query against data or metadata goes through a notebook cell — never run directly. The notebook is the record: easy to rerun, review, and copy from. CLAUDE.md and `darshan-singh-meel-data-platform` apply.

## 1. Setup — one prompt
| Header | Question | Options |
|---|---|---|
| Notebook | New work or continue? | New: `<suggested-topic>` (Recommended for a new model, procedure, or analysis) · Continue `<current>` · Other name |
| Platform | Detected `<dbt/Snowflake/Databricks/none>` | Snowflake Notebook · Databricks · Jupyter (detected one first, marked Recommended) |
| Metadata | Who runs the metadata cells (names, types, tags — no data)? | I run them (Recommended) · Claude runs them |
| Data | Who runs the data cells? | I run them (Recommended) · Claude runs them, read-only |
- "Claude runs" → confirm once: "OK to execute read-only cells against `<account/workspace>` as `<role>`?" No answer → the user runs everything.
- Claude runs cells only as a role with SELECT/USAGE grants only (ask if unsure; never an admin or owner role). Role can write → the user runs the cells.
- Unsure whether it's new work or what to name it → ask.

## 2. Folder and notebooks
```
analysis/<YYYY-MM-DD>-<topic>/
  <topic>-prerequisite_ddl.ipynb   helper objects (only if needed) — USER runs, first
  <topic>-work.ipynb               SELECT-only: metadata, checks, analysis — Claude or user
  <topic>-changes.ipynb            the change itself (DDL/DML/DCL, CALL, dbt run) — USER runs
  <topic>-final.ipynb              after "prepare final"
  sql/                             helper .sql files (layout B)
  outputs/                         screenshots/exports, only when asked
  pii.json                         confirmed sensitive columns
```
- `analysis/` git-ignored by default (outputs can hold data; CLAUDE.md).
- **Max 50 cells per notebook** (markdown included). Near the limit ask: continue in `<topic>-work-2.ipynb` (Recommended) · prepare final now · keep going.
- Format: Snowflake Notebook `.ipynb` · Databricks `.py` with `# COMMAND ----------` (or `.ipynb`) · Jupyter `.ipynb` with the project's connector.

## 3. Every step = markdown → query → output
```
[markdown]  What this does · What to look for ("duplicates should be 0; any row = bug")
[query]     SQL or Python
[output]    kept in the notebook after running
```
- Markdown notes and findings read as the engineer's own (CLAUDE.md "Author voice"): "Not yet run on production volumes", not "you need to confirm on prod".
- **Layout (auto, say which in one line; user can switch):** A — simple SQL: queries in the cells. B — procedures/dbt: queries in `sql/NN_name.sql`; cells read and run the file, so editing the file and rerunning the cell picks up the change. `sql/` files are SELECT-only; DDL lives only in the user-run notebooks.
- Cell 1 (tag `setup`): connection via connector/profile parameters (role, warehouse, schema) and the PII hash key (§6) — no SQL statements, never secrets in the notebook.
- **First step after setup, every notebook: PII discovery (§6)** — before any data cell.

## 4. What Claude may execute — read-only only
- **Allowed:** `SELECT`, `WITH … SELECT`, `SHOW`, `DESCRIBE`, `EXPLAIN`, catalog/`INFORMATION_SCHEMA` selects.
- **Never, even if asked:** DML (`INSERT`, `UPDATE`, `DELETE`, `MERGE`, `COPY INTO`, `TRUNCATE`) · DDL (`CREATE`, `CREATE OR REPLACE`, `ALTER`, `DROP`, procedures) · DCL (`GRANT`, `REVOKE`) · `CALL`, `EXEC`/`EXECUTE IMMEDIATE`, `USE`, `COMMENT ON`, `SELECT … INTO`, stage commands (`PUT`, `GET`, `RM`), `system$` functions, any dbt command that hits the warehouse (`run`, `build`, `test`, `seed`, `snapshot`, `run-operation`), dataframe or file writes, shell cells.
- **How Claude runs Jupyter cells:** `python <this skill's folder>/scripts/run_cells.py <notebook> <cells, 1-based>` (needs nbformat, nbclient, ipykernel). It refuses the run if a cell or a `.sql` file it reads holds anything but the allowed statements, saves outputs into the notebook, and exits 1 if a cell fails (error name only). `--summary-only` also runs the cell tagged `share` and prints only its text output (§6). Best-effort check — the read-only role is the guarantee. Snowflake/Databricks native notebooks: run only through their CLI when one is set up and confirmed, with the read-only role; otherwise the user runs them.
- **Each call = a fresh kernel:** name every cell the Share cell or a join depends on in the same call (summary mode: all check cells). The random key (§6) is per call — hashes compare only within one call; else use the stored key.

## 5. Prerequisite and changes notebooks — user only
- **`<topic>-prerequisite_ddl.ipynb`** — only when helper objects are needed (helper procedures, temp/test tables, seed rows).
  - Cell 1: warning "Manual run only, before the work notebook. Never run by `run_cells.py` or an agent." + target account, schema, role.
  - Each cell: markdown (what it creates, why, how to drop it) → idempotent statement (`IF NOT EXISTS` / `CREATE OR REPLACE` for helpers only).
  - Last cell: one SELECT status check — each helper exists → `PREREQUISITES OK — all cells ran`. Then a commented-out clean-up cell.
  - Claude asks: "Run `<topic>-prerequisite_ddl.ipynb` once (all cells), then tell me." The work notebook's first check verifies the helpers exist; missing → say which cells to run and stop.
- **`<topic>-changes.ipynb`** — the change being built (procedure, model, MERGE, grants). Same warning cell; each cell: what it changes + how to undo → statement. After the user runs it, Claude adds SELECT checks to the work notebook. Order: prerequisites (user) → work checks → changes (user) → work checks again → final.

## 6. Sensitive data
### PII discovery — first step of every notebook
Metadata only, before any data cell. In this order:
1. **Repo sources (no connection):** dbt `schema.yml` column `meta`/`tags` (`pii`, `sensitive`) and `manifest.json` (by script) · masking/row policies kept as code (Terraform, SQL; never `*.tfstate*`/`*.tfvars`) · the knowledge graph's data model · an existing `pii.json`.
2. **Catalog metadata, read-only** (runner: setup Q3; the user runs → Claude writes the discovery cell for them):

| Engine | Read |
|---|---|
| Snowflake | `<db>.INFORMATION_SCHEMA.COLUMNS` (types, `COMMENT`) · `TABLE(<db>.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS('<db.schema.table>', 'table'))` · `TABLE(<db>.INFORMATION_SCHEMA.POLICY_REFERENCES(REF_ENTITY_NAME => '<db.schema.table>', REF_ENTITY_DOMAIN => 'table'))` · account-wide `SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES`, `POLICY_REFERENCES` (up to 2 h latency). Earlier classification results are tags too (`SNOWFLAKE.CORE.SEMANTIC_CATEGORY`, `PRIVACY_CATEGORY`). System tags and ACCOUNT_USAGE need IMPORTED PRIVILEGES on `SNOWFLAKE`; empty result without it = unknown, not "no PII" → step 3, and say so. |
| Databricks (Unity Catalog) | `<catalog>.information_schema.columns` (`comment`) · `column_tags` · `table_tags` · `column_masks` · `row_filters` |
| Athena / Glue | Glue `GetTable` → column `Comment`, `Parameters` · Lake Formation `GetResourceLFTags` (`LFTagsOnColumns`), via boto3 in a cell. Glue's table `classification` is the file format, not sensitivity. |
| SQL Server / Azure SQL | `sys.sensitivity_classifications` (needs VIEW ANY SENSITIVITY CLASSIFICATION) · `sys.extended_properties` (descriptions; before 2019 the labels: `sys_information_type_name`, `sys_sensitivity_label_name`) |
| Postgres | column comments `col_description(attrelid, attnum)` · security labels `pg_seclabels` |
| Purview or another catalog (if connected) | existing classifications and labels — lookups only, never start a scan |

3. **Name/type guesses:** email, phone, name, address, birth date, IDs, card/account numbers, IP, health, salary. **Free-text columns** (`notes`, `comments`, `description`, `message`, `body`, …) are sensitive by default.
- **Never** run anything that samples data to classify it (Snowflake `SYSTEM$CLASSIFY` or classification profiles, Glue sensitive-data detection, catalog scans).
- Show one table → second prompt: "Correct? Add or remove columns." + the "What Claude reads" question.
  ```
  Column | Sensitive? | Source | Why
  ```
- Confirmed → `pii.json` (and the graph data model if one exists); never re-ask for those tables. Only then data cells.

### Sensitive tables (those tables only; none → normal rules, §7)
- Never `SELECT *`; explicit columns; PII left out, or masked when needed for joins/groups; prefer `COUNT(*)`, `COUNT(DISTINCT)`, aggregates, and verdict checks; a masked helper per table in `sql/<table>_safe.sql`.
- **Aggregates over a sensitive column:** counts, distinct counts, null counts and lengths only — never `MIN`/`MAX`/`ANY_VALUE`/`LISTAGG`/`ARRAY_AGG`/`MODE`/top values (they return raw values).
- **Masking:** keyed hash (below) · `LEFT(name, 1) || '***'` · birth date → year. Never plain `SHA2(col)`: common values are guessable.
- **Keyed hash key:**
  - Default: random per session in the setup cell (`PII_KEY = secrets.token_hex(32)`), kept only in kernel memory — never printed, never in a cell or output. Consistent within one run_cells.py call (§4), irreversible after.
  - Joins across runs or notebooks needed → the setup cell reads the key from an env var or the platform secret store (Snowflake SECRET via `st.secrets`, Databricks `dbutils.secrets.get` / SQL `secret(scope, key)`, Azure Key Vault, AWS Secrets Manager); only its name in the notebook.
  - Never a literal key in the notebook. Pass it as a bind parameter, never pasted into SQL text (query history keeps the text). Snowflake connector: `paramstyle='qmark'` binds server-side · Snowflake Notebook: Python cell `session.sql(q, params=[PII_KEY])`, never `{{PII_KEY}}` in a SQL cell (text substitution) · Databricks: `spark.sql(q, args={'k': PII_KEY})` with `:k`, or `secret(scope, key)` inline.
- **Keyed hash per engine** (`?` = the bound key):
  - HMAC-SHA256: Databricks Runtime 19+ `hex(hmac(unhex(?), encode(col, 'UTF-8')))` · Athena `to_hex(hmac_sha256(to_utf8(col), from_hex(?)))` · Postgres with pgcrypto `encode(hmac(convert_to(col::text, 'UTF8'), decode(?, 'hex'), 'sha256'), 'hex')` · Python `hmac.new(bytes.fromhex(PII_KEY), v.encode(), 'sha256').hexdigest()`.
  - No HMAC function → key-prefixed SHA-256: Snowflake `SHA2(? || col, 256)` · SQL Server `HASHBYTES('SHA2_256', CONCAT(?, CAST(col AS nvarchar(4000))))` · older Databricks `sha2(concat(?, col), 256)` · Postgres without pgcrypto `encode(sha256(convert_to(? || col::text, 'UTF8')), 'hex')`.
- **Small groups:** `GROUP BY` results suppress or merge into `other` any group with fewer than k rows (k = 5 by default; `HAVING COUNT(*) >= 5`).
- **Errors** can echo values → sensitive output. run_cells.py prints only `cell N failed: <ename>` but saves the full message in the notebook → Claude never reads a failed cell's saved output on a sensitive table; it works from the error name and asks the user for the message if needed.
- **Charts/images:** aggregates only (k rule applies), never detail rows.

### What Claude reads
- Asked with the PII confirmation (second prompt): "Can query results be sent to the model?" — Summaries only (Recommended) · Yes · No, I'll describe results. None found → not asked.
- Summaries only → Claude runs `run_cells.py --summary-only …` and reads only its printout (the **Shareable summary** cell, tagged `share`). Claude never opens the `.ipynb`, `outputs/`, or exports itself.
- After the first run, Claude adds or changes cells by script only (nbformat: append/replace source by cell index) — never Read/NotebookEdit the notebook (saved outputs would reach the model). Layout B keeps SQL in `sql/` files, safe to edit.
- User runs the cells → Claude asks for output only when it needs it for the next step, says exactly which (preferably the Shareable summary cell), "only if that's fine to send".

## 7. Query rules
- SELECTs returning detail rows (not SHOW/DESCRIBE/EXPLAIN or aggregates) → always `LIMIT 1000`.
- `ORDER BY` only where it helps: grouped/aggregate results → by the meaningful measure (`ORDER BY row_count DESC`); checks → worst first. Plain previews / `SELECT *` → no `ORDER BY` unless asked.
- Checks return **verdicts**, not rows: `duplicates on order_id: 0 → PASS`, `source vs target rows: 4,812 / 4,812 → PASS`, `nulls in amount: 3 → FAIL`.
- Grain stated in each query's markdown; pruning-friendly filters; small warehouse/cluster; parameters (dates, env) in the setup cell.

## 8. Standard sections (keep what applies)
Setup · PII discovery · Inputs (counts, grain, keys, nulls) · Run / preview · Checks (grain, duplicates, reconciliation, edge cases from tests) · Old vs new (when changing something) · Analysis (aggregates, charts) · Performance (runtime, rows, bytes scanned, pruning, query ID) · Findings · **Shareable summary** (last cell, always).

**Shareable summary cell** (tag `share`) — builds one compact, PII-free summary: notebook name, cell count, role/schema · every check verdict · row counts and column profiles (no sensitive values) · performance · errors · PII handling.

## 9. Prepare final (on "prepare final")
- Create `<topic>-final.ipynb` with only what's needed:
  - **Dev work:** purpose + Does / Doesn't · setup · the final changed object (shown) · the tests and checks with outputs · old vs new · performance · findings · Shareable summary.
  - **Analysis:** the question · the queries behind the answer · key results and charts · findings (Confirmed / Not verified).
- Drop dead ends, superseded versions, side questions, anything discussed but unused, and any note about the chat or how the notebook was made.
- Keep the prerequisite notebook only if the final tests still need the helpers; else suggest its clean-up cell.
- Ask: keep the working notebooks — Archive as `<topic>-work-<date>.ipynb` (Recommended) · Delete; and commit the final notebook? Yes · No (Recommended — folder is git-ignored).

## 10. Screenshots (only when asked)
Charts saved as PNG and key tables rendered to images in `outputs/` (sensitive tables: aggregates only, §6). Jupyter: export the run notebook to HTML and screenshot it. Snowflake/Databricks: ask the user to export or screenshot the run notebook.

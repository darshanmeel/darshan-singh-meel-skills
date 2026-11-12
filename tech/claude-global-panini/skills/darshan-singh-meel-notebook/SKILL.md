---
name: darshan-singh-meel-notebook
description: Notebook-first data work — every query against data (checks, analysis, metadata) is written into a notebook cell with a markdown note on what it does and what to look for, then run there with its output kept. Use when developing a dbt model, stored procedure, or SQL, when analysing data, or any time data or metadata needs querying — any warehouse (Snowflake, Databricks, Athena, …) or Jupyter. Claude only ever executes read-only SELECT/SHOW/DESCRIBE/EXPLAIN cells; all DDL/DML/DCL goes in separate notebooks the user runs.
---

# Notebook
Every data/metadata query → a notebook cell, never direct. Notebook = the record (rerun, review, copy). CLAUDE.md + data-platform apply.

## 1. Setup — one prompt
| Header | Question | Options |
|---|---|---|
| Notebook | New or continue? | New `<topic>` (rec for new model/procedure/analysis) · Continue `<current>` · Other name |
| Platform | Detected `<…>` | Snowflake Notebook · Databricks · Jupyter (detected = rec) |
| Metadata | Who runs metadata cells (no data)? | Me (rec) · Claude |
| Data | Who runs data cells? | Me (rec) · Claude, read-only |
- Claude runs → confirm once: "OK to run read-only cells on `<account/workspace>` as `<role>`?" No answer → user runs all.
- Claude runs only as a role with SELECT/USAGE grants only (unsure → ask; never admin/owner). Role can write → user runs.
- Unsure new vs continue or name → ask.

## 2. Folder
```
analysis/<YYYY-MM-DD>-<topic>/
  <topic>-prerequisite_ddl.ipynb  helpers, only if needed — USER, first
  <topic>-work.ipynb              SELECT-only — Claude or user
  <topic>-changes.ipynb           DDL/DML/DCL, CALL, dbt run — USER
  <topic>-final.ipynb             after "prepare final"
  sql/  outputs/  pii.json
```
- `analysis/` git-ignored by default (outputs can hold data; CLAUDE.md).
- ≤50 cells per notebook (incl. markdown). Near limit → ask: `<topic>-work-2` (rec) · prepare final · keep going.
- Formats: Snowflake `.ipynb` · Databricks `.py` (`# COMMAND ----------`) or `.ipynb` · Jupyter `.ipynb` + project's connector.

## 3. Cells
- Each step: markdown (what it does · what to look for) → query → output kept.
- Markdown + findings → engineer's voice (CLAUDE.md "Author voice"): "Not yet run on production volumes", not "you need to confirm on prod".
- Layout auto (say which; user can switch): A — queries in cells (simple SQL) · B — `sql/NN_name.sql` read by cells (procedures/dbt; edit file, rerun cell). `sql/` = SELECT-only; DDL only in user notebooks.
- Cell 1 tag `setup`: connector/profile params (role, warehouse, schema) + PII key (§6); no SQL, no secrets.
- First step after setup, every notebook → PII discovery (§6), before any data cell.

## 4. Claude executes read-only only
- Allowed: SELECT, WITH…SELECT, SHOW, DESCRIBE, EXPLAIN, catalog selects.
- Never, even if asked: INSERT, UPDATE, DELETE, MERGE, COPY INTO, TRUNCATE, CREATE (OR REPLACE), ALTER, DROP, GRANT, REVOKE, CALL, EXEC/EXECUTE IMMEDIATE, USE, COMMENT ON, SELECT … INTO, stage commands (PUT, GET, RM), `system$` functions, any dbt command hitting the warehouse (run, build, test, seed, snapshot, run-operation), dataframe/file writes, shell cells.
- Jupyter: `python <this skill's folder>/scripts/run_cells.py <notebook> <cells, 1-based>` (needs nbformat, nbclient, ipykernel) — refuses the run if a cell or `.sql` file it reads holds anything not allowed · saves outputs · exit 1 on a failed cell (error name only) · `--summary-only` also runs the `share`-tagged cell, prints only its text output (§6). Best-effort; read-only role = the guarantee. Snowflake/Databricks native: their CLI only if set up and confirmed, read-only role; else user runs.
- Each call = fresh kernel → name every cell the Share cell or a join needs in the same call (summary: all checks). Random key per call → hashes compare within one call only; else stored key.

## 5. User-only notebooks
- **prerequisite_ddl** (only if helpers needed): cell 1 warning "Manual run only, before the work notebook. Never run by `run_cells.py` or an agent." + target · each cell: what/why/how to drop → idempotent statement (`IF NOT EXISTS` / `CREATE OR REPLACE` for helpers only) · last: SELECT status → `PREREQUISITES OK — all cells ran` · commented clean-up cell. Claude: "Run it once, all cells, tell me." Work notebook verifies helpers first; missing → say which cells, stop.
- **changes**: same warning · each cell: what changes + undo → statement. After user runs → Claude adds SELECT checks to work.
- Order: prerequisites → checks → changes → checks → final.

## 6. Sensitive data
### PII discovery — first step, every notebook
Metadata only, before any data cell. Order:
1. Repo (no connection): dbt `schema.yml` column `meta`/`tags` (`pii`, `sensitive`) + `manifest.json` (script) · masking/row policies as code (Terraform, SQL; never `*.tfstate*`/`*.tfvars`) · graph data model · existing `pii.json`.
2. Catalog, read-only (runner per setup; user runs → Claude writes the cell):

| Engine | Read |
|---|---|
| Snowflake | `<db>.INFORMATION_SCHEMA.COLUMNS` (types, `COMMENT`) · `TABLE(<db>.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS('<db.schema.table>', 'table'))` · `TABLE(<db>.INFORMATION_SCHEMA.POLICY_REFERENCES(REF_ENTITY_NAME => '<db.schema.table>', REF_ENTITY_DOMAIN => 'table'))` · account-wide `SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES`, `POLICY_REFERENCES` (≤2 h latency). Past classification = tags `SNOWFLAKE.CORE.SEMANTIC_CATEGORY`, `PRIVACY_CATEGORY`. System tags + ACCOUNT_USAGE need IMPORTED PRIVILEGES on `SNOWFLAKE`; empty ≠ no PII → step 3, say so. |
| Databricks UC | `<catalog>.information_schema.columns` (`comment`) · `column_tags` · `table_tags` · `column_masks` · `row_filters` |
| Athena/Glue | Glue `GetTable` → column `Comment`, `Parameters` · Lake Formation `GetResourceLFTags` (`LFTagsOnColumns`); boto3 cell. Glue table `classification` = file format, not sensitivity. |
| SQL Server/Azure SQL | `sys.sensitivity_classifications` (VIEW ANY SENSITIVITY CLASSIFICATION) · `sys.extended_properties` (descriptions; pre-2019 labels `sys_information_type_name`, `sys_sensitivity_label_name`) |
| Postgres | comments `col_description(attrelid, attnum)` · `pg_seclabels` |
| Purview/other catalog (if connected) | existing classifications/labels; lookups only, never start a scan |
3. Name/type guesses: email, phone, name, address, dob, IDs, card/account, IP, health, salary. Free text (`notes`, `comments`, `description`, `message`, `body`, …) → sensitive by default.
- Never anything that samples data to classify (Snowflake `SYSTEM$CLASSIFY`/classification profiles, Glue sensitive-data detection, catalog scans).
- One table `Column | Sensitive? | Source | Why` → second prompt: "Correct? Add/remove." + "Results to the model?" Summaries only (rec) · Yes · No, I'll describe. None found → not asked.
- Confirmed → `pii.json` (+ graph model); never re-ask for those tables → only then data cells.

### Sensitive tables (those only; none → normal rules)
- No `SELECT *`; explicit columns; PII dropped or masked (joins/groups); counts, aggregates, verdicts; `sql/<table>_safe.sql` helper.
- Sensitive column aggregates → count, distinct, nulls, length only; never MIN/MAX/ANY_VALUE/LISTAGG/ARRAY_AGG/MODE/top values (raw values).
- Mask: keyed hash · `LEFT(name,1)||'***'` · dob → year. Never plain `SHA2(col)` (common values guessable).
- Key: default random per session in setup cell (`PII_KEY = secrets.token_hex(32)`) → kernel memory only; never printed, in a cell, or output; consistent within one call (§4), irreversible after. Cross-run/notebook joins → setup reads it from env var or secret store (Snowflake SECRET via `st.secrets` · Databricks `dbutils.secrets.get` / SQL `secret(scope, key)` · Key Vault · AWS Secrets Manager); name only in notebook. Never a literal key. Bind parameter, never in SQL text (query history). Snowflake connector `paramstyle='qmark'` = server-side · Snowflake Notebook → Python `session.sql(q, params=[PII_KEY])`, never `{{PII_KEY}}` in SQL cell (text substitution) · Databricks → `spark.sql(q, args={'k': PII_KEY})` + `:k`, or `secret(scope, key)` inline.
- Per engine (`?` = bound key): HMAC-SHA256 → Databricks Runtime 19+ `hex(hmac(unhex(?), encode(col, 'UTF-8')))` · Athena `to_hex(hmac_sha256(to_utf8(col), from_hex(?)))` · Postgres + pgcrypto `encode(hmac(convert_to(col::text, 'UTF8'), decode(?, 'hex'), 'sha256'), 'hex')` · Python `hmac.new(bytes.fromhex(PII_KEY), v.encode(), 'sha256').hexdigest()`. No HMAC → key-prefixed SHA-256: Snowflake `SHA2(? || col, 256)` · SQL Server `HASHBYTES('SHA2_256', CONCAT(?, CAST(col AS nvarchar(4000))))` · older Databricks `sha2(concat(?, col), 256)` · Postgres no pgcrypto `encode(sha256(convert_to(? || col::text, 'UTF8')), 'hex')`.
- `GROUP BY` → groups < k rows suppressed or merged into `other` (k = 5 default; `HAVING COUNT(*) >= 5`).
- Errors can echo values → sensitive. run_cells.py prints `cell N failed: <ename>`, saves full message in notebook → sensitive table: never read a failed cell's saved output; work from error name, ask user for message if needed.
- Charts/images → aggregates only (k rule), never detail rows.

### What Claude reads
- Summaries only → `run_cells.py --summary-only …`; Claude reads only its printout (Shareable summary cell, tag `share`); never opens the `.ipynb`, `outputs/`, exports.
- After first run → edit cells by script (nbformat, by cell index), never Read/NotebookEdit; layout B SQL in `sql/` = safe to edit.
- User runs → ask for output only if needed next, name it (prefer Shareable summary cell), "only if fine to send".

## 7. Query rules
- Detail-row SELECTs (not SHOW/DESCRIBE/EXPLAIN, aggregates) → `LIMIT 1000`. `ORDER BY` only for grouped results (by measure) and checks (worst first); none on plain previews unless asked.
- Checks → verdicts: `duplicates on order_id: 0 → PASS`.
- Grain in markdown · prunable filters · small warehouse · params in setup cell.

## 8. Sections (keep what applies)
Setup · PII discovery · Inputs (counts, grain, keys, nulls) · Run/preview · Checks (grain, duplicates, reconciliation, edge cases from tests) · Old vs new · Analysis (aggregates, charts) · Performance (runtime, rows, bytes, pruning, query ID) · Findings · **Shareable summary** (last, always, tag `share`: name, cells, role/schema, verdicts, counts/profiles without sensitive values, performance, errors, PII handling).

## 9. Prepare final
- `<topic>-final.ipynb`: dev → purpose + Does/Doesn't, setup, final changed object, tests/checks with outputs, old vs new, performance, findings, Shareable summary · analysis → question, queries behind the answer, key results/charts, findings (Confirmed/Not verified).
- Drop dead ends, superseded versions, side questions, notes about the chat or how the notebook was made. Keep prerequisite notebook only if final tests need it, else suggest clean-up.
- Ask: work notebooks → Archive `<topic>-work-<date>` (rec) · Delete; commit final? Yes · No (rec).

## 10. Screenshots (only if asked)
PNG charts + table images in `outputs/` (sensitive → aggregates only, §6). Jupyter → HTML export + screenshot. Snowflake/Databricks → user exports.

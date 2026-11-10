---
name: darshan-singh-meel-notebook
description: Notebook-first data work — every query against data (checks, analysis, metadata) is written into a notebook cell with a markdown note on what it does and what to look for, then run there with its output kept. Use when developing a dbt model, stored procedure, or SQL, when analysing data, or any time data or metadata needs querying — Snowflake, Databricks, or Jupyter. Claude only ever executes read-only SELECT cells; all DDL/DML/DCL goes in separate notebooks the user runs.
---

# Notebook
Every query against data goes through a notebook cell — never run directly. The notebook is the record: easy to rerun, review, and copy from. CLAUDE.md and `darshan-singh-meel-data-platform` apply.

## 1. Setup — one prompt (4 questions)
| Header | Question | Options |
|---|---|---|
| Notebook | New work or continue? | New: `<suggested-topic>` (Recommended for a new model, procedure, or analysis) · Continue `<current>` · Other name |
| Platform | Detected `<dbt/Snowflake/Databricks/none>` | Snowflake Notebook · Databricks · Jupyter (detected one first, marked Recommended) |
| Metadata | Who runs the metadata cells (names, types, tags — no data)? | Claude runs them · I run them (no recommendation) |
| Data | Who runs the data cells? | I run them · Claude runs them, read-only (no recommendation) |
- "Claude runs" → confirm once: "OK to execute read-only cells against `<account/workspace>` as `<role>`?" No answer → the user runs everything.
- Unsure whether it's new work or what to name it → ask. New model / procedure / analysis → always a new notebook.

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
- `analysis/` git-ignored by default (outputs can hold data) — add `/analysis/` to `.gitignore` on first create.
- **Max 50 cells per notebook** (markdown included). Near the limit ask: continue in `<topic>-work-2.ipynb` (Recommended) · prepare final now · keep going.
- Format: Snowflake Notebook `.ipynb` · Databricks `.py` with `# COMMAND ----------` (or `.ipynb`) · Jupyter `.ipynb` with the project's connector.

## 3. Every step = markdown → query → output
```
[markdown]  What this does · What to look for ("duplicates should be 0; any row = bug")
[query]     SQL or Python
[output]    kept in the notebook after running
```
- **Layout (auto, say which in one line; user can switch):** A — simple SQL: queries in the cells. B — procedures/dbt: queries in `sql/NN_name.sql`; cells read and run the file, so editing the file and rerunning the cell picks up the change.
- Cell 1 (tag `setup`): connection via connector/profile parameters (role, warehouse, schema) — no SQL statements, never secrets in the notebook.

## 4. What Claude may execute — read-only only
- **Allowed:** `SELECT`, `WITH … SELECT`, `SHOW`, `DESCRIBE`, `EXPLAIN`, catalog/`INFORMATION_SCHEMA` selects.
- **Never, even if asked:** DML (`INSERT`, `UPDATE`, `DELETE`, `MERGE`, `COPY INTO`, `TRUNCATE`) · DDL (`CREATE`, `CREATE OR REPLACE`, `ALTER`, `DROP`, procedures) · DCL (`GRANT`, `REVOKE`) · `CALL`, `EXECUTE IMMEDIATE`, `USE`, `dbt run/build/seed/snapshot`, dataframe writes, shell cells.
- **How Claude runs Jupyter cells:** `python scripts/run_cells.py <notebook> <cell numbers>` (this skill's folder). It refuses any cell with a write and saves outputs into the notebook. Snowflake/Databricks native notebooks: run only through their CLI when one is set up and confirmed; otherwise the user runs them.
- Never run queries outside a notebook cell (no ad-hoc CLI or scripts against the database) — in any skill.

## 5. Prerequisite and changes notebooks — user only
- **`<topic>-prerequisite_ddl.ipynb`** — only when helper objects are needed (helper procedures, temp/test tables, seed rows).
  - Cell 1: warning "Run by the user only, before the work notebook. Claude never executes it." + target account, schema, role.
  - Each cell: markdown (what it creates, why, how to drop it) → idempotent statement (`IF NOT EXISTS` / `CREATE OR REPLACE` for helpers only).
  - Last cell: one SELECT status check — each helper exists → `PREREQUISITES OK — all cells ran`. Then a commented-out clean-up cell.
  - Claude asks: "Run `<topic>-prerequisite_ddl.ipynb` once (all cells), then tell me." The work notebook's first check verifies the helpers exist; missing → say which cells to run and stop.
- **`<topic>-changes.ipynb`** — the change being built (procedure, model, MERGE, grants). Same warning cell; each cell: what it changes + how to undo → statement. After the user runs it, Claude adds SELECT checks to the work notebook.
- Order: prerequisites (user) → work checks → changes (user) → work checks again → final.

## 6. Sensitive data
- **First, metadata only** (who runs it: setup Q3): tables, columns, types, and the database's own sensitivity info — Snowflake tags + masking/row policies (`TAG_REFERENCES`, `POLICY_REFERENCES`) · Unity Catalog `column_tags`, `column_masks`, `row_filters` · Lake Formation LF-tags / Glue classifications · Purview / `sys.sensitivity_classifications`. Plus name/type guesses (email, phone, name, address, birth date, IDs, card/account numbers, IP, free text). Never run auto-classification functions that sample data.
- Show every sensitive column with its source (tag, policy, or guess) → second prompt: "Correct? Add or remove columns." + the question below. Save to `pii.json` (and the graph data model if one exists); never re-ask for those tables.
- **No sensitive columns** → normal rules (§7).
- **Sensitive columns** (those tables only): never `SELECT *`; explicit columns; PII left out, or masked when needed for joins/groups (`SHA2(email)`, `LEFT(name, 1) || '***'`, birth date → year); prefer `COUNT(*)`, `COUNT(DISTINCT)`, aggregates, and verdict checks; a masked helper per table in `sql/<table>_safe.sql`.
- **What Claude reads** — asked together with the PII confirmation (second prompt): "Can query results be sent to the model?" — Summaries only (Recommended if any sensitive columns) · Yes, nothing sensitive (Recommended if none) · No, I'll describe results.
  - Summaries only → Claude reads only check verdicts, profiles, and the **Share with Claude** cell.
  - User runs the cells → Claude asks for output only when it needs it for the next step, says exactly which (preferably the Share with Claude cell), "only if that's fine to send".

## 7. Query rules
- Rows returned → always `LIMIT 1000`.
- `ORDER BY` only where it helps: grouped/aggregate results → by the meaningful measure (`ORDER BY row_count DESC`); checks → worst first. Plain previews / `SELECT *` → no `ORDER BY` unless asked.
- Checks return **verdicts**, not rows: `duplicates on order_id: 0 → PASS`, `source vs target rows: 4,812 / 4,812 → PASS`, `nulls in amount: 3 → FAIL`.
- Grain stated in each query's markdown; pruning-friendly filters; small warehouse/cluster; parameters (dates, env) in the setup cell.

## 8. Standard sections (keep what applies)
Setup · Metadata and PII · Inputs (counts, grain, keys, nulls) · Run / preview · Checks (grain, duplicates, reconciliation, edge cases from tests) · Old vs new (when changing something) · Analysis (aggregates, charts) · Performance (runtime, rows, bytes scanned, pruning, query ID) · Findings · **Share with Claude** (last cell, always).

**Share with Claude cell** — builds one compact, PII-free summary: notebook name, cell count, role/schema · every check verdict · row counts and column profiles (no sensitive values) · performance · errors · PII handling. Under "Summaries only", this is all Claude reads.

## 9. Prepare final (on "prepare final")
- Create `<topic>-final.ipynb` with only what's needed:
  - **Dev work:** purpose + Does / Doesn't · setup · the final changed object (shown) · the tests and checks with outputs · old vs new · performance · findings · Share with Claude.
  - **Analysis:** the question · the queries behind the answer · key results and charts · findings (Confirmed / Not verified).
- Drop dead ends, superseded versions, side questions, anything discussed but unused.
- Keep the prerequisite notebook only if the final tests still need the helpers; else suggest its clean-up cell.
- Ask: keep the working notebooks — Archive as `<topic>-work-<date>.ipynb` (Recommended) · Delete; and commit the final notebook? Yes · No (Recommended — folder is git-ignored).

## 10. Screenshots (only when asked)
Charts saved as PNG and key tables rendered to images in `outputs/` (masked if sensitive). Jupyter: export the run notebook to HTML and screenshot it. Snowflake/Databricks: ask the user to export or screenshot the run notebook.

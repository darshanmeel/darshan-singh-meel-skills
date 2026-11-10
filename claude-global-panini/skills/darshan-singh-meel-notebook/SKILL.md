---
name: darshan-singh-meel-notebook
description: Notebook-first data work — every query against data (checks, analysis, metadata) is written into a notebook cell with a markdown note on what it does and what to look for, then run there with its output kept. Use when developing a dbt model, stored procedure, or SQL, when analysing data, or any time data or metadata needs querying — Snowflake, Databricks, or Jupyter. Claude only ever executes read-only SELECT cells; all DDL/DML/DCL goes in separate notebooks the user runs.
---

# Notebook
Every data/metadata query → a notebook cell, never direct. Notebook = the record (rerun, review, copy). CLAUDE.md + data-platform apply.

## 1. Setup — one prompt
| Header | Question | Options |
|---|---|---|
| Notebook | New or continue? | New `<topic>` (rec for new model/procedure/analysis) · Continue `<current>` · Other name |
| Platform | Detected `<…>` | Snowflake Notebook · Databricks · Jupyter (detected = rec) |
| Metadata | Who runs metadata cells (no data)? | Claude · Me (no rec) |
| Data | Who runs data cells? | Me · Claude, read-only (no rec) |
- Claude runs → confirm once: "OK to run read-only cells on `<account>` as `<role>`?" No answer → user runs all.
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
- `/analysis/` → `.gitignore` on first create.
- ≤50 cells per notebook (incl. markdown). Near limit → ask: `<topic>-work-2` (rec) · prepare final · keep going.
- Formats: Snowflake `.ipynb` · Databricks `.py` (`# COMMAND ----------`) or `.ipynb` · Jupyter `.ipynb`.

## 3. Cells
- Each step: markdown (what it does · what to look for) → query → output kept.
- Layout auto (say which): A — queries in cells (simple SQL) · B — `sql/NN_name.sql` read by cells (procedures/dbt; edit file, rerun cell).
- Cell 1 tag `setup`: connector/profile params (role, warehouse, schema); no SQL, no secrets.

## 4. Claude executes read-only only
- Allowed: SELECT, WITH…SELECT, SHOW, DESCRIBE, EXPLAIN, catalog selects.
- Never, even if asked: INSERT, UPDATE, DELETE, MERGE, COPY INTO, TRUNCATE, CREATE (OR REPLACE), ALTER, DROP, GRANT, REVOKE, CALL, EXECUTE IMMEDIATE, USE, dbt run/build/seed/snapshot, dataframe writes, shell cells.
- Jupyter: `python scripts/run_cells.py <notebook> <cells>` — refuses writes, saves outputs. Snowflake/Databricks native: their CLI only if set up and confirmed; else user runs.
- No queries outside notebook cells, in any skill.

## 5. User-only notebooks
- **prerequisite_ddl** (only if helpers needed): cell 1 warning "User only, before work notebook; Claude never runs it" + target · each cell: what/why/how to drop → idempotent statement · last: SELECT status → `PREREQUISITES OK — all cells ran` · commented clean-up cell. Claude: "Run it once, all cells, tell me." Work notebook verifies helpers first; missing → say which cells, stop.
- **changes**: same warning · each cell: what changes + undo → statement. After user runs → Claude adds SELECT checks to work.
- Order: prerequisites → checks → changes → checks → final.

## 6. Sensitive data
- Metadata first (runner per setup): tables, columns, types + DB sensitivity info — Snowflake `TAG_REFERENCES`, `POLICY_REFERENCES` · Unity Catalog `column_tags`, `column_masks`, `row_filters` · LF-tags / Glue classifications · Purview / `sys.sensitivity_classifications` · + name/type guesses (email, phone, name, address, dob, IDs, card/account, IP, free text). Never auto-classify (samples data).
- Second prompt: list each sensitive column + source → "Correct? Add/remove." + "Results to the model?" Summaries only (rec if any sensitive) · Yes, nothing sensitive (rec if none) · No, I'll describe. Save `pii.json` (+ graph model); never re-ask.
- None sensitive → normal rules. Sensitive (those tables only): no `SELECT *`; explicit columns; PII dropped or masked (`SHA2(email)`, `LEFT(name,1)||'***'`, dob → year); counts, aggregates, verdicts; `sql/<table>_safe.sql` helper.
- Summaries only → Claude reads verdicts, profiles, Share with Claude cell only. User runs → ask for output only if needed next, name it (prefer Share cell), "only if fine to send".

## 7. Query rules
- Rows → `LIMIT 1000`. `ORDER BY` only for grouped results (by measure) and checks (worst first); none on plain previews unless asked.
- Checks → verdicts: `duplicates on order_id: 0 → PASS`.
- Grain in markdown · prunable filters · small warehouse · params in setup cell.

## 8. Sections (keep what applies)
Setup · Metadata/PII · Inputs · Run/preview · Checks · Old vs new · Analysis · Performance (runtime, rows, bytes, pruning, query ID) · Findings · **Share with Claude** (last, always: name, cells, role/schema, verdicts, counts/profiles without sensitive values, performance, errors, PII handling).

## 9. Prepare final
- `<topic>-final.ipynb`: dev → purpose + Does/Doesn't, setup, final changed object, tests/checks with outputs, old vs new, performance, findings, Share cell · analysis → question, queries behind the answer, key results/charts, findings (Confirmed/Not verified).
- Drop dead ends, superseded versions, side questions. Keep prerequisite notebook only if final tests need it, else suggest clean-up.
- Ask: work notebooks → Archive `<topic>-work-<date>` (rec) · Delete; commit final? Yes · No (rec).

## 10. Screenshots (only if asked)
PNG charts + table images in `outputs/` (masked if sensitive). Jupyter → HTML export + screenshot. Snowflake/Databricks → user exports.

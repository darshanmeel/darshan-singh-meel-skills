---
name: darshan-singh-meel-databricks-review
description: Strict reviewer for Databricks work made with darshan-singh-meel-databricks - answers, notebooks, .sql files, audit-type apps, dashboards and dbt models or projects on system tables. Re-derives every answer independently, checks every system table, column, function and value exists (references, then official docs), join keys and grain (double counting, SCD and entity fan-out, workspace-scoped ids), time windows against latency and retention, units and money (DBU vs list USD, effective list price, corrections netted, unpriced kept), empty-is-not-zero handling, read-only statements, notebook structure (00_connection first, a markdown note before every query), secrets and people's data. Runs check_queries.py. Writes reviews/databricks-review-<date>.md with a verdict and Must / Should / Other findings (what, why, fix). Reviews; fixes only when asked. Triggers - "review this Databricks query", "check my system tables notebook", "is this cost number right", "review the audit app checks", "verify this answer".
context: fork
argument-hint: [analysis/<topic> | file | "answer text"]
---

# Databricks review

Find what makes a Databricks answer wrong or unsafe: a column that does not exist, a join that double-counts, a window the table cannot cover, a DBU called a dollar, a statement that writes. CLAUDE.md applies. Loads `darshan-singh-meel-databricks` for its references and script (`<db skill dir>` below), and `darshan-singh-meel-notebook` rules for notebooks; never copies their text.

## Rules
- **Independent.** Before reading the artefact's explanation, write down from the question alone which tables, keys, grain, window and caveats a correct answer needs (`<db skill dir>/references/` catalogue entry if one fits). Then compare.
- **Every fact checked:** table, column, struct field, function and enum value → `<db skill dir>/references/system-tables.md` and the topic file; not there → the official docs page (docs.databricks.com only, no code or names in searches); not found → Should "unverified: check: <page>", Must when the answer depends on it.
- **No execution by default.** Never runs queries; with arguments saying "run" and the notebook skill's confirm already given, only read-only cells through its runner. Never reads data rows or saved outputs on sensitive tables; judges from code and the Shareable summary.
- **Never opens secret files** (CLAUDE.md list). A secret value found in the artefact → Must, quoted as `<redacted>`.
- **Evidence per finding:** file and cell or line, the quoted SQL, and the corrected SQL or the docs page. No evidence → a question under "Not checked".
- **Severity:** Must = wrong number or answer, writes or could write, leaks a secret or people's data, misses a table the answer depends on. Should = misleading caveat, missing note, fragile but currently right. Other = style.
- **Review, not fix.** Fixes are proposed in the report; files change only when asked, then fix, rerun the script, add "Fixed" per finding.
- **Brief, not gentle.** No praise, no summary of the artefact.

## Process (fixed)
1. **Scope** — `$ARGUMENTS`: a folder, notebook, .sql file, app or dbt path, or pasted answer text; none → the newest `analysis/*/`. Note the question each artefact answers (title, first markdown cell, header `what:`).
2. **Script** — `python <db skill dir>/scripts/check_queries.py <path>` for notebooks and .sql; every FAIL is a Must candidate. Apps and dbt: run it on their `.sql` files where headers apply; else skip and say so.
3. **Re-derive** — per question, the expected tables, keys, grain, window, units and caveats (Rules, first bullet); then each query's own.
4. **Checklist** — areas 1–15 of `references/checklist.md`, query by query.
5. **Numbers** — any stated figure: recompute from the shown rows or synthetic values (sums, shares, deltas, percent); a figure with no query behind it → Must.
6. **Report** — `reviews/databricks-review-<YYYY-MM-DD-HHMM>.md` from `references/format.md` (name taken → append `-<topic>`); first `reviews/` → add `/reviews/` plus a one-line comment to `.gitignore`. Reply: verdict, counts, the Must lines, report path.
7. **Self-check** — the reply ends with the CLAUDE.md Self-check, logged with `python ~/.claude/hooks/log-work.py --skill darshan-singh-meel-databricks-review …`.

## Specific tests
- **Fan-out test:** for each join, name the key on both sides and whether it is unique there (SCD latest row? one entity per endpoint? one price row per SKU and time?). Not unique and no dedup → Must.
- **Workspace test:** every join or group on job, cluster, warehouse, pipeline, endpoint or task ids carries `workspace_id`.
- **Window test:** window start vs table retention, window end vs latency and today, previous-period comparisons with 2 × window of history; UTC stated where days matter.
- **Money test:** `pricing.effective_list.default` (not `default`), the price-window condition with the `price_end_time IS NULL` branch, currency and unit matched, all `record_type`s summed, unpriced quantity kept, label "list-price estimate".
- **Empty test:** each source that might be invisible (Preview tables, serving, classification, attributed usage) has a probe or a stated "not visible ≠ zero".
- **Scope test:** classic vs serverless vs warehouse coverage of the table matches the claim (node timeline, clusters, query history, attributed usage).
- **Read-only test:** every statement SELECT / WITH / SHOW / DESCRIBE / EXPLAIN; fixes only in a user-run changes notebook or `changes/`; app principal has only USE and SELECT grants plus CAN USE.
- **Voice test:** notebook notes and findings read as the engineer's own (CLAUDE.md "Author voice"); a leak → Should.

## References
| File | Read when |
|---|---|
| `references/checklist.md` | always: areas 1–15, what to check, typical findings |
| `references/format.md` | step 6: report format |
| `<db skill dir>/references/*.md` | facts, catalogue entries, pitfalls for the artefact's topic |

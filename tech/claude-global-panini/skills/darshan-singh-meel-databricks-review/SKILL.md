---
name: darshan-singh-meel-databricks-review
description: Strict reviewer for Databricks work made with darshan-singh-meel-databricks - answers, notebooks, .sql files, audit-type apps, dashboards and dbt models or projects on system tables. Re-derives every answer independently, checks every system table, column, function and value exists (references, then official docs), join keys and grain (double counting, SCD and entity fan-out, workspace-scoped ids), time windows against latency and retention, units and money (DBU vs list USD, effective list price, corrections netted, unpriced kept), empty-is-not-zero handling, read-only statements, notebook structure (00_connection first, a markdown note before every query), secrets and people's data. Runs check_queries.py. Writes reviews/databricks-review-<date>.md with a verdict and Must / Should / Other findings (what, why, fix). Reviews; fixes only when asked. Triggers - "review this Databricks query", "check my system tables notebook", "is this cost number right", "review the audit app checks", "verify this answer".
context: fork
argument-hint: [analysis/<topic> | file | "answer text"]
---

# Databricks review
Find what makes a Databricks answer wrong or unsafe: nonexistent column · double-counting join · window the table can't cover · DBU called dollar · statement that writes. CLAUDE.md applies. Loads `darshan-singh-meel-databricks` for references + script (`<db skill dir>`), `darshan-singh-meel-notebook` rules for notebooks; never copies their text.

## Rules
- **Independent:** before reading the artefact's explanation → write from the question alone the tables · keys · grain · window · caveats a correct answer needs (`<db skill dir>/references/` catalogue entry if one fits) → then compare.
- **Every fact checked:** table · column · struct field · function · enum value → `<db skill dir>/references/system-tables.md` + topic file → else official docs (docs.databricks.com only, no code or names in searches) → not found: Should "unverified: check: <page>"; Must if the answer depends on it.
- **No execution by default:** never runs queries. Arguments say "run" + notebook skill's confirm given → only read-only cells via its runner. Never reads data rows or saved outputs of sensitive tables; judges from code + Shareable summary.
- **Never opens secret files** (CLAUDE.md list). Secret value in the artefact → Must, quoted `<redacted>`.
- **Evidence per finding:** file + cell/line · quoted SQL · corrected SQL or docs page. No evidence → question under "Not checked".
- **Severity:**
  - Must = wrong number/answer · writes or could write · leaks secret or people's data · misses a table the answer depends on.
  - Should = misleading caveat · missing note · fragile but currently right.
  - Other = style.
- **Review, not fix:** fixes proposed in the report; files change only when asked → then fix → rerun script → add "Fixed" per finding.
- **Brief, not gentle:** no praise, no artefact summary.

## Process (fixed)
1. **Scope** — `$ARGUMENTS`: folder · notebook · .sql · app/dbt path · pasted answer text; none → newest `analysis/*/`. Note the question each artefact answers (title · first markdown cell · header `what:`).
2. **Script** — `python <db skill dir>/scripts/check_queries.py <path>` for notebooks, .sql; every FAIL = Must candidate. Apps, dbt: run on their `.sql` where headers apply; else skip, say so.
3. **Re-derive** — per question: expected tables · keys · grain · window · units · caveats (Rules, 1st bullet) → then each query's own.
4. **Checklist** — areas 1–15 of `references/checklist.md`, query by query.
5. **Numbers** — each stated figure: recompute from shown rows or synthetic values (sums · shares · deltas · percent); figure with no query behind it → Must.
6. **Report** — `reviews/databricks-review-<YYYY-MM-DD-HHMM>.md` from `references/format.md` (name taken → append `-<topic>`); first `reviews/` → add `/reviews/` + one-line comment to `.gitignore`. Reply: verdict · counts · Must lines · report path.
7. **Self-check** — reply ends with CLAUDE.md Self-check, logged `python ~/.claude/hooks/log-work.py --skill darshan-singh-meel-databricks-review …`.

## Specific tests
- **Fan-out:** each join → key on both sides, unique there? (SCD latest row? one entity per endpoint? one price row per SKU and time?). Not unique, no dedup → Must.
- **Workspace:** every join/group on job · cluster · warehouse · pipeline · endpoint · task ids carries `workspace_id`.
- **Window:** window start vs table retention · window end vs latency and today · previous-period comparisons need 2 × window of history · UTC stated where days matter.
- **Money:** `pricing.effective_list.default` (not `default`) · price-window condition with the `price_end_time IS NULL` branch · currency, unit matched · all `record_type`s summed · unpriced quantity kept · label "list-price estimate".
- **Empty:** each possibly invisible source (Preview tables · serving · classification · attributed usage) has a probe or stated "not visible ≠ zero".
- **Scope:** classic vs serverless vs warehouse coverage of the table matches the claim (node timeline · clusters · query history · attributed usage).
- **Read-only:** every statement SELECT · WITH · SHOW · DESCRIBE · EXPLAIN; fixes only in user-run changes notebook or `changes/`; app principal only USE + SELECT grants + CAN USE.
- **Voice:** notebook notes and findings read as the engineer's own (CLAUDE.md "Author voice"); leak → Should.

## References
| File | Read when |
|---|---|
| `references/checklist.md` | always: areas 1–15 · what to check · typical findings |
| `references/format.md` | step 6: report format |
| `<db skill dir>/references/*.md` | facts · catalogue entries · pitfalls for the artefact's topic |

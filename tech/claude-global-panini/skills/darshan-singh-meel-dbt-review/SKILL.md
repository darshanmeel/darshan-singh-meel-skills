---
name: darshan-singh-meel-dbt-review
description: Reviewer for dbt work and answers made with darshan-singh-meel-dbt - models, YAML, tests, macros, snapshots, analysis notebooks, SQL files, answers and audit-type apps on dbt. Re-derives every answer independently; checks refs and sources, grain and unique_key, incremental logic (is_incremental filter, lookback, full-refresh parity, on_schema_change, strategy fits the adapter), tests and contracts, every system view, column and function against the dbt skill's references and official docs, join keys and fan-out, time windows vs latency and retention, credits and currency, read-only queries, notebook structure (00_connection first, markdown before every query), secrets and machine paths; runs the dbt skill's check scripts. Writes reviews/dbt-review-<YYYY-MM-DD-HHMM>.md with verdict and Must / Should / Other (what, why, fix). Reviews; fixes only when asked. Triggers - "review my dbt model", "check this incremental", "review the dbt notebook", "is this dbt answer right", "review the dbt project changes".
argument-hint: [path to models, notebook folder, SQL files or answer]
---

# dbt review
Find what makes a dbt change/answer wrong, unsafe, misleading: wrong grain · lost or duplicated rows · non-existent view/column · window the data cannot cover · money summed wrong · query that writes · secret in a file. CLAUDE.md · `darshan-singh-meel-data-platform` apply. Loads `darshan-singh-meel-dbt` for its references, scripts (`<dbt skill>`) — never copies them.

## Setup — one prompt (skip what the arguments say)
- Scope: what to review? Changed files vs main (rec) · A folder or files I name · The last answer in this session.
- Platform: detected `<adapter>` → Snowflake · Databricks · Both.
- Docs: verify facts not in the dbt skill's references? Yes, official docs only (rec) · No, references only.

## Process (fixed)
1. **Inventory by script:** `git diff --stat` or named paths · `python <dbt skill>/scripts/dbt_inventory.py target/manifest.json health` if a manifest exists · `python <dbt skill>/scripts/check_queries.py analysis/<topic>` per analysis folder (sees only SQL written in the cells → read every code cell too). Counts into the report.
2. **Re-derive first, then compare:** per question answered → write the answer yourself from the dbt skill's references (docs if allowed) before reading the author's; per model → state the grain and expected result of an incremental run with late and duplicate rows. Differences = findings.
3. **Check every area** in `references/checklist.md`; each finding needs evidence (file:line · quoted text · script output · doc page).
4. **Never run** anything that connects (dbt `compile`/`run`/`build`/`test`/`show`/…, warehouse queries). Check needs data → "Not checked" + the read-only query the user can run (in their chosen delivery).
5. **Write** `reviews/dbt-review-<YYYY-MM-DD-HHMM>.md` from `references/templates/review-skeleton.md` (example `references/examples/review-cost-notebook.md`); first creation → add `/reviews/` to `.gitignore`.
6. **Reply:** verdict · Must count · report path → then CLAUDE.md endings.

## Severity
- **Must:** wrong numbers/rows (fan-out · lost late rows · wrong unique_key · money doubled · window beyond retention) · non-existent view/column/function · write in an analysis query · secret or machine path · destructive config (`full_refresh` on a snapshot-like history table · `sync_all_columns` dropping used columns) · "not assessed" shown as zero.
- **Should:** missing PK test or contract on a public model · no lookback · unclear grain · no markdown before a query · unverified fact without `check:` · cost of the query itself too high (no window, no pruning).
- **Other:** naming · docs · small simplifications.

## Rules
- **Independent:** trust no result, count or claim in the reviewed work → re-derive or "Not checked".
- **Facts:** view, column, function, latency, retention names from the dbt skill's references; not there → official docs (docs.getdbt.com, docs.snowflake.com, docs.databricks.com) if allowed, else "unverified — check: <page>".
- **Never open secret files** (CLAUDE.md list, `profiles.yml`) or data (`target/run/` · stored test failures · seeds with personal data · notebook outputs on sensitive tables). Secret found → path + rule, value `<redacted>`.
- **Review, not fix.** Fixes go in the report; files change only when asked → then "Fixed" line per finding + rerun step 1.
- **Brief, not gentle:** no praise section · no summary of the work · no taste-only findings.
- Report, replies: relative paths only.

# Review checklist

Areas 1-10 for every query; 11 for apps; 12 for dbt models. Each item names the failure it catches. Rules and facts live in the snowflake skill's references (`account-usage-map.md`, `cost.md` and the topic files); this list only says what to check.

## 1. Question and answer
- The query answers the question asked, not a nearby one (spend vs usage, readers vs writers, declared dependencies vs real pipelines).
- The stated conclusion follows from the shown result; every number in the text traces to an output and recomputes.
- `confirmed` vs `not verified` is honest: a claim about a job, user or cause needs a query that shows it.

## 2. Names exist
- Every view, column, table function and SHOW column is in the references or on its docs page, with the right schema (AU vs OU vs IS vs DSU).
- Each column belongs to the view it is read from: check `view.column` pairs, not bare names (`CREDITS_USED_COMPUTE` is on the metering views, not on `QUERY_ATTRIBUTION_HISTORY`).
- Renamed or deprecated sources: `SEARCH_OPTIMIZATION_HISTORY.TABLE_ID` (now `BASE_TABLE_ID`), `TABLE_STORAGE_METRICS.TABLE_ID` (it is `ID`), old Cortex views, `REPLICATION_USAGE_HISTORY`, `EVENT_USAGE_HISTORY`.
- Views that do not exist: `AU.STREAMS`, `AU.DYNAMIC_TABLES`, `AU.EXTERNAL_TABLES`, `AU.ICEBERG_TABLES`, `AU.AUTHENTICATION_POLICIES`, any budgets view.
- `GET_QUERY_OPERATOR_STATS` keys match the page (`equality_join_condition`, `pruning:partitions_scanned`, `spilling:bytes_spilled_remote_storage`, `overall_percentage`).

## 3. Grain and joins
- The grain of each source is stated and matched: hourly metering vs daily metering, per query vs per query-hour (`QUERY_METERING_HISTORY`), 5-minute load ratios, per-version object views.
- Each side is aggregated to the join key before joining; no join repeats rows that are then summed (attribution x query history without `GROUP BY query_id`, a rate table with several rows per key, several tags per object, double `FLATTEN` counted per row).
- IDs, not names, for objects that can be dropped and recreated; `objectDomain` with `objectId` in access history.
- Live objects filtered: `DELETED IS NULL` / `DELETED_ON IS NULL`; the six-condition live filter on `TABLE_STORAGE_METRICS`; revoked grants excluded.
- Outer joins where a missing side must not drop rows (attribution without a query history row, untagged warehouses).

## 4. Time
- One window with an exclusive end; the filter is on the view's own time column (and is pruning-friendly).
- The window fits retention (365 days AU; 7 / 14 days / 6 months for IS functions; 14 days for operator stats; 90 days for stage details) - asking for more silently returns less.
- Latency respected: the newest hours excluded or marked partial (45 min to 72 h by view; attribution 8 h; OU billing 72 h).
- Time zone: `TIMEZONE = 'UTC'` set when daily `USAGE_DATE` meets hourly `TIMESTAMP_LTZ` columns; set as a connection parameter, not `ALTER SESSION` in a Claude-run cell.
- Zero days filled (spine) where averages, medians or spike baselines are computed.
- Comparisons use equal windows; data start dates respected (attribution mid-Aug 2024; Cortex views 2026).

## 5. Units and money
- Credits, bytes, TB and currency in separate columns; no sum across units.
- The bill = `METERING_DAILY_HISTORY.CREDITS_BILLED`; hourly `CREDITS_USED` presented as spend is a Must. Warehouse figures adjust cloud services by the day's billed share.
- Attribution never presented as the warehouse total; idle = compute - attributed only for hours past the lag and non-NULL attribution.
- Per-feature serverless views split totals and are not added to them; old and new Cortex views not added together; `IS_COMPLETED` filtered.
- Price: one rate per key, joined once or pasted as a literal; its source stated; unknown price = NULL, never 0; AI and storage at their own rates; currency only from OU.
- VARCHAR and VARIANT numbers cast before `SUM` (`TRY_TO_DOUBLE`); bytes converted with `POWER(1024, n)` consistently.
- Spend, change, waste and saving never summed together; waste counted only on flagged rows.

## 6. Visibility and edition
- Role-filtered sources (SHOW, `RESOURCE_MONITORS`, `COPY_HISTORY`, `PIPES`, `TAG_REFERENCES`, `POLICY_REFERENCES`, `COMPLETE_TASK_GRAPHS`, ...) have a probe or a cross-check; an empty result is reported as "not visible", not as none.
- Enterprise-only views on a Standard account are flagged as "not assessed", not as clean.
- `POLICY_REFERENCES` not used for authentication, password or session policies.
- Privileges named for each source (SNOWFLAKE database role, `MONITOR` for operator stats, `ORGANIZATION_BILLING_VIEWER`).

## 7. Read-only and execution
- Cells and files meant for Claude: only `SELECT`, `WITH`, `SHOW`, `DESCRIBE`, `EXPLAIN`. `SYSTEM$`, `CALL`, `ALTER`, `USE`, DDL and DML only in `NN_user_*` notebooks or files, which start with the manual-run warning.
- Detail queries carry `LIMIT`; heavy scans filter time first; the warehouse is small.

## 8. Notebook and file structure
- `00_connection.ipynb` first, connection only (environment variable names, session parameters, one test SELECT); every question notebook's first code cell equals it.
- A markdown note before every query with What / Reads / Look for; one query per cell; a Findings cell at the end in the engineer's voice (no chat traces).
- SQL files: a header per statement; parameters in a `p` CTE; statements end with `;`.
- On-screen answers: each query has its one-line note; at most 4 queries.

## 9. Secrets and personal data
- No passwords, tokens, keys or connection strings in any cell, file or output; only environment variable names.
- No `QUERY_TEXT`, `*_DEFINITION`, `POLICY_BODY`, `BIND_VALUES`, `LOGIN_DETAILS` selected by default.
- User names, emails and IPs aggregated or masked where results go to the model or a shared report; error messages treated as possibly holding data values.
- No machine paths; paths relative to the repo root.

## 10. Reading guidance
- The note or answer says which columns answer the question, their units, the grain of a row, normal vs bad values, and the caveats that apply (latency, retention, visibility).
- The next query offered actually narrows the open point.

## 11. Audit-type apps
- One read-only guard before every execute (single statement, comments stripped, literals blanked), with tests for hidden writes.
- A visibility probe before the run; per-check outcome `ok` / `empty` / `NOT_ASSESSED` with a reason / `failed` with a cause; "cannot see" never empty.
- Fallbacks state their shorter windows and partial coverage; `MONITOR USAGE` gated; IS `QUERY_HISTORY` read in slices with failures noted.
- One as-of date and one price per run, recorded in the manifest and shown in the UI; OU checks settle the billing lag.
- Check headers complete (reads, requires, params, caveats, empty_if, money); manifest generated from them; lint for hard-coded windows and status labels.
- Shared SQL fragments for money and liveness; a test that totals agree across checks.
- Local cache loaded atomically; the data folder git-ignored; deploy refuses fake data; Streamlit in Snowflake uses a deploy role separate from the read-only role.
- Tests run every check against a fake account and cover the scenario databases (no org access, limited role, Standard edition).

## 12. dbt models over ACCOUNT_USAGE
- dbt models that read `SNOWFLAKE.ACCOUNT_USAGE` / `ORGANIZATION_USAGE`: areas 2-6; everything else → `darshan-singh-meel-dbt-review`.

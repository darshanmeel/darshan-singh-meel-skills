# Checklist

Walk every area per query or artefact. Typical findings in italics are examples, not a limit.

| # | Area | Check | Typical Must |
|---|---|---|---|
| 1 | Answer | Does the result answer the asked question, at the asked level (account, workspace, object)? | *answers "cost by SKU" when asked "why did cost jump"* |
| 2 | Names exist | Every table, column, struct field, map key, function, enum value against the db skill references (columns appendix in `system-tables.md`, then the topic file), then docs | *`usage_metadata.job_run` or `usage_metadata.sql_warehouse_id` (do not exist); `CANCELED` on job runs (jobs use `CANCELLED`); `table_catalog` on `column_masks` (it uses `catalog_name`)* |
| 3 | Joins and keys | Keys on both sides, unique on the lookup side, `workspace_id` included | *jobs joined without latest-row filter → cost × versions* |
| 4 | Grain | Stated grain equals the GROUP BY; no mixing of overlapping cuts (tags, resource types) | *summing workspace rows and job rows together* |
| 5 | SCD handling | Latest row per key then `delete_time`; as-of joins where history matters | *`delete_time IS NULL` inside the ROW_NUMBER filter → deleted objects reappear as live* |
| 6 | Time window | Time column filtered (partition columns), window ≤ retention, end before today or partial marked, UTC, read-back for runs that started earlier | *90-day trend on a table with less history; today's billing counted as full* |
| 7 | Money and units | Effective list price, price window with `IS NULL` branch, unit and currency matched, corrections netted, unpriced kept, DBU never called dollars, ESTIMATED_DBU labelled | *`pricing.default` used; ORIGINAL rows only; dollars summed across currencies* |
| 8 | Run and event semantics | Final slice for job outcomes, last attempt for final state, 0 = not reported on run-level phase columns, `period_start_time = period_end_time` = never started | *average duration from run-level columns of multi-task jobs (all 0)* |
| 9 | Coverage and visibility | Probe or statement for invisible sources; serverless/classic/warehouse scope; region; privilege-aware views called "what this principal sees" | *"no PII found" from an empty `data_classification.results`* |
| 10 | Read-only | Only SELECT / WITH / SHOW / DESCRIBE / EXPLAIN in queries; fixes in user-run files; app principal minimal | *OPTIMIZE in a question notebook; app service principal with MODIFY* |
| 11 | Structure | `00_connection.ipynb` first, connection by env-var names, setup cell per notebook, markdown note (Does / Reads / Look for) before every query, parameters not string formatting, Findings + Shareable summary; .sql header `what / views / joins / grain / look for / params` | *f-string building SQL from a user value* |
| 12 | Secrets and people's data | No tokens, passwords, hosts with credentials; every column in the people's-data list of `system-tables.md` (identities such as `executed_by`, `created_by`, `run_as`, `owned_by`, `user_identity.email`, `requester`; `statement_text`, `error_message`, ON-clause or other text; IPs; `notebook_path`) aggregated or keyed-hashed with a bound `:k`, never plain `sha2(col)`; `data_classification.results.samples` never selected | *raw `statement_text` or `executed_by` in outputs; `samples` selected* |
| 13 | Query cost | Partition or time filter, no `SELECT *` on wide tables, LIMIT on detail rows, one statement per source where a missing table would fail a UNION | *full scan of `query.history` without a date filter* |
| 14 | Apps and dbt | Apps: read-only principal, status enum with NOT_ASSESSED + reason, manifest of source visibility, money basis named, cache git-ignored, tests with synthetic fixtures. dbt: sources with freshness, latest-row models for SCD sources, `unique`/`not_null` on the grain, incremental with look-back for late and corrected rows | *incremental billing model on `usage_date > max()` without look-back drops restatements* |
| 15 | Runs as written | Python SQL strings raw (`q(r"""…""")`) when they hold a backslash; no select-list alias reused in another expression under `GROUP BY ALL` (`LATERAL_COLUMN_ALIAS_IN_GROUP_BY`); `delete_time` / `table_dropped_time` filters after the latest-row QUALIFY, not in WHERE; `information_schema.views.view_definition` NULL for views the caller does not own (a text search over it needs the NULL count beside it); one statement per cell | *regex `'\\b…'` in a non-raw string matches nothing; view search returning 0 read as "no views"* |

## Verdict
- **Fail** — any Must.
- **Pass with fixes** — Should only.
- **Pass** — Other only or nothing.

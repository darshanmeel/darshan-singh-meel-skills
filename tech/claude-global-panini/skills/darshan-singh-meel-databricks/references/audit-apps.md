# Building audit-type apps on system tables

Read-only apps, dashboards or dbt projects that turn `system.*` into checks and numbers. Design rules first, then the build options.

## Principles
- **Read-only principal:** a service principal with `USE CATALOG` on `system`, `USE SCHEMA` + `SELECT` on the needed schemas, `CAN USE` on one SQL warehouse; nothing else. The app prints the grant SQL for an admin; it never runs grants.
  ```sql
  GRANT USE CATALOG ON CATALOG system TO `<service principal application id>`;
  GRANT USE SCHEMA, SELECT ON SCHEMA system.billing TO `<service principal application id>`;
  ```
- **One money basis:** effective list price; columns named `*_usd_list`; discounts only as a separate what-if; never called "actual" or "invoice". Reconciliation check: every cut sums back to the billed total within a cent.
- **Status per check:** `OK` / `WARN` / `CRITICAL` / `NOT_ASSESSED` + `not_assessed_reason`. NOT_ASSESSED is never a pass and never a zero.
- **Visibility is data:** classify every failed source read — `schema_not_enabled`, `table_not_found`, `no_grant`, `timeout`, `too_much_data`, `unknown` — and record it per source in a run manifest, so the UI says "not visible" instead of "nothing found".
- **Honest windows:** as-of cutoff (exclude today, or mark today partial); `days_used = min(window, history)`, window shown partial when shorter; previous-period comparisons need 2 × window of history, else NOT_ASSESSED.
- **Materiality:** floors in dollars (scaled to the window) so tiny findings do not flag; thresholds in config with precedence `config[check] → config[_all] → header default`.
- **People's data:** identity masking on display (`<id or hash prefix> <first 2 chars>***`, keep an unmasked key or collisions merge people); optional row-level access by workspace or other columns; unknown user sees nothing.

## Check catalogue design
- One `.sql` file per check, one statement, read-only, with a header the app parses:
  ```
  -- query_id · title · domain · reads (system tables) · requires (grants, GA/Preview, scope)
  -- empty_if (schema_not_enabled, privilege_scoped, compute_scope_gap, ingestion_lag, retention_window, no_activity)
  -- params (:period_days, thresholds with defaults) · grain (one row = …) · read_this · healthy · investigate_if
  -- actions (free / config / spend) · next (related checks) · not_assessed_reasons · caveats · confidence (+ how to confirm on an account)
  ```
- A linter checks headers, params and that the body emits `status`; a test per check on synthetic fixtures; a corrections register for known defects in borrowed queries.
- Known defect patterns to test for: NULL + NULL falling through to OK; plain AVG diluted by zeros; 0 treated as a measurement; COUNT(DISTINCT x) inside GROUP BY x; row cap applied after a UNION cutting the summary rows; ordering that keeps the least important rows under a cap; fan-out from SCD or entity joins; mixing `pricing.default` and `effective_list`.

## Build options
| Option | Fits | Watch |
|---|---|---|
| AI/BI (Lakeview) dashboard on live `system.*` | quick, shared in the workspace | each viewer's or the publisher's credentials decide visibility; heavy queries rerun on every open |
| Scheduled snapshot: job copies needed system rows or check results into a schema, dashboards read it | stable numbers, cheap reads | job runs as a service principal; snapshot schema needs its own grants and retention |
| Export → local cache (parquet + DuckDB) → local web app | offline review, tests with fakes, no warehouse time per click | translate Databricks SQL to DuckDB (map access, regex, `dayofweek`, `date_sub`, intervals); open the DB read-only; cache holds account data → git-ignore it |
| Databricks App (Apps platform) | in-workspace UI with SSO | app runs as its own service principal (warehouse as an app resource) or on behalf of the user (check: Apps authorization page); a redeploy wipes local disk → reload data; a token stored in app config is readable by anyone who can read the app folder |
| dbt project over system tables or the snapshot | tested models, lineage, docs | sources with freshness on the time column; latest-row models for SCD tables; incremental by date with a look-back for late and corrected rows; grain tests (`unique`) on every model |

## Export and caching
- One statement per check per window; `LIMIT max_rows + 1` with a `truncated` flag; windows 7/30/90 reuse a longer run when history is shorter.
- Cache results with a manifest: per source `ok` / reason, row counts, cut-off time; the app reads the manifest to show freshness and gaps.
- Refresh as a separate subprocess with timeouts; only admins may trigger it when row-level access is on.

## Testing with fakes
- Fixture DDL generated from a `DESCRIBE` dump of the system tables (names and types only), so fixtures follow schema drift.
- Synthetic builders per scenario (idle warehouse, failing job, unpriced SKU, price change mid-window, restatement, SCD rename, multi-workspace, other cloud) with a fixed clock.
- A fake account with hand-worked answers ("warehouse W idles 42 minutes") checked end to end.
- Every check has a grain test and at least one deciding-case test; a coverage tool fails the build when a check has none.

## Deploy
- Asset Bundles or the CLI from CI; config in files, secrets in a secret scope or app resources — env-var names only in code.
- Dashboards as JSON in the repo, generated and tested to equal a rebuild.

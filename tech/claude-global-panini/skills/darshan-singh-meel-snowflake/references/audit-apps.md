# Building audit-type apps on Snowflake

For apps that read `SNOWFLAKE.ACCOUNT_USAGE` / `ORGANIZATION_USAGE` and show checks, costs or risks. The app reads; it never changes the account.

## Shape that works
```
check catalogue (one .sql per check, header fields)
  → export: visibility probe → run checks read-only → per-check outcome + rows → local files + manifest
  → loader: files → one local DuckDB file (atomic replace)
  → app: reads only the local file (no Snowflake call at view time)
```
- Separating export from viewing keeps the warehouse cost to one run, lets people without Snowflake access view results, and makes tests possible without an account.
- Hand-off option: an **export kit** (the SQL plus a small runner) that someone with access runs; results come back as files.

## Read-only, enforced in code
- One guard function before every `execute`: strip comments, blank string literals, refuse anything that is not a single `SELECT`, `WITH` or `SHOW` statement (no `;` left outside literals). Unit-test it with a `DROP` hidden after a comment and inside a string.
- A dedicated read-only role (user-run setup, below); the guard is the second line, the role is the guarantee.
- Session settings via connection parameters (`TIMEZONE = 'UTC'`, `QUERY_TAG = '<app>:<check>'`), not `ALTER SESSION`. The query tag lets the app measure its own cost (`cost.md` C6).
- Never select `QUERY_TEXT`, `VIEW_DEFINITION`, `*_DEFINITION`, `POLICY_BODY`, `BIND_VALUES`, `LOGIN_DETAILS` into results.
```sql
-- User-run setup (an admin runs this once; never the app)
CREATE ROLE IF NOT EXISTS AUDIT_READER;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE AUDIT_READER;   -- or the SNOWFLAKE.*_VIEWER database roles
GRANT USAGE ON WAREHOUSE AUDIT_XS_WH TO ROLE AUDIT_READER;              -- X-Small, auto_suspend 60
GRANT MONITOR ON WAREHOUSE <wh> TO ROLE AUDIT_READER;                   -- per warehouse, for operator stats and SHOW
-- optional, widens SHOW and fallbacks: GRANT MONITOR USAGE ON ACCOUNT TO ROLE AUDIT_READER;
-- org billing: GRANT DATABASE ROLE SNOWFLAKE.ORGANIZATION_BILLING_VIEWER TO ROLE AUDIT_READER;  (organization account)
```
check: grant-database-role (the exact org database role names available in the account).

## Check catalogue design
- One file per check: `<check_id>.sql`, a header of `-- field: value` lines, then one statement. Fields that pay off: `query_id`, `title`, `domain`, `reads` (every system view the SQL touches), `requires` (role, edition), `params` with defaults, `read_this` (one row = what), `healthy`, `investigate_if`, `actions`, `caveats` (latency, retention, visibility), `empty_if` (`role_cannot_see`, `edition_too_low`, `no_activity`), `money` (the one headline money column), `entity` (the key columns).
- Generate the manifest from the headers; a linter fails the build when `reads` misses a view used in the body, a window is hard-coded instead of `:period_days`, or a status label is outside the vocabulary.
- Shared SQL fragments (`cost lines`, `billed ratio`, `live tables`, `access events`) included by name, so every check computes money and liveness the same way; a test asserts that totals from different checks agree.
- Every row carries `status` (`OK`, `WARN`, `CRITICAL`, `NOT_ASSESSED`), a `reasons` text and `not_assessed_reason`. Thresholds are params, not literals.
- Placeholders filled once per run: `__AS_OF_DATE__` (one exclusive end date for every window), prices, account id. Windows: `>= DATEADD(day, -:period_days, __AS_OF_DATE__) AND < __AS_OF_DATE__`. OU checks end `:settle_days` (default 3) earlier for the 72 h billing lag.

## Visibility: "cannot see" is never "nothing found"
- Before the run, probe every source with `SELECT 1 FROM <view> LIMIT 0`, run each check's `SHOW` prerequisites, and compare warehouses that billed in `WAREHOUSE_METERING_HISTORY` with `SHOW WAREHOUSES`.
- Per check: edition too low → `NOT_ASSESSED edition_too_low`; source unreadable with a fallback → run the fallback; no fallback → `NOT_ASSESSED role_cannot_see`; fallback failed → `NOT_ASSESSED` again, never empty.
- Inside SQL, detect hidden objects from other evidence: task runs in `TASK_HISTORY` with no `TASKS`/`SHOW TASKS` row → a "(not visible to this role)" row; a warehouse with credits but no SHOW row → its monitor check reads NOT_ASSESSED.
- Classify errors by code and message: `timeout`, `edition_too_low`, `no_access` (codes 2003, 3001, 2043, "insufficient privileges"), `view_missing` ("does not exist"), else `failed`; keep the code and the first line of the message.

## Fallbacks when ACCOUNT_USAGE is not granted
- Rebuild a view from INFORMATION_SCHEMA table functions and SHOW ("shims") with the same columns, then run the check's own SQL against the shim. Windows shrink (`account-usage-map.md`): say so in the result ("last 7 days only").
- Per-database functions run once per database (`each: database`): a database that fails drops only its part; record "3 of 40 databases could not be read".
- Gates: metering and storage functions return no rows, not an error, without `MONITOR USAGE` → test it (a 3-day count > 0) and mark the check NOT_ASSESSED when missing. SHOW lists only objects the role holds a privilege on unless it has `MANAGE GRANTS`.
- `INFORMATION_SCHEMA.QUERY_HISTORY` returns at most 10,000 rows per call: read it in time slices (for example 28 slices of 6 h for 7 days), all async, and note slices that failed. A slice that hits the cap undercounts. check: query_history function (RESULT_LIMIT maximum).
- Seen in the field: one statement reading table-function rows through a CTE used twice aborted with an internal error; passing small intermediate results as literal `VALUES` avoided it.
- No equivalent exists for `ACCESS_HISTORY`, `QUERY_ATTRIBUTION_HISTORY`, `TAG_REFERENCES` (account-wide), `TABLE_STORAGE_METRICS`, `WAREHOUSE_EVENTS_HISTORY`, Cortex usage, OU views.
- Optional `sources:` setting to read the views from the customer's own copies; validate the identifiers (plain or double-quoted parts only) because they are spliced into SQL.

## Money in the app
- One price per run, resolved in order: user input → `RATE_SHEET_DAILY` → 90-day `USAGE_IN_CURRENCY_DAILY` average → configured list price → NULL (unpriced, never $0). Record the source and show it next to every $ figure.
- Paste the price as a literal into the SQL instead of joining a rate table.
- Separate money kinds (spend, change, waste, saving, balance, context); one headline column per check; waste and saving sum only over WARN and CRITICAL rows; total and tie-out rows excluded from sums; a discount what-if never applies to invoice-derived amounts.
- Rules for credits, cloud services, attribution and storage: `cost.md`.

## Local cache
- Export writes Parquet (or CSV) per check plus `manifest.json` (as-of, price sources, role, edition, per-check outcome and reason, row counts, durations). Load into one DuckDB file: write `<db>.tmp`, then `os.replace` so a failed load never leaves a half file.
- The app opens a configured path, else a pointer file, else the default; it shows the export's as-of and price source on every page.
- Results can hold user names and object names: keep the folder out of git (`data/`, `analysis/`), mask user names in shared views.

## Testing with a fake account
- A fake `SNOWFLAKE` database in DuckDB, built by code with a fixed seed and a fixed as-of: tables with the same names and columns as the system views and SHOW outputs.
- Transpile each check to DuckDB (sqlglot, Snowflake → DuckDB) and run every check in CI: compile errors, columns, status vocabulary, `NOT_ASSESSED` rows carry a reason.
- Money tests on the fake: totals agree across checks at 7, 30 and 90 days; the cloud services adjustment rule (compute 100, cloud services 15 → billed 105); a zero-usage day counts in a median.
- Scenario databases: full access, no org access, limited role (SHOW sees part), Standard edition detected and not detected.
- Keep the fakes honest: a script that dumps live column names and types (names and types only, from `INFORMATION_SCHEMA.COLUMNS` and `DESCRIBE RESULT` of each SHOW) and a test that compares them with the fake schema.
- Deploy refuses a database that still holds fake data (a marker such as an account id starting `FAKE`).

## Streamlit in Snowflake
- Ship the app plus the loaded DuckDB file to a stage; use a separate deploy role, never the read-only audit role; viewers need `USAGE` on the Streamlit object, database and schema.
- Warehouse runtime (packages from the Snowflake conda channel, no compute pool) vs container runtime (PyPI packages, compute pool): details and the React bridge in `darshan-singh-meel-streamlit-snowflake` and `darshan-singh-meel-streamlit-snowflake-react`.
- Inside Snowflake the app could query live with the viewer's or owner's rights; an exported file keeps cost and visibility predictable. Say which one the app does.

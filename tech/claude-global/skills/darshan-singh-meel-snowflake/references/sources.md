# Sources and verification status

Official pages only (`docs.snowflake.com`, `docs.getdbt.com`). Status: **read** = read on the page (September to November 2026) · **field** = seen on live accounts, not stated on a page · **check** = not confirmed; verify on the page named before relying on it.

## Pages used
| Fact in this skill | Page | Status |
|---|---|---|
| ACCOUNT_USAGE view list, columns, latency, retention, edition of the views in `account-usage-map.md` and the topic files | `https://docs.snowflake.com/en/sql-reference/account-usage` and each view's page under `/en/sql-reference/account-usage/<view>` | read |
| ORGANIZATION_USAGE billing views (`USAGE_IN_CURRENCY_DAILY`, `RATE_SHEET_DAILY`, `REMAINING_BALANCE_DAILY`, `METERING_DAILY_HISTORY`, `STORAGE_DAILY_HISTORY`, `ACCOUNTS`), 72 h lag, `IS_ADJUSTMENT`, legacy `USAGE_TYPE` | `https://docs.snowflake.com/en/sql-reference/organization-usage` and view pages | read |
| `METERING_DAILY_HISTORY.CREDITS_BILLED` and the cloud services adjustment (10% of daily warehouse compute) | `/en/sql-reference/account-usage/metering_daily_history`, `/en/user-guide/cost-understanding-compute` | read |
| `QUERY_ATTRIBUTION_HISTORY` exclusions (idle, about 100 ms queries, adaptive warehouses), 8 h lag | `/en/sql-reference/account-usage/query_attribution_history` | read |
| `CORTEX_AI_FUNCTIONS_USAGE_HISTORY` columns, `IS_COMPLETED`, data start dates; older Cortex views no longer updated | `/en/sql-reference/account-usage/cortex_ai_functions_usage_history` | read |
| `GET_QUERY_OPERATOR_STATS`: output columns, argument (literal, session variable or `LAST_QUERY_ID()`), completed queries of the past 14 days, `OPERATE` or `MONITOR` on the warehouse, Join / TableScan / Filter / Aggregate attributes, pruning and spilling statistics, execution time breakdown keys | `/en/sql-reference/functions/get_query_operator_stats` | read |
| `ACCESS_HISTORY` columns and JSON fields (`objectDomain`, `objectId`, `objectName`, `columns`, `baseSources`, `directSources`, `operationType`), Enterprise, 3 h, 365 days, what is not recorded, `joinObjects` | `/en/sql-reference/account-usage/access_history` | read |
| INFORMATION_SCHEMA table function history windows (7 days, 14 days, 6 months) | `/en/sql-reference/info-schema` | read |
| Persisted query results: 24 h, reset on reuse up to 31 days, reuse conditions, `USE_CACHED_RESULT` | `/en/user-guide/querying-persisted-results` | read |
| `QUERY_ATTRIBUTION_HISTORY.ROOT_QUERY_ID` / `ACCESS_HISTORY.ROOT_QUERY_ID` NULL for a query without a parent | `/en/sql-reference/account-usage/query_attribution_history`, `/en/sql-reference/account-usage/access_history` | read |
| `LOCK_WAIT_HISTORY.BLOCKER_QUERIES` keys; `STAGE_STORAGE_USAGE_DETAILS.STAGE_TYPE` values and latency; `QUERY_INSIGHTS` latency and retention; `SHARES` / `GRANTS_TO_SHARES` 3 h | each view's page; `/en/sql-reference/account-usage` | read |
| `GLOBALORGADMIN` role | `/en/user-guide/organization-administrators` | read |
| `WAREHOUSE_EVENTS_HISTORY` event names, reasons and states | `/en/sql-reference/account-usage/warehouse_events_history` | read |
| `GRANTS_TO_ROLES` columns and 2 h latency | `/en/sql-reference/account-usage/grants_to_roles` | read; role-to-role rows (`GRANTED_ON = 'ROLE'`, `PRIVILEGE = 'USAGE'`, `GRANTED_TO` `'ROLE'` or `'ACCOUNT ROLE'`): field |
| SHOW output and the `->>` pipe; `RESULT_SCAN` same user within 24 h | `/en/sql-reference/sql/show`, `/en/sql-reference/functions/result_scan` | read |
| Warehouse billing per second with a 60 s minimum; Gen1 credit rates doubling per size | `/en/user-guide/warehouses-overview`, Snowflake Service Consumption Table | read |

## Field knowledge (not on a page)
- Live accounts have billed AI under a service type other than `AI_SERVICES` (`AI_INFERENCE`). check: metering_daily_history.
- Error codes 2003, 3001, 2043 (access or missing object) and 630 (timeout). check: no official error code list.
- An internal error when one statement reads table-function rows through a CTE used twice; avoided with literal `VALUES`.

## Open `check:` items
- `account-usage-map.md`: role-to-role rows in `GRANTS_TO_ROLES`.
- `cost.md`: AI service type names; `DATA_TRANSFER` service type in `USAGE_IN_CURRENCY_DAILY`; dbt `query_tag` config (`https://docs.getdbt.com/reference/resource-configs/snowflake-configs`).
- `performance.md`: result-cache hit marker in `QUERY_HISTORY`; `QUERY_INSIGHTS` edition; `EXPLAIN` output fields.
- `joins-lineage.md`: WHERE-only columns of a SELECT in `base_objects_accessed`.
- `pipelines.md`: stream staleness rules; `SHOW TASKS` `last_suspended_reason`; `SHOW STREAMS` `stale` type; dynamic table lag definition; `SERVERLESS_ALERT_HISTORY`.
- `security.md`: `USERS.TYPE` values; `QUERY_TYPE` values for grant and user DDL; `GRANTS_TO_SHARES.SHARE_NAME` format; `GRANTS_TO_ROLES` role rows.
- `troubleshooting.md`: error code meanings; `STATEMENT_TIMEOUT_IN_SECONDS` default.
- `audit-apps.md`: org database role names for grants; `INFORMATION_SCHEMA.QUERY_HISTORY` `RESULT_LIMIT` maximum.
- Templates: `snowflake-connector-python` `private_key_file` connect parameter (`https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-api`).

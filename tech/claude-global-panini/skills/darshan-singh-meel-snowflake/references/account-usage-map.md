# Account usage map

The system views and commands, how they join, and what limits them. AU = `SNOWFLAKE.ACCOUNT_USAGE`, OU = `SNOWFLAKE.ORGANIZATION_USAGE`, IS = `<db>.INFORMATION_SCHEMA`, DSU = `SNOWFLAKE.DATA_SHARING_USAGE`. Pages: `sources.md`.

## Sources compared
| Source | History | Latency | Scope | Visibility |
|---|---|---|---|---|
| AU views | 365 days (asking for more returns fewer rows, no error) | 45 min to 12 h by view | whole account, dropped objects kept | `IMPORTED PRIVILEGES` on `SNOWFLAKE`, or the database roles below; some views role-filtered |
| OU views | billing views kept indefinitely (from Jun 2020); others 365 days | 2 h to 72 h | all accounts in the org | `ORGANIZATION_USAGE_VIEWER`, `ORGANIZATION_BILLING_VIEWER` (billing), `ORGANIZATION_ACCOUNTS_VIEWER`; most need the organization account; not for reseller customers |
| IS table functions | `QUERY_HISTORY`, `TASK_HISTORY`, `LOGIN_HISTORY`, `DYNAMIC_TABLE_REFRESH_HISTORY` 7 days · `COPY_HISTORY`, `PIPE_USAGE_HISTORY`, `SERVERLESS_TASK_HISTORY`, `AUTOMATIC_CLUSTERING_HISTORY`, `MATERIALIZED_VIEW_REFRESH_HISTORY`, `WAREHOUSE_LOAD_HISTORY` 14 days · `WAREHOUSE_METERING_HISTORY`, `DATABASE_STORAGE_USAGE_HISTORY` 6 months | none | one database (the IS's own) | what the current role can see; metering functions return nothing without `MONITOR USAGE` |
| `SHOW` | current state only | none | per command | objects the role holds a privilege on (`MANAGE GRANTS` sees all); max 10,000 rows; output columns lower case |
| DSU | 365 days | up to 2 days | listings, marketplace | provider or consumer account |

- **SNOWFLAKE database roles:** `USAGE_VIEWER` (metering, storage, warehouses) · `GOVERNANCE_VIEWER` (query and access history, policies, tag references, classification) · `OBJECT_VIEWER` (objects, dependencies, tags) · `SECURITY_VIEWER` (users, roles, grants, logins, network, secrets, Trust Center). Name the role the question needs.
- **Reading SHOW output in SQL:** `SHOW WAREHOUSES ->> SELECT "name", "size" FROM $1;` (pipe operator) or `RESULT_SCAN(LAST_QUERY_ID())` in the next statement; quote the lower-case names. `RESULT_SCAN` works for the same user within 24 h.

## Latency (end windows earlier, or mark the last hours partial)
| Latency | Views |
|---|---|
| 45 min | `QUERY_HISTORY`, `TASK_HISTORY`, `COMPLETE_TASK_GRAPHS` |
| 90 min | `QUERY_INSIGHTS`, `TABLES`, `COLUMNS`, `VIEWS`, `TABLE_STORAGE_METRICS`, `LOAD_HISTORY` |
| 2 h | security views (`USERS`, `ROLES`, `GRANTS_TO_ROLES`, `GRANTS_TO_USERS`, `LOGIN_HISTORY`, policies), `COPY_HISTORY` (up to 2 days when quiet), `STAGES`, `SCHEMATA`, `FUNCTIONS`, `DATA_TRANSFER_HISTORY` |
| 3 h | `SHARES`, `GRANTS_TO_SHARES`, metering (`METERING_*`, `WAREHOUSE_METERING_HISTORY`), `WAREHOUSE_LOAD_HISTORY`, `WAREHOUSE_EVENTS_HISTORY`, `ACCESS_HISTORY`, `OBJECT_DEPENDENCIES`, `DYNAMIC_TABLE_REFRESH_HISTORY`, `PIPE_USAGE_HISTORY`, `SESSIONS`, serverless feature views |
| 4 h | `TABLE_QUERY_PRUNING_HISTORY`, `COLUMN_QUERY_PRUNING_HISTORY` |
| 6 h | cloud services credits, `TABLE_PRUNING_HISTORY`, `TABLE_DML_HISTORY`, `SEARCH_OPTIMIZATION_BENEFITS` |
| 8 h | `QUERY_ATTRIBUTION_HISTORY`, `ANOMALIES_DAILY`, `MODEL_SERVING_USAGE_HISTORY` |
| 12 h | `SNOWPIPE_STREAMING` metering, `SNOWPIPE_STREAMING_FILE_MIGRATION_HISTORY` |
| 72 h | OU billing (`USAGE_IN_CURRENCY_DAILY`, `REMAINING_BALANCE_DAILY`); values can change until month end (`IS_ADJUSTMENT`) |

## Join keys
| From | To | Key | Watch |
|---|---|---|---|
| `QUERY_HISTORY` | `QUERY_ATTRIBUTION_HISTORY`, `ACCESS_HISTORY`, `QUERY_INSIGHTS`, `QUERY_ACCELERATION_ELIGIBLE`, `EXTERNAL_ACCESS_HISTORY`, `CORTEX_AI_FUNCTIONS_USAGE_HISTORY`, `TASK_HISTORY.QUERY_ID`, `DYNAMIC_TABLE_REFRESH_HISTORY.QUERY_ID`, `LOCK_WAIT_HISTORY` | `QUERY_ID` | aggregate attribution per `QUERY_ID` first; read `QUERY_HISTORY` one day wider so a query that started before the window still joins; `EXTERNAL_ACCESS_HISTORY` has one row per IP |
| child query | its caller (procedure, task) | `PARENT_QUERY_ID`, `ROOT_QUERY_ID` (attribution, access history) | roll up by `COALESCE(ROOT_QUERY_ID, QUERY_ID)`: `ROOT_QUERY_ID` is NULL for a query without a parent |
| `QUERY_HISTORY` | `SESSIONS` → `LOGIN_HISTORY` | `SESSION_ID`; `SESSIONS.LOGIN_EVENT_ID = LOGIN_HISTORY.EVENT_ID` | `SESSIONS` skips SQL API transient and system sessions |
| any warehouse view | `WAREHOUSE_METERING_HISTORY`, `WAREHOUSE_LOAD_HISTORY`, `WAREHOUSE_EVENTS_HISTORY`, `SHOW WAREHOUSES` | `WAREHOUSE_ID` (name in SHOW) | `QUERY_HISTORY.WAREHOUSE_ID` vs SHOW `"name"`: join SHOW by name, live warehouses only |
| `TABLES.TABLE_ID` | `TABLE_STORAGE_METRICS.ID`, `TABLE_PRUNING_HISTORY`, `TABLE_QUERY_PRUNING_HISTORY`, `COLUMN_QUERY_PRUNING_HISTORY`, `AUTOMATIC_CLUSTERING_HISTORY`, `TABLE_DML_HISTORY`, `SEARCH_OPTIMIZATION_BENEFITS.TABLE_ID`, `SEARCH_OPTIMIZATION_HISTORY.BASE_TABLE_ID`, `COPY_HISTORY.TABLE_ID` | table id | TABLE_STORAGE_METRICS key is `ID`; SEARCH_OPTIMIZATION_HISTORY renamed to `BASE_TABLE_ID` (read both while the change rolls out) |
| `ACCESS_HISTORY` objects | `TABLES`, `COLUMNS` | `objectId` = `TABLE_ID` (with `objectDomain`), `columnId` = `COLUMNS.COLUMN_ID` | FLATTEN the arrays; names upper-case |
| `OBJECT_DEPENDENCIES` | `TABLES` | `REFERENCED_OBJECT_ID` / `REFERENCING_OBJECT_ID` + `*_OBJECT_DOMAIN` | `REFERENCED_OBJECT_ID` NULL for shared objects |
| `USERS.NAME` | `QUERY_HISTORY.USER_NAME`, `LOGIN_HISTORY.USER_NAME`, `GRANTS_TO_USERS.GRANTEE_NAME` | user name | `USERS` keeps dropped users (`DELETED_ON`); LOGIN_HISTORY user can be NULL on early failures |
| `GRANTS_TO_ROLES` | itself (role tree), `GRANTS_TO_USERS` | `NAME` (role granted) → `GRANTEE_NAME` (role that receives it) where `GRANTED_ON IN ('ROLE','DATABASE_ROLE') AND PRIVILEGE = 'USAGE'` | `GRANTED_TO` reads `'ROLE'` or `'ACCOUNT ROLE'`: match both. check: grants_to_roles (the page does not describe role rows) |
| `POLICY_REFERENCES` | `MASKING_POLICIES`, `ROW_ACCESS_POLICIES` | `POLICY_ID` | role-filtered; no authentication, password or session policies |
| `TAG_REFERENCES` | `TABLES`, `COLUMNS`, warehouses | `OBJECT_ID` + `DOMAIN` (+ `COLUMN_ID`) | direct assignments only, no inheritance; `OBJECT_DELETED IS NULL` |
| `METERING_DAILY_HISTORY` | `WAREHOUSE_METERING_HISTORY` | `USAGE_DATE` = `CAST(START_TIME AS DATE)` in UTC | needs `TIMEZONE = 'UTC'` in the session |
| OU `USAGE_IN_CURRENCY_DAILY` | OU `RATE_SHEET_DAILY`, `METERING_DAILY_HISTORY` | `ACCOUNT_LOCATOR` (+ `USAGE_DATE`/`DATE`, `SERVICE_TYPE`) | reduce rates to one row per key before joining |

## Grain
- Hourly per warehouse: `WAREHOUSE_METERING_HISTORY`. Daily per service: `METERING_DAILY_HISTORY` (one row per day and `SERVICE_TYPE`, account-wide). Hourly per service and entity: `METERING_HISTORY`.
- Per query: `QUERY_HISTORY` (one row per statement, including child statements of procedures). `QUERY_METERING_HISTORY`: one row per query and metering hour (adaptive warehouses) - never count its rows as queries.
- Per 5 minutes per warehouse: `WAREHOUSE_LOAD_HISTORY` (load ratios: average or peak them, never sum).
- Per minute per parameterized hash: `AGGREGATE_QUERY_HISTORY`, `AGGREGATE_ACCESS_HISTORY` (metrics are OBJECTs: `col:sum::NUMBER`).
- Per version: object views (`TABLES`, `VIEWS`, `DATABASES`, `PIPES`) keep a row per object and dropped versions; filter `DELETED IS NULL` for live, group by ID.
- Per event: `WAREHOUSE_EVENTS_HISTORY` (STARTED and COMPLETED rows, cluster and warehouse level: filter `EVENT_STATE = 'COMPLETED' AND CLUSTER_NUMBER IS NULL` for one row per warehouse action).

## Types that need a cast
- VARCHAR numbers: `MATERIALIZED_VIEW_REFRESH_HISTORY.CREDITS_USED`, `SERVERLESS_TASK_HISTORY.CREDITS_USED` → `TRY_TO_DOUBLE(...)`.
- VARIANT: `RESOURCE_MONITORS.CREDIT_QUOTA`, `USED_CREDITS`; `DATA_TRANSFER_HISTORY.BYTES_TRANSFERRED` (AU and OU); `PIPE_USAGE_HISTORY.FILES_INSERTED`; `EXTERNAL_ACCESS_HISTORY.SENT_BYTES`, `RECEIVED_BYTES`; `USERS.DISABLED` → `TRY_TO_DOUBLE(TO_VARCHAR(x))` or `x::BOOLEAN`.
- YES/NO text: `TABLES.IS_TRANSIENT`, `IS_ICEBERG`, `IS_DYNAMIC`, `IS_HYBRID`, `AUTO_CLUSTERING_ON`; `SCHEMATA.IS_MANAGED_ACCESS`; `LOGIN_HISTORY.IS_SUCCESS`; `PIPES.IS_AUTOINGEST_ENABLED`.
- `ERROR_CODE` is NUMBER in `QUERY_HISTORY` and `LOGIN_HISTORY`, VARCHAR in `TASK_HISTORY`. `TASK_HISTORY.ROOT_TASK_ID` is VARCHAR.
- `DELETED` is BOOLEAN in `TABLE_STORAGE_METRICS`, a timestamp elsewhere.
- JSON in text: `LOGIN_HISTORY.LOGIN_DETAILS`, `SESSIONS.CLIENT_ENVIRONMENT` → `PARSE_JSON`.

## Missing or replaced views
| Asked for | Use |
|---|---|
| `AU.STREAMS` | `SHOW STREAMS IN ACCOUNT` (`stale`, `stale_after`, `mode`) |
| `AU.DYNAMIC_TABLES` | `TABLES WHERE IS_DYNAMIC = 'YES'`, `SHOW DYNAMIC TABLES`; history in `DYNAMIC_TABLE_REFRESH_HISTORY` |
| `AU.EXTERNAL_TABLES`, `AU.ICEBERG_TABLES` | `TABLES` (`TABLE_TYPE = 'EXTERNAL TABLE'`, `IS_ICEBERG = 'YES'`), `SHOW EXTERNAL TABLES` / `SHOW ICEBERG TABLES IN ACCOUNT` |
| `AU.AUTHENTICATION_POLICIES` | `SHOW AUTHENTICATION POLICIES` then `DESCRIBE AUTHENTICATION POLICY` |
| budgets | no view: `CALL ...!GET_SPENDING_HISTORY(...)` is a CALL → user-run only |
| `REPLICATION_USAGE_HISTORY` | deprecated → `REPLICATION_GROUP_USAGE_HISTORY` (target account only) |
| `CORTEX_FUNCTIONS_*`, `CORTEX_AISQL_USAGE_HISTORY` | `CORTEX_AI_FUNCTIONS_USAGE_HISTORY`; never add old and new together (date ranges overlap) |
| `EVENT_USAGE_HISTORY` | `METERING_*` with `SERVICE_TYPE = 'TELEMETRY_DATA_INGEST'` |
| per-stage bytes | `STAGE_STORAGE_USAGE_DETAILS` (90 days, AWS and Azure, days missing = unknown) |

## Visibility probe (put before an answer that could come back empty)
```sql
-- Can this role read the views the answer needs? 0 rows from the view itself proves nothing.
SELECT 'WAREHOUSE_METERING_HISTORY' AS src, COUNT(*) AS rows_7d
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
UNION ALL
SELECT 'ACCESS_HISTORY', COUNT(*)
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE query_start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP());
```
- Error "does not exist or not authorized" → no access: name the database role needed.
- 0 rows on a view that every active account fills (metering, query history) → access is partial or the account is idle; check `SHOW WAREHOUSES` and `CURRENT_ROLE()`.
- Enterprise-only views on Standard edition exist but stay empty: `ACCESS_HISTORY`, `MATERIALIZED_VIEW_REFRESH_HISTORY`, `SEARCH_OPTIMIZATION_*`, `QUERY_ACCELERATION_HISTORY`, `TAG_REFERENCES`, masking and row access policies. Empty is not "good".
- Role-filtered AU views: `RESOURCE_MONITORS`, `COPY_HISTORY`, `PIPES`, `STAGES`, `SCHEMATA`, `FUNCTIONS`, `PROCEDURES`, `TAGS`, `TAG_REFERENCES`, `MASKING_POLICIES`, `POLICY_REFERENCES`, `NETWORK_RULES`, `COMPLETE_TASK_GRAPHS`, `TASKS`. Cross-check: warehouses that billed in `WAREHOUSE_METERING_HISTORY` but are missing from `SHOW WAREHOUSES` = hidden from this role.

## Window pattern
```sql
WITH p AS (SELECT 30 AS days, CURRENT_DATE() AS end_date)   -- end_date is exclusive: today left out
SELECT ...
FROM SNOWFLAKE.ACCOUNT_USAGE.<VIEW> v, p
WHERE v.start_time >= DATEADD(day, -p.days, p.end_date) AND v.start_time < p.end_date
```
- Day series with no usage: build a spine (`SELECT DATEADD(day, -ROW_NUMBER() OVER (ORDER BY SEQ4()), p.end_date) AS d FROM TABLE(GENERATOR(ROWCOUNT => 400)), p`; `SEQ4()` alone can skip numbers) and LEFT JOIN, so a quiet day counts as 0 in averages and medians.
- Period over period: same length windows, both inside retention; label a window partial when its end is within the view's latency.
